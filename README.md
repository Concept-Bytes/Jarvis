# Jarvis
This Python script, jarvis.py, emulates a conversational AI assistant similar to Jarvis from Iron Man. It utilizes OpenAI's Whisper V3 for accurate speech recognition, GPT-3.5 Turbo for intelligent and context-aware response generation, and OpenAI's TTS (Text-to-Speech) to verbalize responses.

# Features
Real-Time Speech Recognition: Leveraging Whisper V3 to convert spoken language into text.
Intelligent Response Generation: Uses GPT-3.5 Turbo to generate relevant responses based on the user's input.
Speech Output: Converts text responses back into speech using OpenAI's TTS, providing a seamless conversational experience.
Hotword Detection: The script actively listens for specific trigger words to initiate interaction.

# Requirements
Python 3.9+
OpenAI's Whisper, GPT, and TTS models
SpeechRecognition library
PyTorch

## Installation
Ensure Python and the necessary libraries are installed:
```
pip install openai speechrecognition torch
```

Go to https://platform.openai.com/assistants to set up your assistant to get
-assistant id
-thread id

## Usage
Set Up Your Microphone: Ensure your microphone is set up and configured as the default recording device.
Run the Script: Start the script using the command:
```
python jarvis.py
```
Speak to Jarvis: Begin speaking to the system. Use the hotwords like "Hey Jarvis" to initiate commands. Note it may take some time to load the model.

## Command Line Arguments
--model: Specify the Whisper model size (default: tiny). Options are tiny, base, small, medium, large.
--non_english: Use a non-English model if required.
--energy_threshold: Set the microphone energy threshold for detecting speech.
--record_timeout: Duration in seconds for how real-time the recording is.
--phrase_timeout: Duration in seconds for the silence interval to detect the end of a phrase.

## Configuration
Modify the script's hot_words list to customize the trigger words according to your preference.
Tweak the energy_threshold, record_timeout, and phrase_timeout settings to optimize speech detection based on your environment.

##Notes
Ensure that your API keys and model access privileges are correctly configured before running the script.
The quality of TTS output and the responsiveness of the assistant depend on the selected models and system performance.

## License
Distributed under the MIT License. See LICENSE for more information.

## Contact
Reach out with any feedback or support needs via GitHub or email.
