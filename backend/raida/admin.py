from django.contrib import admin
from .models import Lesson, GeneratedPDF, TeacherInfo


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'user', 'level', 'period', 'week', 'session', 'created_at']
    list_filter = ['subject', 'level', 'period', 'user']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(GeneratedPDF)
class GeneratedPDFAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'user', 'filename', 'generated_at']
    list_filter = ['generated_at', 'user']
    readonly_fields = ['generated_at']


@admin.register(TeacherInfo)
class TeacherInfoAdmin(admin.ModelAdmin):
    list_display = ['user', 'updated_at']
    list_filter = ['user']
