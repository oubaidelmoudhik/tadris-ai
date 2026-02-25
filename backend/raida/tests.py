"""
Unit tests for raida services.
Tests PPTX, Cache, AI, and PDF services.
"""
import pytest
import os
import json
from unittest.mock import patch, MagicMock
from django.test import override_settings
from rest_framework.test import APIClient

# Mark all tests that need database access
pytestmark = pytest.mark.django_db


# ====================
# PPTX Service Tests
# ====================

class TestPPTXService:
    """Tests for raida.services.pptx_service"""
    
    def test_extract_metadata_short_format_french(self):
        """Test short format metadata extraction for French."""
        from raida.services.pptx_service import extract_metadata_from_filename
        
        result = extract_metadata_from_filename("FR_N5_P1_SEM1_S3_V2.pptx")
        
        assert result['subject'] == 'français'
        assert result['level'] == '5'
        assert result['period'] == '1'
        assert result['week'] == '1'
        assert result['session'] == '3'
        assert 'FR N5 P1 SEM1 S3 V2' in result['title']
    
    def test_extract_metadata_short_format_math(self):
        """Test short format metadata extraction for Math."""
        from raida.services.pptx_service import extract_metadata_from_filename
        
        result = extract_metadata_from_filename("MATH_N5_P2_SEM3_S1.pptx")
        
        assert result['subject'] == 'mathématiques'
        assert result['level'] == '5'
        assert result['period'] == '2'
        assert result['week'] == '3'
        assert result['session'] == '1'
    
    def test_extract_metadata_short_format_arabic(self):
        """Test short format metadata extraction for Arabic."""
        from raida.services.pptx_service import extract_metadata_from_filename
        
        result = extract_metadata_from_filename("AR_N5_P1_SEM2_S4.pptx")
        
        assert result['subject'] == 'langue arabe'
    
    def test_extract_metadata_long_format(self):
        """Test long format metadata extraction."""
        from raida.services.pptx_service import extract_metadata_from_filename
        
        result = extract_metadata_from_filename("Français_Niv5_Parcour1_Palier3_Séance1.pptx")
        
        assert result['subject'] == 'français'
        assert result['level'] == '5'
        assert result['period'] == '3'
        assert result['week'] == '1'
        assert result['session'] == '1'
    
    def test_extract_objective_found(self):
        """Test objective extraction when found."""
        from raida.services.pptx_service import extract_objective
        
        content = "Voici le texte\nObjectif: être capable de lire\nSuite du contenu"
        result = extract_objective(content)
        
        assert "Objectif" in result
    
    def test_extract_objective_not_found(self):
        """Test objective extraction when not found."""
        from raida.services.pptx_service import extract_objective
        
        # Content without objective keyword should return first line (fallback behavior)
        content = "Voici juste du contenu sans objectif"
        result = extract_objective(content)
        
        # Returns first line as it's the first occurrence
        assert result in content


# ====================
# Cache Service Tests
# ====================

class TestCacheService:
    """Tests for raida.services.cache_service"""
    
    def test_generate_cache_key(self):
        """Test cache key generation."""
        from raida.services.cache_service import generate_cache_key
        
        key = generate_cache_key("content", "French", "français", "1")
        
        assert key.startswith("lesson_cache:")
        assert len(key) > 20
    
    def test_generate_cache_key_different_inputs(self):
        """Test different inputs produce different keys."""
        from raida.services.cache_service import generate_cache_key
        
        key1 = generate_cache_key("content1", "French", "français", "1")
        key2 = generate_cache_key("content2", "French", "français", "1")
        
        assert key1 != key2
    
    def test_generate_cache_key_same_input(self):
        """Test same input produces same key."""
        from raida.services.cache_service import generate_cache_key
        
        key1 = generate_cache_key("content", "French", "français", "1")
        key2 = generate_cache_key("content", "French", "français", "1")
        
        assert key1 == key2
    
    def test_set_and_get_cached_lesson(self):
        """Test setting and getting cached lesson."""
        from raida.services.cache_service import set_cached_lesson, get_cached_lesson
        
        test_data = {"lesson_data": {"objective": "Test", "steps": []}}
        
        # Set
        set_cached_lesson("test content", "French", "français", "1", test_data)
        
        # Get
        result = get_cached_lesson("test content", "French", "français", "1")
        
        assert result is not None
    
    def test_clear_cache(self):
        """Test cache clearing."""
        from raida.services.cache_service import set_cached_lesson, clear_cache, get_cached_lesson
        
        test_data = {"test": "data"}
        set_cached_lesson("content", "French", "français", "1", test_data)
        
        clear_cache()
        
        result = get_cached_lesson("content", "French", "français", "1")
        assert result is None
    
    def test_get_cache_stats(self):
        """Test cache stats retrieval."""
        from raida.services.cache_service import get_cache_stats
        
        stats = get_cache_stats()
        
        assert "hits" in stats
        assert "misses" in stats
        assert "cache_backend" in stats


