# import asyncio
# import json
# import websockets
# import speech_recognition as sr
# import pyttsx3
# from openai import OpenAI
# import os
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()
# client = OpenAI()

# # OpenAI API Key
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# if not OPENAI_API_KEY:
#     print('Missing OpenAI API key. Please set it in the .env file.')
#     exit(1)

# OpenAI.api_key = OPENAI_API_KEY

# # Initialize text-to-speech engine
# engine = pyttsx3.init()
# engine.setProperty('rate', 150)  # Speed of speech
# engine.setProperty('voice', 'english')  # Set voice property

# # System message and constants
# SYSTEM_MESSAGE = "You are a helpful and bubbly AI assistant..."
# VOICE = "alloy"
# PORT = 5000

# # Initialize speech recognizer
# recognizer = sr.Recognizer()

# # Function to convert speech to text
# def recognize_speech():
#     with sr.Microphone() as source:
#         print("Listening for input...")
#         audio = recognizer.listen(source)
#         try:
#             return recognizer.recognize_google(audio)
#         except sr.UnknownValueError:
#             print("Could not understand audio")
#             return None

# # Function to synthesize speech from text
# def speak_text(text):
#     engine.say(text)
#     engine.runAndWait()

# # WebSocket handler
# async def handler(websocket, path):
#     print("Client connected")

#     async def openai_stream():
#         # Function to send OpenAI response live
#         openai_ws = await websockets.connect(
#             'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
#             extra_headers={
#                 'Authorization': f'Bearer {OPENAI_API_KEY}',
#                 'OpenAI-Beta': 'realtime=v1'
#             }
#         )
#         session_update = {
#             "type": "session.update",
#             "session": {
#                 "turn_detection": {"type": "server_vad"},
#                 "input_audio_format": "g711_ulaw",
#                 "output_audio_format": "g711_ulaw",
#                 "voice": "Echo",  # This will be specific to OpenAI's voice option
#                 "instructions": SYSTEM_MESSAGE,
#                 "modalities": ["text", "audio"],
#                 "temperature": 0.8,
#             }
#         }

#         await openai_ws.send(json.dumps(session_update))

#         while True:
#             try:
#                 message = await openai_ws.recv()
#                 response = json.loads(message)

#                 if response.get('type') == 'response.audio.delta':
#                     audio_response = response['delta']
#                     print(f"Received audio response: {audio_response}")
#                     await websocket.send(audio_response)  # Send live response

#             except websockets.ConnectionClosed:
#                 print("Connection to OpenAI closed")
#                 break

#         await openai_ws.close()

#     # Start OpenAI live response
#     asyncio.create_task(openai_stream())

#     while True:
#         # Receive audio or text from client (here, speech input is simulated)
#         user_speech = recognize_speech()
#         if user_speech:
#             print(f"Recognized speech: {user_speech}")
#             # Send the recognized speech to OpenAI
#             await websocket.send(user_speech)
#             response = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                  messages=[
#                         {"role": "system", "content": "You are a helpful assistant."},
#                         {
#                             "role": "user",
#                             "content": user_speech
#                         }
#                 ]
#                 )

#             ai_response = response.choices[0].message.content
#             print(ai_response)
#             # print(f"OpenAI response: {ai_response}")
#             speak_text(ai_response)

# # Start the WebSocket server
# start_server = websockets.serve(handler, "localhost", PORT)

# print(f"Server running on ws://localhost:{PORT}")
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()
import asyncio
import json
import websockets
import speech_recognition as sr
from gtts import gTTS
import os
from dotenv import load_dotenv
import tempfile
import playsound
from openai import OpenAI
# Load environment variables from .env file
load_dotenv()
client = OpenAI()
# OpenAI API Key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    print('Missing OpenAI API key. Please set it in the .env file.')
    exit(1)

# System message and constants
SYSTEM_MESSAGE = "You are a helpful and bubbly AI assistant..."
PORT = 5000

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Function to convert speech to text
def recognize_speech():
    with sr.Microphone() as source:
        print("Listening for input...")
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None

# Function to synthesize speech from text using gTTS
def speak_text(text):
    tts = gTTS(text=text, lang='en', slow=False)
    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        tts.save(f"{temp_file.name}.mp3")
        playsound.playsound(f"{temp_file.name}.mp3")

# WebSocket handler
async def handler(websocket, path):
    print("Client connected")

    async def openai_stream():
        # Function to send OpenAI response live
        openai_ws = await websockets.connect(
            'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
            extra_headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'OpenAI-Beta': 'realtime=v1'
            }
        )
        session_update = {
            "type": "session.update",
            "session": {
                "turn_detection": {"type": "server_vad"},
                "input_audio_format": "g711_ulaw",
                "output_audio_format": "g711_ulaw",
                "voice": "alloy",  # This will be specific to OpenAI's voice option
                "instructions": SYSTEM_MESSAGE,
                "modalities": ["text", "audio"],
                "temperature": 0.8,
            }
        }

        await openai_ws.send(json.dumps(session_update))

        while True:
            try:
                message = await openai_ws.recv()
                response = json.loads(message)

                if response.get('type') == 'response.audio.delta':
                    audio_response = response['delta']
                    print(f"Received audio response: {audio_response}")
                    await websocket.send(audio_response)  # Send live response

            except websockets.ConnectionClosed:
                print("Connection to OpenAI closed")
                break

        await openai_ws.close()

    # Start OpenAI live response
    asyncio.create_task(openai_stream())

    while True:
        # Receive audio or text from client (here, speech input is simulated)
        user_speech = recognize_speech()
        if user_speech:
            print(f"Recognized speech: {user_speech}")
            # Send the recognized speech to OpenAI
            await websocket.send(user_speech)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_MESSAGE},
                    {
                        "role": "user",
                        "content": user_speech
                    }
                ]
            )

            ai_response = response.choices[0].message.content
            print(ai_response)
            # Speak the AI response
            speak_text(ai_response)

# Start the WebSocket server
start_server = websockets.serve(handler, "localhost", PORT)

print(f"Server running on ws://localhost:{PORT}")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
