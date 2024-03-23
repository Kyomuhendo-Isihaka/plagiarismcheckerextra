from difflib import SequenceMatcher
from django.conf import settings 
from django.http import JsonResponse
import pyttsx3
import PyPDF2
import os 
import threading

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



def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['u_file']
        
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
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