# ====================
# AI Service Tests
# ====================

class TestAIService:
    """Tests for raida.services.ai_service"""
    
    def test_get_lesson_steps_french_session_1(self):
        """Test French session 1 steps."""
        from raida.services.ai_service import get_lesson_steps
        
        steps = get_lesson_steps("français", "1")
        
        assert len(steps) == 3
        assert "Présentation du vocabulaire" in steps
    
    def test_get_lesson_steps_french_session_2(self):
        """Test French session 2 steps."""
        from raida.services.ai_service import get_lesson_steps
        
        steps = get_lesson_steps("français", "2")
        
        assert len(steps) == 3
        assert "Oral – Acte de parole 1" in steps
    
    def test_get_lesson_steps_math_session_5(self):
        """Test Math session 5 steps (Arabic)."""
        from raida.services.ai_service import get_lesson_steps
        
        steps = get_lesson_steps("mathématiques", "5")
        
        assert len(steps) == 6
        assert "افتتاح الدرس" in steps
    
    def test_get_lesson_steps_math_default(self):
        """Test Math default steps."""
        from raida.services.ai_service import get_lesson_steps
        
        steps = get_lesson_steps("mathématiques", "3")
        
        assert len(steps) == 5
        assert "الافتتاح" in steps
    
    def test_get_lesson_steps_arabic(self):
        """Test Arabic steps."""
        from raida.services.ai_service import get_lesson_steps
        
        steps = get_lesson_steps("langue arabe", "1")
        
        assert len(steps) == 5
        assert "الافتتاح" in steps
    
    @patch('raida.services.ai_service.client')
    def test_process_with_ai_success(self, mock_client):
        """Test successful AI processing."""
        from raida.services.ai_service import process_with_ai
        
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "lesson_data": {
                "subject": "français",
                "level": "5",
                "period": "1",
                "week": "1",
                "session": "1",
                "objective": "Test objective",
                "steps": [
                    {"name": "Step 1", "duration": "10min", "icon": "📝", "content": "Content"}
                ]
            }
        })
        mock_client.chat.completions.create.return_value = mock_response
        
        result = process_with_ai(
            title="Test Title",
            subject="français",
            level="5",
            period="1",
            week="1",
            session="1",
            content="Test content"
        )
        
        assert result is not None
        assert result['objective'] == "Test objective"
        assert len(result['steps']) == 1
    
    @patch('raida.services.ai_service.client')
    def test_process_with_ai_returns_cached(self, mock_client):
        """Test that cached data is returned without API call."""
        from raida.services.ai_service import process_with_ai
        from raida.services.cache_service import set_cached_lesson
        
        # Pre-cache the data
        cached_data = {
            "subject": "français",
            "objective": "Cached objective",
            "steps": [{"name": "Cached Step", "duration": "5min", "icon": "📝", "content": "Cached"}]
        }
        set_cached_lesson("cached content", "French", "français", "1", cached_data)
        
        result = process_with_ai(
            title="Test",
            subject="français",
            level="5",
            period="1",
            week="1",
            session="1",
            content="cached content"
        )
        
        # Should return cached data without calling API
        assert result['objective'] == "Cached objective"
        mock_client.chat.completions.create.assert_not_called()


# ====================
# Model Tests
# ====================

class TestLessonModel:
    """Tests for Lesson model."""
    
    def test_create_lesson(self):
        """Test creating a lesson."""
        from raida.models import Lesson
        
        lesson = Lesson.objects.create(
            title="Test Lesson",
            subject="français",
            level="5",
            period="1",
            week="1",
            session="1",
            content="Test content"
        )
        
        assert lesson.id is not None
        assert lesson.title == "Test Lesson"
        assert str(lesson) == "Test Lesson (français)"
    
    def test_lesson_default_values(self):
        """Test lesson default values."""
        from raida.models import Lesson
        
        lesson = Lesson.objects.create(title="Test")
        
        assert lesson.subject == "français"
        assert lesson.objective == "......"
        assert lesson.processed_content is None


