from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'lessons', views.LessonViewSet, basename='lesson')

urlpatterns = [
    # Health check - equivalent to Flask GET /
    path('', views.health_check, name='health_check'),
    
    # Include router URLs
    path('', include(router.urls)),
    
    # Auth endpoints
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/me/', views.me, name='me'),
    path('auth/refresh/', views.refresh_token, name='refresh_token'),
    
    # Lesson upload - equivalent to Flask POST /upload_lesson
    path('lessons/upload/', views.upload_lesson, name='upload_lesson'),
    
    # Generate PDF from upload - equivalent to Flask POST /generate
    path('lessons/generate/', views.generate_from_upload, name='generate_from_upload'),
    
    # Generate PDF from lesson ID - equivalent to Flask POST /generate_from_id/<id>
    path('lessons/<int:lesson_id>/generate/', views.generate_from_id, name='generate_from_id'),
    
    # Download PDF - equivalent to Flask GET /download_pdf/<filename>
    path('lessons/pdf/<str:filename>/', views.download_pdf, name='download_pdf'),
    
    # Teacher info - equivalent to Flask GET/POST /teacher-info
    path('teacher-info/', views.teacher_info, name='teacher_info'),
    
    # Cache - equivalent to Flask GET /cache/stats and POST /cache/clear
    path('cache/stats/', views.cache_stats, name='cache_stats'),
    path('cache/clear/', views.clear_cache_view, name='clear_cache'),
]
