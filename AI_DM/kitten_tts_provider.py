import threading
import queue
import numpy as np
import sounddevice as sd
from kittentts import KittenTTS

class KittenTTSProvider:
    def __init__(self, model_name="KittenML/kitten-tts-nano-0.8", voice="Bruno"):
        self.model_name = model_name
        self.voice = voice
        self.sample_rate = 24000
        self.m = KittenTTS(model_name)
        self.queue = queue.Queue()
        self.running = True
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def _worker(self):
        while self.running:
            text = self.queue.get()
            if text is None:
                break
            try:
                # Streaming generation for lower latency
                for chunk in self.m.generate_stream(text=text, voice=self.voice):
                    audio = chunk.squeeze()
                    sd.play(audio, samplerate=self.sample_rate)
                    sd.wait()
            except Exception as e:
                print(f"[KittenTTS] Error: {e}")
            finally:
                self.queue.task_done()

    def speak(self, text: str):
        self.queue.put(text)

    def wait(self):
        """Wait until all queued speech is finished."""
        self.queue.join()

    def stop(self):
        self.running = False
        self.queue.put(None)
        self.thread.join()

if __name__ == "__main__":
    # Test
    tts = KittenTTSProvider()
    tts.speak("Greetings, hero. I am your new voice.")
    import time
    time.sleep(5)
    tts.stop()
