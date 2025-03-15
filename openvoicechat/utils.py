import multiprocessing
import os
import queue
import random
import threading
import time
import librosa
import numpy as np
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

TIMING = int(os.environ.get("TIMING", 0))
LOGGING = int(os.environ.get("LOGGING", 0))

timing_path = os.environ.get("TIMING_PATH", "times.csv")


def log_to_file(file_path, text):
    with open(file_path, "a") as file:
        file.write(text + "\n")


def run_chat(
    mouth,
    ear,
    chatbot,
    minibot_args=None,
    verbose=True,
    stopping_criteria=lambda x: False,
    starting_message=True,
    logging_path="chat_log.txt",
):
    """
    Runs a chat session between a user and a bot.

    Parameters: mouth (object): An object responsible for the bot's speech output. ear (object): An object
    responsible for listening to the user's input. chatbot (object): An object responsible for generating the bot's
    responses. verbose (bool, optional): If True, prints the user's input and the bot's responses. Defaults to True.
    stopping_criteria (function, optional): A function that determines when the chat should stop. It takes the bot's
    response as input and returns a boolean. Defaults to a function that always returns False.

    The function works by continuously listening to the user's input and generating the bot's responses in separate
    threads. If the user interrupts the bot's speech, the remaining part of the bot's response is saved and prepended
    to the user's next input. The chat stops when the stopping_criteria function returns True for a bot's response.
    """
    if TIMING:
        pd.DataFrame(columns=["Model", "Time Taken"]).to_csv(timing_path, index=False)

    if starting_message:
        agent_name = minibot_args.get("agent_name")
        organization_name = minibot_args.get("organization_name")
        initial_message = random.choice(
            [
                f"Hello, I am {agent_name} from {organization_name}. How can I help you?",
                f"Hello! This is {agent_name} from {organization_name}. How can I be of assistance?",
                f"Hi! This is {organization_name}'s representative {agent_name}. What can I do for you?",
                f"Hi! You're speaking with {agent_name} from {organization_name}. What can I do for you?",
                f"Hey, there! You're speaking with {agent_name} from {organization_name}. How can I assist you?",
            ]
        )
        mouth.say_text(initial_message)

    pre_interruption_text = ""
    while True:
        user_input = pre_interruption_text + " " + ear.listen()

        if verbose:
            print("USER: ", user_input)
        if LOGGING:
            log_to_file(logging_path, "USER: " + user_input)

        llm_output_queue = queue.Queue()
        interrupt_queue = queue.Queue()
        llm_thread = threading.Thread(
            target=chatbot.generate_response_stream,
            args=(user_input, llm_output_queue, interrupt_queue, minibot_args),
        )
        tts_thread = threading.Thread(
            target=mouth.say_multiple_stream,
            args=(llm_output_queue, ear.interrupt_listen, interrupt_queue),
        )

        llm_thread.start()
        tts_thread.start()

        llm_thread.join()
        tts_thread.join()
        if not interrupt_queue.empty():
            pre_interruption_text = interrupt_queue.get()
        else:
            pre_interruption_text = ""

        res = llm_output_queue.get()
        if stopping_criteria(res):
            break
        if verbose:
            print("BOT: ", res)
        if LOGGING:
            log_to_file(logging_path, "BOT: " + res)


class Player_ws:
    def __init__(self, q):
        self.output_queue = q
        self.playing = False
        self._timer_thread = None
        self.interrupted = False

    def play(self, audio_array, samplerate):
        self.playing = True
        self.interrupted = False
        duration = len(audio_array) / samplerate
        if audio_array.dtype == np.int16:
            audio_array = audio_array / (1 << 15)
        audio_array = audio_array.astype(np.float32)
        audio_array = librosa.resample(
            y=audio_array, orig_sr=samplerate, target_sr=44100
        )
        audio_array = audio_array.tobytes()
        
        if not self.interrupted:
            self.output_queue.put(audio_array)
            
        if self._timer_thread is not None:
            if self._timer_thread.is_alive():
                self._timer_thread.terminate()
        self._timer_thread = multiprocessing.Process(
            target=time.sleep, args=(duration,)
        )
        self._timer_thread.start()

    def stop(self):
        self.playing = False
        self.interrupted = True
        self.output_queue.queue.clear()
        self.output_queue.put("stop".encode())
        if self._timer_thread and self._timer_thread.is_alive():
            self._timer_thread.terminate()

    def wait(self):
        if self._timer_thread:
            self._timer_thread.join()
        self.playing = False

        
class Listener_ws:
    def __init__(self, q):
        self.input_queue = q
        self.listening = False
        self.CHUNK = 5945
        self.RATE = 16_000

    def read(self, x):
        data = self.input_queue.get()
        data = np.frombuffer(data, dtype=np.float32)
        data = librosa.resample(y=data, orig_sr=44100, target_sr=16_000)
        data = data * (1 << 15)
        data = data.astype(np.int16)
        data = data.tobytes()
        return data

    def close(self):
        pass

    def make_stream(self):
        self.listening = True
        self.input_queue.queue.clear()
        return self
