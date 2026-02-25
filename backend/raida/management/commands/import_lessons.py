"""
Management command to import lessons from JSON file.
"""
import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from raida.models import Lesson


class Command(BaseCommand):
    help = 'Import lessons from lessons.json into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json-file',
            type=str,
            default='data/lessons.json',
            help='Path to lessons.json file (relative to backend directory)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        dry_run = options['dry_run']
        
        # Resolve full path
        base_dir = getattr(settings, 'BASE_DIR', os.getcwd())
        json_path = os.path.join(base_dir, json_file)
        
        self.stdout.write(f"Reading from: {json_path}")
        
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f"File not found: {json_path}"))
            return
        
        # Load JSON
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                lessons_data = json.load(f)
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Invalid JSON: {e}"))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading file: {e}"))
            return
        
        if not isinstance(lessons_data, list):
            self.stdout.write(self.style.ERROR("JSON must contain a list of lessons"))
            return
        
        self.stdout.write(f"Found {len(lessons_data)} lessons in JSON file")
        
        # Import each lesson
        imported = 0
        skipped = 0
        updated = 0
        
        for lesson_data in lessons_data:
            # Check if lesson with same filename exists
            filename = lesson_data.get('filename', '')
            
            if not filename:
                skipped += 1
                continue
            
            existing = Lesson.objects.filter(filename=filename).first()
            
            if existing:
                if not dry_run:
                    existing.title = lesson_data.get('title', existing.title)
                    existing.subject = lesson_data.get('subject', existing.subject)
                    existing.level = lesson_data.get('level', existing.level)
                    existing.period = lesson_data.get('period', existing.period)
                    existing.week = lesson_data.get('week', existing.week)
                    existing.session = lesson_data.get('session', existing.session)
                    existing.objective = lesson_data.get('objective', existing.objective)
                    existing.content = lesson_data.get('content', existing.content)
                    existing.save()
                updated += 1
                self.stdout.write(f"  Updated: {filename}")
            else:
                if not dry_run:
                    Lesson.objects.create(
                        title=lesson_data.get('title', ''),
                        subject=lesson_data.get('subject', 'français'),
                        level=lesson_data.get('level', ''),
                        period=lesson_data.get('period', ''),
                        week=lesson_data.get('week', ''),
                        session=lesson_data.get('session', ''),
                        filename=filename,
                        objective=lesson_data.get('objective', '......'),
                        content=lesson_data.get('content', '')
                    )
                imported += 1
                self.stdout.write(f"  Imported: {filename}")
        
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Summary:"))
        self.stdout.write(f"  New imports: {imported}")
        self.stdout.write(f"  Updated: {updated}")
        self.stdout.write(f"  Skipped: {skipped}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run - no changes made"))
