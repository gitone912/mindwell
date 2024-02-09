from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from PIL import Image, ImageDraw, ImageFont


APIKEY = "fc840027bd2e413a85efcdce2bae3d0b"
ENDPOINT = "https://ic2024faceapi.cognitiveservices.azure.com/"
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(APIKEY))

single_image_name = "pexels-photo-3777931.webp"
image = open(single_image_name, 'r+b')

face_attributes = ['emotion']
detected_faces = face_client.face.detect_with_stream(image, face_attributes)
if not detected_faces:
	raise Exception('No face detected from image {}'.format(single_image_name))

def get_rectangle(face_dictionary):
    rect = face_dictionary.face_rectangle
    left = rect.left
    top = rect.top
    right = left + rect.width
    bottom = top + rect.height

    return ((left, top), (right, bottom))


def get_emotion(emotion):
    max_emotion_value = 0.0
    emotion_type = None

    for emotion_name, emotion_value in vars(emotion).items():
        if emotion_name == "additional_properties":
           continue

        if emotion_value > max_emotion_value:
           max_emotion_value = emotion_value
           emotion_type = emotion_name

    return emotion_type

def detect_faces_and_emotions(image_name: str, detected_faces, font_size_percentage = 5):
    img = Image.open(image_name)

    font_size = round(img.height * font_size_percentage / 100)
    font = ImageFont.truetype('arial.ttf', font_size)

    draw = ImageDraw.Draw(img)
    for face in detected_faces:
        rect = get_rectangle(face)
        draw.rectangle(rect, outline='red')
        face_emotion = get_emotion(face.face_attributes.emotion)
        draw.text(rect[0], face_emotion, 'white', font=font)

    return img

detect_faces_and_emotions(single_image_name, detected_faces, 3)