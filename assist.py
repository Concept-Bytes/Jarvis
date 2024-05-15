from openai import OpenAI
import time
from pathlib import Path
from pygame import mixer
import time
import os
from db import insert_conversation
from dotenv import find_dotenv, load_dotenv, set_key

# Load .env file
dotenv_path = find_dotenv()
if not dotenv_path:
    print("Error: .env file not found")
    exit(1)
load_dotenv(dotenv_path,override=True)

# Access the API key
OpenAI.api_key = os.getenv("OPENAI_API_KEY")
openai_assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
openai_thread_id = os.getenv("OPENAI_THREAD_ID")

# Initialize the client
client = OpenAI()
mixer.init()

def create_or_update_assistant_thread(openai_assistant_id, openai_thread_id):
    global assistant
    global thread
    name = "Jarvis"
    model = "gpt-3.5-turbo-0125"
    date_and_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    context = """
        You are an assistant named Jarvis like from the ironman movies. 
        You are to act like him and provide help as best you can.  
        Be funny and witty. Keep it brief and serious. 
        Be a little sassy in your responses. 
        You have a variety of smart devices to control. 
        You can control them by ending your sentence with #light1-off like this. 
        Only use commands like this if I tell you to do so. End your sentence with #lamp-1 for on and #lamp-0 for off. 
        If I tell you you have a preference, remember it. Embrace it. Make it a part of you.
        Response in less than 80 words. 
        """ + date_and_time
    if not openai_assistant_id:
        assistant = client.beta.assistants.create(
            model=model,
            name=name,
            instructions=context,
        )
        openai_assistant_id = assistant.id
        set_key(dotenv_path, "OPENAI_ASSISTANT_ID", openai_assistant_id)
        print(f"Created new assistant with ID: {openai_assistant_id}")
    else:
        assistant = client.beta.assistants.update(
            assistant_id=openai_assistant_id,
            model=model,
            name=name,
            instructions=context,
        )
        print(f"Updated existing assistant with ID: {openai_assistant_id}")
    if not openai_thread_id:
        thread = client.beta.threads.create()
        openai_thread_id = thread.id
        set_key(dotenv_path, "OPENAI_THREAD_ID", openai_thread_id)
        print(f"Created new thread with ID: {openai_thread_id}")
    else:
        thread = client.beta.threads.retrieve(
            thread_id=openai_thread_id
        )
        print(f"Using existing thread with ID: {openai_thread_id}")
    return assistant, thread

# Function for conversation with memory
def ask_question_memory(question):
    global assistant
    global thread
    global thread_message
    # Create or update the assistant and thread
    create_or_update_assistant_thread(openai_assistant_id, openai_thread_id)
    thread_message = client.beta.threads.messages.create(
        thread.id,
        role="user",
        content=question,
        )
    # Create a run for the thread using the defined assistant
    run = client.beta.threads.runs.create(
      thread_id=thread.id,
      assistant_id=assistant.id,
    )
    # Wait for the run to complete
    while True:
        run_status = client.beta.threads.runs.retrieve(
          thread_id=thread.id,
          run_id=run.id
        )
        if run_status.status == 'completed':
            break
        elif run_status.status == 'failed':
            return "The run failed."
        time.sleep(1)  # Wait for 1 second before checking again
    # Retrieve messages after the run has succeeded
    messages = client.beta.threads.messages.list(
      thread_id=thread.id
    )
    response = messages.data[0].content[0].text.value
    # Insert the conversation into the database
    insert_conversation(question, response)
    return response

# Function to ask a question to the assistant with an image
def play_sound(file_path):
    mixer.music.load(file_path)
    mixer.music.play()
    
# Function to generate TTS for each sentence and play them
def TTS(text):
    speech_file_path = Path(f"speech.mp3")
    speech_file_path = generate_tts(text, speech_file_path)
    play_sound(speech_file_path)
    while mixer.music.get_busy():  # Wait for the mixer to finish
        time.sleep(1)
    mixer.music.unload()
    # Delete the file after playing
    os.remove(speech_file_path)

    return "done"
            
# Function to generate TTS and return the file path
def generate_tts(sentence, speech_file_path):
    
    response = client.audio.speech.create(
        model="tts-1",
        voice="echo",
        input=sentence,
    )
    response.stream_to_file(speech_file_path)
    return str(speech_file_path)
