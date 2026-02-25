"""
API Views for raida app.
Migrated from Flask's app.py endpoints.
"""
import os
import json
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from .models import Lesson, GeneratedPDF, TeacherInfo
from .serializers import (
    LessonSerializer, GeneratedPDFSerializer, TeacherInfoSerializer,
    UserSerializer, RegisterSerializer, LoginSerializer
)
from .services.pptx_service import extract_metadata_from_filename, extract_text_from_pptx
from .services.ai_service import process_with_ai
from .services.pdf_service import generate_pdf_from_lesson_data, schedule_pdf_deletion
from .services.cache_service import get_cache_stats, clear_cache


# ====================
# Auth Views
# ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    POST /api/auth/register/
    Register a new user and create an empty TeacherInfo profile.
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # TeacherInfo is created by the serializer
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    POST /api/auth/login/
    Login and return JWT tokens.
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if user is None:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    POST /api/auth/logout/
    Logout by blacklisting the refresh token.
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'Logout successful'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """
    GET /api/auth/me/
    Get current user info.
    """
    return Response(UserSerializer(request.user).data)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    POST /api/auth/refresh/
    Refresh access token.
    """
    try:
        refresh = RefreshToken(request.data.get('refresh'))
        return Response({
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    except Exception as e:
        return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)


# ====================
# Health Check
# ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint - equivalent to Flask GET /"""
    return Response({
        "status": "running", 
        "service": "tadris-ai-backend-django"
    })


# ====================
# Lesson Views
# ====================

class LessonViewSet(viewsets.ModelViewSet):
    """ViewSet for Lesson CRUD operations."""
    
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [AllowAny]
    
    def list(self, request, *args, **kwargs):
        """GET /api/lessons/ - List all lessons."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """POST /api/lessons/ - Create a new lesson."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ====================
