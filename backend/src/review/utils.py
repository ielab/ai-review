# import
import os, logging, hashlib, nbib, json, math, uuid
from time import sleep
from datetime import datetime, timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.text import get_valid_filename
from django.conf import settings
from django.shortcuts import get_object_or_404
import re
from typing import Dict, Any, Optional

# import utilities function
from account.models import User
from review.models import Corpus

logger = logging.getLogger(__name__)


# functions
def get_utc_datetime():
    # Get the current UTC datetime
    return datetime.now(timezone.utc).isoformat()


def creat_user_dir(user, format_user_id):
    """
    Create temp and corpus directory for each user.
        @param      user                object      An user's who upload the file.
        @param      format_user_id      string      Format user id.
    """
    # Create user directory if not exist
    for dir in ["temp", "corpus"]:

        # Is directory exist
        user_dir = os.path.join(settings.MOUNT_CORPUS_PATH, format_user_id, dir)
        if not os.path.exists(user_dir):
            # Create directory
            os.makedirs(user_dir)
            logger.info(f"Create folder '{user_dir}' for user({user.username}).")


def hash_blake2s_32digit(key, value):
    """
    Hash the value and return the hash value in hexadecimal format 32-bit long.
        @param      key         key to be hashed
        @param      value       value to be hashed
        @return     hash value in hexadecimal format
    """
    hash_obj = hashlib.blake2s(key.encode("utf-8"), digest_size=16)
    hash_obj.update(value.encode("utf-8"))
    return hash_obj.hexdigest()


def validate_upload_file(format_user_id: int, nbib_file: str):
    """
    Validate upload file.
        @param      format_user_id      string      An user id who upload the file.
        @param      nbib_file           string      A dataset file.
    """
    # Get file extension
    file_extension = nbib_file.name.split(".")[-1]

    # Real corpus path
    real_corpus_path = os.path.join(settings.MOUNT_CORPUS_PATH, format_user_id, "temp", nbib_file.name)

    # Validate .nbib file
    if not (file_extension in ["nbib", "ris"]):
        raise ValueError(
            f"Invalid file format: .{file_extension}. Please upload a file with a .nbib or .ris extension.")

    # Validate duplicate file (in temp)
    if os.path.exists(real_corpus_path):
        raise FileExistsError(
            f"File with the same name('{nbib_file.name}') already exists. Please rename the file before upload again.")


def validate_unique_pmid(corpus_path: str):
    seen_pmids = set()
    with open(corpus_path, 'r') as infile:
        corpus_data = json.load(infile)

        for study in corpus_data:
            pmid = study.get('pmid')
            if pmid in seen_pmids:
                raise ValueError(f"Uploaded file has duplicated pmid: {pmid}")
            seen_pmids.add(pmid)


def save_temp_file(user: object, format_user_id: str, format_corpus_id: str, nbib_file: str):
    """
    Save upload .nbib file.
        @param      user                object      An user's who upload the file.
        @param      format_user_id      string      Format user id.
        @param      format_corpus_id    string      Format corpus id.
        @param      nbib_file           string      A corpus file.
    """
    # Sanitize the filename to prevent directory traversal
    safe_filename = get_valid_filename(nbib_file.name)
    save_path = os.path.join("user-corpus", format_user_id, "temp", safe_filename)

    # path to save corpus.json file
    save_corpus_path = os.path.join(settings.MOUNT_CORPUS_PATH, format_user_id, "corpus", format_corpus_id)
    save_corpus_filename = os.path.join(save_corpus_path, "corpus.json")
    os.makedirs(save_corpus_path, exist_ok=True)

    # Create upload folder
    upload_folder = os.path.join(save_corpus_path, "upload")
    os.makedirs(upload_folder, exist_ok=True)

    # Save file into local storage
    default_storage.save(save_path, ContentFile(nbib_file.read()))

    return save_path, save_corpus_filename, upload_folder


def get_uploaded_file_path(user_id, corpus_id):
    user_upload_dir = os.path.join(settings.MOUNT_CORPUS_PATH, f"u{user_id:05d}", "corpus", f"c{corpus_id:05d}",
                                   "upload")
    return [os.path.join(user_upload_dir, i) for i in os.listdir(user_upload_dir)][0]


