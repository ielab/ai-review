# Import
import json, logging, random
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer
from langchain_google_genai import GoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from asgiref.sync import sync_to_async
from django.utils import timezone

# Logger
logger = logging.getLogger(__name__)


# Class
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Accepts the WebSocket connection and initializes the LLM model."""
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.review_id = self.scope['url_route']['kwargs']['review_id']
        self.room_group_name = f'chat_{self.user_id}_{self.review_id}'

        # Get study context info from query string using Django's built-in parser
        from urllib.parse import parse_qs
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        query_params = parse_qs(query_string)

        # parse_qs returns lists, so we get the first value of each parameter
        self.page_index = int(query_params.get('page_index', [0])[0]) if query_params.get('page_index') else None
        self.study_index = int(query_params.get('study_index', [0])[0]) if query_params.get('study_index') else None

        logger.info(f"[WebSocket Params] Page: {self.page_index}, Study: {self.study_index}")

        # Add the channel to the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Fetch context and LLM config from Review/study
        self.study_context, self.llm_config, self.study_pmid = await self.get_study_context(
            self.review_id, self.user_id, self.page_index, self.study_index
        )

        logger.info(f"[Chat Session] User: {self.user_id}, Review: {self.review_id}, PMID: {self.study_pmid}")

        # Create or load chat session for this user/review/study
        self.chat_session = await self.get_or_create_session()

        # Use LLM config from review
        self.llm = ChatOpenAI(
            model=self.llm_config.get("model_name", "gpt-4o"),
            api_key=settings.OPENAI_API_KEY,
            temperature=self.llm_config.get("temperature", 0),
            max_tokens=self.llm_config.get("max_tokens", 2048),
        )

        self.output_parser = StrOutputParser()

    @sync_to_async
    def get_study_context(self, review_id, user_id, page_index=None, study_index=None):
        from review.models import Review
        review = Review.objects.get(id=review_id, user_id=user_id)
        study_pmid = None
        study = {}
        context = {}

        # Extract study data based on structure type
        if review.structure_type == "page_based" and page_index is not None and study_index is not None:
            try:
                study = review.screening_pages["pages"][page_index]["studies"][study_index]
                study_pmid = study.get("pmid")
            except (KeyError, IndexError):
                logger.error(f"Study not found at page {page_index}, study {study_index}")

        elif review.structure_type == "study_centric" and page_index is not None:
            # For study_centric, use page_index as direct study index in the studies array
            try:
                study = review.screening_pages["studies"][page_index]
                study_pmid = study.get("pmid")
            except (KeyError, IndexError):
                logger.error(f"Study not found at index {page_index} in study_centric structure")
        else:
            logger.error(
                f"Invalid parameters: structure={review.structure_type}, page_index={page_index}, study_index={study_index}")

        # Collect context fields if they exist
        for field in ["ask_ai_response", "detailed_reasoning", "pico_extraction", "post_response", "user_feedback"]:
            if field in study:
                context[field] = study[field]
        context["title"] = study.get("title", "")
        context["abstract"] = study.get("abstract", "")
        context["authors"] = study.get("authors", "")
        context["inclusion_criteria"] = review.inclusion_criteria
        return context, review.llm_parameters, study_pmid

    @sync_to_async
    def get_or_create_session(self):
        from .models import ChatSession
        from review.models import Review
        from account.models import User
        user = User.objects.get(id=self.user_id)
        review = Review.objects.get(id=self.review_id)
        session, _ = ChatSession.objects.get_or_create(
            user=user, review=review, study_pmid=self.study_pmid,
            defaults={"history": []}
        )
        return session

    @sync_to_async
    def save_message(self, role, content):
        from .models import ChatSession
        session = ChatSession.objects.get(user_id=self.user_id, review_id=self.review_id, study_pmid=self.study_pmid)
        history = session.history or []
        history.append({
            "role": role,
            "content": content,
            "timestamp": timezone.now().isoformat()
        })
        session.history = history
        session.save()

    def determine_context_prompt(self):
        """Determine which prompt to use and collect all existing co responses"""

        # Check for co (collaborative) responses - these are cumulative
        co_responses = []

        # Add ask_ai if exists
        if self.study_context.get('ask_ai_response'):
            co_responses.append({
                "prompt_type": "co_ask_ai_prompt",
                "response": self.study_context.get('ask_ai_response')
            })

        # Add pico_extract if exists
        if self.study_context.get('pico_extraction'):
            co_responses.append({
                "prompt_type": "co_pico_extract_prompt",
                "response": self.study_context.get('pico_extraction')
            })

        # Add detail_reason if exists
        if self.study_context.get('detailed_reasoning'):
            co_responses.append({
                "prompt_type": "co_detail_reason_prompt",
                "response": self.study_context.get('detailed_reasoning')
            })

        # Check for post response (separate system prompt)
        if self.study_context.get('post_response'):
            return {
                "prompt_type": "post_prompt",
                "co_responses": [],  # Post doesn't include co responses
                "post_response": self.study_context.get('post_response')
            }

        # Return co context (use ask_ai prompt as base since they share same system)
        return {
            "prompt_type": "co_ask_ai_prompt",  # Base co prompt for system message
            "co_responses": co_responses,
            "post_response": None
        }

    @sync_to_async
    def get_prompt_config(self, prompt_type):
        from review.models import MasterPromptConfig
        # Fetch the correct system prompt from MasterPromptConfig for the current task
        try:
            prompt_config = MasterPromptConfig.objects.get(
                user_id=self.user_id,
                review_id=self.review_id,
                prompt_type=prompt_type
            )
        except MasterPromptConfig.DoesNotExist:
            prompt_config = None
        return prompt_config

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"[WebSocket Closed] Code: {close_code}")

    async def receive(self, text_data):
        try:
            # Parse user message
            text_data_json = json.loads(text_data)
            message = text_data_json.get("message", "").strip()
            current_task = text_data_json.get("task", "ask_ai")  # Default to ask_ai if not provided
            logger.info(f"[User Message] {message} (task: {current_task})")

            if not message:
                await self.send(json.dumps({"error": "Empty message received"}))
                return

            # Save user message to chat history
            await self.save_message("user", message)

            # Always fetch the latest context and LLM config from DB before each LLM call
            self.study_context, self.llm_config, self.study_pmid = await self.get_study_context(
                self.review_id, self.user_id, self.page_index, self.study_index
            )

            # Determine which prompt to use based on existing responses
            context_info = self.determine_context_prompt()
            prompt_type = context_info["prompt_type"]
            co_responses = context_info["co_responses"]
            post_response = context_info["post_response"]

            prompt_config = await self.get_prompt_config(prompt_type)
            if not prompt_config:
                await self.send(json.dumps({"error": f"Prompt config for {prompt_type} not found."}))
                return

            # Get system template and assistant template
            system_template = prompt_config.prompt_content.get("system", "")

            logger.info(
                f"[Context] Using {prompt_type}, co_responses: {len(co_responses)}, post_response: {bool(post_response)}")
            logger.info(f"[System Template] {system_template[:100]}...")

            # Build conversation messages
            messages = [("system", system_template)]

            if co_responses or post_response:
                # We have existing responses - build cumulative conversation

                # Add each co response as user prompt + assistant response
                for co_resp in co_responses:
                    # Get the specific prompt template for this response type
                    co_prompt_config = await self.get_prompt_config(co_resp["prompt_type"])
                    if co_prompt_config:
                        co_assistant_template = co_prompt_config.prompt_content.get("assistant", "")
                        try:
                            co_user_prompt = co_assistant_template.format(
                                title=self.study_context.get('title', ''),
                                abstract=self.study_context.get('abstract', ''),
                                authors=self.study_context.get('authors', ''),
                                inclusion_criteria=self.study_context.get('inclusion_criteria', ''),
                                ask_ai_response=self.study_context.get('ask_ai_response', ''),
                                detailed_reasoning=self.study_context.get('detailed_reasoning', ''),
                                pico_extraction=self.study_context.get('pico_extraction', ''),
                                post_response=self.study_context.get('post_response', ''),
                                user_feedback=self.study_context.get('user_feedback', ''),
                                rating=self.study_context.get('rating', ''),
                                decision=self.study_context.get('decision', ''),
                            )
                            messages.append(("user", co_user_prompt))
                            messages.append(("assistant", co_resp["response"]))
                            logger.info(f"[Added Context] {co_resp['prompt_type']}: {co_resp['response'][:100]}...")
                        except KeyError as e:
                            logger.error(f"[Template Error in {co_resp['prompt_type']}] Missing variable: {e}")

                # Add post response if exists
                if post_response:
                    post_prompt_config = await self.get_prompt_config("post_prompt")
                    if post_prompt_config:
                        post_assistant_template = post_prompt_config.prompt_content.get("assistant", "")
                        try:
                            post_user_prompt = post_assistant_template.format(
                                title=self.study_context.get('title', ''),
                                abstract=self.study_context.get('abstract', ''),
                                authors=self.study_context.get('authors', ''),
                                inclusion_criteria=self.study_context.get('inclusion_criteria', ''),
                                decision=self.study_context.get('decision', ''),
                            )
                            messages.append(("user", post_user_prompt))
                            messages.append(("assistant", post_response))
                            logger.info(f"[Added Context] post_prompt: {post_response[:100]}...")
                        except KeyError as e:
                            logger.error(f"[Template Error in post_prompt] Missing variable: {e}")

                # Add current user question
                messages.append(("user", "{input}"))

            else:
                # No existing responses, start fresh with ask_ai prompt
                assistant_template = prompt_config.prompt_content.get("assistant", "")
                try:
                    formatted_initial_prompt = assistant_template.format(
                        title=self.study_context.get('title', ''),
                        abstract=self.study_context.get('abstract', ''),
                        authors=self.study_context.get('authors', ''),
                        inclusion_criteria=self.study_context.get('inclusion_criteria', ''),
                        ask_ai_response=self.study_context.get('ask_ai_response', ''),
                        detailed_reasoning=self.study_context.get('detailed_reasoning', ''),
                        pico_extraction=self.study_context.get('pico_extraction', ''),
                        post_response=self.study_context.get('post_response', ''),
                        user_feedback=self.study_context.get('user_feedback', ''),
                        rating=self.study_context.get('rating', ''),
                        decision=self.study_context.get('decision', ''),
                    )
                    full_user_message = f"{formatted_initial_prompt}\n\nUser Question: {message}"
                    messages.append(("user", "{input}"))
                except KeyError as e:
                    logger.error(f"[Template Error] Missing variable: {e}")
                    await self.send(json.dumps({"error": f"Missing template variable: {e}"}))
                    return

            # Create LLM processing chain
            chain = (
                    ChatPromptTemplate.from_messages(messages) |
                    self.llm.with_config({"run_name": "model"}) |
                    self.output_parser.with_config({"run_name": "Assistant"})
            )

            # Determine input message format
            if co_responses or post_response:
                # Continuing conversation - just use the user's new message
                input_message = message
            else:
                # Starting fresh - use formatted prompt + user message
                input_message = full_user_message

            # Stream responseAdd commentMore actions
            await self.streaming_response(chain, input_message)


        except json.JSONDecodeError:
            await self.send(json.dumps({"error": "Invalid JSON format"}))

        except Exception as e:
            logger.error(f"[ChatConsumer Error] {str(e)}", exc_info=True)
            await self.send(json.dumps({"error": f"An error occurred: {str(e)}"}))

    async def streaming_response(self, chain, message):
        # Stream response
        response_text = ""
        try:
            # Try streaming first
            logger.info("[Streaming] Starting LLM stream...")

            async for chunk in chain.astream_events(
                    {"input": message}, version="v1", include_names=["Assistant"]
            ):
                # event_type = chunk.get("event", "")
                # logger.info(f"[Stream Event] {event_type}")

                if chunk["event"] in ["on_parser_start", "on_parser_stream", "on_parser_end"]:
                    chunk_data = chunk.get("data", {})
                    event_type = chunk.get("event", "")

                    safe_data = {}
                    if event_type == "on_parser_end":
                        # on_parser_end just marks the end of streaming - don't send additional content
                        # All content should have already been sent via on_parser_stream events
                        safe_data["chunk"] = ""
                    else:
                        # on_parser_start and on_parser_stream
                        if isinstance(chunk_data, dict) and "chunk" in chunk_data:
                            # Extract just the chunk text if it's a string
                            chunk_text = chunk_data.get("chunk", "")
                            if isinstance(chunk_text, str):
                                safe_data["chunk"] = chunk_text
                            else:
                                safe_data["chunk"] = str(chunk_text) if chunk_text else ""
                        else:
                            safe_data["chunk"] = ""

                serializable_chunk = {
                    "event": chunk.get("event"),
                    "name": chunk.get("name", ""),
                    "data": safe_data
                }
                await self.send(json.dumps(serializable_chunk))
                response_text += chunk.get("data", {}).get("chunk", "")

        except Exception as e:
            logger.error(f"[Streaming Error] {e}", exc_info=True)
            response_text = "Sorry, I encountered an error processing your request."
        #
        logger.info(f"[LLM Response] {response_text[:100]}..." if len(response_text) > 100 else f"[LLM Response] {response_text}")

        # Save assistant response to chat history
        await self.save_message("assistant", response_text)