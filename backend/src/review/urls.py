from django.urls import path
from review.views import *
from django.urls import re_path
from rest_framework import permissions


urlpatterns = [
    path('studies', StudyListAPIView.as_view()),
    path('study_cards', StudyCardView.as_view()),
    path('generative_content', GetStudyByIdView.as_view()),
    path('upload_corpus', FileUploadView.as_view()),
    path('dataset_creation', DatasetCreationView.as_view()),
    path('llm_config', LlmConfigView.as_view()),
    path('llm_process', LlmProcessView.as_view()),
    path('user_feedback', UserFeedbackView.as_view()),
    path('get_llm_config', GetLlmConfigView.as_view()),
    path('update_pagination', UpdatePaginationView.as_view()),
    path('migrate_structure', MigrateStructureView.as_view()),
    path('update_sorting', UpdateSortingView.as_view()),
    path('results_checking_pause', ResultsCheckingPauseView.as_view()),
    path('results_checking_final', ResultsCheckingFinalView.as_view()),
    path('review_progress', ReviewProgressView.as_view()),
    path('post_review_table', PostReviewTableView.as_view()),
    path('update_prompt', UpdatePromptView.as_view())

]
