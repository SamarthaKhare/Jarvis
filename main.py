import json
import requests
from fastapi import FastAPI
import uvicorn
from datetime import datetime
from elevenlabs.client import ElevenLabs
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from fastapi.responses import JSONResponse
from speech_v1 import SpeechToText
import vertexai
import datetime
from vertexai.preview.generative_models import GenerativeModel, FunctionDeclaration, Tool, HarmCategory, HarmBlockThreshold, Content, Part
import os

ELEVENLABS_API_KEY = "sk_aa9201c98a9f4bbb66001c04ff9a120391358810bb4e3a9a"
SERP_API_KEY = "47ce997875239b7ec3450278e62e1a2c309438ff6bfb88c87fdcbe6a1063fa46"
TELEGRAM_BOT_TOKEN = "7605025029:AAHIhViLBJC_aqHz1Cq3PmXM8yweliyr6IQ"
CHAT_ID = "1710925764"
PROJECT_ID = "zif5x-437508" 
LOCATION = "us-central1" 
vertexai.init(project=PROJECT_ID, location=LOCATION)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'emerald-bastion-433109-e0-fb7a9d5222ab.json'
SCOPES = ["https://www.googleapis.com/auth/calendar"]
app = FastAPI()

# Function to authenticate Google Calendar
def authenticate_user():
    flow = InstalledAppFlow.from_client_secrets_file("oauth-credentials.json", SCOPES)
    creds = flow.run_local_server(port=8080)
    return creds

# Fetch unread Telegram messages
def check_messages():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    response = requests.get(url).json()
    messages = [update["message"]["text"] for update in response.get("result", [])]
    return {"unread_messages": messages}

# Send a message via Telegram
def send_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, json=data).json()
    return {"status": response.get("ok", False)}

