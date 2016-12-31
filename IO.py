from __future__ import print_function

import json
import random
import sys
import time

import cv2
import glob
import json
import imageio
from video import *

skipFrame = 0
readFrame = 5
skipfirstFrame = 1

def readVideo(path):
    if len(path) == 0:
        cap = cv2.VideoCapture('1.MOV')
    else:
        cap = cv2.VideoCapture(path)

    if not cap.isOpened():
        print('Cannot initialize video capture')
        sys.exit(-1)

    result = Video()
    readFrame = int((cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)-skipfirstFrame)/(skipFrame+1))
    # ret, frame = cap.read()
    for i in range(skipfirstFrame):
        ret, frame = cap.read()
    ret, frame = cap.read()
    # while(ret):
    for i in range(readFrame):
        result.addFrame(frame)
        for i in range(skipFrame):
            ret, frame = cap.read()
        ret, frame = cap.read()

    cap.release()
    return result

def readFlowVideoFromFile(path):
    result = FlowVideo()
    for filename in glob.glob(path + r'*.txt'):
        frame = readMat(filename)
        result.addFrame(frame)
    return result

def readMat(path):
    with open(path) as fin:
        result = json.load(fin)
        mat = np.array(result["data"])
        mat.resize(result["rows"], result["cols"],2)
        fin.close()
    return mat


def readFlowVideo(path):
    result = FlowVideo()

    cap = cv2.VideoCapture(path)
    readFrame = int((cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT) - skipfirstFrame) / (skipFrame + 1))
    if not cap.isOpened():
        print('Cannot initialize video capture')
        sys.exit(-1)

    # the parameter for Optical Flow
    # windowName = "test"
    # frameNunber = 0
    prevFrame = None
    pyramidScale = 0.5
    pyramidLevels = 1
    windowSize = 7
    iterations = 10
    polynomialNeighborhoodSize = 5
    polynomialSigma = 1.1
    flags =  cv2.OPTFLOW_USE_INITIAL_FLOW  # cv2.OPTFLOW_FARNEBACK_GAUSSIAN #cv2.OPTFLOW_FARNEBACK_GAUSSIAN #

    for i in range(skipfirstFrame-1):
        ret, frame = cap.read()
    ret, frame = cap.read()
    prevFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, frame = cap.read()
    # prevFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # while (ret):
    for i in range(readFrame):
        nextFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # cv2.imshow(windowName, frame)
        result.addFrame(cv2.calcOpticalFlowFarneback(prevFrame,
                                                     nextFrame,
                                                     pyramidScale,
                                                     pyramidLevels,
                                                     windowSize,
                                                     iterations,
                                                     polynomialNeighborhoodSize,
                                                     polynomialSigma,
                                                     flags))
        for i in range(skipFrame):
            ret, frame = cap.read()
        ret, frame = cap.read()
        prevFrame = nextFrame

        # print flows
    cap.release()
    # return flows
    # cv2.destroyAllWindows()

    return result


def writeColoredSegmentationVideo(path, video, fig, orivideo, distill, source):
    colors = []
    for i in range(video.getSegmentNumber()):
        colors += [[0, 0, 0]]

    t = 0
    numToC = {}
    gif = []
    bgLabels = np.zeros((video.getFrameHeight(), video.getFrameWeight(), 3), dtype=np.uint8)
    for t in range(video.getFrameNumber()):
        labels = video.getFrame(t)
        coloredLabels = np.zeros((len(labels), len(labels[0]), 3), dtype=np.uint8)
        if (distill) and (t == 0):
            for i in range(len(labels)):
                for j in range(len(labels[i])):
                    label = labels[i][j]
                    while colors[label][0] == 0:
                        colors[label][0] = random.randrange(1, 256)
                        colors[label][1] = random.randrange(1, 256)
                        colors[label][2] = random.randrange(1, 256)
                    coloredLabels[i][j] = colors[label]

            # cv2.imwrite(str(path) + '.' + str(t) + '.jpg', coloredLabels)
            cv2.imwrite("./public/images/result/" + source + '.jpg', coloredLabels)
            sys.stdout.flush()
            time.sleep(1)
            print (source)
            sys.stdout.flush()
            name = raw_input("")
            fig = json.loads(name)
            print ("fig width" + str(len(fig)))
            print ("fig h" + str(len(fig[0])))
            for i in range(len(labels)):
                for j in range(len(labels[i])):
                    if (fig[i][j] == 1):
                        numToC[labels[i][j]] = [255, 255, 255]

        if (distill):
            cv2.imread("./videoTemp/" + source + '.bg', bgLabels)
        for i in range(len(labels)):
            for j in range(len(labels[i])):
                label = labels[i][j]
                if (distill):
                    if (numToC.has_key(label)):
                        #if numToC[label] == [255, 255, 255]:
                        coloredLabels[i][j] = orivideo.get(t, i, j)
                    else:
                        coloredLabels[i][j] = [0, 0, 0]
                        coloredLabels[i][j] = bgLabels[i][j]
                else:
                    while colors[label][0] == 0:
                        colors[label][0] = random.randrange(0, 256)
                        colors[label][1] = random.randrange(0, 256)
                        colors[label][2] = random.randrange(0, 256)
                    coloredLabels[i][j] = colors[label]
        # write as image
        # coloredLabels
        cv2.imwrite(str(path) + '.' + str(t) + '.jpg', coloredLabels)
        if (distill):
            gif.append(coloredLabels[:])
    if (distill):
        #writeGif("gif.gif", gif, duration=1, subRectangles = False)
        imageio.mimsave("./public/images/result/" + source + '.gif', gif)

    return t
