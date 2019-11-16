import warnings
warnings.filterwarnings("ignore") 

import cv2
from imageai.Detection import ObjectDetection
from moviepy.editor import VideoFileClip
import os
from PIL import Image
import pytesseract
import sys

proxy = 'http://edcguest:edcguest@172.31.100.29:3128'

os.environ['http_proxy'] = proxy 
os.environ['HTTP_PROXY'] = proxy
os.environ['https_proxy'] = proxy
os.environ['HTTPS_PROXY'] = proxy

def convert_to_photo_text(filepath, keyword):
    # print(cv2.__version__)
    os.system("mkdir temp")
    vidcap = cv2.VideoCapture(filepath)
    success,image = vidcap.read()
    count = 0
    success = True
    clip = VideoFileClip(filepath)
    clipDuration = clip.duration;
    while success:
      vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*9000))
      cv2.imwrite("./temp/frame%d.jpg" % count, image)     # save frame as JPEG file
      success,image = vidcap.read()
      # print ('Read a new frame: ', success)
      count += 1
    clipDuration /= count;
    frameTime = []
    finalTime = []
    for i in range (count):
        frameTime.append(i*clipDuration);
    # print(frameTime)
    execution_path = os.getcwd()
    for i in range (count):
        text = pytesseract.image_to_string(Image.open("./temp/frame%d.jpg" % i),config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz --psm 6")
        # print(text.lower())
        if keyword in text.lower():
            finalTime.append(round(frameTime[i], 3))
    # print(finalTime)
    os.system("rm -r ./temp")
    return finalTime


if __name__ == '__main__':
    url = sys.argv[1]
    keyword = sys.argv[2]
    timestamps = convert_to_photo_text(url, keyword)
    print((timestamps), end='')

# print(convert_to_photo_text("/home/ankitb/Downloads/gkcs.mp4", "hash"))