# Get upcoming Google Calendar events
def get_calendar_events():
    creds = authenticate_user()
    service = build("calendar", "v3", credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + "Z"
    events_result = service.events().list(calendarId="primary", timeMin=now, maxResults=10).execute()
    events = events_result.get("items", [])
    return [event for event in events] if events else ["No upcoming events"]

# Block time in Google Calendar
def block_time(start_time: str, end_time: str, message: str = "Blocked Slot"):
    creds = authenticate_user()
    service = build("calendar", "v3", credentials=creds)
    event = {
        "summary": message,
        "start": {"dateTime": start_time, "timeZone": "Asia/Calcutta"},
        "end": {"dateTime": end_time, "timeZone": "Asia/Calcutta"},
    }
    event = service.events().insert(calendarId="primary", body=event).execute()
    return {"status": "Event created", "event_id": event.get("id")}

# Perform Google search using SerpAPI
def search_web(query: str):
    url = f"https://serpapi.com/search.json?engine=google&q={query}&api_key={SERP_API_KEY}"
    response = requests.get(url).json()
    results = [res["title"] for res in response.get("organic_results", [])]
    return {"search_results": results}

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def play_song(song_name: str):
    """
    Searches for a song on YouTube and plays the first result automatically.

    Args:
        song_name (str): The name of the song to search for.
    """
    if not song_name:
        return "Please specify a song name."

    # Set up the Selenium WebDriver (ensure ChromeDriver is installed)
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")  # Ignore SSL errors
    options.add_argument("--disable-web-security")  # Disable security settings
    options.add_argument("--allow-running-insecure-content")  # Allow insecure content
    options.add_argument("--start-maximized")  # Open in full-screen
    driver = webdriver.Chrome(options=options)

    try:
        # Open YouTube search page
        driver.get("https://www.youtube.com/")
        
        # Wait for the page to load
        time.sleep(3)

        # Find the search bar, type the song name, and hit Enter
        search_box = driver.find_element(By.NAME, "search_query")
        search_box.send_keys(song_name + " song")
        search_box.send_keys(Keys.RETURN)

        # Wait for results to load
        time.sleep(3)

        # Click on the first video
        first_video = driver.find_element(By.XPATH, '(//a[@id="video-title"])[1]')
        first_video.click()

        return f"Playing '{song_name}' on YouTube..."
    
    except Exception as e:
        return f"Error: {str(e)}"
    
# Example usage:
# play_song("Shape of You")

# 🔹 Pass Functions as Tools to Gemini
check_messages_del=FunctionDeclaration(
    name="check_messages",
    description="check messages on my telegram",
    parameters={
        'type':'object',
        'properties':None
    }
)

send_message_del=FunctionDeclaration(
    name='send_message',
    description="send message to me on my telegram",
    parameters={
        "type":"object",
        "properties": {
            "message":{
                "type":"string",
                "description":"The text that you want to send"
            }
        },
        'required':['message']
    }
)

get_calendar_events_del=FunctionDeclaration(
    name='get_calendar_events',
    description='Get your upcoming planned events',
    parameters={
        "type": "object",
        "properties": {}
    }
)

block_time_del=FunctionDeclaration(
    name='block_time',
    description='create an event',
    parameters={
        'type':'object',
        'properties':{
            'start_time':{
                'type':'string',
                'description':'The start date time of your event in RFC3339 format'
            },
            'end_time':{
                'type':'string',
                'description':'The end date time of your event in RFC3339 format'
            },
            'message':{
                'type':'string',
                'description':'The description of your event'
            }
        },
        'required':['start_time','end_time']
    }
)

search_web_del=FunctionDeclaration(
    name='search_web',
    description='Use it for retriving real time data like stock price,latest new,google search',
    parameters={
        "type":"object",
        "properties": {
            "query":{
                "type":"string",
                "description":"realtime query for which you need a response"
            }
        },
        'required':['query']
    }
)

play_song_del=FunctionDeclaration(
    name="play_song",
    description="Plays the requested song",
    parameters={
        'type':'object',
        'properties':{
            'song_name':{
                'type':'string',
                'description':'The name of song you want to play'
            }
        },
        'required':['song_name']
    }
)

CallableFunctions = {
    "search_web": search_web,
    "send_message": send_message,
    "check_messages":check_messages,
    "get_calendar_events":get_calendar_events,
    "block_time":block_time,
    'play_song':play_song
}

generation_config = {
    "max_output_tokens": 128,
    "temperature": 0.5,
    "top_p": 0.3,
}
tools = Tool(function_declarations=[check_messages_del,search_web_del,send_message_del,block_time_del,get_calendar_events_del,play_song_del])
model = GenerativeModel(model_name = 'gemini-1.5-pro', generation_config = generation_config, tools = [tools])

today = datetime.date.today()

def mission_prompt(prompt:str):
    return f"""
    I am helpfull assistant
    Thought: I need to understand the user's request and determine if I need to use any tools to assist them.
    Action: 
    - When processing the date specify month and date (not year)
    - For sharing any information/file with me use telegram (by default)
    - Already tools are provided for various automation task like block time or send message on telegram call them appropriately.
    - Call the tools with proper parameters if you need any extra information ask.
    - For web/google search use search_web tool,while sharing the result on telegram send the top web search result as well 
    - Respond with the final answer only.
    [QUESTION] 
    {prompt}
    [DATETIME]
    {today}
    """.strip()

# 🔹 Process Command & Call Function
def process_command(command):
    prompt = mission_prompt(command)
    chat = model.start_chat(response_validation=False)
    response1 = chat.send_message("Hello")
    response = chat.send_message(prompt)
    tools = response.candidates[0].function_calls
    while tools:
        for tool in tools:
            print(tool)
            # **(tool.args or {})
            function_res = CallableFunctions[tool.name](**(tool.args))
            response = chat.send_message(Content(role="function_response",parts=[Part.from_function_response(name=tool.name, response={"result": function_res})]))
            print('Function res')
            print(function_res)
        tools = response.candidates[0].function_calls
    speak_response(response.text)
    return response.text


# Initialize ElevenLabs Client
def speak_response(text):
    from playsound import playsound
    import pygame
    api_key = ELEVENLABS_API_KEY
    client = ElevenLabs(api_key=api_key)
    pygame.mixer.quit()
    output_file='output.mp3'
    # Check if the file exists and delete it safely
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
        except PermissionError:
            print(f"Could not delete {output_file}. It may be in use.")

    # Convert text to speech
    audio = client.text_to_speech.convert(
        text=text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    # Save the audio file
    with open(output_file, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    print(f"Audio saved as {output_file}")

    # Play the audio using pygame
    pygame.mixer.init()
    pygame.mixer.music.load(output_file)
    pygame.mixer.music.play()

    # Wait for audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Stop and release the file after playing
    pygame.mixer.music.stop()
    pygame.mixer.quit()

stt = SpeechToText()
speech_thread = None
transcribed_text = ""
import threading

@app.get("/start-speech", response_class=JSONResponse)
async def start_speech():
    global speech_thread, transcribed_text
    print("\n[DEBUG] Received speech start request.")

    # **Ensure previous session is stopped properly**
    if speech_thread and speech_thread.is_alive():
        print("[DEBUG] Previous speech thread is running, stopping it...")
        stt.stop_signal = True
        speech_thread.join()  # Ensure previous thread has stopped
        print("[DEBUG] Previous thread stopped.")

    # **Reset the transcription state**
    stt.final_transcript = "" 
    stt.stop_signal = False
    stt.last_speech_time = time.time()  # Reset silence detection
    transcribed_text = ""

    # **Start a new thread for speech recognition**
    def run_stt():
        print("[DEBUG] Starting new speech recognition thread.")
        stt.final_transcript = stt.stream_audio()
        print(f"[DEBUG] Final Transcript: {stt.final_transcript}")

    speech_thread = threading.Thread(target=run_stt)
    speech_thread.start()
    speech_thread.join()
    final_transcript=stt.final_transcript.strip()
    res=process_command(final_transcript)
    return {"message": "Speech-to-text completed", "transcription": res}

"""
@app.get("/stop-speech", response_class=JSONResponse)
async def stop_speech():
    global speech_thread, transcribed_text
    stt.stop_signal = True
    if speech_thread:
        speech_thread.join()
    transcribed_text = stt.final_transcript.strip()
    res=process_command(transcribed_text)
    speak_response(res)
    return {"message": "Speech-to-text stopped", "transcription": "Submitting your request"}
"""
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
