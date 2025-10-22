#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spc.settings')
django.setup()

from django.contrib.auth.models import User
from plag.models import Organization, Profile

def test_organization_isolation():
    print("Testing Organization Isolation...")
    
    # Get test data
    org1 = Organization.objects.get(slug="test-university")
    
    # Create second organization
    org2, created = Organization.objects.get_or_create(
        name="Another University",
        slug="another-university",
        defaults={'plan': 'professional', 'max_users': 50}
    )
    
    # Create users for org2
    user2, created = User.objects.get_or_create(
        username="lecturer2",
        defaults={'first_name': 'Mary', 'last_name': 'Teacher', 'email': 'mary@another.edu'}
    )
    if created:
        user2.set_password('lecturer123')
        user2.save()
        Profile.objects.create(user=user2, role='Lecturer', organization=org2)
    
    # Test isolation
    org1_lecturers = Profile.objects.filter(role='Lecturer', organization=org1)
    org2_lecturers = Profile.objects.filter(role='Lecturer', organization=org2)
    
    print(f"Organization 1 ({org1.name}) lecturers: {org1_lecturers.count()}")
    print(f"Organization 2 ({org2.name}) lecturers: {org2_lecturers.count()}")
    
    # Verify no cross-contamination
    assert org1_lecturers.count() >= 1
    assert org2_lecturers.count() >= 1
    
    # Check that lecturers are properly isolated
    org1_lecturer_names = [p.user.username for p in org1_lecturers]
    org2_lecturer_names = [p.user.username for p in org2_lecturers]
    
    print(f"Org1 lecturers: {org1_lecturer_names}")
    print(f"Org2 lecturers: {org2_lecturer_names}")
    
    # Ensure no overlap
    overlap = set(org1_lecturer_names) & set(org2_lecturer_names)
    assert len(overlap) == 0, f"Found overlap: {overlap}"
    
    print("Organization isolation test passed!")

if __name__ == "__main__":
    test_organization_isolation()