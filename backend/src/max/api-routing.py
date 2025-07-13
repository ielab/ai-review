import nbib
import json
from pathlib import Path
import pandas as pd
from typing import Dict, Any, Optional
import re

"""
1. Function/API route
parse the nbib file and store in the database
"""
def parse_corpus(corpus_nbib_path: str, corpus_file: str = 'corpus.json') -> json:
    """
    Parse a corpus from a nbib file and extract specific fields into a JSON format.

    Args:
        corpus_nbib_path (str): Path to the corpus text in nbib format.
        corpus_file (str): Output file path for the resulting JSON file (default is 'corpus.json').
    """
    output_name = corpus_file
    keep_fields = ['pubmed_id', 'title', 'abstract', 'authors']
    refs = nbib.read_file(corpus_nbib_path)

    # first_entry = refs[0]
    filtered_entries = []

    for study in refs:
        filtered = {field: study.get(field, "") for field in keep_fields}

        if 'pubmed_id' in filtered:
            filtered['pmid'] = filtered.pop('pubmed_id')

        filtered_entries.append(filtered)

    with open(output_name, 'w') as f:
        json.dump(filtered_entries, f, indent=4)

def preview_corpus(corpus_nbib_path: str, n_entries: int):
    """
    Extract the first N entries from the corpus nbib file for preview.

    Returns:
        entries: list of first N entries.
    """
    current_entry = []
    entries = []
    with open(corpus_nbib_path, 'r') as infile:
        for line in infile:
            current_entry.append(line)

            if line.strip() == "":
                entries.append("".join(current_entry))
                current_entry = []

                if len(entries) == n_entries:
                    break

    for entry in entries:
        print(entry)

    return entries


def get_study(corpus_nbib_path: str, idx: int):
    """
    Retrieves a specific study from a JSON corpus file by index.

    Args:
        corpus_nbib_path (str): Path to the JSON file containing the study corpus.
        idx (int): Index of the study to retrieve.

    Returns:
        dict: A dictionary containing the study's title, abstract, and authors.
    """
    # Load the JSON file into a list of studies
    studies = json.loads(Path(corpus_nbib_path).read_text())

    # Retrieve the study at the specified index
    raw_study = studies[idx]

    # Extract title and abstract
    title = raw_study["title"]
    abstract = raw_study["abstract"]

    # Extract and format the list of abbreviated author names
    abbr_authors_list = [i["author_abbreviated"] for i in raw_study["authors"]]
    abbreviated_authors = ", ".join(abbr_authors_list)

    # Create the study dictionary
    study = {
        "title": title,
        "abstract": abstract,
        "authors": abbreviated_authors,
    }

    return study


def load_inclusion_criteria(prompt_path: str) -> Dict[str, Any]:
    """Load inclusion criteria from JSON file."""
    with open(prompt_path, 'r') as f:
        return json.load(f)


def load_llm_config(prompt_path: str) -> Dict[str, Any]:
    """Load llm configurations  from JSON file."""
    with open(prompt_path, 'r') as f:
        return json.load(f)


def extract_rating(ask_ai_response: str) -> Optional[int]:
    """Extract rating from ask_ai response."""
    patterns = [
        r"Rated\s*(\d)/4",
        r"Rating:\s*(\d)",
        r"Relevance:\s*Rated\s*(\d)"
    ]
    for pattern in patterns:
        if match := re.search(pattern, ask_ai_response):
            return int(match.group(1))
    return None

def extract_pre(pre_resonse: str):
    patterns = [
        r"Decision:\s*(\w+)"
    ]
    for pattern in patterns:
        if match := re.search(pattern, pre_resonse):
            return str(match.group(1))
    return None

"""
2. Function/API route
load data into screening_pages and save response from user and llms
"""

def get_study_template(study_id, title, abstract, llm_config):
    """Creates a template for each study with dynamic LLM responses based on configuration."""
    return {
        "study_id": study_id,
        "title": title,
        "abstract": abstract,
        "pre_review_status": "processing" if "pre_reviewer" in llm_config else "disabled",
        "co_review_status": "pending" if "co_reviewer" in llm_config else "disabled",
        "post_review_status": "pending" if "post_reviewer" in llm_config else "disabled",
        "user_feedback": {
            "decision": None
        },
        "llm_responses": {
            "pre_reviewer": None if "pre_reviewer" in llm_config else "unused",
            "co_reviewer": {
                "ask_ai_judgment": None if "co_reviewer" in llm_config else "unused",
                "tasks": {
                    "detailed_reasoning": None if llm_config.get("co_reviewer") == "high" else "unused",
                    "pico_extraction": None if llm_config.get("co_reviewer") == "high" else "unused"
                }
            } if "co_reviewer" in llm_config else "unused",
            "post_reviewer": None if "post_reviewer" in llm_config else "unused"
        },
        "chat_sessions": {
            "co_reviewer": [] if llm_config.get("co_reviewer") == "high" else "disabled",
            "post_reviewer": [] if llm_config.get("post_reviewer") == "high" else "disabled"
        }
    }

def get_screening_template(ai_config, pipeline):
    """Creates the main screening_pages.json structure based on AI config and pipeline."""
    return {
        "ai_interaction_level": ai_config,  # Defines if LLM responses are visible or interactive
        "pipeline": pipeline,  # Defines LLM processing order
        "pages": []  # Will store paginated studies
    }

def create_screening_pages(corpus_file, llm_config, pipeline, page_size=10):
    """
    Initializes screening_pages.json by structuring studies according to the LLM configuration.
    """
    with open(corpus_file, "r", encoding="utf-8") as f:
        corpus_data = json.load(f)

    screening_data = get_screening_template(llm_config, pipeline)

    pages = []
    for i in range(0, len(corpus_data), page_size):
        page_studies = corpus_data[i : i + page_size]
        page_index = i // page_size

        studies_list = [
            get_study_template(study["study_id"], study["title"], study["abstract"], llm_config)
            for study in page_studies
        ]

        page_entry = {
            "page_index": page_index,
            "studies": studies_list
        }
        pages.append(page_entry)

    screening_data["pages"] = pages

    with open("screening_pages.json", "w", encoding="utf-8") as f:
        json.dump(screening_data, f, indent=4)

    print(f"✅ Screening pages initialized with {len(pages)} pages.")