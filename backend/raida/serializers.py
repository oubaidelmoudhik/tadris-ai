from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Lesson, GeneratedPDF, TeacherInfo


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        # Create empty TeacherInfo for the user
        TeacherInfo.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model."""
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'subject', 'level', 'period', 'week', 'session',
            'filename', 'objective', 'content', 'processed_content',
            'pptx_file', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Customize representation to match Flask JSON structure."""
        data = super().to_representation(instance)
        # Add lesson_id for compatibility with Flask response format
        data['lesson_id'] = instance.id
        return data


class GeneratedPDFSerializer(serializers.ModelSerializer):
    """Serializer for GeneratedPDF model."""
    
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = GeneratedPDF
        fields = ['id', 'lesson', 'lesson_title', 'file', 'filename', 'generated_at', 'expires_at']
        read_only_fields = ['id', 'generated_at']


class TeacherInfoSerializer(serializers.ModelSerializer):
    """Serializer for TeacherInfo model."""
    
    class Meta:
        model = TeacherInfo
        fields = [
            'user',
            'ppr', 'annee_scolaire',
            'nom', 'etablissement', 'niveau',
            'nom_ar', 'etablissement_ar', 'niveau_ar',
            'updated_at'
        ]
        read_only_fields = ['user', 'updated_at']
