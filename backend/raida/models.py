from django.db import models
from django.contrib.auth.models import User


class Subject(models.TextChoices):
    FRENCH = 'français', 'Français'
    MATH = 'mathématiques', 'Mathématiques'
    ARABIC = 'langue arabe', 'Langue Arabe'


def get_default_user():
    """Get or create a default user for lessons without a specific user."""
    user, _ = User.objects.get_or_create(
        username='default',
        defaults={'email': 'default@example.com'}
    )
    return user


class TeacherInfo(models.Model):
    """Model representing teacher information (bilingual) - tied to User."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_info', primary_key=True)
    
    # Shared fields (same for both languages)
    ppr = models.CharField(max_length=50, blank=True, default="")
    annee_scolaire = models.CharField(max_length=20, blank=True, default="")
    
    # French fields
    nom = models.CharField(max_length=255, blank=True, default="")
    etablissement = models.CharField(max_length=255, blank=True, default="")
    niveau = models.CharField(max_length=100, blank=True, default="")
    
    # Arabic fields
    nom_ar = models.CharField(max_length=255, blank=True, default="")
    etablissement_ar = models.CharField(max_length=255, blank=True, default="")
    niveau_ar = models.CharField(max_length=100, blank=True, default="")
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Teacher Info'
    
    def __str__(self):
        return f"Teacher Info for {self.user.username}"


class Lesson(models.Model):
    """Model representing a lesson extracted from PPTX."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lessons', default=get_default_user)
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=50, choices=Subject.choices, default=Subject.FRENCH)
    level = models.CharField(max_length=10, blank=True, default='')
    period = models.CharField(max_length=10, blank=True, default='')
    week = models.CharField(max_length=10, blank=True, default='')
    session = models.CharField(max_length=10, blank=True, default='')
    filename = models.CharField(max_length=255, blank=True, default='')
    objective = models.TextField(blank=True, default='......')
    content = models.TextField(blank=True, default='')
    
    # Processed content from AI (JSON with lesson_data)
    processed_content = models.JSONField(null=True, blank=True)
    
    # File fields
    pptx_file = models.FileField(upload_to='lessons/', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.subject})"


class GeneratedPDF(models.Model):
    """Model representing a generated PDF for a lesson."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pdfs', default=get_default_user)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='pdfs')
    file = models.FileField(upload_to='pdfs/')
    filename = models.CharField(max_length=255)
    
    # Timestamps
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # For cleanup scheduling
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"PDF for {self.lesson.title}"
