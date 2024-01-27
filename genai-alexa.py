import json
import requests
from gtts import gTTS
import os
import speech_recognition as sr
import time

# Replace 'YOUR_OPENAI_API_KEY' with your actual OpenAI API key
openai_api_key = "OPENAI_API_KEY"
welcome_file = "genai_welcome.txt"

def run_chatbot(user_query):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_api_key}',
    }

    payload = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': 'You are a chatbot and you are going to give an answer to my query.'},   
            {'role': 'user', 'content': user_query}
        ],
        'max_tokens': 150,
    }

    try:
        response = requests.post('https://api.openai.com/v1/chat/completions', json=payload, headers=headers)      
        response.raise_for_status()

        choices = response.json().get('choices', [])

        if choices:
            answer = choices[0].get('message', {}).get('content', '').strip()
            return answer
        else:
            return 'Invalid response from OpenAI API'

    except requests.exceptions.RequestException as e:
        print(e)
        return 'Internal server error'

def text_to_speech(text):
    # Using gTTS to convert text to speech
    tts = gTTS(text, lang='en')
    tts.save('output.mp3')

    # Playing the generated audio file
    os.system('start output.mp3')

def display_welcome_message():
    print("Hi! Welcome to GenAI-Alexa.")
    print("I am your personal Alexa assistant. How may I help you today?")

def speech_to_text():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        display_welcome_message()

        while True:
            try:
                print("Say something:")
                recognizer.dynamic_energy_threshold = True
                recognizer.energy_threshold = 4000
                audio = recognizer.listen(source, timeout=5)  # Set a timeout to prevent continuous listening
                user_query = recognizer.recognize_google(audio)
                print(f"User said: {user_query}")

                if user_query.lower() == "exit":
                    break  # Exit the loop if the user says "exit"

                answer = run_chatbot(user_query)
                text_to_speech(answer)

                recognizer = sr.Recognizer()  # Reset the recognizer for a fresh start

                time.sleep(1)  # Add a delay to allow the microphone to release resources

            except sr.UnknownValueError:
                print("Sorry, I could not understand what you said.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
            except sr.WaitTimeoutError:
                pass  # Suppress the timeout error message

if __name__ == "__main__":
    speech_to_text()
