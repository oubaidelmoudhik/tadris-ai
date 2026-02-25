"""
PDF Service - Generate PDFs from lesson data using Jinja2 and Playwright.
Migrated from Flask's pdf_generator.py
"""
import os
import json
from typing import Dict, Any, Optional
from django.conf import settings
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright


def get_teacher_info(language: str = "fr", subject_name: str = "") -> Dict[str, Any]:
    """
    Load teacher info from database or JSON file.
    
    Args:
        language: Language code (fr/ar)
        subject_name: Subject name for display
        
    Returns:
        Dictionary with teacher info
    """
    from raida.models import TeacherInfo
    
    final_info = {}
    
    # Try to get from database first
    try:
        teacher_info = TeacherInfo.objects.first()
        if teacher_info:
            if language == "fr":
                # French fields
                if teacher_info.nom:
                    final_info["Nom"] = teacher_info.nom
                if teacher_info.etablissement:
                    final_info["Établissement"] = teacher_info.etablissement
                if teacher_info.niveau:
                    final_info["Niveau"] = teacher_info.niveau
            else:
                # Arabic fields
                if teacher_info.nom_ar:
                    final_info["الأستاذ"] = teacher_info.nom_ar
                if teacher_info.etablissement_ar:
                    final_info["المؤسسة"] = teacher_info.etablissement_ar
                if teacher_info.niveau_ar:
                    final_info["المستوى"] = teacher_info.niveau_ar
            
            # Shared fields (same for both languages)
            if teacher_info.ppr:
                final_info["PPR" if language == "fr" else "رقم التأجير"] = teacher_info.ppr
            if teacher_info.annee_scolaire:
                final_info["Année Scolaire" if language == "fr" else "السنة الدراسية"] = teacher_info.annee_scolaire
    except Exception as e:
        print(f"❌ Error loading teacher info from DB: {e}")
    
    # Fallback to JSON file
    if not final_info or (not final_info.get("Nom") and not final_info.get("الأستاذ")):
        teacher_info_path = os.path.join(settings.BASE_DIR, "teacherInfo.json")
        if os.path.exists(teacher_info_path):
            try:
                with open(teacher_info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
                    if isinstance(info, list) and len(info) > 0:
                        raw_data = info[0].get(language, {})
                        
                        keys_to_exclude = ["Matière", "المالة"]
                        
                        for k, v in raw_data.items():
                            if k not in keys_to_exclude and v and str(v).strip():
                                final_info[k] = v
            except Exception as e:
                print(f"❌ Error loading teacher info from file: {e}")
    
    # Auto-inject Subject if not manually set
    if language == "ar":
        final_info["المادة"] = subject_name if subject_name else "الرياضيات"
    else:
        final_info["Matière"] = subject_name if subject_name else "Français"
        
    return final_info


def generate_pdf_from_lesson_data(
    lesson_data: Dict[str, Any], 
    pdf_filename: str,
    lesson_id: int = None
) -> Optional[str]:
    """
    Generate a PDF from lesson data.
    
    Args:
        lesson_data: Dictionary with lesson_data containing steps, objective, etc.
        pdf_filename: Name for the output PDF file
        lesson_id: Optional lesson ID for database tracking
        
    Returns:
        Path to generated PDF or None on failure
    """
    # Select template based on subject
    subject = lesson_data.get("subject", "français").lower()
    
    # Determine template and language
    if "math" in subject or "رياضيات" in subject:
        template_name = "template_math.html"
        lang_key = "ar"
        display_subject = "الرياضيات"
        print("📐 Using Math template (Arabic)")
    elif "arabe" in subject or "عربية" in subject:
        template_name = "template_arabe.html"
        lang_key = "ar"
        display_subject = "اللغة العربية"
        print("🌙 Using Arabic template")
    else:
        template_name = "template_french.html"
        lang_key = "fr"
        display_subject = "Français"
        print("📚 Using French template")
    
    # Load teacher info
    teacher_data = get_teacher_info(lang_key, display_subject)
    
    # Build template path
    templates_dir = os.path.join(settings.BASE_DIR, "templates")
    
    # Check if template exists
    template_path = os.path.join(templates_dir, template_name)
    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        # Fallback to generic template
        template_name = "template.html"
        template_path = os.path.join(templates_dir, template_name)
        if not os.path.exists(template_path):
            print(f"❌ Fallback template also not found")
            return None
    
    # Render HTML with Jinja2
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template(template_name)
    html_content = template.render(lesson_data=lesson_data, teacher_data=teacher_data)
    
    # Save temporary HTML file
    temp_html_dir = getattr(settings, 'TEMP_HTML_DIR', os.path.join(settings.BASE_DIR, 'temp_html'))
    os.makedirs(temp_html_dir, exist_ok=True)
    html_path = os.path.join(temp_html_dir, f"temp_{lesson_id or 'gen'}.html")
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Define PDF output path
    pdf_output_dir = getattr(settings, 'PDF_OUTPUT_DIR', os.path.join(settings.BASE_DIR, 'output_pdfs'))
    os.makedirs(pdf_output_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_output_dir, pdf_filename)
    
    # Render and export with Playwright (headless Chromium)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--lang=ar"])
            page = browser.new_page()
            page.goto(f"file://{os.path.abspath(html_path)}")
            page.pdf(
                path=pdf_path,
                format="A4",
                print_background=True,
                margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"}
            )
            browser.close()
        
        print(f"✅ PDF created: {pdf_path}")
        
        # Clean up temp HTML
        try:
            os.remove(html_path)
        except:
            pass
        
        return pdf_path
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return None


def schedule_pdf_deletion(pdf_path: str, delay: int = 120) -> None:
    """
    Schedule a PDF file for deletion after a delay.
    
    Args:
        pdf_path: Path to the PDF file
        delay: Delay in seconds before deletion (default: 120)
    """
    import threading
    import time
    
    def delayed_delete():
        time.sleep(delay)
        try:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                print(f"🗑️ Deleted temporary file: {pdf_path}")
        except Exception as e:
            print(f"❌ Error deleting file {pdf_path}: {e}")
    
    thread = threading.Thread(target=delayed_delete)
    thread.daemon = True
    thread.start()
