"""
Management command to scan lessons folder for new PPTX files.
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from raida.models import Lesson
from raida.services.pptx_service import extract_metadata_from_filename, extract_text_from_pptx


class Command(BaseCommand):
    help = 'Scan lessons folder for new PPTX files and import them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--lessons-dir',
            type=str,
            default='lessons',
            help='Path to lessons directory (relative to backend directory)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing'
        )
        parser.add_argument(
            '--delete-processed',
            action='store_true',
            help='Delete PPTX files after processing (to keep app light)'
        )

    def handle(self, *args, **options):
        lessons_dir = options['lessons_dir']
        dry_run = options['dry_run']
        delete_processed = options['delete_processed']
        
        # Resolve full path
        base_dir = getattr(settings, 'BASE_DIR', os.getcwd())
        lessons_path = os.path.join(base_dir, lessons_dir)
        
        self.stdout.write(f"Scanning: {lessons_path}")
        
        if not os.path.exists(lessons_path):
            self.stdout.write(self.style.WARNING(f"Directory not found: {lessons_path}"))
            return
        
        # Get all PPTX files
        pptx_files = [f for f in os.listdir(lessons_path) if f.endswith('.pptx')]
        
        if not pptx_files:
            self.stdout.write("No PPTX files found")
            return
        
        self.stdout.write(f"Found {len(pptx_files)} PPTX files")
        
        # Check each file
        imported = 0
        skipped = 0
        
        for filename in pptx_files:
            # Check if already exists in database
            existing = Lesson.objects.filter(filename=filename).first()
            if existing:
                skipped += 1
                self.stdout.write(f"  Skipped (exists): {filename}")
                continue
            
            # Extract metadata and content
            pptx_path = os.path.join(lessons_path, filename)
            metadata = extract_metadata_from_filename(filename)
            content = extract_text_from_pptx(pptx_path)
            
            self.stdout.write(f"  New: {filename}")
            self.stdout.write(f"    Subject: {metadata['subject']}, Level: {metadata['level']}, Period: {metadata['period']}, Week: {metadata['week']}, Session: {metadata['session']}")
            
            if not dry_run:
                Lesson.objects.create(
                    title=metadata['title'],
                    subject=metadata['subject'],
                    level=metadata['level'],
                    period=metadata['period'],
                    week=metadata['week'],
                    session=metadata['session'],
                    filename=filename,
                    objective="......",
                    content=content
                )
                
                # Delete processed file if flag is set
                if delete_processed:
                    try:
                        os.remove(pptx_path)
                        self.stdout.write(f"    Deleted: {filename}")
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"    Error deleting {filename}: {e}"))
            
            imported += 1
        
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Summary:"))
        self.stdout.write(f"  New imports: {imported}")
        self.stdout.write(f"  Skipped (already exist): {skipped}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run - no changes made"))
