import pyaudio

audio = pyaudio.PyAudio()

print(f"Found {audio.get_device_count()} devices\n")

for i in range(audio.get_device_count()):
    info = audio.get_device_info_by_index(i)
    print(f"Device {i}")
    print(f"  Name: {info['name']}")
    print(f"  Max input channels: {info['maxInputChannels']}")
    print(f"  Max output channels: {info['maxOutputChannels']}")
    print(f"  Default sample rate: {info['defaultSampleRate']}")
    print()

audio.terminate()