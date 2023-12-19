import os
import json
from PIL import Image
import sys
import requests
import urllib.parse

from flask import Flask, render_template, request
from flask_login import LoginManager, login_required
from werkzeug.utils import secure_filename

# TODO: does this work like this or do i need to call it auth
from app.auth import User
from app.util.custom_vision import custom_vision_predict, custom_vision_classify_moncherie
from app.util.image_helpers import draw_bb_on_img
from app.util.gradio_call import call_gradio_api
from app.util.transcription import whisper_transcribe
from app.util.image_helpers import save_img


from .auth import auth as auth_blueprint

def create_app():
    app = Flask(__name__)
    # TODO: add to power point
    app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]

    app.register_blueprint(auth_blueprint)

    # TODO: add to power point
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # TODO: what does this do?
    @login_manager.user_loader
    def load_user(user_id):
        user = User()
        user.id = "Adam"
        return user
    
    # TODO: add the login manager
    return app

app = create_app()

# TODO: make blueprints and somehow do cluster the functions <vision_version> or something
@app.route('/')
@login_required
def index():
    # TODO: there might be a nicer way to do this....
    nav = [
       {'name': 'Schweißnähte', 'url': '/wheelding', 'img': '/static/images/sample_wheelding.jpg'},
       {'name': 'MonCherie', 'url': '/moncherie', 'img' : "/static/images/moncherie2.png"},
       {'name': 'Cups', 'url': '/cups',  'img' : "/static/images/cup.jpg"},
       {"name": "Huggingface Whisper Inference API", 'url': '/audio_upload', 'img' : '/static/images/sample_wheelding.jpg'},
       {'name': 'SpeechProtocol', 'url': '/gradio', 'img': '/static/images/sample_wheelding.jpg'}
       ]
    return render_template('index.html', nav=nav)


# TODO: clean up the routes and the names to make the consistent
@app.route('/wheelding')
@login_required
def upload_wheelding():
    return render_template("upload.html", processing_action="/process_wheelding")


@app.route('/process_wheelding', methods=['POST'])
@login_required
def process_wheelding():

    selected_image, img_path = save_img(request)

    mode = "wheelding"
    predictions = custom_vision_predict(img_path, mode)

    img_with_bb =  draw_bb_on_img(selected_image, predictions, mode, threshold=0.5, threshold_2=0.1)

    return render_template("wheelding.html", img_path=img_with_bb)


@app.route('/moncherie')
@login_required
def upload_moncherie():
    return render_template("upload.html", processing_action="/process_moncherie")


@app.route("/process_moncherie", methods=['POST'])
@login_required
def process_moncherie():

    selected_image, img_path = save_img(request)

    mode = "moncherie"
    predictions = custom_vision_predict(img_path, mode)
    # TODO: this could be like a slider or some other kind of input
    threshold = 0.5
    threshold_2 = 0.1
    img_with_bb =  draw_bb_on_img(selected_image, predictions, mode, threshold, threshold_2)

    biggest_probablity, winner_label, classifier_result = custom_vision_classify_moncherie(img_path)
    rendered_result = "Most certainly (" + str(biggest_probablity * 100)[:5] + "%) the box is " + winner_label 

    return render_template("moncherie.html", info=rendered_result, classification_info = str(classifier_result), img_obj=img_with_bb)


@app.route("/cups")
@login_required
def cups_page():
    return render_template("upload.html", processing_action="/process_cups")


@app.route("/process_cups", methods=['POST'])
@login_required
def process_cups():
    selected_image, img_path = save_img(request)
    
    mode = "cups"
    predictions = custom_vision_predict(img_path, mode)
    # TODO: this could be like a slider or some other kind of input
    threshold = 0.5
    threshold_2 = 0.1
    img_with_bb =  draw_bb_on_img(selected_image, predictions, mode, threshold, threshold_2)

    return render_template("cups.html", img_obj=img_with_bb)


@app.route("/audio_upload")
@login_required
def upload_audio():
    return render_template("upload.html", processing_action="/hf_whisper")


@app.route("/hf_whisper")
@login_required
def call_inference_api_whisper():
    # TODO: if this works, rename to data_input or something..
    whisper_transcribe(request.files['image'])
    return render_template("speech_protocol.html")


@app.route("/get_url_for_caption")
@login_required
def get_url_for_caption():
    return render_template("image_url.html")


@app.route("/captions")
@login_required
def call_computer_vision_api():
    # get the url input
    # TODO: check weather the input is valid...
    # TODO...
    img_url = request.form.get('img_url')

    if 'COMPUTER_VISION_KEY' in os.environ:
        subscription_key = os.environ['COMPUTER_VISION_KEY']
    else:
        print("\nSet the COMPUTER_VISION_KEY environment variable.\n**Restart your shell or IDE for changes to take effect.**")
        sys.exit()

    if 'COMPUTER_VISION_ENDPOINT' in os.environ:
        endpoint = os.environ['COMPUTER_VISION_ENDPOINT']

    analyze_url = endpoint + "computervision/imageanalysis:analyze?api-version=2023-10-01&%s"

    headers = {'Ocp-Apim-Subscription-Key': subscription_key}
    params = urllib.parse.urlencode({
        'features': 'denseCaptions', # TODO: syntax for multiple features 
        'model-version': 'latest',
        'language': 'en',
    })
    data = {'url': img_url}

    response = requests.post(analyze_url, headers=headers,
                            params=params, json=data)
    response.raise_for_status()
    analysis = response.json()
    return json.dumps(response.json())


@app.route('/gradio')
@login_required
def show_gradio_app():
    return render_template("speech_protocol.html")


# TODO: this is unused, delete or something...
@app.route('/speech_protocol')
@login_required
def generate_protocol():
    # TODO: use this file?? what for?
    if request.method == "POST":
        file = request.files['file']
        if file:
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            return render_template('speech_protocol.html', result=call_gradio_api(audio_path))
    # TODO: include the gradio call
    # this page has the gradio space embedded
    return render_template('speech_protocol.html', result="no result, wrong path")




# TODO: brauche ich das?
if __name__ == '__main__':
   app.run(debug=True)
 