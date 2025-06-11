from flask import Flask, request, jsonify, render_template
from asr_module import ASRModule
from mt_module import PreloadedTranslator
from tts_module import TTSModule
import os
import tempfile

# app = Flask(__name__)
app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), 'static'),
    static_url_path='/static'
)

# Initialize modules
asr = ASRModule()
translator = PreloadedTranslator(gemini_api_key="AIzaSyBVtcSFbdPwT0yL5eSb-XuY-XWUzVmTBO8")
tts = TTSModule()

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/translate', methods=['POST'])
def translate():
    try:
        if 'audio_data' not in request.files:
            return jsonify({'status': 'error', 'message': 'No audio file provided'})

        audio_file = request.files['audio_data']
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            audio_path = tmp.name
            audio_file.save(audio_path)

        text, detected_lang = asr.transcribe_audio(audio_path)

        target_lang = request.form.get('target_lang', 'hi')
        translated_text = translator.translate_with_detection(text, target_lang)

        output_dir = os.path.join("static", "audio")
        os.makedirs(output_dir, exist_ok=True)
        output_audio = os.path.join(output_dir, "output.mp3")
        tts.sync_text_to_speech(translated_text, target_lang, output_audio)

        os.unlink(audio_path)

        return jsonify({
            'status': 'success',
            'original_text': text,
            'detected_language': detected_lang,
            'translated_text': translated_text,
            'audio_output': '/static/audio/output.mp3'
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})








# @app.route('/translate', methods=['POST'])
# def translate():
#     try:
#         recording, sample_rate = asr.record_audio(duration=5)
        
#         with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
#             audio_path = asr.save_audio(recording, sample_rate, tmp.name)
        
#         text, detected_lang = asr.transcribe_audio(audio_path)
        
#         target_lang = request.form.get('target_lang', 'hi')
        
#         translated_text = translator.translate_with_detection(text, target_lang)

#         output_dir = os.path.join("static", "audio")
#         os.makedirs(output_dir, exist_ok=True)
#         output_audio = os.path.join(output_dir, "output.mp3")
#         tts.sync_text_to_speech(translated_text, target_lang, output_audio)
        
#         os.unlink(audio_path)

#         return jsonify({
#             'status': 'success',
#             'original_text': text,
#             'detected_language': detected_lang,
#             'translated_text': translated_text,
#             'audio_output': '/static/audio/output.mp3'
#         })
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)})

# @app.route('/translate', methods=['POST'])
# def translate():
#     try:
#         # Step 1: Record audio
#         recording, sample_rate = asr.record_audio(duration=5)
        
#         # Save temporary audio file
#         with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
#             audio_path = asr.save_audio(recording, sample_rate, tmp.name)
        
#         # Step 2: Transcribe audio
#         text, detected_lang = asr.transcribe_audio(audio_path)
        
#         # Get target language from request
#         target_lang = request.form.get('target_lang', 'hi')
        
#         # Step 3: Translate text
#         translated_text = translator.translate_with_detection(text, target_lang)
        
#         # Step 4: Generate speech
#         output_audio = os.path.join(tempfile.gettempdir(), "output.mp3")
#         tts.sync_text_to_speech(translated_text, target_lang, output_audio)
        
#         # Clean up
#         os.unlink(audio_path)
        
#         return jsonify({
#             'status': 'success',
#             'original_text': text,
#             'detected_language': detected_lang,
#             'translated_text': translated_text,
#             'audio_output': output_audio
#         })
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)