def clear_temp_folder(user, format_user_id: str):
    """
    Remove nbib file in temporarity that store more than 24 hr.
        @param      user                object      An user's who upload the file.
        @param      format_user_id      string      Format user id.
    """
    # Temp path
    temp_path = os.path.join(settings.MOUNT_CORPUS_PATH, format_user_id, "temp")
    now = datetime.now()

    # List all files and directories in the specified path
    files = os.listdir(temp_path)
    for f in files:
        # File path
        file_path = os.path.join(temp_path, f)

        # Get the time of last modified
        modified_time = os.path.getmtime(file_path)

        # Converting the time in seconds to datetime
        last_modified = datetime.fromtimestamp(modified_time)

        # Calculate difference hour
        diff = (now - last_modified).total_seconds() // 3600

        # Remove file if store in temp >= 24 hr
        if diff >= 24:
            os.remove(file_path)
            logger.info(
                f"Remove user({user})'s previously uploaded file, because this file({file_path}) is older than 24 hours.")


# def get_number_of_queue(queue_name):

#     rabbitmq_user       = settings.RABBITMQ_DEFAULT_USER
#     rabbitmq_password   = settings.RABBITMQ_DEFAULT_PASS

#     sleep(0.75)
#     response = requests.get(
#         f"http://rabbitmq:15672/api/queues/%2F/{queue_name}",
#         auth=(rabbitmq_user, rabbitmq_password),
#     )

#     queue_info = response.json()
#     return queue_info["messages"]


# Save temporary JSON files
def save_temporary_file(user_corpus_dir, data, input_type):
    """
    Saves data to a temporary file in the specified directory.

    Parameters:
        user_corpus_dir (str): Directory where the file should be saved.
        data (dict or list): Data to be saved.
        input_type (str): Type of input to determine file name and format.

    Returns:
        str: Path to the saved file.
    """
    # Define file name based on input type
    file_mapping = {
        "pico_query": "query.json",
        "corpus4tevatron": "corpus4tevatron.jsonl"
    }
    if input_type not in file_mapping:
        raise ValueError(f"Unsupported input_type: {input_type}")

    save_path = os.path.join(user_corpus_dir, file_mapping[input_type])

    # Save data
    with open(save_path, "w") as f:
        if input_type == "pico_query":
            json.dump(data, f)
        else:  # "corpus4tevatron"
            f.writelines(json.dumps(record) + "\n" for record in data)

    logger.info(f"Created temporary file: {save_path}")
    return save_path


def update_feedback(review_obj, page_index, in_page_rank_index, pmid, feedback):
    # Update user interaction
    def update_user_interact(previous_feedback, study):
        # Retrieve user interactions or initialize as an empty list
        user_interact = review_obj.user_interaction or []

        # Return early if feedback hasn't changed
        if previous_feedback == study["feedback"]:
            return user_interact

        # Extract study details
        pmid = study["pmid"]
        feedback = study["feedback"]
        timestamp = study["feedback_updated_at"]

        if feedback == "unjudge":
            # Remove entries with the same PMID
            user_interact = [item for item in user_interact if item["pmid"] != pmid]
        else:
            # Attempt to find the study in the list
            for item in user_interact:
                if item["pmid"] == pmid:
                    # Update existing entry
                    item.update({"feedback": feedback, "timestamp": timestamp})
                    break
            else:
                # Append a new entry if not found
                user_interact.append({"pmid": pmid, "feedback": feedback, "timestamp": timestamp})

        return user_interact

    # Validate indices and structure
    if page_index >= len(review_obj.ranking_pages) or page_index < 0:
        raise ValueError(f"Page index {page_index} is out of range.")

    ranking_page = review_obj.ranking_pages[page_index]

    if "in_page_docs" not in ranking_page or in_page_rank_index >= len(
            ranking_page["in_page_docs"]) or in_page_rank_index < 0:
        raise ValueError(f"In-page rank index {in_page_rank_index} is out of range or 'in_page_docs' is missing.")

    # Access the specific study
    study = ranking_page["in_page_docs"][in_page_rank_index]

    # Validate PMID
    if "pmid" not in study or study["pmid"] != pmid:
        raise ValueError(f"Mismatch: Page({page_index}), Rank Index({in_page_rank_index}), PMID({pmid}) not found.")

    # Capture previous feedback
    previous_feedback = study.get("feedback", None)

    # Update feedback fields
    now = get_utc_datetime()
    study["feedback"] = feedback
    study["feedback_created_at"] = now if study["feedback_created_at"] is None else study["feedback_created_at"]
    study["feedback_updated_at"] = now

    # Save changes
    review_obj.ranking_pages[page_index]["in_page_docs"][in_page_rank_index] = study
    review_obj.user_interaction = update_user_interact(previous_feedback, study)
    review_obj.save()

    # Return previous feedback
    return previous_feedback


