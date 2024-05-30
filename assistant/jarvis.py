#! python3.7
import io
import speech_recognition as sr
import whisper
import torch
import assist
import tools
from db import init_db
from datetime import datetime, timedelta
from queue import Queue
from tempfile import NamedTemporaryFile
import time
import asyncio

async def main():
    await tools.init_smart_plug()
    init_db()
    
    # The last time a recording was retrieved from the queue.
    phrase_time = None
    # Current raw audio bytes.
    last_sample = bytes()
    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = 3000
    # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = False
    
    # Set the mic source
    source = sr.Microphone(sample_rate=16000, device_index=1)

    audio_model = whisper.load_model("tiny.en")
    print("Model loaded.\n")
    
    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio:sr.AudioData) -> None:
        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        # Grab the raw bytes and push it into the thread safe queue.
        data = audio.get_raw_data()
        data_queue.put(data)

    # How real time the recording is in seconds.
    record_timeout = 15
    # How much empty space between recordings before we consider it a new line in the transcription.
    phrase_timeout = 3
    # Create a background thread that will pass us raw audio bytes.
    # This enables the microphone to listen, comes from SpeechRecognizer package
    def is_listening(is_speaking):
        global start_listening
        if not is_speaking:
            start_listening = recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)
        else:
            start_listening(wait_for_stop=False)

    temp_file = NamedTemporaryFile().name
    transcription = ['']
    
    # Cue the user that we're ready to go.
    print("main loop starting")
    is_listening(False)
    
    # Define cues to initiate AI assitant listening
    hot_words = ["jarvis"]
    # Define cues to keep AI assistant listening
    convo_words = ["?"]
    tts_enabled = True
    continue_listening = False

    while True:
        now = datetime.utcnow()
        # Pull raw recorded audio from the queue.
        if not data_queue.empty():
            phrase_complete = False
            # If enough time has passed between recordings, consider the phrase complete.
            # Clear the current working audio buffer to start over with the new data.
            if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                last_sample = bytes()
                phrase_complete = True
            # This is the last time we received new audio data from the queue.
            phrase_time = now

            # Concatenate our current audio data with the latest audio data.
            while not data_queue.empty():
                data = data_queue.get()
                last_sample += data

            # Use AudioData to convert the raw data to wav data.
            audio_data = sr.AudioData(last_sample, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
            wav_data = io.BytesIO(audio_data.get_wav_data())

            # Write wav data to the temporary file as bytes.
            with open(temp_file, 'w+b') as f:
                f.write(wav_data.read())

            # Read the transcription.
            result = audio_model.transcribe(temp_file, fp16=torch.cuda.is_available())
            text = result['text'].strip()

            # If we detected a pause between recordings, add a new item to our transcription.
            # Otherwise edit the existing one.
            if phrase_complete:
                transcription.append(text)
                
                # Check if line contains any words from hot_words
                print("checking")
                if any(hot_word in text.lower() for hot_word in hot_words) or continue_listening:
                    # Make sure text is not empty
                    if text:
                        print("User: " + text)
                        print("ASKING AI")
                        response = assist.ask_question_memory(text)
                        print("AI: " + response)
                        if any(convo_word in response for convo_word in convo_words):
                            continue_listening = True
                            print("AI asked a question, continue listening")
                        else:
                            continue_listening = False
                        speech = response.split("#")[0]
                        # Check if there is a command
                        if len(response.split("#")) > 1:
                            command = response.split("#")[1]
                            await tools.parse_command(command)
                        # This enables the response from the assistant to be spoken aloud
                        if tts_enabled:
                            is_listening(True)
                            done = assist.TTS(speech)
                            print(done)
                            is_listening(False)
                
                else:
                    print("Listening...")
            else:
                transcription[-1] = text
            print('', end='', flush=True)

            # Infinite loops are bad for processors, must sleep.
            await asyncio.sleep(0.25)