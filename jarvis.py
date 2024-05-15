import os
from dotenv import load_dotenv
import speech_recognition as sr
import whisper
from tempfile import NamedTemporaryFile
import time
import assist

load_dotenv()

def main():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 1000
    recognizer.dynamic_energy_threshold = False

    device_index = int(os.getenv('DEVICE_INDEX', '1'))
    audio_model = whisper.load_model("tiny.en")

    microphone = sr.Microphone(device_index=device_index)
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)

    def callback(recognizer, audio):
        try:
            with NamedTemporaryFile(delete=True) as temp_file:
                temp_file.write(audio.get_wav_data())
                temp_file.seek(0)
                result = audio_model.transcribe(temp_file.name)
                handle_transcription(result['text'])
        except Exception as e:
            print(f"Error processing audio: {e}")

    stop_listening = recognizer.listen_in_background(microphone, callback)

    print("Listening... Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping...")
        stop_listening(wait_for_stop=False)

def handle_transcription(text):
    print(f"Transcribed: {text}")
    if "jarvis" in text.lower():
        response = assist.ask_question_memory(text)
        print(f"Response: {response}")
        if response:
            assist.TTS(response)

if __name__ == "__main__":
    main()
