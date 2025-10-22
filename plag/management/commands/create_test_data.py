from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from plag.models import Organization, Profile, Notification

class Command(BaseCommand):
    help = 'Create test data for organizations and users'

    def handle(self, *args, **options):
        # Create test organization
        org, created = Organization.objects.get_or_create(
            name="Test University",
            slug="test-university",
            defaults={
                'plan': 'institution',
                'max_users': 100,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f"Created organization: {org.name}")
        
        # Create super admin (separate from org admin)
        super_admin, created = User.objects.get_or_create(
            username="superadmin",
            defaults={
                'first_name': 'Super',
                'last_name': 'Admin',
                'email': 'superadmin@system.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            super_admin.set_password('super123')
            super_admin.save()
            self.stdout.write(f"Created super admin: {super_admin.username}")
        
        # Create org admin
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'email': 'admin@test.edu'
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            Profile.objects.create(user=admin_user, role='Admin', organization=org)
            self.stdout.write(f"Created admin user: {admin_user.username}")
        
        # Create test lecturer
        lecturer_user, created = User.objects.get_or_create(
            username="lecturer1",
            defaults={
                'first_name': 'John',
                'last_name': 'Lecturer',
                'email': 'lecturer@test.edu'
            }
        )
        
        if created:
            lecturer_user.set_password('lecturer123')
            lecturer_user.save()
            Profile.objects.create(user=lecturer_user, role='Lecturer', organization=org)
            self.stdout.write(f"Created lecturer: {lecturer_user.username}")
        
        # Create test student
        student_user, created = User.objects.get_or_create(
            username="student1",
            defaults={
                'first_name': 'Jane',
                'last_name': 'Student',
                'email': 'student@test.edu'
            }
        )
        
        if created:
            student_user.set_password('student123')
            student_user.save()
            Profile.objects.create(user=student_user, role='Student', organization=org)
            self.stdout.write(f"Created student: {student_user.username}")
        
        # Create individual user
        individual_user, created = User.objects.get_or_create(
            username="individual1",
            defaults={
                'first_name': 'Bob',
                'last_name': 'Individual',
                'email': 'bob@example.com'
            }
        )
        
        if created:
            individual_user.set_password('individual123')
            individual_user.save()
            Profile.objects.create(user=individual_user, role='Individual', is_individual=True)
            self.stdout.write(f"Created individual user: {individual_user.username}")
        
        self.stdout.write(self.style.SUCCESS('Test data created successfully!'))
        self.stdout.write('Login credentials:')
        self.stdout.write('Super Admin: superadmin/super123')
        self.stdout.write('Org Admin: admin/admin123')
        self.stdout.write('Lecturer: lecturer1/lecturer123')
        self.stdout.write('Student: student1/student123')
        self.stdout.write('Individual: individual1/individual123')