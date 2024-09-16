import base64
import ddddocr
from io import BytesIO
from PIL import Image

def recaptchaByPass(code_image):
    ocr = ddddocr.DdddOcr()
    base64_string = code_image.split(",")[1]
    image_data = base64.b64decode(base64_string)
    image = Image.open(BytesIO(image_data))
    res = ocr.classification(image)
    return res

