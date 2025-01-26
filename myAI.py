import wave
import numpy as np
import pyttsx3
import os
import re
import msvcrt 
import getpass
from google.api_core.exceptions import InternalServerError
from threading import Thread
import smtplib
import simpleaudio as sa
import sys
import pyautogui
from docx import Document
import json
from fuzzywuzzy import process
from google.cloud import speech
import speech_recognition as sr
from multiprocessing import Value
sys.stdout.reconfigure(line_buffering=True)
from threading import Thread, Event
from features.checkInternet import *
import threading
from difflib import get_close_matches
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import keyboard
from tkinter import messagebox, font
import geocoder
import tkinter as tk
import requests
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
import psutil
from PyPDF2 import PdfReader
import pygame
from ffpyplayer.player import MediaPlayer
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, timezone,timedelta
import subprocess
from pydub import AudioSegment
import webbrowser
import sys
import cv2
import time
import warnings
import tempfile
import whisper
import sounddevice as sd
from features.copyMatter_from_Wikipedia import create_gui
from features.prints import print_slow
from features.print_slow_and_speak import print_slow_and_speak
from features.news import fetch_and_play_news
from features.reademail import read_recent_emails
from features.playalong import *

sys.path.append(os.path.join(os.path.dirname(__file__), 'features'))

warnings.filterwarnings("ignore", category=FutureWarning, module='whisper')
warnings.filterwarnings("ignore", category=UserWarning, module='whisper')

def get_absolute_path(relative_path):
    return os.path.join(os.path.dirname(__file__), relative_path)

# Initialifze Pygame mixer
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=8192)
SCOPES = ['https://www.googleapis.com/auth/calendar']
# Set your API key
load_dotenv()
api_key = os.getenv("API_KEY")  # Ensure your .env file has this variable
resume_flag = Value('b', False)
genai.configure(api_key=api_key)
whisper_model = whisper.load_model("small")


