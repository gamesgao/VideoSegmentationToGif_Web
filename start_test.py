import cv2
import sys
import time

if len(sys.argv) == 1:
    source = 'test.bmp'
    # sys.exit(-1)
else:
    source = sys.argv[1]

videoTempPath = "./videoTemp/"
resultpath = "./public/images/result/"

a = cv2.imread(videoTempPath + source)
time.sleep(1)
print resultpath + source
cv2.imwrite(resultpath + source, a)
