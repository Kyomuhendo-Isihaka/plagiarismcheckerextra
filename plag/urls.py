from django.urls import path
from plag import views
    
app_name = "plag"
urlpatterns = [ 
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('registration/<str:role>/', views.registration, name='registration'),

    path('logout/', views.logout_view, name='logout'),
    path('checkplagiarism/', views.checkPlag, name='checkplagiarism'),
    path('dictionary/', views.dictionary, name='dictionary'),
    path('work/', views.work, name='work'),
    path('results/', views.results, name='results'),
    path('listen/', views.listen, name='listen'),

    path('profile/', views.profile, name='profile'),

    path('?/<str:role>/', views.users, name='users'),

    path('upload/', views.upload, name='upload'),
    path('pdfview/<str:pdf_file>/', views.view_pdf, name='viewpdf'),
   ]