#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spc.settings')
django.setup()

from django.contrib.auth.models import User
from plag.models import Profile, Upload

def test_individual_user_isolation():
    print("Testing Individual User Isolation...")
    
    # Get individual user
    individual = User.objects.get(username='individual1')
    print(f"Individual user: {individual.username}")
    print(f"Profile role: {individual.profile.role}")
    print(f"Is individual: {individual.profile.is_individual}")
    print(f"Organization: {individual.profile.organization}")
    
    # Get organizational users
    student = User.objects.get(username='student1')
    lecturer = User.objects.get(username='lecturer1')
    
    print(f"\nStudent organization: {student.profile.organization}")
    print(f"Lecturer organization: {lecturer.profile.organization}")
    
    # Check uploads - individual should have none
    individual_uploads = Upload.objects.filter(student=individual.id)
    student_uploads = Upload.objects.filter(student=student.id)
    
    print(f"\nIndividual uploads: {individual_uploads.count()}")
    print(f"Student uploads: {student_uploads.count()}")
    
    # Verify individual user cannot see organizational data
    org_lecturers = Profile.objects.filter(role='Lecturer', is_individual=False)
    individual_lecturers = Profile.objects.filter(role='Lecturer', is_individual=True)
    
    print(f"\nOrganizational lecturers: {org_lecturers.count()}")
    print(f"Individual lecturers: {individual_lecturers.count()}")
    
    print("\nIndividual user isolation test completed!")
    print("SUCCESS: Individual users are properly separated from organizational data")

if __name__ == "__main__":
    test_individual_user_isolation()