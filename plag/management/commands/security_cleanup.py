from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clean up old files and perform security maintenance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete files older than this many days (default: 30)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        self.stdout.write(f"Starting security cleanup (dry_run={dry_run})")
        
        # Clean up old uploaded files
        self.cleanup_old_files(days, dry_run)
        
        # Clean up orphaned files
        self.cleanup_orphaned_files(dry_run)
        
        # Set proper file permissions
        self.fix_file_permissions(dry_run)
        
        self.stdout.write(
            self.style.SUCCESS('Security cleanup completed successfully')
        )

    def cleanup_old_files(self, days, dry_run):
        """Remove files older than specified days"""
        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            return
            
        import time
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        deleted_count = 0
        
        for file_path in media_root.iterdir():
            if file_path.is_file():
                if file_path.stat().st_mtime < cutoff_time:
                    if dry_run:
                        self.stdout.write(f"Would delete: {file_path}")
                    else:
                        try:
                            file_path.unlink()
                            deleted_count += 1
                            logger.info(f"Deleted old file: {file_path}")
                        except Exception as e:
                            logger.error(f"Failed to delete {file_path}: {e}")
        
        if not dry_run:
            self.stdout.write(f"Deleted {deleted_count} old files")

    def cleanup_orphaned_files(self, dry_run):
        """Remove files that don't have corresponding database records"""
        from plag.models import Upload
        
        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            return
            
        # Get all filenames from database
        db_files = set(Upload.objects.values_list('file_name', flat=True))
        
        # Get all files in media directory
        disk_files = {f.name for f in media_root.iterdir() if f.is_file()}
        
        # Find orphaned files
        orphaned_files = disk_files - db_files
        
        for filename in orphaned_files:
            file_path = media_root / filename
            if dry_run:
                self.stdout.write(f"Would delete orphaned file: {file_path}")
            else:
                try:
                    file_path.unlink()
                    logger.info(f"Deleted orphaned file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete orphaned file {file_path}: {e}")
        
        if not dry_run:
            self.stdout.write(f"Deleted {len(orphaned_files)} orphaned files")

    def fix_file_permissions(self, dry_run):
        """Set proper file permissions for security"""
        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            return
            
        fixed_count = 0
        
        for file_path in media_root.rglob('*'):
            if file_path.is_file():
                current_mode = file_path.stat().st_mode & 0o777
                target_mode = 0o644
                
                if current_mode != target_mode:
                    if dry_run:
                        self.stdout.write(f"Would fix permissions: {file_path}")
                    else:
                        try:
                            os.chmod(file_path, target_mode)
                            fixed_count += 1
                        except Exception as e:
                            logger.error(f"Failed to fix permissions for {file_path}: {e}")
        
        if not dry_run:
            self.stdout.write(f"Fixed permissions for {fixed_count} files")