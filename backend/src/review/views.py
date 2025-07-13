# Import
import logging, os, traceback, json, shutil, uuid
from rest_framework.views import APIView
from django.http import JsonResponse
from django.conf import settings
from django.utils.timezone import now
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import concurrent.futures
from functools import partial
import time
import tiktoken
from statistics import mean
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import pandas as pd

# Import Django utility
from .models import Review, MasterPromptConfig
from .serializers import StudySerializer, StudyCardSerializer, InferenceReview
from .utils import *
from max.llm_screen_single_prompt import ScreeningAPI
from urllib.parse import quote

# logger
logger = logging.getLogger(__name__)


# StudyListAPIView Class
class StudyListAPIView(APIView):
    # # Permission
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Query data from the Review table for the current user only
            study_obj = Review.objects.filter(user_id=request.user.id).order_by('id')

            # Serialize the data
            serializer = StudySerializer(study_obj, many=True)

            # Message
            msg = f"Got Review list of user({request.user.id})"
            # msg = f"Got Review list of user"

            # Return the serialized data as a response
            logger.info(msg)
            return JsonResponse(
                data={"message": msg, "data": serializer.data}, status=status.HTTP_200_OK
            )

        except Exception as error:
            logger.error(f"Couldn't get dataset list for user({request.user.id}): {error}\n{traceback.format_exc()}")
            # logger.error(f"Couldn't get dataset list for user: {error}\n{traceback.format_exc()}")
            return JsonResponse(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StudyCardView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Get studies for document cards on screening UI.
        Compatible with both page-based and study-centric structures.
        """
        try:
            # Extract parameters from request
            review_id = request.data.get('review_id')
            page_index = int(request.data.get('page_index', 0))

            # Validate required parameters
            if not review_id:
                raise ValueError("Missing required parameter: 'review_id'")

            # Get review object
            review_obj = Review.objects.get(id=review_id, user=request.user)

            # Get paginated studies using the unified function
            page_data = get_paginated_studies(review_obj, page_index)

            # Add structure type to response
            structure_info = {
                "structure_type": review_obj.structure_type,
                "dataset_name": review_obj.name
            }

            msg = f"Successfully retrieved studies for review({review_id}) page({page_index})"
            logger.info(msg)

            return JsonResponse(
                data={
                    "message": msg,
                    "data": {
                        "studies": page_data["studies"],
                        "pagination": page_data["pagination"],
                        **structure_info
                    }
                },
                status=status.HTTP_200_OK
            )

        except Review.DoesNotExist:
            msg = f"Review({review_id}) not found"
            logger.error(msg)
            return JsonResponse(
                {"error": msg},
                status=status.HTTP_404_NOT_FOUND
            )

        except ValueError as error:
            logger.error(f"Validation error: {error}")
            return JsonResponse(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as error:
            logger.error(f"Error retrieving studies: {error}\n{traceback.format_exc()}")
            return JsonResponse(
                {"error": "Failed to retrieve studies"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetStudyByIdView(APIView):
    # Uncomment the following line if authentication is required
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Extract data from the POST request
            pmid = request.data.get('pmid', None)
            project_field = request.data.get('project_field', None)

            # Validate inputs
            if not pmid or not project_field:
                raise ValueError("Both 'id' and 'project' fields are required.")

            if project_field not in ["ask_ai_response", "detailed_reasoning", "pico_extraction"]:
                raise ValueError(f"Invalid project field '{project_field}'.")

            # Query the Review model by ID
            try:
                study_obj = Review.objects.get(id=int(pmid))
            except Review.DoesNotExist:
                msg = f"Review with ID {pmid} not found."
                logger.error(msg)
                return JsonResponse({"error": msg}, status=status.HTTP_404_NOT_FOUND)

            # Serialize the Review data with project_field passed in the context
            serializer = InferenceReview(study_obj, context={'project_field': project_field})

            if serializer is None:
                raise ValueError(f"The project field '{project_field}' does not exist in the Review.")

            msg = f"Got review dataset ({study_obj.id}) of user ({request.user.id}) with process '{project_field}'."
            logger.info(msg)
            return JsonResponse(data={"message": msg, "data": serializer.data}, status=status.HTTP_200_OK)

        except ValueError as ve:
            logger.error(f"Validation Error: {str(ve)}")
            return JsonResponse({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Unexpected Error: {str(e)}")
            return JsonResponse({"error": "An unexpected error occurred."},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FileUploadView(APIView):
    # Permission
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle file upload.
            @body       nbib_file       File        A .nbib file
            @return     JsonResponse    Success message including the created corpus object
        """
        try:
            # Upload file
            nbib_file = request.FILES.get("nbib_file", None)
            corpus_obj = None

            # Format user id
            format_user_id = f"u{request.user.id:0{5}d}"

            # Create user's directory
            creat_user_dir(user=request.user, format_user_id=format_user_id)

            # Clean user temp folder (clear temp files after 24 hr.)
            clear_temp_folder(user=request.user, format_user_id=format_user_id)

            # Validate .nbib file & check duplicated in temp
            validate_upload_file(format_user_id=format_user_id, nbib_file=nbib_file)

            # Create new Corpus
            corpus_obj = Corpus.objects.create(user=request.user, status="active")
            format_corpus_id = f"c{corpus_obj.id:0{5}d}"

            # Save file into database and local storage
            path_to_temp_file, save_corpus_filename, upload_folder = save_temp_file(
                user=request.user,
                format_user_id=format_user_id,
                format_corpus_id=format_corpus_id,
                nbib_file=nbib_file
            )

            # logger
            logger.info(
                f"User({request.user}) successfully uploaded nbib file ({nbib_file.name}) to temporarily folder.")

            # Call Max's function
            if settings.BYPASS_EXTERNAL_SERVICE:
                # Save file to corpus folder (move from temp)
                parse_corpus(corpus_nbib_path=path_to_temp_file, corpus_file=save_corpus_filename)

                # Hash corpus path
                hash_corpus = hash_blake2s_32digit(key=str(request.user.id), value=save_corpus_filename)

                # Preview corpus
                preview = preview_corpus(path_to_temp_file, 1)[0]

                # Save path file into database
                corpus_obj.hash_corpus_path = hash_corpus
                corpus_obj.real_corpus_path = save_corpus_filename
                corpus_obj.corpus_first_entry = preview
                corpus_obj.save()

                # Validate unique pmid in uploaded file
                validate_unique_pmid(corpus_path=save_corpus_filename)

                # Successful message
                msg = f"Successfully insert corpus({corpus_obj.id}) into database."
                logger.info(msg)

                # Move file from temp
                shutil.move(path_to_temp_file, upload_folder)
                logger.info(f"Move file('{path_to_temp_file}') from temp to {upload_folder}.")

                # Create corpus for tevatron
                pmids = corpus_converter(corpus_path=save_corpus_filename)

                # Save corpus for tevatron into database
                corpus_obj.pmids = pmids
                corpus_obj.save()

            # Returning data
            data = {
                "preview_uploaded_corpus": {"id": corpus_obj.id, "corpus_first_entry": preview},
                "total_documents": len(pmids)
            }

            # Return
            return JsonResponse(
                data = {"message": msg,
                        "data": data,},
                status=status.HTTP_200_OK
            )

        # Exception ValueError
        except ValueError as error:
            # Update corpus status
            if corpus_obj:
                corpus_obj.status = "upload_failed"
                corpus_obj.save()

            # logger
            logger.error(f"user({request.user}) failed to upload nbib file: {error}")
            return JsonResponse(
                {"error": f"user({request.user}) failed to upload nbib file: {error}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Exception FileExistsError
        except FileExistsError as error:
            # Update corpus status
            if corpus_obj:
                corpus_obj.status = "upload_failed"
                corpus_obj.save()

            # logger
            logger.error(f"user({request.user}) failed to upload nbib file: {error}")
            return JsonResponse(
                {"error": f"user({request.user}) failed to upload nbib file: {error}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Exception Other error
        except Exception as error:
            # Update corpus status
            if corpus_obj:
                corpus_obj.status = "upload_failed"
                corpus_obj.save()

            # logger
            logger.error(f"Error while uploading nbib file")
            return JsonResponse(
                {"error": f"Error while uploading nbib file: {error}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request):
        """
        Delete corpus row and its files from VM storage
            @query_param        corpus_id           Corpus ID
            @return             JsonResponse        Success message
        """
        try:
            corpus_id = request.query_params.get("corpus_id")

            # Set the corpus status to 'admin_delete'
            corpus_obj = Corpus.objects.get(id=corpus_id)
            corpus_obj.status = "admin_delete"
            corpus_obj.save()

            # User corpus directory
            user_corpus_dir = os.path.join(f"{settings.MOUNT_CORPUS_PATH}", f"u{request.user.id:0{5}d}", "corpus",
                                           f"c{corpus_obj.id:0{5}d}", "upload")

            # Delete the files from local storaage
            corpus_dir = corpus_obj.real_corpus_path

            # Delete the files from local storage
            for f in [user_corpus_dir, corpus_dir]:
                remove_file_from_local_storage(f)

            # Message
            msg = f"User({request.user.id}) has deleted corpus({corpus_id}) of user({corpus_obj.user.id})."
            logger.info(msg)
            return JsonResponse({"message": msg}, status=status.HTTP_200_OK)

        except Corpus.DoesNotExist as error:
            logger.error(
                f"corpus({corpus_id}) does not exist for user({request.user.id}): {error}"
            )
            return JsonResponse({"error": str(error)}, status=status.HTTP_404_NOT_FOUND)

        except Exception as error:
            logger.error(
                f"Couldn't delete corpus({corpus_id}) of user({request.user.id}): {error}\n{traceback.format_exc()}"
            )
            return JsonResponse(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DatasetCreationView(APIView):
    # Permission
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Dataset creation.
            @body       inclusion_criteria   Criteria for including studies in the review |

            @return     JsonResponse         Success message
        """
        try:
            # Data from request
            corpus_id = request.data.get('corpus_id', None)
            dataset_name = request.data.get('dataset_name', None)
            inclusion_criteria = request.data.get('inclusion_criteria', None)

            structure_type = request.data.get('structure_type', 'page_based')  # Default to page-based
            # Default page size depends on structure type
            default_page_size = 25 if structure_type == 'page_based' else 5
            show_docs_per_page = int(request.data.get('show_docs_per_page', default_page_size))

            review_obj = None

            # Validate structure type
            if structure_type not in ['page_based', 'study_centric']:
                raise ValueError(f"Invalid structure type: {structure_type}. Must be 'page_based' or 'study_centric'.")

            # Query corpus
            corpus_obj = Corpus.objects.get(id=corpus_id, user=request.user)
            logger.info(f">>> real corpus path: {corpus_obj.real_corpus_path}")

            # Validated dataset name duplicate
            is_duplicated = Review.objects.filter(name=dataset_name, user=request.user)
            if is_duplicated:
                raise ValueError(f"The collection name({dataset_name}) is duplicated.")

            # Get number of queue
            n_queue = 1  # get_number_of_queue(queue_name=settings.QUEUE_NAME_1)

            # Initialize screening pages based on structure type
            corpus_json_path = corpus_obj.real_corpus_path
            if structure_type == 'page_based':
                screening_pages = create_page_based_screening_pages(
                    corpus_file=corpus_json_path,
                    page_size=show_docs_per_page
                )
            else:  # study_centric
                screening_pages = create_study_centric_screening_pages(
                    corpus_file=corpus_json_path
                )

            # Create dataset with structure_type field
            review_obj = Review.objects.create(
                user=request.user,
                corpus=corpus_obj,
                name=dataset_name,
                screening_status="not_start",
                structure_type=structure_type,  # Add structure type
                show_docs_per_page=show_docs_per_page,
                inclusion_criteria=inclusion_criteria,
                pos_at_waiting_queue=n_queue,
                screening_pages=screening_pages
            )
            review_obj.save()

            # Message
            msg = f"Your corpus (ID: {corpus_obj.id}) with the name '{review_obj.name}' has been created."
            logger.info(msg)

            # Return
            return JsonResponse(data={"message": msg}, status=status.HTTP_200_OK)

        except ValueError as error:
            # Message
            msg = f"Invalid input for dataset creation: {error}"

            # Update review status
            if review_obj:
                review_obj.index_status = "indexing_error"
                review_obj.indexing_error_msg = msg

            # logging and return
            logger.error(msg)
            return JsonResponse(
                {"error": str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as error:
            # Update review status
            if review_obj:
                review_obj.index_status = "indexing_error"
                review_obj.indexing_error_msg = str(error)

            logger.error(
                f"Couldn't create dataset for '{dataset_name}' of user({request.user.id}): {error}\n{traceback.format_exc()}"
            )
            return JsonResponse(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LlmConfigView(APIView):
    # Permission
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Save LLM configurations for a selected dataset.
            @body       review_id           ID of the review entry
                        pipeline_type |
                        llm_interaction_level |
            @return     JsonResponse         Success message

        """
        try:
            # Extract data from request
            review_id = request.data.get("review_id", None)
            llm_paras_str = request.data.get("llm_parameters", None)

            # Validate required fields
            if not review_id or not llm_paras_str:
                raise ValueError("Missing required fields: 'review_id' or 'llm_paras'.")

            # Parse llm_paras from JSON string
            try:
                llm_parameters = json.loads(llm_paras_str)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format in 'llm_paras'.")

            # Fetch the existing Review entry
            review_obj = get_object_or_404(Review, id=review_id, user=request.user)

            review_obj.llm_parameters = llm_parameters
            # Extract & Save Review fields (pipeline type & AI interaction level)
            review_obj.pipeline_type = request.data.get("pipeline_type", None)
            review_obj.llm_interaction_level = request.data.get("llm_interaction_level", None)

            # Validate required fields
            if review_obj.pipeline_type is None or review_obj.llm_interaction_level is None:
                raise ValueError("Missing 'pipeline_type' or 'llm_interaction_level' in LLM config.")

            review_obj.save()

            # ✅ Ensure all necessary prompts exist
            loaded_prompts = MasterPromptConfig.ensure_prompts_exist(user=request.user, review=review_obj)

            # Logging success
            msg = f"LLM configuration saved successfully for review ID: {review_id}."
            if loaded_prompts:
                msg += f" Loaded prompts: {', '.join(loaded_prompts)}."

            logger.info(msg)

            # Return success response
            return JsonResponse(
                data={"message": msg},
                status=200
            )

        except ValueError as error:
            # Logging validation error
            logger.error(f"Invalid input for LLM configuration: {error}")
            return JsonResponse(
                {"error": str(error)},
                status=400
            )

        except Exception as error:
            # General error handling
            error_msg = f"Failed to save LLM config for review ID ({review_id}): {error}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return JsonResponse(
                {"error": "Internal Server Error."},
                status=500
            )


class LlmProcessView(APIView):

    # Define processing mode constants
    PROCESSING_MODE_AUTO = 'auto'
    PROCESSING_MODE_SINGLE = 'single'
    PROCESSING_MODE_BATCH = 'batch'

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Process LLM requests for co-review operations.
            @body       review_id           ID of the review entry
                        page_index          Index of the current page
                        study_index         Index of the study in current page (for page-based)
                        pmid                PMID of the study (for study-centric)
                        task                Task type ('ask_ai', 'pico_extract', 'detail_reason', 'pre', 'post')
                        processing_mode     Processing mode ('auto', 'single', 'batch')
                        batch_pre           Boolean, whether to process all studies in current page for pre-review (legacy)
            @return     JsonResponse        Success message with LLM response and performance metrics
        """
        try:
            # Extract data from request
            review_id = request.data.get('review_id')
            page_index = int(request.data.get('page_index', 0))
            # These params will depend on structure type
            # pmid = request.data.get('pmid')  # For study-centric
            study_index = request.data.get('study_index')  # For page-based

            task = request.data.get('task')
            # Legacy parameter (kept for backward compatibility)
            batch_pre = request.data.get('batch_pre', False)

            # New processing mode parameter
            processing_mode = request.data.get('processing_mode', self.PROCESSING_MODE_AUTO)

            # Legacy parameters (map to processing_mode if provided)
            if request.data.get('force_batch', False):
                processing_mode = self.PROCESSING_MODE_BATCH
            elif request.data.get('force_single', False):
                processing_mode = self.PROCESSING_MODE_SINGLE

            # Get review object
            review_obj = Review.objects.get(id=review_id, user=request.user)
            structure_type = review_obj.structure_type

            # Validate required parameters
            if not review_id:
                raise ValueError("Missing required parameter: 'review_id'")

            # Validate task against pipeline type
            pipeline_type = review_obj.pipeline_type
            llm_interaction_level = review_obj.llm_interaction_level
            allowed_tasks = {
                'pre-only': ['pre'],
                'co-only': ['ask_ai', 'pico_extract', 'detail_reason'],
                'post-only': ['post'],
                'pre-co': ['pre', 'ask_ai', 'pico_extract', 'detail_reason'],
                'pre-post': ['pre', 'post'],
                'co-post': ['ask_ai', 'pico_extract', 'detail_reason', 'post'],
                'full': ['pre', 'ask_ai', 'pico_extract', 'detail_reason', 'post']
            }

            if pipeline_type not in allowed_tasks:
                raise ValueError(f"Invalid pipeline type: {pipeline_type}")

            if task not in allowed_tasks[pipeline_type]:
                raise ValueError(
                    f"Task '{task}' not allowed in pipeline '{pipeline_type}'. "
                    f"Allowed tasks are: {', '.join(allowed_tasks[pipeline_type])}"
                )

            # Handle original batch_pre flag for backward compatibility
            if task == 'pre' and batch_pre:
                return self._process_as_batch(review_obj, page_index, task, structure_type)

            # Determine processing mode if set to auto
            if processing_mode == self.PROCESSING_MODE_AUTO:
                should_use_batch = self._should_use_batch_processing(task, llm_interaction_level,
                                                                     pipeline_type, review_obj.show_docs_per_page)
                processing_mode = self.PROCESSING_MODE_BATCH if should_use_batch else self.PROCESSING_MODE_SINGLE

            # Process based on determined mode
            if processing_mode == self.PROCESSING_MODE_BATCH:
                return self._process_as_batch(review_obj, page_index, task, structure_type)

            # Single study processing
            if structure_type == 'page_based':
                # We need page_index and study_index for page-based
                if study_index is None:
                    raise ValueError("study_index is required for page-based structure")

                study_index = int(study_index)
                screening_pages = review_obj.screening_pages
                study = screening_pages["pages"][page_index]["studies"][study_index]

                # Process the study with performance tracking
                performance_metrics, llm_response = self._process_study_with_tracking(
                    review_obj, study, task, page_index, study_index
                )

                msg = f"Successfully processed LLM request for study in page {page_index}, position {study_index}"
                return JsonResponse(
                    data={
                        "message": msg,
                        "data": {
                            "llm_response": llm_response.content,
                            "performance": performance_metrics
                        }
                    },
                    status=status.HTTP_200_OK
                )

            else:  # structure_type == 'study_centric'
                # We need pmid for study-centric
                if not pmid:
                    raise ValueError("pmid is required for study-centric structure")

                # Find the study by PMID
                studies = review_obj.screening_pages.get("studies", [])
                study = next((s for s in studies if s.get("pmid") == pmid), None)

                if not study:
                    raise ValueError(f"Study with PMID {pmid} not found")

                # Process the study with performance tracking
                performance_metrics, llm_response = self._process_study_with_tracking(
                    review_obj, study, task
                )

                msg = f"Successfully processed LLM request for study with PMID {pmid}"
                return JsonResponse(
                    data={
                        "message": msg,
                        "data": {
                            "llm_response": llm_response.content,
                            "performance": performance_metrics
                        }
                    },
                    status=status.HTTP_200_OK
                )

        except ValueError as error:
            logger.error(f"Validation error in LLM processing: {error}")
            return JsonResponse(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except (Review.DoesNotExist, MasterPromptConfig.DoesNotExist) as error:
            logger.error(f"Database object not found: {error}")
            return JsonResponse(
                {"error": str(error)},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as error:
            logger.error(f"Error in LLM processing: {error}\n{traceback.format_exc()}")
            return JsonResponse(
                {"error": "Internal server error occurred during LLM processing."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _should_use_batch_processing(self, task, interaction_level, pipeline_type, show_docs_per_page):
        """
        Determine whether batch processing should be used based on criteria.

        Args:
            task: The LLM task ('pre', 'ask_ai', etc.)
            interaction_level: Boolean indicating high/low interaction
            pipeline_type: The pipeline configuration
            show_docs_per_page: Number of docs per page

        Returns:
            Boolean indicating whether to use batch processing
        """
        # For PRE processing, use batch mode if:
        # - Low interaction level (interaction_level=False), or
        # - Pipeline contains 'pre' and fewer than 10 docs per page
        if task == 'pre':
            # return (not interaction_level) or ('pre' in pipeline_type and show_docs_per_page <= 10)
            return True

        # For POST processing, use batch mode if:
        # - Low interaction level (interaction_level=False), or
        # - Fewer than 5 docs per page
        if task == 'post':
            return (not interaction_level) or show_docs_per_page <= 5

        # For other tasks (ask_ai, pico_extract, detail_reason):
        # Never use batch processing by default
        return False

    def _track_performance(self, review_obj, task, structure_type, start_time, processing_metrics, num_studies):
        """
        Log performance metrics without storing in database.
        This lightweight approach logs metrics but doesn't store them permanently.

        Args:
            review_obj: The Review object
            task: The task being performed
            structure_type: The structure type
            start_time: The start time of the batch
            processing_metrics: List of per-study metrics
            num_studies: Number of studies processed
        """
        # Calculate total values
        total_time = time.time() - start_time

        # Extract metrics from potentially nested structure
        processing_times = []
        total_tokens = 0
        total_cost = 0

        for metric_item in processing_metrics:
            if isinstance(metric_item, dict):
                # If metrics are wrapped in a dict with "metrics" key (batch processing)
                if "metrics" in metric_item and isinstance(metric_item["metrics"], dict):
                    metrics = metric_item["metrics"]
                    if "processing_time" in metrics:
                        processing_times.append(metrics["processing_time"])
                    total_tokens += metrics.get("total_tokens", 0)
                    total_cost += metrics.get("estimated_cost", 0)
                # If metrics are directly at the top level (single processing)
                elif "processing_time" in metric_item:
                    processing_times.append(metric_item["processing_time"])
                    total_tokens += metric_item.get("total_tokens", 0)
                    total_cost += metric_item.get("estimated_cost", 0)

        # Calculate averages
        avg_processing_time = mean(processing_times) if processing_times else 0

        # Calculate parallel efficiency
        sum_individual_times = sum(processing_times) if processing_times else 0
        parallel_efficiency = sum_individual_times / total_time if total_time > 0 else 0

        # Get model name
        model_name = review_obj.llm_parameters.get("model_name", "unknown")

        # Log the performance metrics
        logger.info(f"Performance metrics for {task} on review {review_obj.id}:")
        logger.info(f"  Structure type: {structure_type}")
        logger.info(f"  Model: {model_name}")
        logger.info(f"  Total studies: {num_studies}")
        logger.info(f"  Total time: {total_time:.2f}s")
        logger.info(f"  Average time per study: {avg_processing_time:.2f}s")
        logger.info(f"  Total tokens: {total_tokens}")
        logger.info(f"  Estimated cost: ${total_cost:.6f}")
        logger.info(f"  Parallel efficiency: {parallel_efficiency:.2f}")

        # Return metrics dictionary
        return {
            "total_processing_time": total_time,
            "avg_processing_time": avg_processing_time,
            "total_tokens": total_tokens,
            "total_estimated_cost": total_cost,
            "num_studies_processed": num_studies,
            "parallel_efficiency": parallel_efficiency
        }

    def _count_tokens(self, text, model_name):
        """Count tokens using tiktoken without impacting existing code."""
        try:
            # Get encoding for the model
            if "gpt-4" in model_name:
                encoding_name = "cl100k_base"  # GPT-4 encoding
            elif "gpt-3.5" in model_name:
                encoding_name = "cl100k_base"  # GPT-3.5 encoding
            else:
                encoding_name = "p50k_base"  # Default encoding

            # Get the encoder
            encoding = tiktoken.get_encoding(encoding_name)

            # Count tokens
            tokens = len(encoding.encode(text))
            return tokens
        except Exception as e:
            logger.warning(f"Error counting tokens: {e}")
            # Fallback: estimate 1 token per ~4 characters
            return len(text) // 4

    def _estimate_cost(self, input_tokens, output_tokens, model_name):
        """Estimate cost based on token usage and model."""
        # Cost per 1000 tokens (in USD)
        pricing = {
            "gpt-4o": {"input": 0.0025, "output": 0.01},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
        }

        # Get pricing for model or use gpt-3.5-turbo pricing as fallback
        model_pricing = None
        for model_key in pricing:
            if model_key in model_name:
                model_pricing = pricing[model_key]
                break

        if not model_pricing:
            model_pricing = pricing["gpt-3.5-turbo"]

        # Calculate cost
        input_cost = (input_tokens / 1000) * model_pricing["input"]
        output_cost = (output_tokens / 1000) * model_pricing["output"]
        total_cost = input_cost + output_cost

        return total_cost

    def _get_llm_response(self, review_obj, study, task):
        """
        Get LLM response from the ScreeningAPI.

        Args:
            review_obj: The Review object
            study: The study data
            task: The LLM task

        Returns:
            The LLM response
        """
        # Validate task type
        if task not in ['pre', 'ask_ai', 'pico_extract', 'detail_reason', 'post']:
            raise ValueError(f"Invalid task type: {task}")

        # Get prompt from MasterPromptConfig
        prompt_type_map = {
            'pre': 'pre_prompt',
            'ask_ai': 'co_ask_ai_prompt',
            'pico_extract': 'co_pico_extract_prompt',
            'detail_reason': 'co_detail_reason_prompt',
            'post': 'post_prompt'
        }
        prompt_type = prompt_type_map[task]

        # For post task, verify user_feedback exists and map to Decision
        if task == 'post':
            user_feedback = study.get("user_feedback")
            if user_feedback is None:
                raise ValueError(
                    "Cannot generate post-review without human decision. Please provide include/exclude feedback first.")

            # Map user_feedback to Decision format expected by post prompt
            # decision_map = {
            #     "include": "Include",
            #     "exclude": "Exclude"
            # }
            # study["decision"] = decision_map.get(user_feedback)
            # if not study["decision"]:
            #     raise ValueError(f"Invalid user feedback value: {user_feedback}")

        # For detail_reason task, verify co_rating exists
        elif task == 'detail_reason':
            if study.get("co_rating") is None:
                raise ValueError(
                    "Cannot generate detailed reasoning without a prior rating. Please run 'ask_ai' first.")
            study["rating"] = study["co_rating"]

        # Get prompt config
        prompt_config = MasterPromptConfig.objects.get(
            user=review_obj.user,
            review=review_obj,
            prompt_type=prompt_type
        )

        if not prompt_config or not prompt_config.prompt_content:
            raise ValueError(f"Prompt configuration not found for type: {prompt_type}")

        # Get LLM parameters from review
        llm_params = review_obj.llm_parameters
        if not llm_params:
            raise ValueError("LLM parameters not configured for this review")

        # Format LLM config
        llm_config = {
            "model_name": llm_params["model_name"],
            "temperature": llm_params["temperature"],
            "max_tokens": llm_params["max_tokens"],
            "response_format": {"type": "text"} if llm_params["response_format"] == "text"
            else llm_params["response_format"],
            "streaming": llm_params.get("streaming", True),
            "api_key": settings.OPENAI_API_KEY
        }

        # Initialize ScreeningAPI with LLM config
        screening_api = ScreeningAPI(
            prompt_dir=os.path.join(settings.BASE_DIR, "review", "prompts"),
            llm_config=llm_config
        )

        # Get LLM response
        llm_response = screening_api.screen_study(
            study=study,
            role=task if task in ['pre', 'post'] else 'co',
            task='ask_ai' if task == 'pre' else task,
            inclusion_criteria=review_obj.inclusion_criteria
        )

        return llm_response

    def _get_llm_response_with_tracking(self, review_obj, study, task):
        """
        Get LLM response with performance tracking.

        Args:
            review_obj: The Review object
            study: The study data
            task: The LLM task

        Returns:
            tuple: (performance_metrics, llm_response)
        """
        # Start timing
        start_time = time.time()

        # Get the LLM response using the original method
        llm_response = self._get_llm_response(review_obj, study, task)

        # Get prompt type
        prompt_type_map = {
            'pre': 'pre_prompt',
            'ask_ai': 'co_ask_ai_prompt',
            'pico_extract': 'co_pico_extract_prompt',
            'detail_reason': 'co_detail_reason_prompt',
            'post': 'post_prompt'
        }
        prompt_type = prompt_type_map[task]

        # Get prompt config for token counting
        try:
            prompt_config = MasterPromptConfig.objects.get(
                user=review_obj.user,
                review=review_obj,
                prompt_type=prompt_type
            )

            # Extract system and assistant prompts for token counting
            system_prompt = prompt_config.prompt_content.get("system", "")
            assistant_prompt = prompt_config.prompt_content.get("assistant", "")

            # Create input variables for token counting
            input_vars = {
                "title": study.get("title", ""),
                "abstract": study.get("abstract", ""),
                "authors": study.get("authors", ""),
                "inclusion_criteria": review_obj.inclusion_criteria or ""
            }

            # Calculate input tokens
            input_text = system_prompt + assistant_prompt
            for key, value in input_vars.items():
                if isinstance(value, str):
                    input_text += value

            # Get model name
            model_name = review_obj.llm_parameters.get("model_name", "gpt-3.5-turbo")

            # Estimate tokens
            input_tokens = self._count_tokens(input_text, model_name)
            output_tokens = self._count_tokens(llm_response.content, model_name)
            total_tokens = input_tokens + output_tokens

            # Calculate processing time
            processing_time = time.time() - start_time

            # Estimate cost
            estimated_cost = self._estimate_cost(input_tokens, output_tokens, model_name)

            # Create performance metrics
            performance_metrics = {
                "processing_time": processing_time,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "estimated_cost": estimated_cost,
                "model": model_name
            }

        except Exception as e:
            # If any token counting errors occur, create minimal metrics
            logger.warning(f"Error generating detailed metrics: {e}")
            performance_metrics = {
                "processing_time": time.time() - start_time,
                "total_tokens": len(llm_response.content) // 4,  # Rough estimate
                "estimated_cost": 0.0
            }

        return performance_metrics, llm_response

    def _process_as_batch(self, review_obj, page_index, task, structure_type):
        """
        Process studies in batch mode with parallel execution and performance tracking.

        Args:
            review_obj: The Review object
            page_index: The page index
            task: The LLM task
            structure_type: The structure type ('page_based' or 'study_centric')

        Returns:
            JsonResponse with performance metrics and responses
        """
        # Get studies for the current page
        page_data = get_paginated_studies(review_obj, page_index)
        studies = page_data["studies"]

        # For safety, limit batch size
        if len(studies) > 20:
            raise ValueError("Batch processing limited to 20 studies at a time")

        # Start performance tracking
        start_time = time.time()
        total_tokens = 0
        total_cost = 0
        processing_times = []

        # Process studies in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []

            # For page-based structure
            if structure_type == 'page_based':
                for idx, study in enumerate(studies):
                    future = executor.submit(
                        self._process_study_with_tracking,
                        review_obj, study, task, page_index, idx
                    )
                    futures.append((future, idx, None))

            # For study-centric structure
            else:  # structure_type == 'study_centric'
                for study in studies:
                    future = executor.submit(
                        self._process_study_with_tracking,
                        review_obj, study, task
                    )
                    futures.append((future, None, study.get("pmid")))

            # Collect results
            responses = []
            detailed_metrics = []
            model_name = None

            for future, idx, pmid in futures:
                try:
                    performance_metrics, llm_response = future.result()

                    # Save the model name for later (should be the same for all)
                    if model_name is None and 'model' in performance_metrics:
                        model_name = performance_metrics['model']

                    # Add metrics to totals
                    total_tokens += performance_metrics['total_tokens']
                    total_cost += performance_metrics['estimated_cost']
                    processing_times.append(performance_metrics['processing_time'])

                    # Save detailed metrics
                    if structure_type == 'page_based':
                        detailed_metrics.append({
                            "study_index": idx,
                            "metrics": performance_metrics
                        })
                    else:
                        detailed_metrics.append({
                            "pmid": pmid,
                            "metrics": performance_metrics
                        })

                    # Add to responses
                    if structure_type == 'page_based':
                        responses.append({
                            "study_index": idx,
                            "content": llm_response.content,
                            "performance": performance_metrics
                        })
                    else:  # structure_type == 'study_centric'
                        responses.append({
                            "pmid": pmid,
                            "content": llm_response.content,
                            "performance": performance_metrics
                        })
                except Exception as exc:
                    logger.error(f"Study processing generated an exception: {exc}")
                    if structure_type == 'page_based':
                        responses.append({
                            "study_index": idx,
                            "error": str(exc)
                        })
                    else:  # structure_type == 'study_centric'
                        responses.append({
                            "pmid": pmid,
                            "error": str(exc)
                        })

        # Track performance and get aggregate metrics
        aggregate_metrics = self._track_performance(
            review_obj, task, structure_type,
            start_time, detailed_metrics, len(studies)
        )

        # Prepare response
        msg = f"Successfully processed batch of {len(responses)} studies for task '{task}'"
        return JsonResponse(
            data={
                "message": msg,
                "data": {
                    "responses": responses,
                    "performance": aggregate_metrics
                }
            },
            status=status.HTTP_200_OK
        )

    def _process_study_with_tracking(self, review_obj, study, task, page_index=None, study_index=None):
        """
        Process a study with performance tracking.
        Works with both page-based and study-centric structures.

        Args:
            review_obj: The Review object
            study: The study data
            task: The LLM task
            page_index: The page index (for page-based structure)
            study_index: The study index (for page-based structure)

        Returns:
            tuple: (performance_metrics, llm_response)
        """
        # --- LLM response caching logic ---
        # Get prompt config updated_at
        prompt_type_map = {
            'pre': 'pre_prompt',
            'ask_ai': 'co_ask_ai_prompt',
            'pico_extract': 'co_pico_extract_prompt',
            'detail_reason': 'co_detail_reason_prompt',
            'post': 'post_prompt'
        }
        prompt_type = prompt_type_map[task]
        try:
            prompt_config = MasterPromptConfig.objects.get(
                user=review_obj.user,
                review=review_obj,
                prompt_type=prompt_type
            )
            prompt_version = str(getattr(prompt_config, 'updated_at', ''))
        except Exception:
            prompt_version = ''
        # Get llm_parameters updated_at if available
        llm_params = review_obj.llm_parameters or {}
        llm_params_version = str(llm_params.get('updated_at', ''))
        # Compose version string
        llm_version = f"{prompt_version}_{llm_params_version}"
        # Field names for response and version
        response_field = None
        version_field = None
        if task == 'pre':
            response_field = 'pre_response'
            version_field = 'pre_llm_config_version'
        elif task == 'ask_ai':
            response_field = 'ask_ai_response'
            version_field = 'ask_ai_llm_config_version'
        elif task == 'pico_extract':
            response_field = 'pico_extraction'
            version_field = 'pico_extract_llm_config_version'
        elif task == 'detail_reason':
            response_field = 'detailed_reasoning'
            version_field = 'detail_reason_llm_config_version'
        elif task == 'post':
            response_field = 'post_response'
            version_field = 'post_llm_config_version'
        # Check for cached response
        cached_response = study.get(response_field)
        cached_version = study.get(version_field)
        if cached_response is not None and cached_version == llm_version:
            # Return cached result with dummy metrics (or you could store metrics too)
            performance_metrics = {
                "cached": True,
                "processing_time": 0,
                "input_tokens": 0,
                "output_tokens": len(cached_response) // 4,
                "total_tokens": len(cached_response) // 4,
                "estimated_cost": 0.0,
                "model": llm_params.get("model_name", "cached")
            }

            class DummyLLMResponse:
                def __init__(self, content):
                    self.content = content
            llm_response = DummyLLMResponse(cached_response)
            
            # Still update study object if needed (e.g., for co_rating)
            if task == 'ask_ai':
                rating = extract_rating(cached_response)
                if study.get('co_rating') != rating:
                    study['co_rating'] = rating
            return performance_metrics, llm_response
        # --- End caching logic ---
        # Get LLM response with metrics
        performance_metrics, llm_response = self._get_llm_response_with_tracking(review_obj, study, task)

        # Store version string with response
        study[version_field] = llm_version

        # Process the study appropriately based on structure
        structure_type = review_obj.structure_type

        if structure_type == 'page_based' and page_index is not None and study_index is not None:
            # For page-based structure
            self._update_page_based_study(review_obj, study, task, page_index, study_index, llm_response)
        else:
            # For study-centric structure
            self._update_study_centric_study(review_obj, study, task, llm_response)

        return performance_metrics, llm_response

    def _update_page_based_study(self, review_obj, study, task, page_index, study_index, llm_response):
        """Update a page-based study with LLM response"""
        # Implementation from _process_page_based_study
        screening_pages = review_obj.screening_pages

        # Update the appropriate field based on task
        if task == 'pre':
            screening_pages["pages"][page_index]["studies"][study_index]["pre_response"] = llm_response.content
        elif task == 'post':
            screening_pages["pages"][page_index]["studies"][study_index]["post_response"] = llm_response.content
        elif task == 'ask_ai':
            screening_pages["pages"][page_index]["studies"][study_index]["ask_ai_response"] = llm_response.content
            rating = extract_rating(llm_response.content)
            screening_pages["pages"][page_index]["studies"][study_index]["co_rating"] = rating
        elif task == 'detail_reason':
            screening_pages["pages"][page_index]["studies"][study_index]["detailed_reasoning"] = llm_response.content
        elif task == 'pico_extract':
            screening_pages["pages"][page_index]["studies"][study_index]["pico_extraction"] = llm_response.content

        # Save changes
        review_obj.screening_pages = screening_pages
        review_obj.save()

    def _update_study_centric_study(self, review_obj, study, task, llm_response):
        """Update a study-centric study with LLM response"""
        studies = review_obj.screening_pages.get("studies", [])
        pmid = study.get("pmid")

        # Find the study by PMID
        for i, s in enumerate(studies):
            if s.get("pmid") == pmid:
                # Update the appropriate field based on task
                if task == 'pre':
                    studies[i]["pre_response"] = llm_response.content
                elif task == 'post':
                    studies[i]["post_response"] = llm_response.content
                elif task == 'ask_ai':
                    studies[i]["ask_ai_response"] = llm_response.content
                elif task == 'detail_reason':
                    studies[i]["detailed_reasoning"] = llm_response.content
                elif task == 'pico_extract':
                    studies[i]["pico_extraction"] = llm_response.content
                break

        # Save changes
        review_obj.screening_pages["studies"] = studies
        review_obj.save()


class ReviewProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Update review progress status and handle screening state transitions.
            @body       review_id           ID of the review entry
                        action              Action to perform ('start', 'pause', 'resume', 'finish', 'post_review')
                        page_index          Current page index (optional, for tracking progress)
            @return     JsonResponse        Success message with updated status
        """
        # Parse input data
        review_id = request.data.get('review_id')
        page_index = int(request.data.get('page_index', 0))
        action = request.data.get('action')
        # is_finished = int(request.data.get('is_finished', 0))
        # is_post_review= int(request.data.get('is_post_review', 0))

        try:
            # Query review object
            review_obj = Review.objects.filter(id=review_id, user=request.user).first()

            # Check if review exists
            if not review_obj:
                logger.error(f"Review({review_id}) does not exist for user({request.user.id})")
                return JsonResponse({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

            # Get current status
            current_status = review_obj.screening_status

            # Handle status transitions based on action
            if action == 'start':
                if current_status != 'not_start':
                    raise ValueError(
                        f"Cannot start screening. Current status is '{current_status}'. Expected 'not_start'.")

                # Start screening
                review_obj.screening_status = 'screening'
                review_obj.started_screening_at = now()
                review_obj.current_screening_page = 1

                msg = f"User ({request.user.id}) has started screening the dataset ({review_obj.name})."

            elif action == 'pause':
                if current_status not in ['screening']:
                    raise ValueError(
                        f"Cannot pause screening. Current status is '{current_status}'. Expected 'screening'.")

                # Pause screening
                review_obj.screening_status = 'paused'
                review_obj.paused_screening_at = now()

                msg = f"User ({request.user.id}) has paused screening the dataset ({review_obj.name})."

            elif action == 'resume':
                if current_status != 'paused':
                    raise ValueError(
                        f"Cannot resume screening. Current status is '{current_status}'. Expected 'paused'.")

                # Resume screening
                review_obj.screening_status = 'screening'
                # Clear paused timestamp since we're resuming
                review_obj.paused_screening_at = None

                msg = f"User ({request.user.id}) has resumed screening the dataset ({review_obj.name})."

            elif action == 'finish':
                if current_status not in ['screening', 'paused', 'post-review']:
                    raise ValueError(
                        f"Cannot finish screening. Current status is '{current_status}'. Expected 'screening', 'paused', or 'post-review'.")
                # Finish screening
                review_obj.screening_status = 'finished'
                review_obj.finished_screening_at = now()
                msg = f"User ({request.user.id}) has finished screening the dataset ({review_obj.name})."

            elif action == 'post_review':
                # Only allow post-review for certain pipeline types
                if review_obj.pipeline_type in ['pre-only', 'pre-co', 'co-only']:
                    raise ValueError(f"Cannot start post-review. Current pipeline is '{review_obj.pipeline_type}'.")

                # Start post-review
                review_obj.screening_status = 'post-review'

                msg = f"User ({request.user.id}) has started post-review for the dataset ({review_obj.name})."

            # Update current page if provided
            if page_index is not None:
                try:
                    page_index = int(page_index)
                    if page_index >= 0:
                        review_obj.current_screening_page = page_index + 1  # Convert to 1-based indexing
                except (ValueError, TypeError):
                    logger.warning(f"Invalid page_index provided: {page_index}. Ignoring.")

            # Save changes
            review_obj.save()

            response_data = {
                "review_id": review_obj.id,
                "previous_status": current_status,
                "current_status": review_obj.screening_status,
                "current_page": review_obj.current_screening_page,
                "action": action
            }

            # Log the action
            logger.info(msg)

            return JsonResponse(
                data={"message": msg, "data": response_data},
                status=status.HTTP_200_OK
            )

        except ValueError as error:
            logger.error(f"Validation error in review progress update: {error}")
            return JsonResponse(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as error:
            logger.error(
                f"Error updating review progress for user({request.user.id}): {error}\n{traceback.format_exc()}")
            return JsonResponse(
                {"error": "An error occurred while updating review progress."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Store user's feedback (include/exclude) for a study.
        Compatible with both page-based and study-centric structures.
            @body       review_id           ID of the review entry
                        pmid                PMID of the study (for study-centric structure)
                        page_index          Index of the page (for page-based structure)
                        study_index         Index of the study in the page (for page-based structure)
                        feedback            User's feedback ('include', 'exclude')
            @return     JsonResponse        Success message
        """
        try:
            # Extract common data
            review_id = request.data.get('review_id')
            feedback = request.data.get('feedback')

            # Validate common fields
            if not review_id:
                raise ValueError("Missing required field: 'review_id'")

            if not feedback:
                raise ValueError("Missing required field: 'feedback'")

            # Validate feedback value
            if feedback not in ['include', 'exclude']:
                raise ValueError("Feedback must be either 'include', 'exclude'")

            # Get review object
            review_obj = Review.objects.get(id=review_id, user=request.user)
            structure_type = review_obj.structure_type

            # Handle based on structure type
            if structure_type == 'study_centric':
                return self._handle_study_centric_feedback(review_obj, request.data)
            else:  # page_based
                return self._handle_page_based_feedback(review_obj, request.data)

        except ValueError as error:
            logger.error(f"Validation error in storing user feedback: {error}")
            return JsonResponse(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Review.DoesNotExist as error:
            logger.error(f"Review not found: {error}")
            return JsonResponse(
                {"error": str(error)},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as error:
            logger.error(f"Error in storing user feedback: {error}\n{traceback.format_exc()}")
            return JsonResponse(
                {"error": "Internal server error occurred while storing feedback."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _handle_study_centric_feedback(self, review_obj, data):
        """Handle feedback for study-centric structure"""
        pmid = data.get('pmid')
        feedback = data.get('feedback')

        if not pmid:
            raise ValueError("Missing required field: 'pmid'")

        # Find and update the study
        studies = review_obj.screening_pages.get("studies", [])
        study_found = False

        for i, study in enumerate(studies):
            if study.get("pmid") == pmid:
                # Store the previous feedback
                prev_feedback = study.get("user_feedback")

                # Update the feedback
                studies[i]["user_feedback"] = feedback

                # Update timestamps
                now = get_utc_datetime()
                if not studies[i].get("feedback_created_at"):
                    studies[i]["feedback_created_at"] = now
                studies[i]["feedback_updated_at"] = now

                # Update include/exclude lists
                self._update_inclusion_lists(review_obj, pmid, prev_feedback, feedback)

                study_found = True
                break

        if not study_found:
            raise ValueError(f"Study with PMID {pmid} not found")

        # Save changes
        review_obj.screening_pages["studies"] = studies
        review_obj.save()

        msg = f"Successfully stored user feedback for study with PMID {pmid}"
        logger.info(msg)
        return JsonResponse(
            data={"message": msg, "data": feedback},
            status=status.HTTP_200_OK
        )

    def _handle_page_based_feedback(self, review_obj, data):
        """Handle feedback for page-based structure"""
        page_index = data.get('page_index')
        study_index = data.get('study_index')
        feedback = data.get('feedback')

        if page_index is None:
            raise ValueError("Missing required field: 'page_index'")

        if study_index is None:
            raise ValueError("Missing required field: 'study_index'")

        # Convert to integers
        try:
            page_index = int(page_index)
            study_index = int(study_index)
        except (ValueError, TypeError):
            raise ValueError("page_index and study_index must be integers")

        # Get the screening pages
        screening_pages = review_obj.screening_pages

        # Validate indices
        if "pages" not in screening_pages:
            raise ValueError("No pages found in review")

        if page_index >= len(screening_pages["pages"]) or page_index < 0:
            raise ValueError(f"Invalid page_index: {page_index}")

        page = screening_pages["pages"][page_index]

        if "studies" not in page:
            raise ValueError(f"No studies found in page {page_index}")

        if study_index >= len(page["studies"]) or study_index < 0:
            raise ValueError(f"Invalid study_index: {study_index}")

        # Get the study
        study = page["studies"][study_index]

        # Store the previous feedback
        prev_feedback = study.get("user_feedback")

        # Update the feedback
        screening_pages["pages"][page_index]["studies"][study_index]["user_feedback"] = feedback

        # Update timestamps
        now = get_utc_datetime()
        if "feedback_created_at" not in study:
            screening_pages["pages"][page_index]["studies"][study_index]["feedback_created_at"] = now
        screening_pages["pages"][page_index]["studies"][study_index]["feedback_updated_at"] = now

        # Update include/exclude lists
        self._update_inclusion_lists(review_obj, study.get("pmid"), prev_feedback, feedback)

        # Save changes
        review_obj.screening_pages = screening_pages
        review_obj.save()

        msg = f"Successfully stored user feedback for study in page {page_index}, position {study_index}"
        logger.info(msg)
        return JsonResponse(
            data={"message": msg, "data": feedback},
            status=status.HTTP_200_OK
        )

    def _update_inclusion_lists(self, review_obj, pmid, prev_feedback, new_feedback):
        """Update inclusion/exclusion lists based on feedback change"""
        if not pmid:
            return

        include_docs = review_obj.include_docs or []
        exclude_docs = review_obj.exclude_docs or []
        # maybe_docs = review_obj.maybe_docs or []

        # Remove from previous list if needed
        if prev_feedback == 'include' and pmid in include_docs:
            include_docs.remove(pmid)
        elif prev_feedback == 'exclude' and pmid in exclude_docs:
            exclude_docs.remove(pmid)
        # elif prev_feedback == 'maybe' and pmid in maybe_docs:
        #     maybe_docs.remove(pmid)

        # Add to new list
        if new_feedback == 'include' and pmid not in include_docs:
            include_docs.append(pmid)
        elif new_feedback == 'exclude' and pmid not in exclude_docs:
            exclude_docs.append(pmid)
        # elif new_feedback == 'maybe' and pmid not in maybe_docs:
        #     maybe_docs.append(pmid)

        # Update review object
        review_obj.include_docs = include_docs
        review_obj.exclude_docs = exclude_docs
        # review_obj.maybe_docs = maybe_docs


class GetLlmConfigView(APIView):
    """View to get the current LLM configuration for a review"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Get the current LLM configuration for a review.
            @body       review_id           ID of the review entry
            @return     JsonResponse        Success message with LLM configuration
        """
        try:
            # Extract review_id from request
            review_id = request.data.get('review_id')

            # Validate required parameter
            if not review_id:
                raise ValueError("Missing required field: 'review_id'")

            # Get review object
            try:
                review_obj = Review.objects.get(id=review_id, user=request.user)
            except Review.DoesNotExist:
                return JsonResponse(
                    {"error": f"Review with ID {review_id} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Extract LLM configuration
            llm_config = {
                "pipeline_type": review_obj.pipeline_type,
                "llm_interaction_level": review_obj.llm_interaction_level,
                "llm_parameters": review_obj.llm_parameters
            }

            msg = f"Successfully retrieved LLM configuration for review ID: {review_id}"
            logger.info(msg)

            return JsonResponse(
                data={"message": msg, "data": llm_config},
                status=status.HTTP_200_OK
            )

        except ValueError as error:
            logger.error(f"Validation error in retrieving LLM configuration: {error}")
            return JsonResponse(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as error:
            logger.error(f"Error in retrieving LLM configuration: {error}\n{traceback.format_exc()}")
            return JsonResponse(
                {"error": "Internal server error occurred while retrieving LLM configuration."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdatePromptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Update or create a prompt template for a review.
        @body   review_id: int
                prompt_type: str (e.g., 'pre_prompt', 'co_ask_ai_prompt', ...)
                prompt_content: dict (JSON)
        @return JsonResponse with success message and updated prompt
        """
        try:
            review_id = request.data.get('review_id')
            prompt_type = request.data.get('prompt_type')
            prompt_content = request.data.get('prompt_content')

            if not review_id or not prompt_type or prompt_content is None:
                raise ValueError("Missing required fields: review_id, prompt_type, or prompt_content.")

            # Get review object
            review_obj = Review.objects.get(id=review_id, user=request.user)

            # Update or create the prompt config
            prompt_config, _ = MasterPromptConfig.objects.update_or_create(
                user=request.user,
                review=review_obj,
                prompt_type=prompt_type,
                defaults={"prompt_content": prompt_content}
            )

            msg = f"Prompt '{prompt_type}' updated for review {review_id}."
            logger.info(msg)
            return JsonResponse({
                "message": msg,
                "data": {
                    "review_id": review_id,
                    "prompt_type": prompt_type,
                    "prompt_content": prompt_config.prompt_content
                }
            }, status=200)

        except Review.DoesNotExist:
            return JsonResponse({"error": f"Review with ID {review_id} not found."}, status=404)
        except Exception as e:
            logger.error(f"Error updating prompt: {e}\n{traceback.format_exc()}")
            return JsonResponse({"error": str(e)}, status=400)


class UpdatePaginationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Update the number of studies per page setting.
        For study-centric structure only - page-based has fixed page sizes.
        """
        try:
            # Extract parameters from request
            review_id = request.data.get('review_id')
            page_size = int(request.data.get('page_size', 10))

            # Validate parameters
            if not review_id:
                raise ValueError("Missing required parameter: 'review_id'")

            if page_size < 1 or page_size > 100:
                raise ValueError("Page size must be between 1 and 100")

            # Get review object
            review_obj = Review.objects.get(id=review_id, user=request.user)

            # Only allow changing page size for study-centric structure
            if review_obj.structure_type != 'study_centric':
                raise ValueError("Changing page size is only supported for study-centric structure")

            # Update the page size
            old_page_size = review_obj.show_docs_per_page
            review_obj.show_docs_per_page = page_size
            review_obj.save()

            msg = f"Successfully updated pagination from {old_page_size} to {page_size} studies per page"
            logger.info(msg)

            return JsonResponse(
                data={"message": msg},
                status=status.HTTP_200_OK
            )

        except ValueError as error:
            logger.error(f"Validation error in updating pagination: {error}")
            return JsonResponse(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Review.DoesNotExist:
            msg = f"Review({review_id}) not found"
            logger.error(msg)
            return JsonResponse(
                {"error": msg},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as error:
            logger.error(f"Error updating pagination: {error}\n{traceback.format_exc()}")
            return JsonResponse(
                {"error": "An error occurred while updating pagination"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MigrateStructureView(APIView):
    """API endpoint to migrate between page-based and study-centric structures"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Migrate a review between page-based and study-centric structures
            @body       review_id           ID of the review entry
                        target_structure     Target structure ('page_based' or 'study_centric')
            @return     JsonResponse        Success message
        """
        try:
            # Extract parameters
            review_id = request.data.get('review_id')
            target_structure = request.data.get('target_structure')

            # Validate parameters
            if not review_id:
                raise ValueError("Missing required parameter: 'review_id'")

            if not target_structure:
                raise ValueError("Missing required parameter: 'target_structure'")

            if target_structure not in ['page_based', 'study_centric']:
                raise ValueError("Invalid target_structure. Must be 'page_based' or 'study_centric'.")

            # Get review
            review_obj = Review.objects.get(id=review_id, user=request.user)

            # Skip if already in target structure
            if review_obj.structure_type == target_structure:
                return JsonResponse(
                    {"message": f"Review is already using {target_structure} structure."},
                    status=status.HTTP_200_OK
                )

            # Perform migration
            if target_structure == 'page_based':
                result = self._migrate_to_page_based(review_obj)
            else:  # target_structure == 'study_centric'
                result = self._migrate_to_study_centric(review_obj)

            # Update structure type
            review_obj.structure_type = target_structure
            review_obj.save()

            msg = f"Successfully migrated review to {target_structure} structure"
            logger.info(msg)

            return JsonResponse(
                data={"message": msg, "data": {"structure_type": target_structure}},
                status=status.HTTP_200_OK
            )

        except ValueError as error:
            logger.error(f"Validation error in structure migration: {error}")
            return JsonResponse(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Review.DoesNotExist:
            msg = f"Review with ID {review_id} not found"
            logger.error(msg)
            return JsonResponse(
                {"error": msg},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as error:
            logger.error(f"Error in structure migration: {error}\n{traceback.format_exc()}")
            return JsonResponse(
                {"error": "An error occurred during structure migration"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _migrate_to_page_based(self, review):
        """
        Migrate a review from study-centric to page-based structure.

        Args:
            review: The Review object to migrate

        Returns:
            The new page-based structure
        """
        if not review.screening_pages or "studies" not in review.screening_pages:
            raise ValueError(f'Review has no studies to migrate')

        # Get all studies
        studies = review.screening_pages.get("studies", [])

        # Initialize page-based structure
        page_based = {"pages": []}
        page_size = review.show_docs_per_page

        # Group studies into pages
        for i in range(0, len(studies), page_size):
            page_studies = studies[i: i + page_size].copy()  # Create copies to avoid reference issues
            page_index = i // page_size

            page_entry = {
                "page_index": page_index,
                "studies": page_studies
            }
            page_based["pages"].append(page_entry)

        # Save new structure
        review.screening_pages = page_based

        return page_based

    def _migrate_to_study_centric(self, review):
        """
        Migrate a review from page-based to study-centric structure.

        Args:
            review: The Review object to migrate

        Returns:
            The new study-centric structure
        """
        if not review.screening_pages or "pages" not in review.screening_pages:
            raise ValueError(f'Review has no pages to migrate')

        # Initialize study-centric structure
        study_centric = {"studies": []}

        # Extract all studies from all pages
        for page in review.screening_pages.get("pages", []):
            for study in page.get("studies", []):
                # Create a copy to avoid reference issues
                study_copy = study.copy()

                # Ensure each study has a pmid
                if "pmid" not in study_copy:
                    # Generate a unique ID if no pmid exists
                    study_copy["pmid"] = f"p-{uuid.uuid4()}"

                # Add to flat list
                study_centric["studies"].append(study_copy)

        # Save new structure
        review.screening_pages = study_centric

        return study_centric


class UpdateSortingView(APIView):
    """
    API endpoint to update the sorting/ranking method for studies.

    Special note about "original" sorting:
    - The "original" method preserves the original order in which studies were loaded
    - This order is maintained using the original_index field in each study
    - Users can always revert to this order by setting ranking_method to "original"
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Update the sorting method for studies
            @body       review_id           ID of the review entry
                        ranking_method      The sorting method ('original', 'alphabetic', 'dense', 'custom')
                        sort_direction      Optional: Direction of sort ('asc' or 'desc'), default 'asc'
                        sort_field          Optional: Field to sort by for 'custom' method (e.g., 'pmid', 'authors')
            @return     JsonResponse        Success message
        """
        try:
            # Extract parameters
            review_id = request.data.get('review_id')
            ranking_method = request.data.get('ranking_method')
            sort_direction = request.data.get('sort_direction', 'asc')
            sort_field = request.data.get('sort_field')

            # Validate parameters
            if not review_id:
                raise ValueError("Missing required parameter: 'review_id'")

            if not ranking_method:
                raise ValueError("Missing required parameter: 'ranking_method'")

            # Validate ranking method
            valid_rankings = ["original", "alphabetic", "dense", "custom"]
            if ranking_method not in valid_rankings:
                raise ValueError(
                    f"Invalid ranking method: '{ranking_method}'. Must be one of: {', '.join(valid_rankings)}")

            # Validate direction (skip for 'original' method)
            if ranking_method != "original" and sort_direction not in ['asc', 'desc']:
                raise ValueError(f"Invalid sort direction: '{sort_direction}'. Must be 'asc' or 'desc'.")

            # Validate custom sort field
            if ranking_method == "custom" and not sort_field:
                raise ValueError("Custom sorting requires 'sort_field' parameter.")

            # Get review
            review_obj = Review.objects.get(id=review_id, user=request.user)

            # For "original" sorting, ensure original_index exists for all studies
            if ranking_method == "original" and review_obj.structure_type == 'study_centric':
                add_original_index_to_studies(review_obj)

            # Get the current sorting configuration
            current_sorting_config = review_obj.sorting_config or {}

            # Skip if already using this exact configuration
            current_direction = current_sorting_config.get('sort_direction')
            current_field = current_sorting_config.get('sort_field')

            if (review_obj.ranking_method == ranking_method and
                    (ranking_method == "original" or current_direction == sort_direction) and
                    current_field == sort_field):
                return JsonResponse(
                    {"message": f"Review is already using these sort settings."},
                    status=status.HTTP_200_OK
                )

            # Update sorting configuration
            old_method = review_obj.ranking_method
            review_obj.ranking_method = ranking_method

            # Store additional sort parameters in sorting_config field
            # For "original" method, we don't need sort_direction
            if ranking_method == "original":
                review_obj.sorting_config = {
                    "sort_field": sort_field if sort_field else None
                }
            else:
                review_obj.sorting_config = {
                    "sort_direction": sort_direction,
                    "sort_field": sort_field
                }

            review_obj.save()

            msg = f"Successfully updated sorting method from '{old_method}' to '{ranking_method}'"
            if ranking_method == "custom":
                msg += f" using field '{sort_field}'"
            if ranking_method != "original":
                msg += f" in {sort_direction}ending order"

            logger.info(msg)

            return JsonResponse(
                data={
                    "message": msg,
                    "data": {
                        "ranking_method": ranking_method,
                        "sort_direction": ranking_method != "original" and sort_direction or None,
                        "sort_field": sort_field
                    }
                },
                status=status.HTTP_200_OK
            )

        except ValueError as error:
            logger.error(f"Validation error in updating sorting method: {error}")
            return JsonResponse(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Review.DoesNotExist:
            msg = f"Review with ID {review_id} not found"
            logger.error(msg)
            return JsonResponse(
                {"error": msg},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as error:
            logger.error(f"Error updating sorting method: {error}\n{traceback.format_exc()}")
            return JsonResponse(
                {"error": "An error occurred while updating sorting method"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ResultsCheckingPauseView(APIView):
    """API endpoint to get results data for the pause page view."""
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        """
        Get results data for the paused review, including filtered studies and
        export options.
            @body       review_id           ID of the review entry
                        export              Boolean indicating if export is requested
                        filter_type         Filter type for export only ('all', 'include', 'exclude', 'unjudged')
            @return     JsonResponse        Success message with results data
        """
        try:
            # Extract parameters
            review_id = request.data.get('review_id')
            export = request.data.get('export', False)
            filter_type = request.data.get('filter_type', 'all')

            # Validate parameters
            if not review_id:
                raise ValueError("Missing required parameter: 'review_id'")

            if filter_type not in ['all', 'include', 'exclude', 'unjudged']:
                raise ValueError("Invalid filter type. Must be one of: 'all', 'include', 'exclude', 'unjudged'")

            # Get review object
            review_obj = Review.objects.get(id=review_id, user=request.user)

            # Ensure review is paused
            if review_obj.screening_status != 'paused':
                raise ValueError("This API endpoint is only for paused reviews")

            # Get all studies up to the current page
            studies_data = []
            screening_pages = review_obj.screening_pages
            current_page = review_obj.current_screening_page or 1

            # Process all pages up to the current page
            for page_idx in range(min(current_page, len(screening_pages.get('pages', [])))):
                page = screening_pages['pages'][page_idx]
                for study in page.get('studies', []):
                    study_data = {
                        'order': len(studies_data) + 1,
                        'pmid': study.get('pmid', ''),
                        'title': study.get('title', ''),
                        'abstract': study.get('abstract', ''),
                        'assessment': study.get('user_feedback', 'unjudged')
                    }
                    studies_data.append(study_data)

            # If export is requested, generate NBIB file
            export_url = None
            if export:
                # For export, we need to filter the data server-side
                if filter_type != 'all':
                    pmids_to_export = [s['pmid'] for s in studies_data if s['assessment'] == filter_type]
                else:
                    pmids_to_export = [s['pmid'] for s in studies_data]

                if pmids_to_export:
                    # Get uploaded file path
                    pmids_to_export = set(str(pmid) for pmid in pmids_to_export)
                    input_ris_file = get_uploaded_file_path(user_id=request.user.id, corpus_id=review_obj.corpus.id)

                    # Export file name
                    formatted_date = now().strftime("%Y%m%d")
                    formatted_datetime = now().strftime("%Y%m%d-%H%M%S")
                    output_file_name = f"{formatted_datetime}_{review_obj.name}_paused_{filter_type}.nbib"

                    # Prepare export file paths
                    user_corpus_dir = os.path.join(settings.MOUNT_CORPUS_PATH, f"u{request.user.id:05d}", "corpus",
                                                   f"c{review_obj.corpus.id:05d}")
                    output_nbib_folder = os.path.join(user_corpus_dir, "export", f"r{review_obj.id:05d}")
                    output_nbib_file = os.path.join(output_nbib_folder, output_file_name)

                    # Create output folder
                    os.makedirs(output_nbib_folder, exist_ok=True)

                    # Extract and export NBIB records
                    self._extract_nbib_records(input_ris_file, pmids_to_export, output_nbib_file)

                    # Check if file exists
                    if not os.path.exists(output_nbib_file):
                        raise FileNotFoundError(f"Exported file not found: {output_nbib_file}")

                    # Generate string-based content
                    with open(output_nbib_file, 'r') as f:
                        export_content = f.read()

                    # Generate Nginx-served URL
                    # relative_path = output_nbib_file.replace(settings.MOUNT_CORPUS_PATH, "")
                    # export_url = f"exports{relative_path}"  # Prefix with '/exports' for Nginx
                    # export_url = export_url.replace("\\", "/")  # Ensure URL uses forward slashes
                    # export_url = quote(export_url)  # URL encode any special characters
                    # export_url = quote(export_url)  # URL encode any special characters
                    #
                    # # For production, add domain name
                    # if settings.ALLOWED_HOSTS:
                    #     export_url = f"https://{settings.ALLOWED_HOSTS[1]}/{export_url}"

            # Calculate simple counts for convenience (frontend could also do this)
            filter_counts = {
                "all": len(studies_data),
                "include": len([s for s in studies_data if s['assessment'] == 'include']),
                "exclude": len([s for s in studies_data if s['assessment'] == 'exclude']),
                "unjudged": len([s for s in studies_data if s['assessment'] == 'unjudged'])
            }

            # --- Add stats for human/LLM reviewed ---
            pipeline_type = review_obj.pipeline_type
            # LLM stats based on pre-review
            enable_llm_stat_types = {'pre-only', 'pre-co', 'pre-post', 'full'}
            reviewed_studies = [s for s in studies_data if s['assessment'] in ['include', 'exclude']]
            n_human_reviewed = len(reviewed_studies)
            n_human_include = len([s for s in reviewed_studies if s['assessment'] == 'include'])
            n_human_exclude = len([s for s in reviewed_studies if s['assessment'] == 'exclude'])
            if pipeline_type not in enable_llm_stat_types:
                n_llm_reviewed = 0
                n_llm_include = 0
                n_llm_exclude = 0
            else:
                n_llm_reviewed = len([s for s in reviewed_studies if s.get('pre_response') is not None])
                n_llm_include = len([s for s in reviewed_studies if
                                     s.get('pre_response') and 'include' in extract_pre(s.get('pre_response')).lower()])
                n_llm_exclude = len([s for s in reviewed_studies if
                                     s.get('pre_response') and 'exclude' in extract_pre(s.get('pre_response')).lower()])
            review_stats = {
                "total_studies": len(studies_data),
                "human_reviewed": n_human_reviewed,
                "human_include": n_human_include,
                "human_exclude": n_human_exclude,
                "llm_reviewed": n_llm_reviewed,
                "llm_include": n_llm_include,
                "llm_exclude": n_llm_exclude
            }

            # Prepare response
            response_data = {
                "studies": studies_data,  # Send all data, let frontend handle filtering
                "total_count": len(studies_data),
                "filter_counts": filter_counts,
                'dataset_name': review_obj.name,
                'review_stats': review_stats
            }

            # Add export URL if applicable
            if export_url:
                response_data["export_url"] = export_url

            # Add export content if applicable
            if export_content:
                response_data["export_content"] = export_content

            msg = f"Successfully retrieved paused results data"
            logger.info(msg)

            return JsonResponse(
                data={"message": msg,"data": response_data},
                status=status.HTTP_200_OK
            )

        except ValueError as error:
            logger.error(f"Validation error in results checking: {error}")
            return JsonResponse(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Review.DoesNotExist:
            msg = f"Review with ID {review_id} not found"
            logger.error(msg)
            return JsonResponse(
                {"error": msg},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as error:
            logger.error(f"Error in results checking: {error}\n{traceback.format_exc()}")
            return JsonResponse(
                {"error": "An error occurred while retrieving results data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _extract_nbib_records(self, corpus_nbib_path, pmids_to_export, output_file):
        """
        Extracts NBIB records from the original corpus based on the provided PMIDs.
        """
        export_records = []
        current_record = []
        record_pmid = None

        with open(corpus_nbib_path, 'r') as infile:
            for line in infile:
                # Check if the line contains a PMID entry
                if line.startswith("PMID- "):
                    record_pmid = line.strip().split("PMID- ")[1]

                # Accumulate the current NBIB entry
                current_record.append(line)

                # Check if we've reached the end of the current NBIB record
                if line.strip() == "":
                    if record_pmid in pmids_to_export:
                        # If the current record's PMID matches one in our export list, store it
                        export_records.append("".join(current_record))
                    # Reset for the next record
                    current_record = []
                    record_pmid = None

        # Write the extracted records to the output file
        with open(output_file, 'w') as outfile:
            for record in export_records:
                outfile.write(record)
                outfile.write("\n\n")  # Separate NBIB entries with two newlines


class ResultsCheckingFinalView(APIView):
    """API endpoint to get results data for the final results page."""
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        """
        Get results data for the completed review, including filtered studies and
        export options.
            @body       review_id           ID of the review entry
                        export              Boolean indicating if export is requested
                        filter_type         Filter type for export only ('all', 'include', 'exclude', 'unjudged')
            @return     JsonResponse        Success message with results data
        """
        try:
            # Extract parameters
            review_id = request.data.get('review_id')
            export = request.data.get('export', False)
            filter_type = request.data.get('filter_type', 'all')

            # Validate parameters
            if not review_id:
                raise ValueError("Missing required parameter: 'review_id'")

            if filter_type not in ['all', 'include', 'exclude', 'unjudged']:
                raise ValueError("Invalid filter type. Must be one of: 'all', 'include', 'exclude', 'unjudged'")

            # Get review object
            review_obj = Review.objects.get(id=review_id, user=request.user)

            # Ensure review is finished
            if review_obj.screening_status != 'finished':
                raise ValueError("This API endpoint is only for completed reviews")

            # Get all studies from all pages
            studies_data = []
            screening_pages = review_obj.screening_pages

            # Process all pages
            for page in screening_pages.get('pages', []):
                for study in page.get('studies', []):
                    study_data = {
                        'order': len(studies_data) + 1,
                        'pmid': study.get('pmid', ''),
                        'title': study.get('title', ''),
                        'abstract': study.get('abstract', ''),
                        'assessment': study.get('user_feedback', 'unjudged')
                    }
                    studies_data.append(study_data)

            # If export is requested, generate NBIB file
            export_url = None
            if export:
                # For export, we need to filter the data server-side
                if filter_type != 'all':
                    pmids_to_export = [s['pmid'] for s in studies_data if s['assessment'] == filter_type]
                else:
                    pmids_to_export = [s['pmid'] for s in studies_data]

                if pmids_to_export:
                    # Get uploaded file path
                    pmids_to_export = set(str(pmid) for pmid in pmids_to_export)
                    input_ris_file = get_uploaded_file_path(user_id=request.user.id, corpus_id=review_obj.corpus.id)

                    # Export file name
                    formatted_date = now().strftime("%Y%m%d")
                    formatted_datetime = now().strftime("%Y%m%d-%H%M%S")
                    output_file_name = f"{formatted_datetime}_{review_obj.name}_final_{filter_type}.nbib"

                    # Prepare export file paths
                    user_corpus_dir = os.path.join(settings.MOUNT_CORPUS_PATH, f"u{request.user.id:05d}", "corpus",
                                                   f"c{review_obj.corpus.id:05d}")
                    output_nbib_folder = os.path.join(user_corpus_dir, "export", f"r{review_obj.id:05d}")
                    output_nbib_file = os.path.join(output_nbib_folder, output_file_name)

                    # Create output folder
                    os.makedirs(output_nbib_folder, exist_ok=True)

                    # Extract and export NBIB records
                    self._extract_nbib_records(input_ris_file, pmids_to_export, output_nbib_file)

                    # Check if file exists
                    if not os.path.exists(output_nbib_file):
                        raise FileNotFoundError(f"Exported file not found: {output_nbib_file}")

                    # Generate string-based content
                    with open(output_nbib_file, 'r') as f:
                        export_content = f.read()

                    # # Generate Nginx-served URL
                    # relative_path = output_nbib_file.replace(settings.MOUNT_CORPUS_PATH, "")
                    # export_url = f"exports{relative_path}"  # Prefix with '/exports' for Nginx
                    # export_url = export_url.replace("\\", "/")  # Ensure URL uses forward slashes
                    #
                    # # For production, add domain name
                    # if settings.ALLOWED_HOSTS:
                    #     export_url = f"https://{settings.ALLOWED_HOSTS[1]}/{export_url}"

            # Calculate simple counts and statistics
            included_count = len([s for s in studies_data if s['assessment'] == 'include'])
            excluded_count = len([s for s in studies_data if s['assessment'] == 'exclude'])
            unjudged_count = len([s for s in studies_data if s['assessment'] == 'unjudged'])
            total_count = len(studies_data)

            filter_counts = {
                "all": total_count,
                "include": included_count,
                "exclude": excluded_count,
                "unjudged": unjudged_count
            }

            review_stats = {
                "total_studies": total_count,
                "included": included_count,
                "excluded": excluded_count,
                "unjudged": unjudged_count,
                "inclusion_rate": f"{(included_count / max(total_count, 1) * 100):.1f}%"
            }

            # Prepare response
            response_data = {
                "studies": studies_data,  # Send all data, let frontend handle filtering
                "total_count": total_count,
                "filter_counts": filter_counts,
                "statistics": review_stats,
                'dataset_name': review_obj.name
            }

            # Add export URL if applicable
            if export_url:
                response_data["export_url"] = export_url

            # Add export content if applicable
            if export_content:
                response_data["export_content"] = export_content

            msg = f"Successfully retrieved final results data"
            logger.info(msg)

            return JsonResponse(
                data={"message": msg,"data": response_data},
                status=status.HTTP_200_OK
            )

        except ValueError as error:
            logger.error(f"Validation error in final results checking: {error}")
            return JsonResponse(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Review.DoesNotExist:
            msg = f"Review with ID {review_id} not found"
            logger.error(msg)
            return JsonResponse(
                {"error": msg},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as error:
            logger.error(f"Error in final results checking: {error}\n{traceback.format_exc()}")
            return JsonResponse(
                {"error": "An error occurred while retrieving results data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _extract_nbib_records(self, corpus_nbib_path, pmids_to_export, output_file):
        """
        Extracts NBIB records from the original corpus based on the provided PMIDs.
        """
        export_records = []
        current_record = []
        record_pmid = None

        with open(corpus_nbib_path, 'r') as infile:
            for line in infile:
                # Check if the line contains a PMID entry
                if line.startswith("PMID- "):
                    record_pmid = line.strip().split("PMID- ")[1]

                # Accumulate the current NBIB entry
                current_record.append(line)

                # Check if we've reached the end of the current NBIB record
                if line.strip() == "":
                    if record_pmid in pmids_to_export:
                        # If the current record's PMID matches one in our export list, store it
                        export_records.append("".join(current_record))

                    # Reset for the next record
                    current_record = []
                    record_pmid = None

        # Write the extracted records to the output file
        with open(output_file, 'w') as outfile:
            for record in export_records:
                outfile.write(record)
                outfile.write("\n\n")  # Separate NBIB entries with two newlines


class PostReviewTableView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Return the post-review table for a review in post-review status.
        For each study, show order, pmid, title, abstract, assessment, and post_reviewer_response (LLM output).
        If post_reviewer_response is missing, call the LLM and store the result.
        """
        try:
            review_id = request.data.get('review_id')
            if not review_id:
                raise ValueError("Missing required parameter: 'review_id'")

            review_obj = Review.objects.get(id=review_id, user=request.user)
            if review_obj.screening_status != 'post-review':
                raise ValueError("Post-review table is only available when review is in 'post-review' status.")

            # Get all studies in original order
            studies = []
            if review_obj.structure_type == 'page_based':
                for page in review_obj.screening_pages.get('pages', []):
                    for study in page.get('studies', []):
                        studies.append(study)
            elif review_obj.structure_type == 'study_centric':
                studies = review_obj.screening_pages.get('studies', [])
            else:
                raise ValueError('Unknown structure type')

            # Prepare output and trigger LLM for missing post_reviewer_response
            output = []
            updated = False
            for idx, study in enumerate(studies):
                assessment = study.get('user_feedback', '')
                post_response = study.get('post_reviewer_response')
                if post_response is None and assessment:
                    # Only run LLM if assessment exists (otherwise skip)
                    try:
                        # Use the same LLM logic as in LlmProcessView, but for post-review
                        llm_response = self._get_post_review_llm_response(review_obj, study)
                        post_response = llm_response.content
                        study['post_reviewer_response'] = post_response
                        updated = True
                    except Exception as e:
                        post_response = f"LLM error: {e}"
                        study['post_reviewer_response'] = post_response
                        updated = True
                output.append({
                    'order': idx + 1,
                    'pmid': study.get('pmid', ''),
                    'title': study.get('title', ''),
                    'abstract': study.get('abstract', ''),
                    'assessment': assessment,
                    'post_reviewer_response': post_response or ''
                })
            # Save if any LLM responses were updated
            if updated:
                if review_obj.structure_type == 'page_based':
                    # Repack studies into pages
                    i = 0
                    for page in review_obj.screening_pages.get('pages', []):
                        for j in range(len(page.get('studies', []))):
                            page['studies'][j] = studies[i]
                            i += 1
                else:
                    review_obj.screening_pages['studies'] = studies
                review_obj.save()
            msg = f"Successfully retrieved post-review table for review({review_id})"
            logger.info(msg)
            return JsonResponse(
                data={
                    'message': msg,
                    'data': output,
                    'dataset_name': review_obj.name
                },
                status=status.HTTP_200_OK
            )
        except Review.DoesNotExist:
            msg = f"Review({review_id}) not found"
            logger.error(msg)
            return JsonResponse({"error": msg}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as error:
            logger.error(f"Validation error in post-review table: {error}")
            return JsonResponse({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            logger.error(f"Error in post-review table: {error}\n{traceback.format_exc()}")
            return JsonResponse({"error": "An error occurred while retrieving post-review table."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_post_review_llm_response(self, review_obj, study):
        # Reuse LLM logic from LlmProcessView for post-review
        from .models import MasterPromptConfig
        prompt_type = 'post_prompt'
        prompt_config = MasterPromptConfig.objects.get(
            user=review_obj.user,
            review=review_obj,
            prompt_type=prompt_type
        )
        llm_params = review_obj.llm_parameters
        llm_config = {
            "model_name": llm_params["model_name"],
            "temperature": llm_params["temperature"],
            "max_tokens": llm_params["max_tokens"],
            "response_format": {"type": "text"} if llm_params["response_format"] == "text" else llm_params["response_format"],
            "streaming": llm_params.get("streaming", True),
            "api_key": settings.OPENAI_API_KEY
        }
        screening_api = ScreeningAPI(
            prompt_dir=os.path.join(settings.BASE_DIR, "review", "prompts"),
            llm_config=llm_config
        )
        # For post-review, require user_feedback to exist
        user_feedback = study.get("user_feedback")
        if user_feedback is None:
            raise ValueError("Cannot generate post-review without human decision. Please provide include/exclude feedback first.")
        # decision_map = {"include": "Include", "exclude": "Exclude"}
        # study["decision"] = decision_map.get(user_feedback)
        # if not study["decision"]:
        #     raise ValueError(f"Invalid user feedback value: {user_feedback}")
        llm_response = screening_api.screen_study(
            study=study,
            role='post',
            task='post',
            inclusion_criteria=review_obj.inclusion_criteria
        )
        return llm_response