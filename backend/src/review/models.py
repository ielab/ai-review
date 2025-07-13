from django.db import models
from account.models import User
import os
import json

PROMPT_DIR = os.path.join(os.path.dirname(__file__), "prompts")

# Create your models here.
class Corpus(models.Model):
    CORPUS_STATUSES = [
        ("active", "Active"),
        ("admin_delete", "Deleted by Admin"),
        ("upload_failed", "Upload Failed"),
    ]

    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    status              = models.CharField(max_length=32, choices=CORPUS_STATUSES)
    hash_corpus_path    = models.CharField(max_length=32, default=None, null=True)
    real_corpus_path    = models.CharField(max_length=100, default=None, null=True)
    corpus_first_entry  = models.TextField(max_length=1000, default=None, null=True)
    pmids               = models.JSONField(default=None, null=True)
    # default fields
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'corpus'

class Review(models.Model):
    STRUCTURE_TYPES = [
        ("page_based", "Page-Based"),
        ("study_centric", "Study-Centric"),
    ]
    
    SCREENING_STATUSES = [
        ("not_start", "Not Start"),
        ("screening", "Screening"),
        ("paused", "Paused"),
        ("finished", "Finished"),
        ("post-review", "Post-Review"),
    ]
    RANKING_METHODS = [
        ("original", "Original"),
        ("alphabetic", "Alphabetic"),
        ("dense", "Dense"),
        ("custom", "Custom Field")
    ]
    PIPELINE_TYPES = [
        ("pre-only", "Pre-only"),
        ("pre-co", "Pre-co"),
        ("co-only", "Co-only"),
        ("pre-post", "Pre-post"),
        ("co-post", "Co-post"),
        ("post-only", "Post-only"),
        ("full", "Full")
    ]

    user                    = models.ForeignKey(User, on_delete=models.CASCADE)
    corpus                  = models.ForeignKey(Corpus, on_delete=models.CASCADE)
    name                    = models.CharField(max_length=150)
    screening_status        = models.CharField(max_length=32, choices=SCREENING_STATUSES, default="not_start")
    structure_type          = models.CharField(max_length=20, choices=STRUCTURE_TYPES, default="page_based",
                                      help_text="Format of the screening pages data structure")
    current_screening_page  = models.IntegerField(default=1, null=True)
    show_docs_per_page      = models.IntegerField(default=5, null=False)
    pipeline_type           = models.CharField(max_length=32, choices=PIPELINE_TYPES, default=None, null=True)
    llm_interaction_level   = models.BooleanField(default=None, null=True)
    inclusion_criteria      = models.JSONField(default=None, null=True)
    # json fields
    screening_pages         = models.JSONField(default=None, null=True)
    ranking_method          = models.CharField(max_length=32, choices=RANKING_METHODS, default="original")
    sorting_config          = models.JSONField(default=dict, help_text="Additional sorting configuration parameters")
    page_screening_log      = models.JSONField(default=None, null=True)
    include_docs            = models.JSONField(default=None, null=True)
    exclude_docs            = models.JSONField(default=None, null=True)
    user_interactions       = models.JSONField(default=None, null=True)
    llm_parameters          = models.JSONField(default=None, null=True)
    co_ask_ai_prompt        = models.JSONField(default=None, null=True)
    # reviewing time
    started_screening_at    = models.DateTimeField(default=None, null=True)
    paused_screening_at     = models.DateTimeField(default=None, null=True)
    finished_screening_at   = models.DateTimeField(default=None, null=True)
    # job
    pos_at_waiting_queue    = models.IntegerField()
    # default fields
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_at              = models.DateTimeField(auto_now=True)
    archived_at             = models.DateTimeField(default=None, null=True)

    class Meta:
        db_table = 'review'

class MasterPromptConfig(models.Model):
    PROMPT_TYPES = [
        ("pre_prompt", "Pre prompt"),
        ("co_ask_ai_prompt", "Co ask AI prompt"),
        ("co_pico_extract_prompt", "Co pico extract prompt"),
        ("co_detail_reason_prompt", "Co detailed reasoning prompt"),
        ("post_prompt", "Post prompt")
    ]

    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    review              = models.ForeignKey(Review, on_delete=models.CASCADE)
    prompt_type         = models.CharField(max_length=32, choices=PROMPT_TYPES, default=None, null=True)
    prompt_content      = models.JSONField(default=None, null=True)
    # default fields
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    @staticmethod
    def default_prompt(prompt_type):
        """
        Loads a default prompt from the 'prompts/' folder.
        Returns both 'system' and 'assistant' parts.
        """
        prompt_path = os.path.join(PROMPT_DIR, f"{prompt_type}.json")

        if not os.path.exists(prompt_path):
            return {}  # Return empty if not found

        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return data.get("aireview_template", {})

        except json.JSONDecodeError:
            return {}

    @classmethod
    def ensure_prompts_exist(cls, user, review):
        """
        Ensures that all required prompts for the selected pipeline are stored.
        """
        PIPELINE_PROMPT_MAP = {
            "pre-only": ["pre_prompt"],
            "co-only": ["co_ask_ai_prompt", "co_detail_reason_prompt", "co_pico_extract_prompt"],
            "post-only": ["post_prompt"],
            "pre-co": ["pre_prompt", "co_ask_ai_prompt", "co_detail_reason_prompt", "co_pico_extract_prompt"],
            "pre-post": ["pre_prompt", "post_prompt"],
            "co-post": ["co_ask_ai_prompt", "co_detail_reason_prompt", "co_pico_extract_prompt", "post_prompt"],
            "full": ["pre_prompt", "co_ask_ai_prompt", "co_detail_reason_prompt", "co_pico_extract_prompt",
                     "post_prompt"]
        }

        required_prompts = PIPELINE_PROMPT_MAP.get(review.pipeline_type, [])
        loaded_prompts = []

        for prompt_type in required_prompts:
            prompt_config, created = cls.objects.get_or_create(
                user=user,
                review=review,
                prompt_type=prompt_type,
                defaults={"prompt_content": cls.default_prompt(prompt_type)}
            )
            if created:
                loaded_prompts.append(prompt_type)

        return loaded_prompts  # Return list of prompts that were just loaded

    class Meta:
        db_table = 'master_prompt_config'