def updated_review_type(review_obj, pmid, previous_feedback, feedback):
    # Helper to update a specific list by removing and adding items
    def update_list(doc_list, pmid, action, title=None):
        if action == "remove":
            doc_list[:] = [doc for doc in doc_list if doc.get("pmid") != pmid]
        elif action == "add" and title is not None:
            doc_list.append({"pmid": pmid, "title": title})

    # Initialize lists
    doc_lists = {
        "include": review_obj.include_docs or [],
        "exclude": review_obj.exclude_docs or [],
        "maybe": review_obj.maybe_docs or []
    }

    # Remove item from the previous feedback list, if it exists
    if previous_feedback in doc_lists:
        update_list(doc_lists[previous_feedback], pmid, "remove")

    # Add item to the new feedback list, if applicable
    if feedback in doc_lists:
        title = review_obj.corpus.pmids[pmid].get("title")
        update_list(doc_lists[feedback], pmid, "add", title=title)

    # Update review_obj lists
    review_obj.include_docs = doc_lists["include"]
    review_obj.exclude_docs = doc_lists["exclude"]
    review_obj.maybe_docs = doc_lists["maybe"]

    # Save changes
    review_obj.save()


def count_user_interaction(user_interaction):
    counter = 0
    x_axis, y_axis = [], []
    for i, j in enumerate(user_interaction or []):
        if j["feedback"] == "include":
            counter += 1
        elif j["feedback"] == "unjudge":
            pass

        x_axis.append(i + 1)
        y_axis.append(counter)

    if len(x_axis) == 0 and len(y_axis) == 0:
        return [0], [0]
    else:
        return x_axis, y_axis


def summary_data(review_obj, page_index, show_total=True):
    # Prepare dashboard data
    dashboard_data = dict()

    # Extract ranking pages and the current page's documents
    ranking_pages = review_obj.ranking_pages
    current_page_docs = ranking_pages[page_index]["in_page_docs"]

    # Initialize counters
    feedback_counter = {"include": 0, "exclude": 0, "maybe": 0}

    # Count feedback on the current page
    for doc in current_page_docs:
        feedback = doc.get("feedback", None)
        if feedback in feedback_counter:
            feedback_counter[feedback] += 1

    # Prepare dashboard data
    dashboard_data["current_page_review"] = {
        "total_number_to_review": len(current_page_docs),
        "reviewed": sum(feedback_counter.values()),
        "include": feedback_counter["include"],
        "maybe": feedback_counter["maybe"],
        "exclude": feedback_counter["exclude"]
    }

    # Total counter
    if show_total:
        # Initialize counters
        total_number_to_review = 0
        total_feedback = {"include": 0, "exclude": 0, "maybe": 0}

        # Count total documents and feedback across all pages
        # for page in ranking_pages:
        #     total_number_to_review += len(page["in_page_docs"]) + len(page["remaining_ranking"])
        total_number_to_review += len(ranking_pages[0]["in_page_docs"]) + len(ranking_pages[0]["remaining_ranking"])

        # Aggregate totals from include, exclude, maybe
        total_feedback["include"] = len(review_obj.include_docs or [])
        total_feedback["exclude"] = len(review_obj.exclude_docs or [])
        total_feedback["maybe"] = len(review_obj.maybe_docs or [])
        total_reviewed = sum(total_feedback.values())

        # Prepare dashboard data
        dashboard_data["total_page_review"] = {
            "total_number_to_review": total_number_to_review,
            "reviewed": total_reviewed,
            "include": total_feedback["include"],
            "maybe": total_feedback["maybe"],
            "exclude": total_feedback["exclude"]
        }

        # Count user interaction
        x_axis, y_axis = count_user_interaction(review_obj.user_interaction)
        dashboard_data["relevance_discovery_curve"] = {
            "x-axis": {
                "value": x_axis,
                "label": "No. of Reviewed Clinical Studies"
            },
            "y-axis": {
                "value": y_axis,
                "label": "No. of Relevant Clinical Studies"
            }
        }

    return dashboard_data


