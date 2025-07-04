import numpy as np
import pyaudio

CHUNK = int(1024 * 2)
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000


def make_stream():
    p = pyaudio.PyAudio()
    return p.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
    )


def record_interruption_parallel(vad, listen_queue):
    frames = []
    stream = make_stream()
    while True:
        a = listen_queue.get()
        if a is None:
            break
        data = stream.read(CHUNK)
        frames.append(data)
        contains_speech = vad.contains_speech(frames[int(RATE / CHUNK) * -2 :])
        if contains_speech:
            stream.close()
            frames = np.frombuffer(b"".join(frames), dtype=np.int16)
            frames = frames / (1 << 15)
            return frames.astype(np.float32)
    stream.close()
    return None


def record_interruption(vad, record_seconds=100, streamer=None):
    print("*Recording for Interruption...")
    frames = []
    if streamer is None:
        stream = make_stream()
        global CHUNK
        global RATE
    else:
        stream = streamer.make_stream()
        CHUNK = streamer.CHUNK
        RATE = streamer.RATE

    for _ in range(0, int(RATE / CHUNK * record_seconds)):
        data = stream.read(CHUNK)
        assert len(data) == CHUNK * 2, "Chunk size does not match 2 bytes per sample."
        frames.append(data)
        contains_speech = vad.contains_speech(frames[int(RATE / CHUNK) * -2 :])
        if contains_speech:
            stream.close()
            frames = np.frombuffer(b"".join(frames), dtype=np.int16)
            frames = frames / (1 << 15)
            return frames.astype(np.float32)
    stream.close()
    return None


def record_user(silence_seconds, vad, streamer=None, started=False):
    frames = []

    if streamer is None:
        stream = make_stream()
        global CHUNK
        global RATE
    else:
        stream = streamer.make_stream()
        CHUNK = streamer.CHUNK
        RATE = streamer.RATE
    one_second_iters = int(RATE / CHUNK)
    print("*Recording...")

    while True:
        data = stream.read(CHUNK)
        assert len(data) == CHUNK * 2, "Chunk size does not match 2 bytes per sample."
        frames.append(data)
        if len(frames) < one_second_iters * silence_seconds:
            continue
        contains_speech = vad.contains_speech(
            frames[int(-one_second_iters * silence_seconds) :]
        )
        if not started and contains_speech:
            started = True
            print("*Listening to Speech...")
        if started and contains_speech is False:
            break
    stream.close()

    print("*Done Recording.")

    frames = np.frombuffer(
        b"".join(frames), dtype=np.int16
    )  # Creating a np array from buffer

    # Normalization: https://discuss.pytorch.org/t/torchaudio-load-normalization-question/71470
    frames = frames / (1 << 15)

    return frames.astype(np.float32)


def record_user_stream(silence_seconds, vad, audio_queue, streamer=None, player=None):
    frames = []
    started = False
    if streamer is None:
        stream = make_stream()
        global CHUNK
        global RATE
    else:
        stream = streamer.make_stream()
        CHUNK = streamer.CHUNK
        RATE = streamer.RATE
    
    one_second_iters = int(RATE / CHUNK)
    print("*Recording...")
    
    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        audio_queue.put(data)
        
        contains_speech = vad.contains_speech(
            frames[int(-one_second_iters * silence_seconds) :]
        )
        
        if not started and contains_speech:
            started = True
            print("*Listening to Speech...")
            # Add None check before calling stop()
            if player is not None:
                player.stop()
        
        if started and contains_speech is False:
            break
    
    audio_queue.put(None)
    stream.close()
    print("*Done Recording.")