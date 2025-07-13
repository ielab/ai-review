from typing import Dict, Any, Optional, Union
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import json


class PromptLoader:
    """Handles loading and managing separate prompt files."""

    PROMPT_FILES = {
        'pre': 'pre_prompt.json',
        'co_ask_ai': 'co_ask_ai_prompt.json',
        'co_pico_extract': 'co_pico_extract_prompt.json',
        'co_detail_reason': 'co_detail_reason_prompt.json',
        'post': 'post_prompt.json'
    }

    def __init__(self, prompt_dir:  Union[str, Path]):
        """Initialize with directory containing prompt files."""
        self.prompt_dir = Path(prompt_dir)
        self.prompts = self._load_all_prompts()

    def _load_prompt_file(self, filepath: Path) -> Dict[str, Any]:
        """Load a single prompt file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data['aireview_template']
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {filepath}")
        except KeyError:
            raise ValueError(f"Invalid prompt format in {filepath}. Expected 'aireview_template' key.")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in prompt file: {filepath}")

    def _load_all_prompts(self) -> Dict[str, Dict[str, str]]:
        """Load all prompt files."""
        prompts = {}
        for key, filename in self.PROMPT_FILES.items():
            filepath = self.prompt_dir / filename
            prompts[key] = self._load_prompt_file(filepath)
        return prompts

    def get_prompt(self, prompt_type: str) -> Dict[str, str]:
        """Get a specific prompt by type."""
        if prompt_type not in self.prompts:
            raise ValueError(f"Invalid prompt type: {prompt_type}")
        return self.prompts[prompt_type]


def create_chat_prompt(prompt_data: Dict[str, str]) -> ChatPromptTemplate:
    """Create a ChatPromptTemplate from prompt data."""
    return ChatPromptTemplate.from_messages([
        ("system", prompt_data["system"]),
        ("assistant", prompt_data["assistant"])
    ])


class ScreeningAPI:
    def __init__(
            self,
            prompt_dir: Union[str, Path],
            llm_config: Union[str, Any]
    ):
        """Initialize the screening API.

        Args:
            prompt_dir: Directory containing prompt JSON files
            llm_config: LLM configuration (model, temperature, etc.)
        """
        self.prompt_loader = PromptLoader(prompt_dir)
        # Initialize chat model
        if 'text' in llm_config["response_format"]:
            self.model = ChatOpenAI(
                model=llm_config["model_name"],
                temperature=llm_config["temperature"],
                max_tokens=llm_config["max_tokens"],
                streaming=llm_config.get("streaming", True),
                api_key=llm_config["api_key"]
            )
        else:
            self.model = ChatOpenAI(
                model=llm_config["model_name"],
                temperature=llm_config["temperature"],
                max_tokens=llm_config["max_tokens"],
                response_format=llm_config["response_format"],
                streaming=llm_config.get("streaming", True),
                api_key=llm_config["api_key"]
            )

    def screen_study(
            self,
            study: Dict[str, str],
            role: str,
            task: Optional[str] = None,
            inclusion_criteria: str = None,
    ) -> str:
        """Screen a study using specified role and task.

        Args:
            study: Study data (title, abstract, etc.)
            role: 'pre', 'co', or 'post'
            task: For co-reviewer: 'ask', 'pico_extract', or 'detail_reason'
            inclusion_criteria: Inclusion criteria for the systematic review
        """
        # Determine prompt type
        if role == 'pre':
            prompt_type = 'pre'
        elif role == 'co':
            if task not in ['ask_ai', 'pico_extract', 'detail_reason']:
                raise ValueError("Co-reviewer task must be 'ask_ai', 'pico_extract', or 'detail_reason'")
            prompt_type = f'co_{task}'
        elif role == 'post':
            prompt_type = 'post'
        else:
            raise ValueError("Role must be 'pre', 'co', or 'post'")

        # Get prompt and create template
        prompt_data = self.prompt_loader.get_prompt(prompt_type)
        chat_prompt = create_chat_prompt(prompt_data)

        # Prepare input variables
        input_vars = {
            "title": study["title"],
            "abstract": study["abstract"]
        }

        if inclusion_criteria:
            input_vars["inclusion_criteria"] = inclusion_criteria

        if "authors" in study:
            input_vars["authors"] = study["authors"]

        if "user_feedback" in study and role == "post":
            input_vars["decision"] = study["user_feedback"]

        if "co_rating" in study and task == "detail_reason":
            input_vars["rating"] = study["co_rating"]

        # Create and invoke chain
        chain = chat_prompt | self.model
        return chain.invoke(input_vars)