def validate_prev_review(prev_review):
    # Validate in page of previous review
    for item in prev_review:
        if item["feedback"] == "unjudge":
            return True


def update_page_screening_log(review_obj, page_index, is_done=False):
    # Define variables
    page_screening_log = review_obj.page_screening_log or []  # Default to empty list
    now = get_utc_datetime()  # Get current UTC datetime

    # Ensure the log list has enough entries for the given index
    while len(page_screening_log) <= page_index:  # Expand the list if index doesn't exist
        page_screening_log.append({"started_at": now, "lastest_resumed_at": now, "finished_at": None})

    # Update the log for the given index
    page_screening_log[page_index]["lastest_resumed_at"] = now  # Always update 'lastest_resumed_at'

    # Mark as finished if specified
    if is_done:
        page_screening_log[page_index]["finished_at"] = now

    # Save updated log back to the review object
    review_obj.page_screening_log = page_screening_log
    review_obj.save()


def get_all_pages(review_obj):
    # Extract ranking pages and the current page's documents
    ranking_pages = review_obj.ranking_pages
    show_docs_per_page = review_obj.show_docs_per_page

    # Count number to review
    total_number_to_review = len(ranking_pages[0]["in_page_docs"]) + len(ranking_pages[0]["remaining_ranking"])

    # Calculate
    return math.ceil(total_number_to_review / show_docs_per_page)


def summary_review_progress(data: list):
    # Initialize counters
    feedback_counter = {"include": 0, "exclude": 0, "maybe": 0}

    for doc in data:
        feedback = doc.get("feedback", None)
        if feedback in feedback_counter:
            feedback_counter[feedback] += 1

    # Prepare dashboard data
    dashboard_data = {
        "reviewed": sum(feedback_counter.values()),
        "include": feedback_counter["include"],
        "maybe": feedback_counter["maybe"],
        "exclude": feedback_counter["exclude"]
    }

    return dashboard_data


def remove_file_from_local_storage(file_path):
    """
    Remove the specified file or the latest file in the specified directory.
        @param      file_path   string   Path to the file or directory.
    """
    if os.path.isdir(file_path):
        # Get the list of files in the directory
        files = os.listdir(file_path)
        if files:
            # Remove the latest file
            latest_file = os.path.join(file_path, files[-1])
            os.remove(latest_file)
            logger.info(f"Removed file: {latest_file}")
        else:
            logger.warning(f"No files to remove in directory: {file_path}")
    else:
        # Remove the file
        os.remove(file_path)
        logger.info(f"Removed file: {file_path}")


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

                if len(entries) > n_entries:
                    break
    print(entries[n_entries])

    return entries


