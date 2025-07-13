# Import
from rest_framework import serializers
from review.models import Review

# Serializer Class
class StudySerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "name",
            "screening_status",
            "pipeline_type",
            "current_screening_page",
            "show_docs_per_page",
            "created_at",
        ]

class StudyCardSerializer(serializers.Serializer):
    pmid = serializers.CharField()
    title = serializers.CharField()
    authors = serializers.CharField()
    abstract = serializers.CharField()
    user_feedback = serializers.CharField(allow_null=True)
    pre_response = serializers.CharField(allow_null=True)
    co_rating = serializers.CharField(allow_null=True)
    post_response = serializers.CharField(allow_null=True)

class InferenceReview(serializers.ModelSerializer):
    class Meta:
            model = Review
            fields = ['id']  # Include only the 'id' field by default

    def to_representation(self, instance):
        """
        Customize the serialized output to include 'id' and the requested 'project_field'.
        """
        # Get the default representation
        data = super().to_representation(instance)

        # Add the project_field dynamically if passed in the serializer's context
        project_field = self.context.get('project_field', None)
        if project_field and hasattr(instance, project_field):
            data[project_field] = getattr(instance, project_field)
        return data