# Upload Lesson
# ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def upload_lesson(request):
    """
    POST /api/lessons/upload/
    Upload a PPTX file, save to database for future use.
    Returns lesson details for user to preview and generate PDF later.
    """
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

    # Validate file type
    if not uploaded_file.name.endswith(".pptx"):
        return Response({"error": "Only .pptx files are allowed"}, status=status.HTTP_400_BAD_REQUEST)

    # Save uploaded file temporarily
    lessons_dir = os.path.join(settings.BASE_DIR, "lessons")
    os.makedirs(lessons_dir, exist_ok=True)
    pptx_path = os.path.join(lessons_dir, uploaded_file.name)
    
    with open(pptx_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    # Extract metadata
    meta = extract_metadata_from_filename(uploaded_file.name)
    
    # Extract content
    content = extract_text_from_pptx(pptx_path)
    
    # Delete the processed PPTX file to keep app light
    try:
        if os.path.exists(pptx_path):
            os.remove(pptx_path)
            print(f"🗑️ Deleted uploaded file: {uploaded_file.name}")
    except Exception as e:
        print(f"⚠️ Could not delete {uploaded_file.name}: {e}")

    # Check if lesson with same filename exists
    existing_lesson = Lesson.objects.filter(filename=uploaded_file.name).first()
    
    if existing_lesson:
        # Update existing lesson
        existing_lesson.title = meta["title"]
        existing_lesson.subject = meta["subject"]
        existing_lesson.level = meta["level"]
        existing_lesson.period = meta["period"]
        existing_lesson.week = meta["week"]
        existing_lesson.session = meta["session"]
        existing_lesson.content = content
        existing_lesson.save()
        lesson = existing_lesson
    else:
        # Create new lesson
        lesson = Lesson.objects.create(
            title=meta["title"],
            subject=meta["subject"],
            level=meta["level"],
            period=meta["period"],
            week=meta["week"],
            session=meta["session"],
            filename=uploaded_file.name,
            objective="......",
            content=content
        )
    
    return Response({
        "message": "Lesson uploaded and saved successfully",
        "lesson_id": lesson.id,
        "title": meta["title"],
        "subject": meta["subject"],
        "level": meta["level"],
        "period": meta["period"],
        "week": meta["week"],
        "session": meta["session"],
    })


# ====================
# Generate PDF
# ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def generate_from_upload(request):
    """
    POST /api/lessons/generate/
    Upload PPTX → Extract → AI → PDF
    """
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

    # Validate file type
    if not uploaded_file.name.endswith(".pptx"):
        return Response({"error": "Only .pptx files are allowed"}, status=status.HTTP_400_BAD_REQUEST)

    # Save uploaded file
    lessons_dir = os.path.join(settings.BASE_DIR, "lessons")
    os.makedirs(lessons_dir, exist_ok=True)
    pptx_path = os.path.join(lessons_dir, uploaded_file.name)
    
    with open(pptx_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    # Extract metadata
    meta = extract_metadata_from_filename(uploaded_file.name)
    
    # Extract content
    content = extract_text_from_pptx(pptx_path)

    # Process with AI
    lesson_data = process_with_ai(
        meta["title"], meta["subject"], meta["level"], 
        meta["period"], meta["week"], meta["session"], content
    )
    
    if not lesson_data:
        return Response({"error": "AI analysis failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Generate PDF
    pdf_filename = f"Period{meta['period']}_Week{meta['week']}_Session{meta['session']}.pdf"
    pdf_path = generate_pdf_from_lesson_data(lesson_data, pdf_filename)
    
    if not pdf_path:
        return Response({"error": "PDF generation failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Schedule PDF deletion
    schedule_pdf_deletion(pdf_path, delay=120)
    
    return Response({
        "title": meta["title"],
        "lesson_data": lesson_data,
        "pdf_path": pdf_path
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_from_id(request, lesson_id):
    """
    POST /api/lessons/<id>/generate/
    Generate PDF from existing lesson.
    """
    try:
        lesson = Lesson.objects.get(id=lesson_id)
    except Lesson.DoesNotExist:
        return Response({"error": "Lesson not found"}, status=status.HTTP_404_NOT_FOUND)

    # Process with AI
    lesson_data = process_with_ai(
        lesson.title, lesson.subject, lesson.level,
        lesson.period, lesson.week, lesson.session, lesson.content
    )
    
    if not lesson_data:
        return Response({"error": "AI analysis failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Save processed content to lesson
    lesson.processed_content = lesson_data
    lesson.save()

    # Generate PDF
    pdf_filename = f"{lesson.title}.pdf"
    pdf_path = generate_pdf_from_lesson_data(lesson_data, pdf_filename, lesson.id)

    if not pdf_path:
        return Response({"error": "PDF generation failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Schedule PDF deletion
    schedule_pdf_deletion(pdf_path, delay=120)

    return Response({
        "title": lesson.title,
        "lesson_data": lesson_data,
        "pdf_path": pdf_path
    })


# ====================
# Download PDF
# ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def download_pdf(request, filename):
    """
    GET /api/lessons/pdf/<filename>/
    Download a generated PDF.
    """
    pdf_output_dir = getattr(settings, 'PDF_OUTPUT_DIR', os.path.join(settings.BASE_DIR, 'output_pdfs'))
    pdf_path = os.path.join(pdf_output_dir, filename)
    
    if not os.path.exists(pdf_path):
        return Response({"error": "PDF not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Schedule deletion after 2 minutes
    schedule_pdf_deletion(pdf_path, delay=120)

    # Return file
    response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ====================
# Teacher Info
# ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def teacher_info(request):
    """
    GET /api/teacher-info/ - Get current user's teacher info
    POST /api/teacher-info/ - Set current user's teacher info
    """
    if request.method == "GET":
        # Return current user's teacher info
        try:
            teacher_info = TeacherInfo.objects.get(user=request.user)
            serializer = TeacherInfoSerializer(teacher_info)
            return Response(serializer.data)
        except TeacherInfo.DoesNotExist:
            # Create empty TeacherInfo for the user
            teacher_info = TeacherInfo.objects.create(user=request.user)
            serializer = TeacherInfoSerializer(teacher_info)
            return Response(serializer.data)
    
    elif request.method == "POST":
        data = request.data
        
        # Handle both array format [{fr:..., ar:...}] and direct format {fr:..., ar:...}
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        
        fr_data = data.get('fr', {})
        ar_data = data.get('ar', {})
        
        # Get or create teacher info for the current user
        teacher_info, created = TeacherInfo.objects.get_or_create(user=request.user)
        
        # Map French fields
        teacher_info.nom = fr_data.get('Nom', '')
        teacher_info.etablissement = fr_data.get('Établissement', '')
        teacher_info.niveau = fr_data.get('Niveau', '')
        
        # Map Arabic fields
        teacher_info.nom_ar = ar_data.get('الأستاذ', '')
        teacher_info.etablissement_ar = ar_data.get('المؤسسة', '')
        teacher_info.niveau_ar = ar_data.get('المستوى', '')
        
        # Shared fields (PPR and Année Scolaire from either language)
        teacher_info.ppr = fr_data.get('PPR', '') or ar_data.get('رقم التأجير', '')
        teacher_info.annee_scolaire = fr_data.get('Année Scolaire', '') or ar_data.get('السنة الدراسية', '')
        
        teacher_info.save()
        
        return Response({"message": "Info updated successfully"})


# ====================
# Cache
# ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def cache_stats(request):
    """GET /api/cache/stats/ - Get cache statistics."""
    return Response(get_cache_stats())


@api_view(['POST'])
@permission_classes([AllowAny])
def clear_cache_view(request):
    """POST /api/cache/clear/ - Clear cache."""
    clear_cache()
    return Response({"message": "Cache cleared successfully"})