def corpus_converter(corpus_path: str):
    """
    Parse the corpus and output three dicts and saved in json or jsonl files.

    Example Inputs:
    docid2pmid.json = {docid(int): pmid(str),}
    corpus4tevatron.jsonl = {"docid": ,"title": ,"text": }{}
    pmids.json = {"pmid": {"title":,"abstract":,"authors":,}{}}
    """
    # docid2pmid = {}
    # corpus4tevatron = []
    pmids = {}

    with open(corpus_path, 'r') as infile:
        corpus_data = json.load(infile)

        for study in corpus_data:
            pmid = study.get('pmid')
            title = study.get('title')
            abstract = study.get('abstract')
            authors = study.get('authors')

            # docid2pmid[pmid] = str(pmid)

            # corpus4tevatron_study = {
            #     "docid": int(pmid),
            #     "title": title,
            #     "text": abstract,
            # }
            # corpus4tevatron.append(corpus4tevatron_study)

            pmids[str(pmid)] = {
                "title": title,
                "abstract": abstract,
                "authors": authors
            }

        # with open('docid2pmid.json', 'w') as outfile:
        #     json.dump(docid2pmid, outfile, indent=4)
        # with open('corpus4tevatron.jsonl', 'w') as outfile:
        #     for study in corpus4tevatron:
        #         jsonl_string = json.dumps(study)
        #         outfile.write(jsonl_string + '\n')
        # with open('pmids.json', 'w') as outfile:
        #     json.dump(pmids, outfile, indent=4)

    # return docid2pmid, corpus4tevatron, pmids
    return pmids


def get_review(request, review_id):
    """Retrieve a review entry from the database."""
    review = get_object_or_404(Review, id=review_id)
    return JsonResponse({
        "id": review.id,
        "title": review.title,
        "status": review.status
    })


def get_study_template(pmid, title, authors, abstract):
    """Creates a template for each study with dynamic LLM responses based on configuration."""
    # Extract and format the list of abbreviated author names
    abbr_authors_list = [i["author_abbreviated"] for i in authors]
    abbreviated_authors = ", ".join(abbr_authors_list)
    return {
        "pmid": pmid,
        "title": title,
        "authors": abbreviated_authors,
        "abstract": abstract,
        # "pre_review_status": "processing" if "pre_reviewer" in llm_config else "disabled",
        # "co_review_status": "pending" if "co_reviewer" in llm_config else "disabled",
        # "post_review_status": "pending" if "post_reviewer" in llm_config else "disabled",
        "user_feedback": None,
        "co_rating": None  # for co_detail_reason
        # "llm_responses": {
        #     "pre_reviewer": None if "pre_reviewer" in llm_config else "unused",
        #     "co_reviewer": {
        #         "ask_ai_judgment": None if "co_reviewer" in llm_config else "unused",
        #         "tasks": {
        #             "detailed_reasoning": None if llm_config.get("co_reviewer") == "high" else "unused",
        #             "pico_extraction": None if llm_config.get("co_reviewer") == "high" else "unused"
        #         }
        #     } if "co_reviewer" in llm_config else "unused",
        #     "post_reviewer": None if "post_reviewer" in llm_config else "unused"
        # },
        # "chat_sessions": {
        #     "co_reviewer": [] if llm_config.get("co_reviewer") == "high" else "disabled",
        #     "post_reviewer": [] if llm_config.get("post_reviewer") == "high" else "disabled"
        # }
    }


def get_screening_template():
    """(DenseReviewer pagination) Creates the main screening_pages.json structure based on AI config and pipeline."""
    return {
        # "ai_interaction_level": ai_config,  # Defines if LLM responses are visible or interactive
        # "pipeline": pipeline,  # Defines LLM processing order
        "pages": []  # Will store paginated studies
    }


def get_page_based_study_template(pmid, title, authors, abstract):
    """Creates a template for page-based structure"""
    # Extract and format the list of abbreviated author names
    if isinstance(authors, list):
        abbr_authors_list = [i.get("author_abbreviated", i.get("name", "")) for i in authors]
        abbreviated_authors = ", ".join(abbr_authors_list)
    else:
        abbreviated_authors = authors

    return {
        "pmid": pmid,
        "title": title,
        "authors": abbreviated_authors,
        "abstract": abstract,
        "user_feedback": None,
        "pre_response": None,
        "co_rating": None,
        "post_response": None
    }


def get_study_centric_template(pmid, title, authors, abstract):
    """Creates a template for study-centric structure with a unique study_id"""
    # Extract and format the list of abbreviated author names
    if isinstance(authors, list):
        abbr_authors_list = [i.get("author_abbreviated", i.get("name", "")) for i in authors]
        abbreviated_authors = ", ".join(abbr_authors_list)
    else:
        abbreviated_authors = authors

    return {
        "study_id": pmid,  # Using PMID as the unique identifier
        "pmid": pmid,
        "title": title,
        "authors": abbreviated_authors,
        "abstract": abstract,
        "user_feedback": None,
        "pre_response": None,
        "co_rating": None,
        "post_response": None,
        "feedback_created_at": None,
        "feedback_updated_at": None
    }


