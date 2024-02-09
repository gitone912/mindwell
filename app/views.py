from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
# from .bot import call_bot
from django.http import JsonResponse
from .models import *
from .intent_ana import *
from .gpt import *
from .llama import *
#import csrf extempt
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
def homepage(request):
    return render(request, 'Homepage.html')
@csrf_exempt
def bot(request):
    if request.method == 'POST':
        try:
            user_input = request.POST.get('user_input', '')
            response = generate_prompt(user_input)
            print(response)
            # Save the chat history
            Chat.objects.create(user_input=user_input, response=response)
            print("created")
            chat_history = Chat.objects.all().order_by('-timestamp')
            return render(request, 'bot.html', {'chat_history': chat_history})
        except Exception as e:
            print(e)
            print("error")
            return render(request, 'bot.html', {'error': str(e)})

    # Retrieve all chat history
    chat_history = Chat.objects.all().order_by('-timestamp')
    return render(request, 'bot.html', {'chat_history': chat_history})


def login_view(request):
    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('survey')  
        else:
            error_message = 'Invalid username or password.'

    return render(request, 'login.html', {'error_message': error_message})

def signup_view(request):
    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists():
            error_message = 'Username already exists. Please choose a different one.'
        elif User.objects.filter(email=email).exists():
            error_message = 'Email already exists. Please use a different one.'
        else:
            User.objects.create_user(username=username, email=email, password=password)
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('login')  

    return render(request, 'signup.html', {'error_message': error_message})

def logout_view(request):
    logout(request)
    return redirect('login')

def analyse_intent(request):
    if request.method == 'POST':
        try:
            # Get the user input from the request data
            user_input = request.POST.get('user_input', '')
            response = main_function(user_input)
            
            return render(request, 'intent.html',{'response': response})
        except Exception as e:
            return render(request, 'intent.html', {'error': str(e)})
    return render(request, 'intent.html')


from django.shortcuts import render
from django.http import HttpResponse
from .models import SadSongs, HappySongs, CalmSongs

def listen_music(request):
    try:
        user_input = Chat.objects.latest('-timestamp').user_input
        response = main_function(user_input)

        if response == 'relationship-b' or "goodbye" or "self-esteem-A" or "relationship-a" or "domesticviolence" or "griefandloss" or "substanceabuse-a" or "family-conflict":
            songs = SadSongs.objects.all()
        elif response == 'greetings':
            songs = HappySongs.objects.all()
        elif response == 'calm':
            songs = CalmSongs.objects.all()
        else:
            songs = SadSongs.objects.all()

        # Render the HTML content
        return render(request, 'music.html', {'songs': songs})

    except Exception as e:
        error_message = str(e)
        return render(request, 'music.html', {'error': error_message})


def playlist(request):
    return render(request, 'playlist.html')

def dashboard(request):
    return render(request,'index.html')

def avatar(request):
    return render(request,'avatar.html')

def task(request):
    return render(request,'Tasks.html')

def survey(request):
    return render(request,'survey.html')


from os.path import join, dirname
from dotenv import load_dotenv
import vonage


def notification(request):
    if request.method == 'POST':
        number = request.POST.get('user_input', '') 
        dotenv_path = join(dirname(__file__), "../.env")
        load_dotenv(dotenv_path)

        VONAGE_API_KEY = "e8e6fb61"
        VONAGE_API_SECRET = "7NCsDAIv5fAUFjLV"
        VONAGE_BRAND_NAME = "akash"
        TO_NUMBER = f'{number}'


        client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)

        responseData = client.sms.send_message(
            {
                "from": VONAGE_BRAND_NAME,
                "to": TO_NUMBER,
                "text": "Hello Dear Hope you doing fine, Wanna Chat a little bit?",
            }
        )

        if responseData["messages"][0]["status"] == "0":
            print("Message sent successfully.")
            return redirect('dashboard')
        else:
            print(f"Message failed with error: {responseData['messages'][0]['error-text']}")
            return redirect('dashboard')
    else:
        return render(request,'notification.html')


def congrats(request):
    return render(request,'congrats.html')


def dynamic_tasks(request):
    user_input = "generate 10 tasks for me to cure my mental health in a list form separated by commas"
    response = run_chatbot(user_input)
            
    return render(request, 'dynamic_tasks.html',{'response': response})

from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import requests
import os

API_KEY = "cd86c2677cef4a878100c664dc169772"
ENDPOINT = "https://ic2024emotiondetection.cognitiveservices.azure.com/"

@csrf_exempt
def camera(request):
    return render(request, 'cmera.html')

@csrf_exempt
def capture_and_analyze(request):
    if request.method == 'POST':
        # Assuming the input field name is 'image'
        image_file = request.FILES.get('image')

        if image_file:
            captured_image = CapturedImage.objects.create(image=image_file)

        result = analyze_image(f'/Users/pranaymishra/Desktop/backend_mindwell/backend/{captured_image.image.url}')
        print(result)

        Results.objects.create(result=result)
        return redirect('result')
    else:
        return render(request, 'cmera.html')

def latest_result(request):
    latest_object = Results.objects.latest('timestamp')
    context = {'latest_result': latest_object}
    return render(request, 'result.html', context)
    
def analyze_image(image_path):
    print("capturing")
    subscription_key = API_KEY
    endpoint = ENDPOINT

    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

    with open(image_path, 'rb') as image_file:
        # Call API with local image
        tags_result = computervision_client.tag_image_in_stream(image_file)

        # Process the result and return relevant information
        tags = [{'name': tag.name, 'confidence': tag.confidence * 100} for tag in tags_result.tags]
        return tags


