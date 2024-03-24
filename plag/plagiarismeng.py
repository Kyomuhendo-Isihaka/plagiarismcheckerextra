from difflib import SequenceMatcher
from django.conf import settings 
from django.http import JsonResponse
import pyttsx3
import PyPDF2
import os 
import threading
import uuid
import fitz

speaker = pyttsx3.init()

def speak(words):
    try:
        speaker = pyttsx3.init()
        voice = speaker.getProperty('voices')
        speaker.setProperty('voices', voice[1])
        speaker.say(words)
        speaker.runAndWait()
    except Exception as e:
        print("An error occurred:", e)
    finally:
        speaker.startLoop()

def extract_pdf_text(pdf_file):
    directory = settings.MEDIA_ROOT
   
    if not os.path.isdir(directory):
        raise ValueError(f"'{directory}' is not a directory.")

    pdf_path = os.path.join(directory, pdf_file)
    if not os.path.isfile(pdf_path):
        text = "PDF not found"
        return text
        

    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()

    return text

def upload_file(request):
    if request.method == 'POST' and 'u_file' in request.FILES:
        uploaded_file = request.FILES['u_file']

        filename = str(uuid.uuid4()) + os.path.splitext(uploaded_file.name)[1]
        
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)   
        return  file_path
    

def read_pdf(file_path):
    
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except FileNotFoundError:
        print("File not found.")
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None