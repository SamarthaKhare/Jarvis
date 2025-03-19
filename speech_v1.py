
import threading
import time
import pyaudio
from google.cloud import speech
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms per frame
STOP_KEY = "Enter"
SILENCE_TIMEOUT = 10  # Stop if silent for 10 seconds

class SpeechToText:
    
    def __init__(self):
        self.stop_signal = False
        self.final_transcript = ""
        self.speech_detected = False  # Track if speech has started
        self.last_speech_time = None  # Start tracking only after speech

    def audio_generator(self, stream):
        """Yields audio chunks from the microphone."""
        while not self.stop_signal:
            chunk = stream.read(CHUNK)
            yield chunk

            # Start tracking silence only after speech is detected
            if self.speech_detected and self.last_speech_time:
                if time.time() - self.last_speech_time > SILENCE_TIMEOUT:
                    print("Silence detected, stopping...")
                    self.stop_signal = True

    def listen_for_stop(self):
        """Listens for user input to manually stop transcription."""
        input(f"Press {STOP_KEY} when done speaking...\n")
        self.stop_signal = True

    def stream_audio(self):
        """Captures audio from the microphone and transcribes it in real-time."""
        client = speech.SpeechClient()

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code="en-US",
            model="default",
            use_enhanced=True
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True,
        )

        audio_interface = pyaudio.PyAudio()
        
        try:
            stream = audio_interface.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
            )
            print("Listening... Speak now!")

            stop_thread = threading.Thread(target=self.listen_for_stop)
            stop_thread.start()

            requests = (speech.StreamingRecognizeRequest(audio_content=chunk)
                        for chunk in self.audio_generator(stream))
            responses = client.streaming_recognize(config=streaming_config, requests=requests)

            for response in responses:
                for result in response.results:
                    if result.is_final:
                        self.final_transcript += result.alternatives[0].transcript + " "
                        print(f"Final Transcript: {self.final_transcript.strip()}")

                        # Mark speech detected and reset silence timer
                        if not self.speech_detected:
                            self.speech_detected = True
                        self.last_speech_time = time.time()
                    else:
                        print(f"Interim Transcript: {result.alternatives[0].transcript}", end="\r")

                if self.stop_signal:
                    break

        finally:
            stream.stop_stream()
            stream.close()
            audio_interface.terminate()

        return self.final_transcript.strip()  # Return final transcript after stopping