from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
    
class Upload(models.Model):
    STATUS = (('Waiting', 'Waiting'), ('Viewed', 'Viewed'))

    subject = models.CharField(max_length=100)
    file_name = models.CharField(max_length=255)
    date_uploaded = models.DateField(default=timezone.now)
    student = models.PositiveIntegerField()
    lecturer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    status = models.CharField(choices = STATUS, max_length=200, default="Waiting")

    def __str__(self):
        return self.subject

class Comment(models.Model):
    comment_text = models.TextField()
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE)

    
