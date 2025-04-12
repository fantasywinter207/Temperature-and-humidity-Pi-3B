#!/usr/bin/env python3
import os
import json
import pyaudio
import pyttsx3
from vosk import Model, KaldiRecognizer
from datetime import datetime
import threading
import time
import requests

# Server configuration
SERVER_URL = "http://localhost:5000/data"

class VoiceAssistant:
    def __init__(self):
        # Verify model path
        self.model_path = "vosk-model-small-en-us-0.15"
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Vosk model not found, please download and place in program directory: {self.model_path}")

        # Initialize speech recognition
        self.model = Model(self.model_path)

        # Initialize audio
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.sample_rate = 16000  # Preferred sample rate
        self.frames_per_buffer = 8000

        # Initialize speech synthesis
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0)

        # System status
        self.running = True
        self.timerRunning = True
        self.wake_word = "computer"
        self.timer = None

    def print_audio_devices(self):
        """Print available audio input devices"""
        print("\nAvailable audio input devices:")
        for i in range(self.audio.get_device_count()):
            dev = self.audio.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                print(f"{i}: {dev['name']}")
                print(f"  Default sample rate: {dev['defaultSampleRate']}Hz")
                print(f"  Max input channels: {dev['maxInputChannels']}")

    def find_compatible_device(self):
        """Find compatible audio input device"""
        for i in range(self.audio.get_device_count()):
            dev = self.audio.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                try:
                    if self.audio.is_format_supported(
                        self.sample_rate,
                        input_device=i,
                        input_channels=1,
                        input_format=pyaudio.paInt16
                    ):
                        print(f"\nFound compatible device: {dev['name']} (supports {self.sample_rate}Hz)")
                        return i
                except:
                    continue

        # If preferred sample rate not supported, try common rates
        test_rates = [8000, 44100, 48000]
        for rate in test_rates:
            for i in range(self.audio.get_device_count()):
                dev = self.audio.get_device_info_by_index(i)
                if dev['maxInputChannels'] > 0:
                    try:
                        if self.audio.is_format_supported(
                            rate,
                            input_device=i,
                            input_channels=1,
                            input_format=pyaudio.paInt16
                        ):
                            print(f"\nFound fallback device: {dev['name']} (using {rate}Hz)")
                            self.sample_rate = rate
                            return i
                    except:
                        continue
        return None

    def setup_audio_stream(self):
        """Set up audio input stream"""
        self.print_audio_devices()
        input_device_index = self.find_compatible_device()

        if input_device_index is None:
            raise Exception("No compatible audio input device found")

        # Reinitialize recognizer to match actual sample rate
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)

        print(f"\nUsing parameters:")
        print(f"  Device index: {input_device_index}")
        print(f"  Sample rate: {self.sample_rate}Hz")
        print(f"  Frames per buffer: {self.frames_per_buffer}")

        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=input_device_index,
                frames_per_buffer=self.frames_per_buffer,
                start=False
            )
            return True
        except Exception as e:
            print(f"Audio stream setup failed: {e}")
            return False

    def monitoring_threshold(self):
        self.min_temperature_value = 10
        self.max_temperature_value = 40
        self.min_humidity_value = 20
        self.max_humidity_value = 95
        self.monitoring_threshold_running = True
        while (self.monitoring_threshold_running):
            temp, humi = self.get_temperature_and_humidity_data()
            if temp is not None and humi is not None:
                if temp <= self.min_temperature_value:
                    self.speak(f"Warning: The current temperature is low, please keep warm! Current temperature is {temp}°C")
                if humi <= self.min_humidity_value:
                    self.speak(f"Warning: The current humidity is low, please pay attention to moisturizing! Current humidity is {humi}%")
                if temp >= self.max_temperature_value:
                    self.speak(f"Warning: The current temperature is high, please keep cool! Current temperature is {temp}°C")
                if humi >= self.max_humidity_value:
                    self.speak(f"Warning: The current humidity is high, please pay attention to ventilation! Current humidity is {humi}%")
            time.sleep(10)

    def process_audio(self):
        """Process audio data"""
        print("\nSystem ready, please say the wake word 'computer'...")
        self.stream.start_stream()
        threading.Thread(target=self.monitoring_threshold).start()
        try:
            while self.running:
                data = self.stream.read(4000, exception_on_overflow=False)
                if len(data) == 0:
                    continue
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        print(f"\nRecognized: {text}")
                        self.process_command(text)
                        text = ""
                
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.stream.stop_stream()

    def get_temperature_and_humidity_data(self):
        """Get temperature and humidity data"""
        try:
            response = requests.get(SERVER_URL, params=None, timeout=2)
            data = response.json()[-1]
            temp = data.get('temperature')
            humi = data.get('humidity')
            return temp, humi
        except requests.exceptions.ConnectionError:
            self.speak("Warning: Unable to connect to server, displaying data only on OLED")
        except requests.exceptions.Timeout:
            self.speak("Warning: Server connection timed out, displaying data only on OLED")
        except FileNotFoundError:
            self.speak("Sensor data file not found")
        except json.JSONDecodeError:
            self.speak("Error decoding sensor data file")

    def stop_method(self, seconds):
        def stop_method():
            self.timerRunning = False
            self.speak("I'm going to step down now")
        self.timerRunning = True
        self.timer = threading.Timer(seconds, stop_method)
        self.timer.start()
    
    def execute_method_for_n_seconds(self, method, seconds):
        self.timerRunning = True
        self.stop_method(seconds)
        method_thread = threading.Thread(target=method)
        method_thread.start()

    def reset_time_and_resume(self, new_seconds):
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
        self.timerRunning = True
        self.stop_method(new_seconds)

    def handle_speak(self):
        while(self.timerRunning):
            text_lower = self.text_lower
            if "temperature" in text_lower or "humidity" in text_lower:
                temp, humi = self.get_temperature_and_humidity_data()
                if temp is not None and humi is not None:
                    self.speak(f"Current temperature is {temp}°C, humidity is {humi}%")
                else:
                    self.speak("Failed to read sensor data")
                self.reset_time_and_resume(30)
                time.sleep(5)
            elif "time" in text_lower:
                self.speak(f"The current time is {datetime.now().strftime('%H:%M')}")
                self.reset_time_and_resume(30)
                time.sleep(3)
            elif "exit" in text_lower or "quit" in text_lower:
                self.speak("Goodbye!")
                self.running = False
            self.text_lower = ""

    def process_command(self, text):
        """Process recognized command"""
        self.text_lower = text.lower()

        if self.wake_word.lower() in text:
            self.speak("How can I help you?")
            self.execute_method_for_n_seconds(self.handle_speak, 30)

    def speak(self, text):
        """Speech output"""
        print(f"Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def run(self):
        """Main execution loop"""
        try:
            if not self.setup_audio_stream():
                return

            self.process_audio()
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            if self.stream:
                self.stream.close()
            self.audio.terminate()
            print("System shutdown")

if __name__ == "__main__":
    try:
        assistant = VoiceAssistant()
        assistant.run()
    except Exception as e:
        print(f"Startup failed: {e}")