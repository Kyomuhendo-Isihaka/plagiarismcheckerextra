from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from plag.models import Profile

class Command(BaseCommand):
    help = 'Create admin user and sample data'

    def handle(self, *args, **options):
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            Profile.objects.create(user=admin_user, role='Admin')
            self.stdout.write(
                self.style.SUCCESS('Superuser created: username=admin, password=admin123')
            )
        else:
            self.stdout.write('Admin user already exists')

        # Create sample lecturer
        if not User.objects.filter(username='lecturer').exists():
            lecturer_user = User.objects.create_user(
                username='lecturer',
                email='lecturer@example.com',
                password='lecturer123',
                first_name='John',
                last_name='Lecturer'
            )
            Profile.objects.create(user=lecturer_user, role='Lecturer')
            self.stdout.write(
                self.style.SUCCESS('Sample lecturer created: username=lecturer, password=lecturer123')
            )

        # Create sample student
        if not User.objects.filter(username='student').exists():
            student_user = User.objects.create_user(
                username='student',
                email='student@example.com',
                password='student123',
                first_name='Jane',
                last_name='Student'
            )
            Profile.objects.create(user=student_user, role='Student')
            self.stdout.write(
                self.style.SUCCESS('Sample student created: username=student, password=student123')
            )

        self.stdout.write(
            self.style.SUCCESS('Setup completed successfully!')
        )