# USAGE
# python real_time_object_detection.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import os
import cv2
import sys
from moviepy.editor import VideoFileClip
def convert_to_photo_fast(filepath, keyword):
    # print(keyword)
    os.system("mkdir temp")
    vidcap = cv2.VideoCapture(filepath)
    success,image = vidcap.read()
    count = 0
    success = True
    clip = VideoFileClip(filepath)
    clipDuration = clip.duration;
    while success:
      vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*1000))
      cv2.imwrite("./temp/frame%d.jpg" % count, image)     # save frame as JPG file
      success,image = vidcap.read()
      # print ('Read a new frame: ', success)
      count += 1

    # initialize the list of class labels MobileNet SSD was trained to
    # detect, then generate a set of bounding box colors for each class
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        "sofa", "train", "tvmonitor"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

    net = cv2.dnn.readNetFromCaffe("/home/ankitb/Documents/visa/python/MobileNetSSD_deploy.prototxt.txt", "/home/ankitb/Documents/visa/python/MobileNetSSD_deploy.caffemodel")
    time.sleep(2.0)
    
    lst = []
    for ii in range(0, count):
        name = './temp/frame'+ str(ii) + '.jpg'
        frame = cv2.imread(name)
        frame = imutils.resize(frame, width=400)

        # grab the frame dimensions and convert it to a blob
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
            0.007843, (300, 300), 127.5)

        # pass the blob through the network and obtain the detections and
        # predictions
        net.setInput(blob)
        detections = net.forward()

        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            if confidence > 0.7:
                idx = int(detections[0, 0, i, 1])
                label = "{}: {:.2f}%".format(CLASSES[idx],
                    confidence * 100)
                # print(label)
                if CLASSES[idx] == keyword:
                    # print("hi")
                    lst.append(ii)
                # print(ii, label, confidence)
    # print(lst)
    lst2=[]
    flag=1
    if not lst:
        return lst
    last=lst[0]
    for i in range(0, len(lst)-1):
        if flag == 1:
            lst2.append(lst[i])
        if last+2 <= lst[i+1]:
            flag=1
            last=lst[i+1]
        else:
            flag=0

    os.system("rm -r ./temp")
    # print(lst2)
    return lst2


if __name__ == '__main__':
    url = sys.argv[1]
    keyword = sys.argv[2]
    timestamps = convert_to_photo_fast(url, keyword)
    print((timestamps), end='')
