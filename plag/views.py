from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from .models import *
from plag import plagiarismeng as ple
import os


# Create your views here.

def login_view(request):
    sms = ""
    if request.method == "POST":
        username = request.POST.get('username') 
        userpassword = request.POST.get('password')  

        user = authenticate(username=username, password=userpassword)  
        if user is not None:
            login(request, user)
            return redirect('plag:dashboard')
        else:
            sms = "Invalid email or password"
    
    context = {
        'sms': sms,
    }

    return render(request, "login.html", context)

def logout_view(request):
    logout(request)
    return redirect('plag:login')

@login_required
def dashboard(request):
    user = request.user
 
    context = {
        'user':user,
    }
    return render(request,"dashboard.html", context)

def view_pdf(reqeust, pdf_file):
    user = reqeust.user
    upload = get_object_or_404(Upload, file_name = pdf_file)
    comments = Comment.objects.filter(upload=upload)
   

    if reqeust.method == "POST":
        comment_text = reqeust.POST.get('comment')
        comment = Comment.objects.create(comment_text=comment_text, upload=upload)
        comment.save()

    if user.profile.role=="Lecturer":
        upload.status = "Viewed"  
        upload.save()

    pdf_text = ple.extract_pdf_text(pdf_file)
    context = {
        'pdf_text':pdf_text,
        'comments':comments
    }
    return render(reqeust, "pages/view_pdf.html", context)



def upload(request):
    lecturers = Profile.objects.filter(role = 'Lecturer')

    if request.method =="POST":
        subject = request.POST.get('subject')
        stdId = request.POST.get('studentId')
        lctId = request.POST.get('lecturerId')

        lecturer = Profile.objects.get(user =lctId)
                
        uploaded_file = ple.upload_file(request)
        if uploaded_file is not None:
            file_name = os.path.basename(uploaded_file)
         
        upload = Upload.objects.create(subject = subject, file_name=file_name, lecturer=lecturer ,student = stdId)
        upload.save()
        return redirect('plag:work')
    
    context = {
        'lecturers':lecturers
    }    
    return render(request, "pages/upload.html", context)

def registration(request, role):
    if request.method == "POST":
        fname = request.POST.get('firstname')
        lname = request.POST.get('lastname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        conf_pass = request.POST.get('conf_pass')

        if password == conf_pass:
            user = User.objects.create_user(username=username, first_name=fname, last_name=lname, email=email, password=password)
            user.is_staff = False
            user.save()
            Profile.objects.create(user=user, role=role)
            
        else:
            print('Passwords do not match')

    context = {
        'role': role,
    }
    return render(request, "registration.html", context)


def checkPlag(request):
    err=""
    file_path = ple.upload_file(request)
    
    text= ple.read_pdf(file_path)
    if text:
        return redirect('plag:results')
   
    context = {
        'err':err,
    }
    return render(request, "checkplag.html", context)

def dictionary(request):
    return render(request, "dictionary.html")


def work(request):
    user = request.user
    students=""

    if user.profile.role== "Student":
        workuploads = Upload.objects.filter(student=user.id).order_by('-pk')
        
    else:
        workuploads = Upload.objects.filter(lecturer=user.profile).order_by('-pk')
        student_ids = workuploads.values_list('student', flat=True)
        students = User.objects.filter(pk__in=student_ids)
                     

    context = {
        'workuploads':workuploads,
        'students':students,
    }    
    return render(request, "work.html", context)

def results(request):
    return render(request, "results.html")

def listen(request):
    text=""
    file_path = ple.upload_file(request)
    if file_path:
        with open(file_path, 'r') as file:
            text= ple.read_pdf(file_path) 
            speaking_thread = ple.threading.Thread(target=ple.speak, args=(text,))
            speaking_thread.start()    
            # ple.speak(text)
    context = {
        'text':text,
    }
    return render(request, "listen.html", context)


def profile(request):
    sms = ""
    user = request.user
    if request.method == "POST":
        userId = request.POST.get('userId')
        fname = request.POST.get('firstname')
        lname = request.POST.get('lastname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        conf_pass = request.POST.get('conf_pass')
        role = user.profile.role

        user = User.objects.filter(id=userId).first()
        if conf_pass==password:   
            user.first_name = fname
            user.last_name = lname
            user.email = email
            user.username = username
            user.set_password(password)
            user.save()

            profile, created = Profile.objects.get_or_create(user=user, defaults={'role': role})
            if not created:
                profile.role = role
                profile.save()
            return redirect('plag:login')
        else:
            sms = 'passwords dont match'             

            
    context = {
        'user': user,  
        'sms':sms     
    }
    return render(request, "profile.html", context)

def users(request, role):
    users = User.objects.all()
    context = {
        'users':users,
        'role':role,
    }
    return render(request, "pages/users.html", context)