def create_screening_pages(corpus_file, page_size=5):
    """
    Initializes screening_pages.json by structuring studies according to the LLM configuration.
    """
    with open(corpus_file, "r", encoding="utf-8") as f:
        corpus_data = json.load(f)

    # screening_data = get_screening_template(llm_config, pipeline)
    screening_data = get_screening_template()

    pages = []
    page_size = int(page_size)
    for i in range(0, len(corpus_data), page_size):
        page_studies = corpus_data[i: i + page_size]
        page_index = i // page_size

        studies_list = [
            get_study_template(study["pmid"], study["title"], study["authors"], study["abstract"])
            for study in page_studies
        ]

        page_entry = {
            "page_index": page_index,
            "studies": studies_list
        }
        pages.append(page_entry)

    screening_data["pages"] = pages
    print(f"✅ Screening pages initialized with {len(pages)} pages.")

    # with open("screening_pages.json", "w", encoding="utf-8") as f:
    #     json.dump(screening_data, f, indent=4)
    return screening_data


def create_page_based_screening_pages(corpus_file, page_size=25):
    """
    Initialize screening pages with traditional page-based structure.
    Default page size is 25 for this mode.
    """
    with open(corpus_file, "r", encoding="utf-8") as f:
        corpus_data = json.load(f)

    screening_data = {"pages": []}

    # Group studies into pages
    for i in range(0, len(corpus_data), page_size):
        page_studies = corpus_data[i: i + page_size]
        page_index = i // page_size

        studies_list = [
            get_page_based_study_template(
                study["pmid"], study["title"], study["authors"], study["abstract"]
            )
            for study in page_studies
        ]

        page_entry = {
            "page_index": page_index,
            "studies": studies_list
        }
        screening_data["pages"].append(page_entry)

    logger.info(f"✅ Screening pages initialized with {len(screening_data['pages'])} pages (page-based structure).")
    return screening_data


def create_study_centric_screening_pages(corpus_file):
    """
    Initialize screening pages with flat study-centric structure.
    """
    with open(corpus_file, "r", encoding="utf-8") as f:
        corpus_data = json.load(f)

    screening_data = {"studies": []}

    # Add all studies to a flat list
    for study in corpus_data:
        study_entry = get_study_centric_template(
            study["pmid"], study["title"], study["authors"], study["abstract"]
        )
        screening_data["studies"].append(study_entry)

    logger.info(
        f"✅ Screening data initialized with {len(screening_data['studies'])} studies (study-centric structure).")
    return screening_data


