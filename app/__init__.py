import os
import json
import requests

from flask import Flask, render_template, request
from flask_login import LoginManager, login_required
from werkzeug.utils import secure_filename

# TODO: does this work like this or do i need to call it auth
from app.auth import User
from app.util.custom_vision import custom_vision_predict, custom_vision_classify_moncherie
from app.util.image_helpers import draw_bb_on_img
from app.util.image_helpers import save_img
from app.util.image_helpers import display_receipt, display_captions

from app.azure_api.captions import call_API_Captions
from app.azure_api.form_recognition import call_API_Receipt


from app.auth import auth as auth_blueprint

def create_app():
    """creates the app and registers blueprints
    which are grouped functionalities
    a load user finction os created, which is used for user loading

    Returns:
        _type_: _description_
    """
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
    return render_template('base.html')


@app.route("/<mode>",  methods=['GET', 'POST'])
@login_required
def upload(mode):
    return render_template("upload.html", processing_action="/process_" +  mode)


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
    # moncherie sw works kindof... 

    selected_image, img_path = save_img(request)

    # TODO: what does this return?, might break the application
    # mode = request.form.get("model_version")

    # TODO: for now only the rgb version will be used 
    mode = "moncherie_color"
    predictions = custom_vision_predict(img_path, mode)

    # TODO: this could be like a slider or some other kind of input
    threshold = 0.5
    threshold_2 = 0.1

    img_with_bb =  draw_bb_on_img(selected_image, predictions, mode, threshold, threshold_2)

    # get the classification
    # TODO: is only trained on the sw images
    if mode == "moncherie_sw":

        biggest_probablity, winner_label, classifier_result = custom_vision_classify_moncherie(img_path)
        rendered_result = "Most certainly (" + str(biggest_probablity * 100)[:5] + "%) the box is " + winner_label

    else:
        rendered_result = "No classification model given for model" + mode
        classifier_result = "No classifier, no info"

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

    return render_template("cups.html", img_obj=img_with_bb, img_path=img_path)


@app.route("/process_receipt", methods=['POST'])
@login_required
def process_receipt():
    selected_image , img_path = save_img(request) 

    result = call_API_Receipt(img_path)
    receipt_info = str(result.to_dict())

    img = display_receipt(img_path, result.to_dict())

    return render_template("receipt.html", img=img, receipt_info=receipt_info, result_dict=result.to_dict())


@app.route("/process_captions", methods=['POST'])
@login_required
def process_captions():
    selected_image, img_path = save_img(request) 

    # TODO: call the image caption thingi
    result = call_API_Captions(img_path)

    img = display_captions(img_path)
    return render_template("captions_upload.html", info=str(result['captions']), img=img)
    # return render_template("captions.html", img_url=img_path)


# TODO: i might need this for the d3.js thingi
# @app.route("/captions",  methods=['POST'])
# @login_required
# def call_computer_vision_api():
#     # TODO: check weather the input is valid...
#     img_url = request.form.get('img_url')

#     if 'COMPUTER_VISION_KEY' in os.environ:
#         subscription_key = os.environ['COMPUTER_VISION_KEY']
#     else:
#         print("\nSet the COMPUTER_VISION_KEY environment variable.\n**Restart your shell or IDE for changes to take effect.**")
#         sys.exit()

#     if 'COMPUTER_VISION_ENDPOINT' in os.environ:
#         endpoint = os.environ['COMPUTER_VISION_ENDPOINT']

#     analyze_url = endpoint + "computervision/imageanalysis:analyze?api-version=2023-10-01&%s"

#     headers = {'Ocp-Apim-Subscription-Key': subscription_key}
#     # TODO: syntax for multiple features
#     params = urllib.parse.urlencode({
#         'features': 'denseCaptions',
#         'model-version': 'latest',
#         'language': 'en',
#     })
#     data = {'url': img_url}

#     # TODO: cant i just use the path here?
#     response = requests.post(analyze_url, headers=headers,
#                             params=params, json=data)
#     response.raise_for_status()
#     json_str = json.dumps(response.json())
#     json_string_safe = re.sub(r'"([^"]*)"', lambda x: x.group(0).replace("'", "´"), json_str)
#     return render_template("captions.html", img_url=img_url, captions_result=json_string_safe)


@app.route('/speech_protocol')
@login_required
def speech_protocol():
    return render_template('speech_protocol.html', result="no result, wrong path")


# TODO: brauche ich das?
if __name__ == '__main__':
   app.run(debug=True)
