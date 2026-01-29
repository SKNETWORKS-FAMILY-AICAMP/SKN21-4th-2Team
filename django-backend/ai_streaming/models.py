from django.db import models
from django.contrib.auth.models import User


class ChatSession(models.Model):
    """채팅 세션 모델 - 각 대화 세션을 관리"""
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    persona = models.CharField(max_length=50, default='기본상담사')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = '채팅 세션'
        verbose_name_plural = '채팅 세션들'
    
    def __str__(self):
        return f"{self.persona} - {self.session_id[:8]}"


class Message(models.Model):
    """메시지 모델 - 각 대화 메시지를 저장"""
    ROLE_CHOICES = [
        ('user', '사용자'),
        ('assistant', '상담사'),
    ]
    
    session = models.ForeignKey(
        ChatSession, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = '메시지'
        verbose_name_plural = '메시지들'
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}"