def get_paginated_studies(review_obj, page_index):
    """
    Get paginated studies based on structure type and page size.
    Handles both page-based and study-centric structures.
    Applies sorting according to the review's ranking_method and sorting_config.
    """
    structure_type = review_obj.structure_type
    page_size = review_obj.show_docs_per_page
    ranking_method = review_obj.ranking_method

    # Get additional sorting parameters from sorting_config
    sorting_config = review_obj.sorting_config or {}
    sort_direction = sorting_config.get('sort_direction', 'asc')
    sort_field = sorting_config.get('sort_field')

    # Handle page-based structure
    if structure_type == 'page_based':
        screening_pages = review_obj.screening_pages

        # Validate page_index
        if "pages" not in screening_pages or not screening_pages["pages"]:
            return {
                "studies": [],
                "pagination": {
                    "current_page": 0,
                    "total_pages": 0,
                    "page_size": page_size,
                    "total_studies": 0
                }
            }

        total_pages = len(screening_pages["pages"])

        # Adjust page_index if out of bounds
        if page_index >= total_pages:
            page_index = total_pages - 1
        if page_index < 0:
            page_index = 0

        # Get the page
        page = screening_pages["pages"][page_index]
        studies = page.get("studies", [])

        # Count total studies across all pages
        total_studies = 0
        for p in screening_pages["pages"]:
            total_studies += len(p.get("studies", []))

        return {
            "studies": studies,
            "pagination": {
                "current_page": page_index,
                "total_pages": total_pages,
                "page_size": len(studies),
                "total_studies": total_studies
            }
        }

    # Handle study-centric structure
    else:  # structure_type == 'study_centric'
        studies = review_obj.screening_pages.get("studies", [])

        # Apply sorting based on ranking method with additional config
        sorted_studies = sort_studies(studies, ranking_method, sort_direction, sort_field)

        # Calculate pagination info
        total_studies = len(sorted_studies)
        total_pages = math.ceil(total_studies / page_size) if total_studies > 0 else 1

        # Validate page_index
        if page_index >= total_pages:
            page_index = total_pages - 1
        if page_index < 0:
            page_index = 0

        # Get studies for current page
        start_idx = page_index * page_size
        end_idx = min(start_idx + page_size, total_studies)
        page_studies = sorted_studies[start_idx:end_idx] if start_idx < total_studies else []

        # Prepare sorting info - for 'original' method, direction is not applicable
        sorting_info = {
            "method": ranking_method,
            "field": sort_field
        }

        # Only include direction for non-original methods
        if ranking_method != "original":
            sorting_info["direction"] = sort_direction

        return {
            "studies": page_studies,
            "pagination": {
                "current_page": page_index,
                "total_pages": total_pages,
                "page_size": page_size,
                "total_studies": total_studies,
                "start_index": start_idx + 1 if studies else 0,
                "end_index": end_idx,
                "sorting": sorting_info
            }
        }


# LLM processing
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


def sort_studies(studies, ranking_method, sort_direction="asc", sort_field=None):
    """
    Sort studies based on the specified ranking method.

    Args:
        studies (list): List of study dictionaries to be sorted
        ranking_method (str): The ranking method to apply ('original', 'alphabetic', 'dense')
        sort_direction (str): Direction of sorting ('asc' or 'desc'), ignored for 'original' method
        sort_field (str, optional): For custom sorting, the field to sort by

    Returns:
        list: Sorted list of studies
    """
    # Create a copy to avoid modifying the original
    sorted_studies = studies.copy()

    # Determine the reverse parameter for sort (True for descending)
    # (ignored for 'original' method)
    reverse = sort_direction.lower() == "desc"

    if ranking_method == "alphabetic":
        # Sort studies alphabetically by title
        sorted_studies.sort(key=lambda study: study.get("title", "").lower(), reverse=reverse)
    elif ranking_method == "dense":
        # Placeholder for future dense ranking implementation
        # For now, maintain original order
        logger.info("Dense ranking not yet implemented, using original order")
    elif ranking_method == "custom" and sort_field:
        # Custom sorting by specified field
        sorted_studies.sort(key=lambda study: study.get(sort_field, ""), reverse=reverse)
    elif ranking_method == "original":
        # For original method, always sort by original_index, ignoring direction
        # Check if studies have original_index field for precise ordering
        if any("original_index" in study for study in studies):
            # Sort by original_index if available (always ascending)
            sorted_studies.sort(key=lambda study: study.get("original_index", 0))
            logger.debug("Sorted studies using original_index")
        else:
            # Keep the original order if no index is available
            logger.debug("Keeping original order (no original_index available)")
    else:  # any unrecognized method
        # Keep the original order
        pass

    return sorted_studies


def add_original_index_to_studies(review_obj):
    """
    Adds original_index to studies if it doesn't exist.
    This ensures backward compatibility for existing reviews.

    Args:
        review_obj: The Review object to update

    Returns:
        bool: True if changes were made, False otherwise
    """
    if review_obj.structure_type != 'study_centric':
        return False

    changed = False
    studies = review_obj.screening_pages.get("studies", [])

    # Check if original_index needs to be added
    if studies and not any("original_index" in study for study in studies):
        logger.info(f"Adding original_index to {len(studies)} studies for review {review_obj.id}")

        # Add original_index to each study
        for idx, study in enumerate(studies):
            study["original_index"] = idx

        # Save changes
        review_obj.screening_pages["studies"] = studies
        review_obj.save()
        changed = True

    return changed