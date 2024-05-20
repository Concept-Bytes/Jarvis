import pyaudio

def list_audio_devices():
    pa = pyaudio.PyAudio()
    info = pa.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (pa.get_device_info_by_index(i).get('maxInputChannels')) > 0:
            print(f"Index {i}: {pa.get_device_info_by_index(i).get('name')} - Input Channels: {pa.get_device_info_by_index(i).get('maxInputChannels')}")
    pa.terminate()

list_audio_devices()