def PlayVideo2(video_path):
    def extract_audio(video_path, audio_path):
        command = [
            'ffmpeg', '-i', video_path, 
            '-q:a', '0', '-map', 'a', audio_path
        ]
        with open(os.devnull, 'w') as devnull:
            subprocess.run(command, stdout=devnull, stderr=devnull)

    def play_audio(filename, stop_event):
        wave_obj = sa.WaveObject.from_wave_file(filename)
        play_obj = wave_obj.play()
        
        while not stop_event.is_set() and play_obj.is_playing():
            pass

    audio_path = "audio.wav"  # Temporary audio file
    extract_audio(video_path, audio_path)  # Extract audio from video

    stop_event = Event()  # Create an event to stop audio playback
    
    # Load the video
    video = cv2.VideoCapture(video_path)

    # Set the window to full screen
    cv2.namedWindow("Starting JARVIS 2.0", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Starting JARVIS 2.0", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Start audio in a separate thread
    audio_thread = Thread(target=play_audio, args=(audio_path, stop_event))
    audio_thread.start()
    
    while True:
        grabbed, frame = video.read()

        if not grabbed:
            print_slow_and_speak("System Started Boss")
            break

        # Display the video frame
        cv2.imshow("Starting JARVIS 2.0", frame)

        # Check for 'Esc' key press
        key = cv2.waitKey(28)  # Adjust as needed
        if key == 27:  # 27 is the ASCII code for the Esc key
            stop_event.set()  # Signal the audio thread to stop
            break

    video.release()
    cv2.destroyAllWindows()
    audio_thread.join()  # Wait for the audio thread to finish

    # Clean up the temporary audio file
    if os.path.exists(audio_path):
        os.remove(audio_path)

def PlayVideo(video_path):
    def PlayAudio(get_frame, player):
        while True:
            frame, val = get_frame()
            if val != 'eof' and frame is not None:
                img, t = frame
            else:
                break

    video = cv2.VideoCapture(video_path)
    player = MediaPlayer(video_path)
    
    # Set the window to full screen
    cv2.namedWindow("StartIng JARVIS 2.0", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("StartIng JARVIS 2.0", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    while True:
        grabbed, frame = video.read()
        audio_frame, val = player.get_frame()

        if not grabbed:
            print_slow_and_speak("System Started Boss")
            break

        # Show the video frame
        cv2.imshow("StartIng JARVIS 2.0", frame)

        # Check for 'Esc' key press
        key = cv2.waitKey(28)
        if key == 27:  # 27 is the ASCII code for the Esc key
            break
        
        if val != 'eof' and audio_frame is not None:
            img, t = audio_frame

    video.release()
    cv2.destroyAllWindows()

def truncate_response(text, max_lines=4):
    lines = text.split('\n')
    if len(lines) > max_lines:
        return '\n'.join(lines[:max_lines]) + '...'
    return text

def play_audio(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():  # Wait until the audio has finished playing
        pygame.time.Clock().tick(10)

def open_powerpoint():
    print_slow_and_speak("OK Boss....Opening PowerPoint application")
    try:
        subprocess.Popen([r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PowerPoint.lnk"], shell=True)
    except Exception:
        print_slow_and_speak("PowerPoint application could not be opened. Please check the path.")

def open_chrome():
    print_slow_and_speak("OK Boss....Opening chrome")
    try:
        subprocess.Popen([r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Chrome.lnk"], shell=True)
    except Exception:
        print_slow_and_speak("Google Chrome application could not be opened. Please check the path.")

def open_github():
    print_slow_and_speak("OK Boss....Opening Github account")
    try:
        subprocess.Popen([r"C:\Users\hp\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Chrome Apps\GitHub.lnk"], shell=True)
    except Exception:
        print_slow_and_speak("GitHub application could not be opened. Please check the path.")

def transcribe_audio_using_sr(file_path):
    # Using SpeechRecognition library (Google Web Speech)
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "JARVIS listen to me."
        except sr.RequestError as e:
            return f"Error with the service: {e}"

def transcribe_audio_using_google(file_path):
    # Using Google Cloud Speech-to-Text API
    client = speech.SpeechClient()

    with open(file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    # Returns the first transcription result
    for result in response.results:
        return result.alternatives[0].transcript
    return ""


def load_contacts():
    # Load contacts from the contacts.json file
    try:
        with open("contacts.json", "r") as file:
            contacts = json.load(file)
            return contacts
    except FileNotFoundError:
        speak_and_play("Contacts file not found.")
        return {}
    except json.JSONDecodeError:
        speak_and_play("Error reading the contacts file.")
        return {}

def match_contact(contact_name, contacts):
    # Use fuzzywuzzy to match the contact name with available contacts
    best_match = process.extractOne(contact_name, contacts.keys())
    if best_match and best_match[1] >= 70:  # 70 is the threshold for matching
        return best_match[0]  # return the contact name with the highest match score
    return None

def get_phone_number_from_user():
    speak_and_play("I couldn't find the contact. Please say the phone number you want to send a message to.")
    while True:
        audio = record_audio(duration=5)
        temp_wav_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_wav_filename = temp_wav_file.name
        temp_wav_file.close()
        save_audio_to_wav(audio, 16000, temp_wav_filename)

        # Use SpeechRecognition or Google Cloud Speech-to-Text for transcription
        phone_number = transcribe_audio_using_sr(temp_wav_filename)  # Or use transcribe_audio_using_google
        print(f"Phone Number: {phone_number}")

        cleaned_phone_number = phone_number.replace(" ", "")  # Removing spaces

        # Validate the phone number format (basic validation)
        if cleaned_phone_number and cleaned_phone_number.isdigit() and len(cleaned_phone_number) >= 10:
            return cleaned_phone_number
        else:
            speak_and_play("Sorry, I didn't understand the number. Please say it again.")

def whatsapp_messaging():
    contacts = load_contacts()

    if not contacts:
        return

    speak_and_play("Boss, to whom should I message on behalf of you?")
    attempts = 0
    matched_contact = None

    while attempts < 3:
        audio = record_audio(duration=5)
        temp_wav_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_wav_filename = temp_wav_file.name
        temp_wav_file.close()
        save_audio_to_wav(audio, 16000, temp_wav_filename)

        # Use SpeechRecognition or Google Cloud Speech-to-Text for transcription
        transcription = transcribe_audio_using_sr(temp_wav_filename)  # Or use transcribe_audio_using_google

        print(f"Transcription: {transcription}")

        # Check if the transcription contains 'phone number'
        if "phone number" in transcription.lower():
            # Trigger phone number input if the user mentions 'phone number'
            phone_number = get_phone_number_from_user()
            break

        # Check if the transcription matches any contact
        contact_name = transcription.capitalize()
        matched_contact = match_contact(contact_name, contacts)

        if matched_contact:
            phone_number = contacts[matched_contact]
            speak_and_play(f"Messaging {matched_contact}.")
            break
        else:
            speak_and_play(f"Contact '{contact_name}' not found. Please try again.")
            attempts += 1

    if matched_contact or phone_number:
        speak_and_play(f"Boss, what message do you want to send?")
        while True:
            audio = record_audio(duration=5)
            temp_wav_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_wav_filename = temp_wav_file.name
            temp_wav_file.close()
            save_audio_to_wav(audio, 16000, temp_wav_filename)

            # Use SpeechRecognition or Google Cloud Speech-to-Text for transcription
            message = transcribe_audio_using_sr(temp_wav_filename)  # Or use transcribe_audio_using_google

            print(f"Message: {message}")

            speak_and_play(f"Sending message: {message}")
            url = f'https://web.whatsapp.com/send?phone={phone_number}&text={message}'
            webbrowser.open(url)

            # Allow time for WhatsApp Web to load and send the message
            time.sleep(10)
            pyautogui.press('enter')
            speak_and_play("Message sent successfully.")
            break
    else:
        speak_and_play("Sorry, I couldn't understand the contact name or phone number.")

def open_whatsapp():
    print_slow_and_speak("OK Boss....Opening Your Whatsapp")
    try:
        
        whatsapp_messaging()
    except Exception:
        print_slow_and_speak("WhatsApp application could not be opened. Please check the internet connection.")

def open_cmd():
    print_slow_and_speak("OK Boss....Opening CMD....but be carefull you can get confused with this cmd and opened cmd")
    try:
        subprocess.Popen([r"C:\Windows\System32\cmd.exe"])
    except Exception:
        print_slow_and_speak("Command Prompt could not be opened. Please check the path.")

def open_linkedin():
    linkedin_url = "https://www.linkedin.com/in/mohd-sohail-7bb81b278//"
    print_slow_and_speak("OK Boss....Opening Your LinkedIn Profile")
    webbrowser.open(linkedin_url)

def open_instagram():
    instagram_url = "https://www.instagram.com/1b_sohailahmed/"
    print_slow_and_speak("OK Boss....Opening Your Instagram Account")
    webbrowser.open(instagram_url)

def open_cmrtc():
    cmrtc_url = "https://cmrtcerp.com/BEESERP/Login.aspx"
    print_slow_and_speak("OK Boss....Opening College Website")
    webbrowser.open(cmrtc_url)
    print_slow_and_speak("Boss....Can you please enter your login credentials")

def open_gmail():
    gmail_url = "https://mail.google.com/mail/u/0/?tab=rm&ogbl#inbox"
    print_slow_and_speak("OK Boss....Opening your Gmail Inbox")
    webbrowser.open(gmail_url)


def save_audio_to_wav(audio, samplerate, filename):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(samplerate)
        wf.writeframes(audio.tobytes())



def record_audio(duration, samplerate=16000):
    print("Listening to You Boss...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    return recording.flatten()


def play_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    cv2.namedWindow('Video', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Video', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow('Video', frame)

        if cv2.waitKey(25) & 0xFF == 27:  # ESC key to stop
            break

    cap.release()
    cv2.destroyAllWindows()

def tell_time():
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    time_message = f"The current time is {current_time}"

    temp_folder = get_absolute_path("temp")
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    
    print_slow_and_speak(time_message)

def text_to_speech(text, filename):
    engine = pyttsx3.init()
    # Create a temporary file
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        temp_filename = temp_file.name
    # Save audio to the temporary file
    engine.save_to_file(text, temp_filename)
    engine.runAndWait()
    
    # Ensure correct WAV format
    audio = AudioSegment.from_wav(temp_filename)
    audio.export(filename, format="wav")
    
    # Clean up temporary file
    os.remove(temp_filename)
# def text_to_speech(text, lang="en"):
#     engine = pyttsx3.init()
#     # Configure voice properties for Hinglish (Hindi-English mix)
#     voices = engine.getProperty('voices')
#     if lang == "hi":
#         engine.setProperty('voice', voices[0].id)  # Set Hindi voice (may vary by TTS setup)
#     else:
#         engine.setProperty('voice', voices[0].id)  # Default English voice
#     engine.setProperty('rate', 150)  # Adjust speed
#     engine.say(text)
#     engine.runAndWait()

def get_gemini_response(model, message):
    retry_attempts = 3  # Set the number of retry attempts
    for attempt in range(retry_attempts):
        try:
            chat = model.start_chat()
            response = chat.send_message(message)
            return response.text
        except InternalServerError as e:
            print(f"Attempt {attempt + 1} failed due to server error: {e}. Retrying...")
            time.sleep(2)  # Wait for 2 seconds before retrying
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break  # Stop the loop on any unexpected error
    return "Failed to get a response after multiple attempts."

def process_response_text(text):
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text

def process_gemini_content(content):
    """
    Process the raw content received from Gemini model.
    This function will clean up the redundant lines and apply formatting.
    """
    processed_content = []
    lines = content.split('\n')
    
    # Process each line to remove redundant content and apply correct formatting
    for line in lines:
        # Remove redundant lines with the format "• This is the content for ..."
        if line.startswith("• This is the content for"):
            continue

        # Remove unnecessary markers like "**" or "##"
        line = re.sub(r'[\*\#\*\*]', '', line)
        
        # Add the cleaned line to processed content
        if line.strip():  # Ensure it's not empty
            processed_content.append(line.strip())

    return processed_content


from docx.shared import RGBColor, Pt
from docx import Document
import re
import tempfile

def process_gemini_content_2(content):
    """
    Process the raw content received from Gemini model.
    This function will clean up the redundant lines, apply correct formatting,
    and detect section names for bold formatting.
    """
    processed_content = []
    lines = content.split('\n')
    
    for line in lines:
        # Skip redundant lines like "• This is the content for ..."
        if line.startswith("• This is the content for"):
            continue
        
        # Remove unnecessary symbols like "**" or "##"
        line = re.sub(r'[\*\#\*\*]', '', line)
        
        # Check if the line is a section name (e.g., "Introduction", "History", etc.)
        if line.strip() and not line.strip()[0].isdigit():  # If not a numbered section
            processed_content.append({'section': line.strip(), 'is_section': True})
        else:
            processed_content.append({'section': line.strip(), 'is_section': False})

    return processed_content

def set_normal_style(paragraph):
    """
    Apply Normal style with Times New Roman font and size 14 to the paragraph.
    """
    run = paragraph.add_run(paragraph.text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(0, 0, 0)  # Set the text color to black

def create_document():
    speak_and_play("What topic would you like to create a document on?")
    
    # Record and transcribe the topic
    topic = ""
    attempts = 0
    while attempts < 3:
        audio = record_audio(duration=5)
        temp_wav_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_wav_filename = temp_wav_file.name
        temp_wav_file.close()
        save_audio_to_wav(audio, 16000, temp_wav_filename)

        topic = transcribe_audio_using_sr(temp_wav_filename)
        print(f"Topic: {topic}")

        if topic:
            speak_and_play(f"Creating document on {topic}")
            break
        else:
            attempts += 1
            speak_and_play("Sorry, I couldn't understand. Please try again.")

    if not topic:
        speak_and_play("I couldn't understand the topic. Please try again later.")
        return

    # Generate content using Gemini model
    model_name = "gemini-1.5-flash-8b"
    gemini_model = genai.GenerativeModel("gemini-1.5-flash-8b")
    message = f"Provide a detailed explanation in a document form with sections about {topic}.(NOTE:THE MATTER SHOULD BE EASILY CONVERTED TO THE DOCUMENT BY JUST PASTING)"
    content = get_gemini_response(gemini_model, message)
    speak_and_play("Generating document content...")

    # Process the content before adding to document
    processed_content = process_gemini_content_2(content)
    
    # Create a new document
    doc = Document()

    # Add Title (Heading 1 - center-aligned, blue, bold)
    title = doc.add_heading(topic, level=1)
    title.alignment = 1  # Center the title
    title_run = title.runs[0]
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(0, 0, 0)  # Set title color to black

    # Add processed content sections
    for item in processed_content:
        if item['is_section']:
            # Add section name in bold (Heading 2)
            section = doc.add_paragraph(item['section'], style='Heading 2')
            section_run = section.runs[0]
            section_run.font.bold = True
            section_run.font.color.rgb = RGBColor(0, 0, 0)  # Set section color to black
        else:
            # Add content under the section with Normal style, Times New Roman, 14 font size, black color
            paragraph = doc.add_paragraph(item['section'])
            set_normal_style(paragraph)

    # Save the document to a file
    file_path = f"C:\\Users\\hp\\Desktop\\{topic.replace(' ', '_')}_Document.docx"
    doc.save(file_path)
    
    speak_and_play(f"Document on {topic} created successfully. You can find it at this location.")
    print(f"Document saved at {file_path}")





def greet_user():
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "Good morning"
    elif 12 <= current_hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    print_slow_and_speak(greeting)
    print_slow_and_speak("Welcome Back Boss, All Systems are fully operational")

def play_audio(file_path):
    """Play an audio file."""
    if os.path.isfile(file_path):
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    else:
        print(f"Audio file not found: {file_path}")

def speak_and_play(prompt):
    temp_folder = get_absolute_path("temp")
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    unique_filename = os.path.join(temp_folder, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_summary.wav")
    text_to_speech(prompt, unique_filename)
    play_audio(unique_filename)

def read_pdf_and_play_audio():
    # Replace audio prompts with print_slow_and_speak
    print_slow_and_speak("Boss...Can you Please provide the path to the PDF file.")
    
    # Ask the user to enter the file path of the PDF
    pdf_path = input("Please enter the path to the PDF file: ").strip()
    
    # Remove double quotes from the path
    sanitized_pdf_path = pdf_path.replace('"', '')

    # Check if the sanitized PDF file path exists
    if not os.path.isfile(sanitized_pdf_path):
        # Inform the user that the path does not exist
        print_slow_and_speak("The specified PDF file does not exist. Please check the path and try again.")
        return

    # Read the PDF content
    def read_pdf_with_pypdf2(file_path):
        pdf_content = ""
        try:
            with open(file_path, "rb") as file:
                reader = PdfReader(file)
                for page in reader.pages:
                    pdf_content += page.extract_text() + "\n"
        except Exception as e:
            print(f"An error occurred while reading the PDF: {e}")
        return pdf_content

    pdf_content = read_pdf_with_pypdf2(sanitized_pdf_path)
    
    if pdf_content:
        # Inform the user that the content is being printed
        print_slow_and_speak("Printing the PDF content.")
        print("PDF Content:")
        print(pdf_content)
    else:
        # Inform the user that no content was found
        print_slow_and_speak("No content found in the PDF.")

def say_goodbye():
    current_hour = datetime.now().hour
    if 21 <= current_hour or current_hour < 5:
        ending_message = "Good night boss, take care.....Bye"
    else:
        ending_message = "Bye boss...Take Care...Come back soon."

    # Use print_slow_and_speak to deliver the message
    print_slow_and_speak(ending_message)


def play_background_with_intro(intro_file, background_file, background_volume=0.3):
    pygame.mixer.init()

    # Load intro and background audio
    intro_segment = pygame.mixer.Sound(intro_file)
    background_segment = pygame.mixer.Sound(background_file)

    # Adjust the background volume
    background_segment.set_volume(background_volume)

    # Play background audio in a loop
    background_segment.play(-1)

    # Play intro audio
    intro_segment.play()

    # Wait for the intro audio to finish
    intro_length = intro_segment.get_length() * 1000  # Convert seconds to milliseconds
    pygame.time.wait(int(intro_length))  # Wait for intro audio to finish

    # Stop the background audio
    background_segment.stop()
def restart_laptop():
    # Prompt the user before restarting the system
    print_slow_and_speak("Boss, have you saved your work? I am going to restart your system. Press 'Enter' to proceed, 'Esc' to cancel, or wait for 5 seconds to restart automatically.")

    # Wait for the user to press 'Enter', 'Esc', or timeout after 5 seconds
    print_slow_and_speak("Waiting for your response...")

    start_time = time.time()
    while time.time() - start_time < 5:  # 5-second window
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\r':  # 'Enter' key
                print_slow_and_speak("Restarting now, boss.")
                subprocess.run(["shutdown", "/r", "/t", "0"])
                return
            elif key == b'\x1b':  # 'Esc' key
                print_slow_and_speak("Restart cancelled, boss.")
                return

    # If no input within 5 seconds, proceed with restart
    print_slow_and_speak("No response received. Restarting the system now.")
    subprocess.run(["shutdown", "/r", "/t", "0"])

def shutdown_laptop():
    # Prompt the user before shutting down the system
    print_slow_and_speak("Boss, have you saved your work? I am going to shut down your system. Press 'Enter' to proceed, 'Esc' to cancel, or wait for 5 seconds to shut down automatically.")

    # Wait for the user to press 'Enter', 'Esc', or timeout after 5 seconds
    print_slow_and_speak("Waiting for your response...")

    start_time = time.time()
    while time.time() - start_time < 5:  # 5-second window
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\r':  # 'Enter' key
                print_slow_and_speak("Shutting down now, boss.")
                subprocess.run(["shutdown", "/s", "/t", "0"])
                return
            elif key == b'\x1b':  # 'Esc' key
                print_slow_and_speak("Shutdown cancelled, boss.")
                return

    # If no input within 5 seconds, proceed with shutdown
    print_slow_and_speak("No response received. Shutting down the system now.")
    subprocess.run(["shutdown", "/s", "/t", "0"])


def ask_user_name():
    # starting_intro_of_jarvis = get_absolute_path("media/jarvis_small_intro.wav")
    # play_audio(starting_intro_of_jarvis)
    print("Welcome to JARVIS 2.0")
    
    attempts = 0
    max_attempts = 5

    valid_names_ascii = [
        [112, 104, 101, 110, 111, 109],
        [98, 111, 115, 115],
        [115, 97, 109, 101, 101, 114],
        [115, 97, 109, 105, 114],
        [115, 97, 109, 101, 101, 114, 32, 104, 117, 115, 115, 97, 105, 110],
        [115, 104, 97, 105, 107],
        [119, 97, 107, 101, 32, 117, 112, 32, 106, 97, 114, 118, 105, 115],
        [119, 101, 108, 99, 111, 109, 101, 32, 98, 97, 99, 107, 32, 106, 97, 114, 118, 105, 115]
    ]
    
    valid_names = [''.join(chr(char) for char in name) for name in valid_names_ascii]

    while attempts < max_attempts:
        # remaining_attempts = max_attempts - attempts
        # prompt_message = f"Sir, you have {remaining_attempts} attempt{'s' if remaining_attempts > 1 else ''} left out of {max_attempts}. Please Enter the code word carefully"
        # print_slow_and_speak(prompt_message)

        # Hide user input
        user_input = getpass.getpass("Please enter the code word: ")

        if any(name in user_input.lower() for name in valid_names):
            return True
        
        error_filename = get_absolute_path("media/Sorry_Not_my_boss.wav")
        play_audio(error_filename)
        attempts += 1
    
    print_slow_and_speak("Maximum attempts reached. Exiting...")
    sys.exit()

def get_location_info():
    prompt_message = "Boss.....! Please Enter the destination: "
    
    # Convert the prompt to speech and play it
    print_slow_and_speak(prompt_message)
    
    # Wait for the prompt to finish before asking for input
    destination = input(prompt_message)
    
    def loc(place):
        try:
            geolocator = Nominatim(user_agent="myUniqueAppName")
            location = geolocator.geocode(place, addressdetails=True)
            
            if not location:
                return None, {'error': 'Location not found'}, None
            
            target_latlng = (location.latitude, location.longitude)
            target_location = location.raw['address']
            target_info = {
                'city': target_location.get('city', 'Unknown City'),
                'state': target_location.get('state', 'Unknown State'),
                'country': target_location.get('country', 'Unknown Country')
            }

            current_loc = geocoder.ip('me')
            current_latlng = current_loc.latlng
            
            if not current_latlng:
                return None, {'error': 'Current location not found'}, None
            
            distance = str(great_circle(current_latlng, target_latlng))
            distance = str(distance.split(' ', 1)[0])
            distance = round(float(distance), 2)

            return current_latlng, target_info, distance
        except Exception as e:
            print(f"Error during geocoding: {e}")
            return None, {'error': str(e)}, None

    def my_location():
        try:
            ip_add = requests.get('https://api.ipify.org').text
            url = f'https://get.geojs.io/v1/ip/geo/{ip_add}.json'
            geo_requests = requests.get(url)
            geo_data = geo_requests.json()
            
            city = geo_data.get('city', 'Unknown City')
            state = geo_data.get('region', 'Unknown State')
            country = geo_data.get('country', 'Unknown Country')
            postal = geo_data.get('postal', 'Unknown Postal Code')
            
            return city, state, country, postal
        except Exception as e:
            print(f"Error getting IP location: {e}")
            return "Unknown City", "Unknown State", "Unknown Country", "Unknown Postal Code"

    current_latlng, destination_info, distance = loc(destination)
    
    if current_latlng and destination_info:
        current_city, current_state, current_country, postal_code = my_location()
        
        # Form the message with a newline between current location and destination
        message = (f"Current Location: {current_city}, {current_state}, {current_country}.\n"
                   f"Destination: {destination_info['city']}, {destination_info['state']}, {destination_info['country']}.\n"
                   f"Boss, The Distance to destination is: {distance} km.")
        
        print_slow_and_speak(message)
        
    else:
        error_message = destination_info['error']
        print_slow_and_speak(error_message)

def get_weather():
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        print_slow_and_speak("API key not found.")
        return
    
    # Prompt the user to press Enter or provide city name
    prompt_text = "Press Enter to check the weather, or type the city name to get its weather details."
    # speech_thread = threading.Thread(target=speak_and_play, args=(prompt_text,))
    # speech_thread.start()
    print_slow_and_speak(prompt_text)
    # speech_thread.join()
    
    user_input = input("Enter city name or press Enter to get weather for your current location: ").strip()

    if user_input == "":
        city = get_current_location()
    else:
        city = user_input

    if city:
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('cod') != 200:
                error_message = "Request failed."
                print_slow_and_speak(error_message)
                # text_to_speech(error_message, "error.wav")
                # play_audio("error.wav")
                return
            
            weather = data['weather'][0]['description']
            temp = data['main']['temp']
            
            # Print the weather information
            weather_report = f"Weather in {city}: {weather.capitalize()}. Temperature: {temp}°C"
            print_slow_and_speak(weather_report)
            
            # Play the weather information as audio
            # text_to_speech(weather_report, "weather_report.wav")
            # play_audio("weather_report.wav")
        
        except requests.RequestException as e:
            error_message = f"Request failed: {e}"
            print_slow_and_speak(error_message)

def get_current_location():
    try:
        ip_add = requests.get('https://api.ipify.org').text
        url = f'https://get.geojs.io/v1/ip/geo/{ip_add}.json'
        geo_requests = requests.get(url)
        geo_data = geo_requests.json()
        
        city = geo_data.get('city', 'Unknown City')
        state = geo_data.get('region', 'Unknown State')
        country = geo_data.get('country', 'Unknown Country')
        
        location = f"{city}, {state}, {country}"
        
        # Print the current location
        print_slow_and_speak(f"Boss, your current location is: {location}. Checking weather now.")
        
        return city
    
    except Exception as e:
        error_message = f"Error: {e}"
        print_slow_and_speak(error_message)
        return None
    
def check_battery_status():
    battery = psutil.sensors_battery()
    if battery:
        percent = battery.percent
        charging = battery.power_plugged
        if charging:
            status_message = f"Laptop is charging. Battery is at {percent} percent."
        else:
            status_message = f"Laptop is not charging. Battery is at {percent} percent."
    else:
        status_message = "Battery information is not available."

    print_slow_and_speak(status_message)

def authenticate_google_calendar():
    creds = None
    credentials_path = get_absolute_path('credentials.json')

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                print_slow_and_speak("Please integrate Google Calendar and obtain the credentials.json file.")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=8080)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)


def get_events():
    service = authenticate_google_calendar()
    now = datetime.now(timezone.utc).isoformat()
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        NoUpcoming = "Boss....! There is no schedule fixed for you."
        print_slow_and_speak('No upcoming events found.')
        # speak_and_play(NoUpcoming)
        return

    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    for event in events:
        # Wait for user input
        print("Press 'Enter' to view the next event or 'Esc' to exit.")
        speak_and_play("Boss..! Please Press 'Enter' to view the next event or 'Esc' to exit")
        while True:
            if keyboard.is_pressed('enter'):
                break
            elif keyboard.is_pressed('esc'):
                print_slow_and_speak("Stopping event retrieval.")
                # speak_and_play("Stopping event retrieval, Boss!")
                return
        
        start = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', 'No Title')
        description = event.get('description', 'Boss....! You did not specify anything for this event.')

        # Convert the start date-time to a date object
        start_dt = datetime.fromisoformat(start[:-6])  # Removes the timezone part
        event_date = start_dt.date()
        formatted_time = start_dt.strftime("%I:%M %p")

        # Check if the event is today or tomorrow
        if event_date == today:
            date_text = "today"
        elif event_date == tomorrow:
            date_text = "tomorrow"
        else:
            date_text = start_dt.strftime("%d %B %Y")

        # Print and speak event details
        print(summary)
        print(description)
        message = f"Boss....! You have scheduled '{summary}' at {formatted_time} {date_text}. {description}"
        speak_and_play(message)


def add_event():
    service = authenticate_google_calendar()
    
    speak_and_play("Boss..! Please Enter title of the event")
    title = input("Boss..! Please Enter title of the event: ")
    speak_and_play("Now Enter event description")
    description = input("Now Enter event description: ")
    speak_and_play("Enter year")
    year = int(input("Enter year (YYYY): "))
    speak_and_play("Enter month")
    month = int(input("Enter month (MM): "))
    speak_and_play("Enter day")
    day = int(input("Enter day (DD): "))
    speak_and_play("Enter time....! or press Enter for default timing")
    time = input("Enter time (HH:MM:SS, or press Enter for default 12:00:00): ") or "12:00:00"
    
    month_str = f"{month:02d}"
    day_str = f"{day:02d}"
    
    start_time = f"{year}-{month_str}-{day_str}T{time}+05:30"
    end_time = f"{year}-{month_str}-{day_str}T{time}+05:30"
    
    event = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Kolkata',
        },
    }
    
    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {event.get('htmlLink')}")
        success_message = "BOSS....! SCHEDULED FIXED FOR YOU SUCCESSFULLY"
        speak_and_play(success_message)
    except Exception as e:
        print(f"An error occurred: {e}")


def update_event():
    service = authenticate_google_calendar()
    
    upcoming_events = service.events().list(calendarId='primary', maxResults=5, singleEvents=True,
                                            orderBy='startTime').execute()
    events = upcoming_events.get('items', [])
    
    if not events:
        message = "No upcoming events found."
        print(message)
        speak_and_play(message)
        return

    for event in events:
        event_id = event['id']
        event_summary = event['summary']
        event_start = event['start'].get('dateTime', event['start'].get('date'))
        event_description = event.get('description', 'No description')
        print(f"Event ID: {event_id}")
        print(f"Summary: {event_summary}")
        print(f"Start: {event_start}")
        print(f"Description: {event_description}\n")  # New line for better readability

        speak_and_play(f"Event title: {event_summary}. Description: {event_description}")
    speak_and_play("Boss...! Please Enter the title of the event to update")
    event_title = input("Boss...! Please Enter the title of the event to update: ")
    speak_and_play("Enter new description for the event")
    updated_description = input("Enter new description for the event: ")

    for event in events:
        if event['summary'] == event_title:
            event_id = event['id']
            event = service.events().get(calendarId='primary', eventId=event_id).execute()
            event['description'] = updated_description
            updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
            message = f"Event updated: {updated_event.get('summary')}"
            print(message)
            speak_and_play(updated_event.get('summary'))  # Play only the updated event title
            return

    message = "No event found with that title."
    print(message)
    speak_and_play(message)

def pause_jarvis():
    global resume_flag
    speak_and_play("Boss...! Waiting for your next commands.")
    
    while True:
        if resume_flag.value:  # Access the shared flag
            speak_and_play("Boss...! Resuming your commands")
            resume_flag.value = False  # Reset the flag
            break
        time.sleep(1)  # Wait for the signal

def delete_event_by_title():
    service = authenticate_google_calendar()
    event_title = input("Enter the title of the event to delete: ")
    now = datetime.now(timezone.utc).isoformat()
    events_result = service.events().list(calendarId='primary', timeMin=now, singleEvents=True).execute()
    events = events_result.get('items', [])
    
    for event in events:
        if event.get('summary') == event_title:
            event_id = event['id']
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            print(f"Deleted event: {event_id}")
            return  # Delete one event and exit after confirmation

    print("No event found with the specified title.")

class CodeGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Generator")
        self.root.attributes("-fullscreen", True)  # Fullscreen

        self.label = tk.Label(root, text="Enter your problem statement:", font=('Arial', 14))
        self.label.pack(pady=10)

        self.problem_entry = tk.Entry(root, width=80, font=('Arial', 14))
        self.problem_entry.pack(pady=10)

        self.generate_button = tk.Button(root, text="Generate Code", font=('Arial', 14), command=self.generate_code)
        self.generate_button.pack(pady=10)

        self.copy_button = tk.Button(root, text="Copy to Clipboard", font=('Arial', 14), command=self.copy_to_clipboard)
        self.copy_button.pack(pady=10)

        self.code_output = tk.Text(root, wrap='word', height=20, width=100, font=('Courier New', 12))
        self.code_output.pack(pady=10)

        # Define fonts for italic and bold
        self.italic_font = font.Font(family='Courier New', size=12, slant='italic')
        self.bold_font = font.Font(family='Courier New', size=12, weight='bold')

        # Syntax highlighting tags for multiple languages
        self.code_output.tag_configure('keyword', foreground='blue', font=self.bold_font)
        self.code_output.tag_configure('string', foreground='green')
        self.code_output.tag_configure('comment', foreground='gray', font=self.italic_font)
        self.code_output.tag_configure('html_tag', foreground='purple')
        self.code_output.tag_configure('html_attr', foreground='orange')

        # Bind Esc key to close the app
        self.root.bind("<Escape>", self.exit_app)

    def exit_app(self, event):
        self.root.destroy()

    def generate_code(self):
        problem = self.problem_entry.get()
        gemini_model = genai.GenerativeModel("gemini-1.5-flash-8b")
        response = get_gemini_response(gemini_model,problem)
        code = self.extract_code(response)
        self.code_output.delete(1.0, tk.END)
        self.insert_with_syntax_highlighting(code)

    def extract_code(self, response):
        code_blocks = re.findall(r'```(?:\w*\n)?(.*?)```', response, re.DOTALL)
        return code_blocks[0].strip() if code_blocks else "No code found."

    def insert_with_syntax_highlighting(self, code):
        lang = self.detect_language(code)
        for line in code.split('\n'):
            start_idx = f"{self.code_output.index(tk.INSERT)}"
            self.code_output.insert(tk.END, line + '\n')
            if lang == 'python':
                self.highlight_python_syntax(line, start_idx)
            elif lang == 'php':
                self.highlight_php_syntax(line, start_idx)
            elif lang == 'java':
                self.highlight_java_syntax(line, start_idx)
            elif lang in ['c', 'cpp']:
                self.highlight_c_syntax(line, start_idx)
            elif lang == 'html':
                self.highlight_html_syntax(line, start_idx)

    def detect_language(self, code):
        if 'def ' in code or 'import ' in code:
            return 'python'
        elif '<?php' in code:
            return 'php'
        elif 'public static void main' in code:
            return 'java'
        elif '#include' in code or 'int main' in code:
            return 'c'
        elif '<html>' in code or '</html>' in code:
            return 'html'
        return 'unknown'

    def highlight_python_syntax(self, line, start_idx):
        keywords = ['def', 'class', 'import', 'from', 'as', 'return', 'if', 'else', 'for', 'while', 'try', 'except']
        self.apply_syntax_highlighting(line, start_idx, keywords)

    def highlight_php_syntax(self, line, start_idx):
        keywords = ['<?php', 'echo', 'function', 'if', 'else', 'foreach', 'while', 'return', 'class', 'public', 'private']
        self.apply_syntax_highlighting(line, start_idx, keywords)

    def highlight_java_syntax(self, line, start_idx):
        keywords = ['public', 'static', 'void', 'class', 'if', 'else', 'for', 'while', 'return', 'new', 'int', 'String']
        self.apply_syntax_highlighting(line, start_idx, keywords)

    def highlight_c_syntax(self, line, start_idx):
        keywords = ['#include', 'int', 'return', 'if', 'else', 'for', 'while', 'printf', 'scanf', 'main', 'struct']
        self.apply_syntax_highlighting(line, start_idx, keywords)

    def highlight_html_syntax(self, line, start_idx):
        html_tags = re.findall(r'<\s*(\w+)', line)
        html_attrs = re.findall(r'(\w+)=', line)
        for tag in html_tags:
            idx = self.code_output.search(f'<{tag}', start_idx, stopindex=f"{start_idx} lineend")
            if idx:
                end_idx = f"{idx}+{len(tag)+2}c"
                self.code_output.tag_add('html_tag', idx, end_idx)
        for attr in html_attrs:
            idx = self.code_output.search(attr, start_idx, stopindex=f"{start_idx} lineend")
            if idx:
                end_idx = f"{idx}+{len(attr)}c"
                self.code_output.tag_add('html_attr', idx, end_idx)

    def apply_syntax_highlighting(self, line, start_idx, keywords):
        if line.strip().startswith("#") or "//" in line or "/*" in line:
            self.code_output.tag_add('comment', start_idx, f"{start_idx} lineend")
        else:
            for word in line.split():
                if word in keywords:
                    idx = self.code_output.search(word, start_idx, stopindex=f"{start_idx} lineend")
                    if idx:
                        end_idx = f"{idx}+{len(word)}c"  
                        self.code_output.tag_add('keyword', idx, end_idx)
                elif '"' in word or "'" in word:
                    idx = self.code_output.search(word, start_idx, stopindex=f"{start_idx} lineend")
                    if idx:
                        end_idx = f"{idx}+{len(word)}c"
                        self.code_output.tag_add('string', idx, end_idx)

    def copy_to_clipboard(self):
        code = self.code_output.get(1.0, tk.END).strip()
        if code:
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            messagebox.showinfo("Success", "Code copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No code to copy!")


def run_code_generator_app():
    time_message = f"OK Boss...! Opening Code Generator"
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav', dir='C:/Users/hp/Desktop/JARVIS2.0/temp', prefix='time_') as tmp_file:
        filename = tmp_file.name
        text_to_speech(time_message, filename)
    play_audio(filename)
    root = tk.Tk()
    app = CodeGeneratorApp(root)
    root.mainloop()

def send_email():
    sender_email = 'sendingemail806@gmail.com'
    sender_password = os.getenv('EMAIL_APP_PASSWORD')

    prompt = "Boss...! Please Enter receiver's email id"
    speak_and_play(prompt)
    receiver_email = input('Enter receiver email: ')

    prompt1 = "Boss...! Please Enter the subject of the email"
    speak_and_play(prompt1)
    subject = input('Enter the subject of the email: ')

    prompt2 = "Boss...! Please Enter the body of the email"
    speak_and_play(prompt2)
    body = input('Enter the body of the email: ')
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login(sender_email, sender_password)
        mail.sendmail(sender_email, receiver_email, msg.as_string())
        mail.close()

        print_slow_and_speak('Boss...! Email has been successfully sent!')
        # speak_and_play("Boss...! Email has been successfully sent!")
    except smtplib.SMTPAuthenticationError:
        print_slow_and_speak('Boss...! Authentication has failed. Please check your email and password.')
        # speak_and_play("Boss...! Authentication has failed. Please check your email and password.")
    except smtplib.SMTPException as e:
        print_slow_and_speak(f'Failed to send email. Error: {e}')
        # speak_and_play("Boss...! Failed to send the email.")

def start_execution():
    global stop_execution
    stop_execution = False
    thread = threading.Thread(target=main)
    thread.start()

def stop_execution_func():
    global stop_execution
    stop_execution = True
    print("Stopping execution...")

def main():
    duration = 5  # seconds
    output_folder = get_absolute_path("MyVoice")
    jarvis_folder = get_absolute_path("JarvisResponse")
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(jarvis_folder, exist_ok=True)
    
    #whisper_model = whisper.load_model("base")
    gemini_model = genai.GenerativeModel("gemini-1.5-flash-8b")
    
    greet_user()

    custom_responses = {
        "what is my name": get_absolute_path("media/Introductory_speech_of_me.wav"),
        #"sameer": get_absolute_path("media/KGF_BGMI.wav"),
        "jarvis introduce myself": get_absolute_path("media/Introductory_speech_of_me.wav"),
        "who made you": get_absolute_path("media/Introductory_speech_of_me.wav"),
        "who created you": get_absolute_path("media/Introductory_speech_of_me.wav"),
        "who is your boss": get_absolute_path("media/who_is_boss.wav"),
        "who is your boss jarvis": get_absolute_path("media/who_is_boss.wav"),
        "jarvis who is your boss jarvis": get_absolute_path("media/who_is_boss.wav"),
        "tell me about myself": get_absolute_path("media/Introductory_speech_of_me.wav"),
        "tell me something about myself": get_absolute_path("media/Introductory_speech_of_me.wav"),
        "who am i": get_absolute_path("media/Introductory_speech_of_me.wav"),
        "who are you": get_absolute_path("media/Jarvis_Introduction.wav"),
        "what is your name": get_absolute_path("media/Jarvis_Introduction.wav"),
        "introduce yourself jarvis": get_absolute_path("media/Jarvis_Introduction.wav"),
        "introduce yourself": get_absolute_path("media/Jarvis_Introduction.wav"),
        "tell me something about yourself": get_absolute_path("media/Jarvis_Introduction.wav"), 
        "open powerpoint": "open_powerpoint",
        "open presentation": "open_powerpoint",
        "presentation": "open_powerpoint",
        "powerpoint": "open_powerpoint",
        "shut down":"shutdown_laptop",
        "jarvis shutdown the system":"shutdown_laptop",
        "close all functions":"shutdown_laptop",
        "shutdown the laptop":"shutdown_laptop",
        "go to sleep":"shutdown_laptop",
        "check battery status":"check_battery_status",
        "check power":"check_battery_status",
        "jarvis write code for me":"run_code_generator_app",
        "write code for me":"run_code_generator_app",
        "open code generator":"run_code_generator_app",
        "start code generator":"run_code_generator_app",
        "how much power left":"check_battery_status",
        "go to sleep jarvis":"shutdown_laptop",
        "sleep jarvis":"shutdown_laptop",
        "shutdown jarvis":"shutdown_laptop",
        "send email":"send_email",
        "jarvis send email":"send_email",
        "send email to hp":"send_email",
        "jarvis can you write a mail for me":"send_email",
        "jarvis can you write a email for me":"send_email",
        "can you write a email for me":"send_email",
        "send email to hp@gmail.com":"send_email",
        "start sending email":"send_email",
        "sleep":"shutdown_laptop",
        "jarvis go to sleep":"shutdown_laptop",
        "go to sleep jarvis":"shutdown_laptop",
        "jarvis restart my system":"restart_laptop",
        "restart my system":"restart_laptop",
        "restart":"restart_laptop",
        "jarvis restart my system":"restart_laptop",
        "open wikipedia":"create_gui",
        "search in wikipedia":"create_gui",
        "open wikipedia":"create_gui",
        "search wikipedia":"create_gui",
        "what is time now": "tell_time",
        "tell me time": "tell_time",
        "wait": "pause_jarvis",
        "wait jarvis": "pause_jarvis",
        "jarvis wait": "pause_jarvis",
        "i said wait jarvis": "pause_jarvis",
        "open pdf": "read_pdf_and_play_audio",
        "open location": "get_location_info",
        "check location": "get_location_info",
        "check weather": "get_weather",
        "open weather app": "get_weather",
        "open weather": "get_weather",
        "open temperature": "get_weather",
        "hotness of surrounding": "get_weather",
        "jarvis how is the weather now": "get_weather",
        "location": "get_location_info",
        "read pdf": "read_pdf_and_play_audio",
        "scan pdf": "read_pdf_and_play_audio",
        "jarvis scan pdf": "read_pdf_and_play_audio",
        "jarvis scan pdf for me": "read_pdf_and_play_audio",
        "can you scan pdf for me": "read_pdf_and_play_audio",
        "present time": "tell_time",
        "open chrome": "open_chrome",
        "open github": "open_github",
        "check my schedule":"get_events",
        "what is there in my schedule":"get_events",
        "what my schedule":"get_events",
        "what is my schedule today":"get_events",
        "jarvis what is my schedule today":"get_events",
        "jarvis what is my schedule":"get_events",
        "what is my schedule":"get_events",
        "jarvis am i free":"get_events",
        "add event":"add_event",
        "jarvis add event":"add_event",
        "jarvis add event in my schedule":"add_event",
        "add event in my schedule":"add_event",
        "github": "open_github",
        "whatsapp": "open_whatsapp",
        "open whatsapp": "open_whatsapp",
        "open command": "open_cmd",
        "open my social media": "open_instagram",
        "open my instagram": "open_instagram",
        "open instagram": "open_instagram",
        "instagram": "open_instagram",
        "open linked in": "open_linkedin",
        "open my college website": "open_cmrtc",
        "college website": "open_cmrtc",
        "open my mail": "open_gmail",
        "open email": "open_gmail",
        "jarvis read my emails": "read_recent_emails",
        "jarvis read my mails": "read_recent_emails",
        "jarvis scan the gmail inbox": "read_recent_emails",
        "jarvis check mails": "read_recent_emails",
        "jarvis check for new messages": "read_recent_emails",
        "check for new messages": "read_recent_emails",
        "jarvis give me trending news":"fetch_and_play_news",
        "jarvis what is going on in the world":"fetch_and_play_news",
        "what is going on in the world":"fetch_and_play_news",
        "jarvis what is the news":"fetch_and_play_news",
        "tell me the latest news":"fetch_and_play_news",
        "jarvis what is the news today":"fetch_and_play_news",
        "what is the news today":"fetch_and_play_news",
        "jarvis give me news headlines":"fetch_and_play_news",
        "give me news headlines":"fetch_and_play_news",
        "jarvis give me trending news":"fetch_and_play_news",
        "jarvis check internet speed":"check_internet_speed",
        "jarvis check internet":"check_internet_speed",
        "what is my internet speed":"check_internet_speed",
        "internet speed":"check_internet_speed",
        "jarvis check internet connection":"check_internet_speed",
        "jarvis create a document":"create_document",
        "create a document":"create_document",
        "document":"create_document",
        "i want a document":"create_document",
        "prepare a document":"create_document",
        "can you help me in document":"create_document",
        "document creation":"create_document",
        "internet connection":"check_internet_speed",
        "jarvis check internet connection":"check_internet_speed",
    }

    stop_phrases = [
        "jarvis stop", "stop it jarvis", "shutup jarvis","enough jarvis", "stop yourself jarvis",
        "stop", "good bye jarvis", "stop it", "exit yourself", "stop yourself jarvis", "exit from command line", "don't anger me"
    ]   
    
    while True:
        # audio = record_audio(duration)
        
        # temp_wav_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        # temp_wav_filename = temp_wav_file.name
        # temp_wav_file.close()
        
        # save_audio_to_wav(np.array(audio, dtype=np.int16), 16000, temp_wav_filename)
        
        # result = whisper_model.transcribe(temp_wav_filename,language="en")
        # transcription = result.get("text", "No text found")
        audio = record_audio(duration=5)
        temp_wav_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_wav_filename = temp_wav_file.name
        temp_wav_file.close()
        save_audio_to_wav(audio, 16000, temp_wav_filename)

        # Use SpeechRecognition or Google Cloud Speech-to-Text for transcription
        transcription = transcribe_audio_using_sr(temp_wav_filename)
        
        print("Sameer Boss:", transcription)
        
        if any(phrase in transcription.lower() for phrase in stop_phrases):
            say_goodbye()
            print("Stopping...")
            os.remove(temp_wav_filename)
            break
        
        matched_response = None
        for phrase, action in custom_responses.items():
            if phrase in transcription.lower():
                matched_response = action
                break
        
        if matched_response:
            if matched_response == "open_powerpoint":
                open_powerpoint()
            elif matched_response == "open_chrome":
                open_chrome()
            elif matched_response == "open_cmd":
                open_cmd()
            elif matched_response == "open_linkedin":
                open_linkedin()
            elif matched_response == "open_cmrtc":
                open_cmrtc()
            elif matched_response == "open_instagram":
                open_instagram()
            elif matched_response == "open_gmail":
                open_gmail()
            elif matched_response == "open_whatsapp":
                open_whatsapp()
            elif matched_response == "open_github":
                open_github()
            elif matched_response == "tell_time":
                tell_time()
            elif matched_response == "read_pdf_and_play_audio":
                read_pdf_and_play_audio()
            elif matched_response == "shutdown_laptop":
                shutdown_laptop()
            elif matched_response == "restart_laptop":
                restart_laptop()
            elif matched_response == "check_battery_status":
                check_battery_status()
            elif matched_response == "get_location_info":
                get_location_info()
            elif matched_response == "get_weather":
                get_weather()
            elif matched_response == "run_code_generator_app":
                run_code_generator_app()
            elif matched_response == "add_event":
                add_event()
            elif matched_response == "get_events":
                get_events()
            elif matched_response == "send_email":
                send_email()
            elif matched_response == "pause_jarvis":
                pause_jarvis()
            elif matched_response == "read_recent_emails":
                read_recent_emails()
            elif matched_response == "create_gui":
                create_gui()
            elif matched_response == "fetch_and_play_news":
                fetch_and_play_news()
            elif matched_response == "check_internet_speed":
                check_internet_speed()
            elif matched_response == "create_document":
                create_document()
            else:
                if os.path.isfile(matched_response):
                        output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav').name
                        if "Introductory_speech_of_me" in matched_response:
                            play_background_with_intro(matched_response, get_absolute_path("media/KGF_BGMI.wav"), background_volume=0.8)
                        else:
                            play_background_with_intro(matched_response, get_absolute_path("media/Tiger_back.wav"), background_volume=0.3)
                else:
                    print(f"File not found: {matched_response}")
        else:
            saved_gemini_response = get_gemini_response(gemini_model, transcription)
            processed_response = process_response_text(saved_gemini_response)
            truncated_response = truncate_response(processed_response)
            timestamp=time.strftime("%Y%m%d_%H%M%S")
            response_file = os.path.join(jarvis_folder, f"jarvis_response_{timestamp}.wav")
            text_to_speech(truncated_response,response_file)
            
            print("Jarvis:", processed_response)
            
            play_audio(response_file)
        
        os.remove(temp_wav_filename)

if __name__ == "__main__":
    video_file = get_absolute_path("media/Jarvis_intro_video.mp4")
    # PlayVideo(video_file)
    # time.sleep(2)
    #fetch_and_play_news()
    main()
    #create_document()
    #read_recent_emails()

    #add_event()
    # if ask_user_name():
    #     main()
    # else:
    #     print("Sorry, You are not my boss")
    #     print("Incorrect name provided. Exiting...")
    #     sys.exit()




