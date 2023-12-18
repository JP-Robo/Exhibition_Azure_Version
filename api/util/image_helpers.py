import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from io import BytesIO
import base64


def save_img(request):
    selected_image = request.files['image']
    img_path =  "/tmp/" + selected_image.filename
    selected_image.save(img_path)
    return selected_image, img_path


def get_bb_scaled_to_img(img, bb):
    w,h = img.size
    left = bb.left * w
    top = bb.top * h
    width = bb.width * w
    height = bb.height * h
    return [left, top, width, height]


def get_edgecolor_pralinen(praline_name):
    if praline_name == "rocher":
         return "springgreen"
    elif praline_name == "moncheri": 
         return "coral"
    elif praline_name == "kuesschen": 
         return "gold"
    return ""


def display_cups(predictions, img, ax):
    # TODO: make different colors
    for prediction in predictions:

        bb = prediction.bounding_box
        bb = get_bb_scaled_to_img(img, bb)

        if prediction.probability > 0.5:
            # TODO: add alphas and colors

            rect = patches.Rectangle(xy=(bb[0], bb[1]), width=bb[2], height=bb[3], linewidth=2, edgecolor='springgreen', facecolor='none', label=str(prediction.probability))
            ax[1].add_patch(rect)
     
    
def display_moncherie(predictions, img, ax):
    counter = {"rocher": 0, "moncheri": 0, "kuesschen": 0}
    for prediction in predictions:

        bb = prediction.bounding_box
        bb = get_bb_scaled_to_img(img, bb)
        
        if prediction.probability > 0.5:

            # make the bounding boxes
            edgecolor = get_edgecolor_pralinen(prediction.tag_name)
            rect = patches.Rectangle(xy=(bb[0], bb[1]), width=bb[2], height=bb[3], linewidth=2, alpha=0.5, edgecolor=edgecolor, facecolor='none', label=str(prediction.probability))
            ax[1].add_patch(rect)

            # add some counter ...
            counter[prediction.tag_name] = counter[prediction.tag_name] + 1

    return counter


def display_wheelding(predictions, img, ax, threshold, threshold_2):
    for prediction in predictions:

        bb = prediction.bounding_box
        bb = get_bb_scaled_to_img(img, bb)

        if prediction.probability > threshold:
                rect = patches.Rectangle(xy=(bb[0], bb[1]), width=bb[2], height=bb[3], linewidth=2, alpha=threshold, edgecolor='springgreen', facecolor='none', label=str(prediction.probability))
                ax[1].add_patch(rect)
        elif prediction.probability > threshold_2:
                rect = patches.Rectangle(xy=(bb[0], bb[1]), width=bb[2], height=bb[3], linewidth=1, alpha=threshold_2, edgecolor='gold', facecolor='none', label=str(prediction.probability))
                ax[1].add_patch(rect)
        else:
                rect = patches.Rectangle(xy=(bb[0], bb[1]), width=bb[2], height=bb[3], linewidth=0.5, alpha=threshold, edgecolor='orangered', facecolor='none', label=str(prediction.probability))


def draw_bb_on_img(img_path, predictions, mode, threshold, threshold_2):

    plt.style.use("seaborn-v0_8-dark")

    fig, ax = plt.subplots(1,2)

    img = Image.open(img_path)
    
    ax[0].imshow(img)
    ax[1].imshow(img)

    # draw the bounding boxes on an image
    # TODO: does it work, because they coords are accesd via index and not key
    if mode == "wheelding":
        display_wheelding(predictions, img, ax, threshold, threshold_2)
    elif mode == "moncherie":
        # TODO: why is there this ","
        counter = display_moncherie(predictions, img, ax,)
        plt.xlabel(str(counter))
    elif mode == "cups":
        display_cups(predictions, img, ax)
         
    buf = BytesIO()
    fig.savefig(buf, format="png")

    # Embed the result in the html output.
    return base64.b64encode(buf.getbuffer()).decode("ascii")