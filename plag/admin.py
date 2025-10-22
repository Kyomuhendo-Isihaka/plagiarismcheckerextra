from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Upload, Comment, Organization, Notification, ReaderDocument

# Unregister the default User admin
admin.site.unregister(User)

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def get_role(self, obj):
        return 'User'
    get_role.short_description = 'Role'

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'plan', 'max_users', 'is_active', 'created_at')
    list_filter = ('plan', 'is_active', 'created_at')
    search_fields = ('name', 'slug')
    readonly_fields = ('created_at',)

@admin.register(ReaderDocument)
class ReaderDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'file_type', 'file_size', 'created_at')
    list_filter = ('file_type', 'created_at')
    search_fields = ('title', 'user__username')
    readonly_fields = ('created_at', 'last_read')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'user__username')
    readonly_fields = ('created_at',)

@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = ('subject', 'file_name', 'get_student_name', 'lecturer', 'status', 'created_at')
    list_filter = ('status', 'lecturer', 'created_at')
    search_fields = ('subject', 'file_name', 'lecturer__user__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    def get_student_name(self, obj):
        try:
            student = User.objects.get(id=obj.student)
            return f"{student.first_name} {student.last_name} ({student.username})"
        except User.DoesNotExist:
            return f"Student ID: {obj.student}"
    get_student_name.short_description = 'Student'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('upload', 'created_by', 'comment_text_preview', 'created_at')
    list_filter = ('created_at', 'created_by')
    search_fields = ('comment_text', 'upload__subject', 'created_by__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def comment_text_preview(self, obj):
        return obj.comment_text[:50] + '...' if len(obj.comment_text) > 50 else obj.comment_text
    comment_text_preview.short_description = 'Comment Preview'

# Register the new UserAdmin
admin.site.register(User, UserAdmin)

# Customize admin site
admin.site.site_header = "Plagiarism Checker Administration"
admin.site.site_title = "Plagiarism Checker Admin"
admin.site.index_title = "Welcome to Plagiarism Checker Administration"