import numpy as np
import cv2
import glob
import sys
import os


# Define the codec and create VideoWriter object
# fourcc = cv2.VideoWriter_fourcc(*'X264')
output = sys.argv[1]
fourcc = cv2.cv.CV_FOURCC('M', 'J', 'P', 'G')
out = cv2.VideoWriter(output,fourcc, 24.0, (1024,436))

for filename in glob.glob(r'.\*.png'):
    frame = cv2.imread(filename)
    # frame = cv2.flip(frame,0)
    # write the flipped frame
    out.write(frame)
    if os.path.exist(filename):
        os.remove(filename)
    # out.write(frame)
    # out.write(frame)
    # cv2.imshow('frame',frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
   

# Release everything if job is finished
# cap.release()
out.release()
# cv2.destroyAllWindows()