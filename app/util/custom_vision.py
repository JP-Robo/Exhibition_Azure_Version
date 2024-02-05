import os
from msrest.authentication import ApiKeyCredentials
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient


def get_prediction_client():
    """get a client by providing the credentials from the 
    enviroment variables

    Returns:
        AzureClient: to talk with the Azure API
    """
    prediction_key = os.environ["VISION_PREDICTION_KEY"]
    prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
    ENDPOINT = os.environ["VISION_PREDICTION_ENDPOINT"]
    return CustomVisionPredictionClient(ENDPOINT, prediction_credentials)


def get_prediction_list(results):
    """iterates over the predictions and
    returns a list with the items

    Args:
        results (ImagePrediction): "result of an image predictions request"

    Returns:
        List: of Prediction
    """
    predictions = []
    for prediction in results.predictions:
        predictions.append(prediction)
    return predictions


def call_custom_vision_classify_moncherie(img_path):
    """call the API for the moncherie project
    (classification of images {touched, untouched, undefined due to occlusion})

    Args:
        img_path (String): path to the image

    Returns:
        List: of predictions
    """
    published_name = "Iteration1"
    project_id = "9ceb71ce-cc4d-4bea-b220-a9b32b171f3a"

    predictor = get_prediction_client()

    with open(img_path, "rb") as image_data:
        result = predictor.classify_image(project_id, published_name, image_data.read())

    return get_prediction_list(result)


def custom_vision_classify_moncherie(img_path):
    """calls another function for the classification of the
    moncherie images
    

    Args:
        img_path (String): path to the image

    Returns:
        Tuple: (int) the most likely classification label
               (string) the label of the winner image
               (TODO) other infos 
    """
    classifier_info = call_custom_vision_classify_moncherie(img_path) 

    classifier_result = {}
    biggest_probablity = 0
    winner_label = ""

    # Find the biggest probability in the list
    for label_info in classifier_info:
        classifier_result[label_info.tag_name] = label_info.probability
        if label_info.probability > biggest_probablity:
            biggest_probablity = label_info.probability
            winner_label = label_info.tag_name

    return biggest_probablity, winner_label, classifier_result


def custom_vision_predict(img_path, version):
    """call the different projects

    Args:
        img_path (String): Path to the image   
        version (String): the version to call

    Returns:
        _type_: _description_
    """
    # TODO: actually it would be better not to intertwine the two calls i guess
    with open(img_path, "rb") as image_contents:
        
        # TODO: if more is added, it would be nice to compose this somehow in a dict
        if version == "wheelding":
            publish_iteration_name = "Iteration1"
            project_id = "a86f394a-cb8e-4caf-9750-8a756c66df96"

        # TODO: i dont know if the keys are right
        elif version == "moncherie_sw":
            publish_iteration_name = "Iteration1"
            project_id = "d15e4652-5873-4d9f-84ba-35505bce730c"

        elif version == "moncherie_color":
            publish_iteration_name = "Iteration1"
            project_id = "9b1ea25b-2534-4731-8f82-041e0fd1ebd4"

        elif version == "cups":
            publish_iteration_name = "Iteration1"
            project_id = "9bd0a2ab-1fc9-4642-8fee-1fdcb4df2ac1"

        predictor = get_prediction_client()
        # call the azure API
        results = predictor.detect_image(project_id, publish_iteration_name, image_contents.read())

    return get_prediction_list(results)