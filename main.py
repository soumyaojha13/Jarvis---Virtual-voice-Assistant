import speech_recognition as sr
import webbrowser
import pyttsx3
import requests
import os
import pygame
from gtts import gTTS
from openai import OpenAI
import spotipy
from spotipy.oauth2 import SpotifyOAuth

recognizer =  sr.Recognizer()


#Spotify Client Setup
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.environ.get("SPOTIPY_CLIENT_ID"),
    client_secret=os.environ.get("SPOTIPY_CLIENT_SECRET"),
    redirect_uri="https://www.google.com/",
    scope="user-read-playback-state"
))

# function for text to speech using pyttsx3 module
def aiprocess(command):
    apikey=os.environ.get("OPENAI_API_KEY")
# Initialize client
    client = OpenAI(api_key=apikey)

# Make a request
    response = client.chat.completions.create(
        model="gpt-4o",  # or gpt-4o, gpt-3.5-turbo
        messages=[
            {"role": "system", "content": "You are a virtual assitant named jarvis skilled in general tasks like alexa,give short reponses "},
            {"role": "user", "content": command}
    ]
)

    return response.choices[0].message.content


def get_news():
    url = f"https://newsdata.io/api/1/news?apikey={os.environ.get('NEWS_API_KEY')}&country=in&language=en"
    response = requests.get(url).json()
    if "results" in response:
        for i, article in enumerate(response["results"][:5], start=1):  # read first 5
            speak(f"{i}. {article['title']}")
    else:
        speak("Sorry, I couldn't fetch Indian news right now.")
   
def speak_old(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

 
def play_song(query):
# search top 5 tracks for better match
    
    results = sp.search(q=f'track:{query}', type='track', limit=5)['tracks']['items']
    if not results:
        print("⚠️ Song not found")
        return

# find the track whose name matches query best (case-insensitive)
    
    query_lower = query.lower()
    best_track = None
    for track in results:
        if track['name'].lower() == query_lower:  # exact match
            best_track = track
            break

    if not best_track:
        best_track = results[0]  # fallback to first result if no exact match

    artists = ", ".join(a['name'] for a in best_track['artists'])
    print(f"🎶 Playing: {best_track['name']} - {artists}")

    # open Spotify link
    url = best_track['external_urls']['spotify']
    webbrowser.open(url)



# function for text to speech using gTTS + pygame


pygame.mixer.init()

def speak(text):
    tts = gTTS(text)
    tts.save("temp.mp3")
     
# Initialize pygame mixer
    pygame.mixer.init()

# Load the mp3 file
    pygame.mixer.music.load('temp.mp3')

# Play the mp3 file
    pygame.mixer.music.play()

# Keep the program running until the music stops
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.music.unload()
    os.remove("temp.mp3")


def processcommand(c):
    if "open google" in c.lower():
        webbrowser.open("https://www.google.com/")
    elif "open instagram" in c.lower():
        webbrowser.open("https://www.instagram.com/")
    elif"open youtube" in c.lower():
        webbrowser.open("https://www.youtube.com/")
    elif"open facebook" in c.lower():
        webbrowser.open("https://www.facebook.com/")
    elif"open linkedin" in c.lower():
        webbrowser.open("https://www.linkedin.com/")
   
    elif "news" in c.lower():
        get_news()
    
    elif c.lower().startswith("play"):
        song = c.lower().replace("play", "").strip()
        print(song)
        play_song(song)

    else:
        #let openAI handle the remaining requests
        results= aiprocess(c)
        speak(results)
    
     
if __name__ == "__main__":
    speak("I am ready")
    
while True:

    #Listen for the wake up word "jarvis"
    #obtain audio from microphone
    r = sr.Recognizer() #responsible for converting audio into text
    
    try:
        with sr.Microphone() as source: #This opens the system microphone as an audio source.
            print("listening....")
            audio = r.listen(source,timeout = 5, phrase_time_limit= 2)
        activationword = r.recognize_google(audio) #The recorded audio (audio) is sent to Google’s speech recognition API
        
        if (activationword.lower()== "jarvis"):
            speak("yes")
        # listen for command
            with sr.Microphone() as source:
                print(" Jarvis active...")
                audio = r.listen(source)
                command = r.recognize_google(audio)

                processcommand(command)
                
    
    except Exception as e :
        print("error {0}".format(e))
