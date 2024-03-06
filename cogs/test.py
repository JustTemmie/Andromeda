import pyttsx3

# Initialize the TTS engine
engine = pyttsx3.init()

# Set Hatsune Miku's voice
# You may need to replace 'miku_voice_path' with the path to the Miku voice synthesizer
engine.setProperty('voice', miku_voice_path)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Test the TTS engine
speak("Hello, I am Hatsune Miku!")

# You can call speak() function with any text you want to be spoken in Hatsune Miku's voice
