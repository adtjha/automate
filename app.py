from flask import Flask, render_template, request
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/audio', methods=['POST'])
def audio():
    audio_data = request.files.get('audio').read()
    print('Received audio data')

    # Create a temporary file to write the audio data to
    with open('audio.mp3', 'wb') as f:
        f.write(audio_data)

    # Transcribe the audio using the OpenAI API client
    with open('audio.mp3', 'rb') as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

    # Clean up the temporary file
    os.remove('audio.mp3')

    return transcript

if __name__ == '__main__':
    app.run(debug=True)
