from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Profile
from plag import plagiarismeng as ple


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


def upload(request):
    lecturers = Profile.objects.filter(role = 'Lecturer')
    
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
    
    return render(request, "work.html")

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


