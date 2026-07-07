import os
import wave
from PIL import Image

def generate_wav_dummies():
    audio_dir = os.path.join('assets', 'audio')
    os.makedirs(audio_dir, exist_ok=True)
    
    # Generate empty .wav files for digits 0-9
    for i in range(10):
        filepath = os.path.join(audio_dir, f'{i}.wav')
        with wave.open(filepath, 'wb') as wav_file:
            # Configure basic parameters for an empty WAV file
            wav_file.setnchannels(1) # Mono
            wav_file.setsampwidth(2) # 2 bytes per sample
            wav_file.setframerate(44100) # 44.1kHz
            # No frames to write
            
    print(f"Generated 10 dummy .wav files in {audio_dir}")

def generate_img_dummy():
    img_dir = os.path.join('assets', 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    filepath = os.path.join(img_dir, 'dummy_estimulo.png')
    # Create a 400x400 solid blue image
    img = Image.new('RGB', (400, 400), color=(50, 100, 200))
    img.save(filepath)
    
    print(f"Generated dummy image in {filepath}")

if __name__ == '__main__':
    generate_wav_dummies()
    generate_img_dummy()
