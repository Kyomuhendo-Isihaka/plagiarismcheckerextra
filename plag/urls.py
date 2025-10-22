from django.urls import path, re_path
from django.views.generic import RedirectView
from plag import views
    
app_name = "plag"
urlpatterns = [ 
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register_select, name='register_select'),
    path('register/individual/', views.individual_register, name='individual_register'),
    path('register/organization/', views.org_register, name='org_register'),
    re_path(r'^registration/(?P<role>Individual)/$', views.registration, name='registration'),
    
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    path('users/individual/', views.individual_users, name='individual_users'),

    path('logout/', views.logout_view, name='logout'),
    path('checkplagiarism/', views.checkPlag, name='checkplagiarism'),
    path('dictionary/', views.dictionary, name='dictionary'),
    path('work/', views.work, name='work'),
    path('results/', views.results, name='results'),
    path('listen/', views.listen, name='listen'),

    path('profile/', views.profile, name='profile'),

    re_path(r'^users/(?P<role>Student|Lecturer)/$', views.users, name='users'),

    path('upload/', views.upload, name='upload'),
    re_path(r'^pdfview/(?P<pdf_file>[\w\-\.]+)/$', views.view_pdf, name='viewpdf'),
    
    # Advanced Analytics and Detection
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('enhanced-check/', views.enhanced_check, name='enhanced_check'),
    path('enhanced-results/', views.enhanced_results, name='enhanced_results'),
]