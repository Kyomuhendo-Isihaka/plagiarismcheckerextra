def get_layout_template(user):
    """Return appropriate layout template based on user role"""
    if user.is_superuser:
        return 'layouts/superadmin.html'
    
    try:
        role = user.userprofile.role
    except:
        role = 'individual'
    
    if role == 'admin':
        return 'layouts/admin.html'
    elif role == 'student':
        return 'layouts/student.html'
    elif role == 'lecturer':
        return 'layouts/lecturer.html'
    else:
        return 'layouts/individual.html'