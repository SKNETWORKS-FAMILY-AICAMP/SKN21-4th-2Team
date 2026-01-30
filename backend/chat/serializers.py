from rest_framework import serializers
from .models import CustomUser, Chat, Chat_Message


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


# 채팅 요청 Serializer
class ChatRequestSerializer(serializers.Serializer):
    question = serializers.CharField(required=True)
    youtuber_name = serializers.CharField(default="김달")


# 채팅 응답 Serializer
class ChatResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    youtuber_name = serializers.CharField()
    status = serializers.CharField(default="success")
