from rest_framework import serializers
from .models import Chat, Chat_Message
from account.models import CustomUser

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat_Message
        fields = ['message_id', 'role', 'message', 'created_at']

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['session_id', 'created_at', 'is_active']


