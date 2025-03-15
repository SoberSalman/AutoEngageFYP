from faster_whisper import WhisperModel
import time

model_size = "distil-large-v3"

model = WhisperModel(model_size, device="cuda", compute_type="float16")




segments, info = model.transcribe("welcome.wav", beam_size=2, language="en", condition_on_previous_text=False)

start = time.time()
segments = list(segments)  # The transcription will actually run here.
end = time.time()

print(f"Transcribed in {end - start:.2f} seconds")
print("Transcription:")
print(segments)