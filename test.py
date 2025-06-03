import pyttsx3
import os

def text_to_speech(text, output_file):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Adjust the speech rate if needed
    engine.setProperty('voice', 'english-us+f3')  # Using Miku's voice
    engine.save_to_file(text, output_file)
    engine.runAndWait()

if __name__ == "__main__":
    text = input("Enter the text you want to convert to Hatsune Miku voice: ")
    output_file = input("Enter the name of the output file (without extension): ") + ".wav"
    text_to_speech(text, output_file)
    print(f"Text converted to Hatsune Miku voice and saved as {output_file}")
