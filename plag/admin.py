from django.contrib import admin
from .models import *

# Register your models here.
class CommentTabulerinline(admin.TabularInline):
    model = Comment
class UploadAdmin(admin.ModelAdmin):
    inlines =[CommentTabulerinline]

admin.site.register(Comment)

admin.site.register(Upload, UploadAdmin)
admin.site.register(Profile)
