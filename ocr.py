import cv2
import sys
import pytesseract
from textblob import TextBlob
import numpy as np
import math
import io

config = ('-l eng --oem 1 --psm 3')

# Read image from disk
def image_to_text():
    img = cv2.imread("image.jpg", cv2.IMREAD_GRAYSCALE)
    target_area = 600000
    ratio = img.shape[0] / img.shape[1]
    x = int(math.sqrt(target_area / ratio))
    y = int(x * ratio)
    size = (x, y)
    crop = cv2.resize(img, size, interpolation=cv2.INTER_CUBIC)
    #thresh = cv2.threshold(crop, 0, 255,
                           #cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]


    #kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    #crop = cv2.filter2D(crop, -1, kernel)

    '''
    ret,thresh = cv2.threshold(img,100,255,cv2.THRESH_BINARY)
    th2 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,31,2)
    th3 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,71,2)
    blur = cv2.GaussianBlur(img,(5,5),0)
    ret2,th4 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    #th3 = cv2.bitwise_not(th3)
    dst = cv2.fastNlMeansDenoising(th3,None,20,7,21)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    opening = cv2.morphologyEx(th3, cv2.MORPH_OPEN, kernel)
    opening = cv2.bitwise_not(opening)
    '''
    '''
    kernel = np.ones((1, 1), np.uint8)
    crop = cv2.dilate(crop, kernel, iterations=1)
    crop = cv2.erode(crop, kernel, iterations=1)
    '''
    #th3 = cv2.adaptiveThreshold(crop, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 71, 2)
    #th3 = cv2.adaptiveThreshold(crop, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    filtered = cv2.adaptiveThreshold(crop.astype(np.uint8), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 41)
    kernel = np.ones((2, 2), np.uint8)
    dilation = cv2.erode(filtered, kernel, iterations=3)

    # Run tesseract OCR on image
    text = pytesseract.image_to_string(dilation, config=config)
    if (text.strip() == ""):
        text = pytesseract.image_to_string(crop, config=config)
    # Print recognized text
    #sentence = TextBlob(text)
    #sentence = sentence.correct()
    print(text)
    return text


image_to_text()


def correctSentence(text):
    blob = TextBlob(text)
    tags = blob.tags
    sentence = ""
    for i, word in enumerate(blob.words):
        if (tags[i][1] != 'NNP'):
            sentence += ""
