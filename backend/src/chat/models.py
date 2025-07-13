from django.db import models
from review.models import Review
from account.models import User

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    study_pmid = models.CharField(max_length=32, null=True, blank=True)  # Optional: for study-level chat
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = models.JSONField(default=list)  # List of {"role": "user"/"assistant", "content": "...", "timestamp": ...}

    class Meta:
        db_table = 'chat_session'