from django.contrib.auth import get_user_model

from rest_framework import serializers

User = get_user_model()

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        