class TestTeacherInfoModel:
    """Tests for TeacherInfo model."""
    
    def test_create_teacher_info(self):
        """Test creating teacher info."""
        from raida.models import TeacherInfo
        
        info = TeacherInfo.objects.create(
            language="fr",
            data={"Nom": "Test Teacher", "Matière": "Français"}
        )
        
        assert info.id is not None
        assert info.language == "fr"
        assert info.data["Nom"] == "Test Teacher"


# ====================
# Serializer Tests
# ====================

class TestLessonSerializer:
    """Tests for Lesson serializer."""
    
    def test_serialize_lesson(self):
        """Test serializing a lesson."""
        from raida.models import Lesson
        from raida.serializers import LessonSerializer
        
        lesson = Lesson.objects.create(
            title="Test Lesson",
            subject="français",
            level="5",
            content="Test content"
        )
        
        serializer = LessonSerializer(lesson)
        data = serializer.data
        
        assert data['title'] == "Test Lesson"
        assert data['subject'] == "français"
        assert 'lesson_id' in data
    
    def test_deserialize_lesson(self):
        """Test deserializing lesson data."""
        from raida.serializers import LessonSerializer
        
        data = {
            "title": "New Lesson",
            "subject": "mathématiques",
            "level": "6",
            "period": "2",
            "week": "3",
            "session": "1",
            "content": "Content"
        }
        
        serializer = LessonSerializer(data=data)
        assert serializer.is_valid()
        
        lesson = serializer.save()
        assert lesson.title == "New Lesson"
        assert lesson.subject == "mathématiques"


# ====================
# API Integration Tests
# ====================

class TestAPIEndpoints:
    """Integration tests for API endpoints."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        client = APIClient()
        response = client.get('/api/')
        
        assert response.status_code == 200
        assert response.data['status'] == 'running'
        assert 'django' in response.data['service']
    
    def test_get_lessons_empty(self):
        """Test GET /api/lessons/ with empty database."""
        client = APIClient()
        response = client.get('/api/lessons/')
        
        assert response.status_code == 200
        assert response.data == []
    
    def test_create_lesson(self):
        """Test POST /api/lessons/"""
        client = APIClient()
        data = {
            "title": "Test Lesson",
            "subject": "français",
            "level": "5",
            "period": "1",
            "week": "1",
            "session": "1",
            "content": "Test content"
        }
        response = client.post('/api/lessons/', data, format='json')
        
        assert response.status_code == 201
        assert response.data['title'] == "Test Lesson"
        assert response.data['id'] is not None
    
    def test_get_lesson_detail(self):
        """Test GET /api/lessons/<id>/"""
        from raida.models import Lesson
        
        lesson = Lesson.objects.create(
            title="Test Lesson",
            subject="français",
            level="5",
            content="Test"
        )
        
        client = APIClient()
        response = client.get(f'/api/lessons/{lesson.id}/')
        
        assert response.status_code == 200
        assert response.data['title'] == "Test Lesson"
    
    def test_teacher_info_get_empty(self):
        """Test GET /api/teacher-info/ with no data."""
        client = APIClient()
        response = client.get('/api/teacher-info/')
        
        assert response.status_code == 200
        assert response.data == []
    
    def test_teacher_info_create(self):
        """Test POST /api/teacher-info/"""
        client = APIClient()
        data = {
            "language": "fr",
            "Nom": "Test Teacher",
            "Matière": "Français"
        }
        response = client.post('/api/teacher-info/', data, format='json')
        
        assert response.status_code == 200
        assert "message" in response.data
    
    def test_teacher_info_get_with_data(self):
        """Test GET /api/teacher-info/ with data."""
        from raida.models import TeacherInfo
        
        TeacherInfo.objects.create(
            language="fr",
            data={"Nom": "Teacher", "Matière": "Français"}
        )
        
        client = APIClient()
        response = client.get('/api/teacher-info/')
        
        assert response.status_code == 200
        assert len(response.data) > 0
    
    def test_cache_stats(self):
        """Test GET /api/cache/stats/"""
        client = APIClient()
        response = client.get('/api/cache/stats/')
        
        assert response.status_code == 200
        assert "cache_backend" in response.data
    
    def test_cache_clear(self):
        """Test POST /api/cache/clear/"""
        client = APIClient()
        response = client.post('/api/cache/clear/')
        
        assert response.status_code == 200
        assert response.data['message'] == "Cache cleared successfully"
