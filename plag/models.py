from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from django.core.validators import MaxLengthValidator
from django.core.exceptions import ValidationError
import uuid

class Organization(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('professional', 'Professional'),
        ('institution', 'Institution'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    max_users = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

# UserProfile model removed to prevent conflicts
class Upload(models.Model):
    STATUS_CHOICES = [
        ('Waiting', 'Waiting'),
        ('Viewed', 'Viewed'),
        ('Reviewed', 'Reviewed'),
    ]
    
    RISK_LEVELS = [
        ('Very Low', 'Very Low'),
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Very High', 'Very High'),
    ]

    subject = models.CharField(max_length=200, validators=[MaxLengthValidator(200)])
    file_name = models.CharField(max_length=255, validators=[MaxLengthValidator(255)])
    date_uploaded = models.DateTimeField(default=timezone.now)
    student = models.PositiveIntegerField()
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default="Waiting")
    
    # AI Detection fields
    ai_confidence = models.FloatField(default=0, help_text="AI detection confidence (0-100)")
    ai_risk_level = models.CharField(choices=RISK_LEVELS, max_length=20, default="Very Low")
    ai_indicators = models.TextField(blank=True, help_text="AI detection indicators")
    is_ai_detected = models.BooleanField(default=False)
    
    # Enhanced Analytics fields
    plagiarism_percentage = models.FloatField(default=0.0)
    ai_probability = models.FloatField(default=0.0)
    citation_count = models.IntegerField(default=0)
    content = models.TextField(blank=True)
    matched_sources = models.TextField(blank=True)
    analysis_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['lecturer']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.subject} - {self.file_name}"
        
    def clean(self):
        if self.student <= 0:
            raise ValidationError('Invalid student ID')
        if self.lecturer and self.lecturer.role != 'lecturer':
            raise ValidationError('Assigned user must be a lecturer')

class Comment(models.Model):
    comment_text = models.TextField(max_length=1000, validators=[MaxLengthValidator(1000)])
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Comment on {self.upload.subject}"
        
    def clean(self):
        if len(self.comment_text.strip()) == 0:
            raise ValidationError('Comment cannot be empty')

class ReaderDocument(models.Model):
    FILE_TYPES = [
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('txt', 'Text File'),
        ('epub', 'EPUB'),
        ('html', 'HTML'),
        ('jpg', 'JPEG Image'),
        ('jpeg', 'JPEG Image'),
        ('png', 'PNG Image'),
        ('bmp', 'BMP Image'),
        ('tiff', 'TIFF Image'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    file_size = models.PositiveIntegerField()
    reading_position = models.PositiveIntegerField(default=0)
    reading_speed = models.FloatField(default=1.0)
    voice_type = models.CharField(max_length=20, default='default')
    created_at = models.DateTimeField(auto_now_add=True)
    last_read = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_read']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('upload', 'File Upload'),
        ('comment', 'New Comment'),
        ('ai_detection', 'AI Content Detected'),
        ('system', 'System Notification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField(max_length=500)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.user.username}"

    
