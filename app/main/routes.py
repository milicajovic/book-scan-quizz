import time

from flask import current_app
from flask import render_template, request, jsonify, send_file
from google_ai.tts import generate_speech_from_ssml
from sqlalchemy import inspect

from . import main
from .. import db


@main.route('/')
def home():
    return render_template('main/home.html')


@main.route('/feedback')
def feedback():
    return render_template('main/feedback.html')


@main.route('/tts-experiment')
def tts_experiment():
    return render_template('main/tts_experiment.html')


@main.route('/about')
def about():
    return render_template('main/about.html')


@main.route('/help')
def help():
    return render_template('main/help.html')


@main.route('/contact')
def contact():
    return render_template('main/contact.html')


@main.route('/db-check')
def db_check():
    try:
        # Measure database connection time
        connect_start = time.time()
        engine = db.engine
        connect_end = time.time()
        connect_latency = (connect_end - connect_start) * 1000  # Convert to milliseconds

        inspector = inspect(engine)
        db_type = engine.name
        db_url = str(engine.url)

        # For security, remove password from the URL if present
        if '@' in db_url:
            db_url = db_url.split('@')[1]

        # Measure time to fetch table names
        fetch_start = time.time()
        tables = inspector.get_table_names()
        fetch_end = time.time()
        fetch_latency = (fetch_end - fetch_start) * 1000  # Convert to milliseconds

        return render_template('main/db_check.html',
                               db_type=db_type,
                               db_url=db_url,
                               tables=tables,
                               connected=True,
                               connect_latency=round(connect_latency, 2),
                               fetch_latency=round(fetch_latency, 2))
    except Exception as e:
        current_app.logger.error(f"Database connection error: {str(e)}")
        return render_template('main/db_check.html',
                               connected=False,
                               error=str(e))


@main.route('/tts-demo', methods=['GET', 'POST'])
def tts_demo():
    if request.method == 'POST':
        ssml_text = request.form['ssml_text']
        try:
            audio_file_path = generate_speech_from_ssml(ssml_text)
            return jsonify({'audio_file': audio_file_path})
        except Exception as e:
            current_app.logger.error(f"TTS failed: {str(e)}")
            return jsonify({'error': f'TTS failed. {str(e)}'}), 500

    return render_template('main/tts_demo.html')


@main.route('/play-audio')
def play_audio():
    audio_file = request.args.get('file')
    try:
        return send_file(audio_file, mimetype='audio/mp3')
    except Exception as e:
        current_app.logger.error(f"Audio playback failed: {str(e)}")
        return jsonify({'error': 'Audio playback failed. Tough luck.'}), 500

@main.route('/voice-activation')
def voice_activation():
    return render_template('/experiments/voice_activation.html')

@main.route('/human-detection')
def human_detection():
    return render_template('/experiments/human_detection.html')
