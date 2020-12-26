import time
import picamera
# import the necessary packages
import numpy as np
import argparse
import cv2
# Explicitly open a new file called my_image.jpg
my_file = open('stream.jpg', 'wb')
with picamera.PiCamera() as camera:
    camera.start_preview()
    time.sleep(2)
    camera.capture(my_file)
# At this point my_file.flush() has been called, but the file has
# not yet been closed
my_file.close()


# load the image
image = cv2.imread('stream2.jpg')
# find all the 'orange' shapes in the image
upper = np.array([90, 110, 200])
lower = np.array([30, 50, 130])

shapeMask = cv2.inRange(image, lower, upper)
new_file=open('filtered.jpg','wb')
cv2.imwrite('filtered.jpg',shapeMask)
new_file.close()

gray=cv2.bilateralFilter(shapeMask,11,17,17)
edged=cv2.Canny(gray,30,200)
gray_file=open('edge.jpg','wb')
cv2.imwrite('edge.jpg',edged)
gray_file.close()

(cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cnts= sorted (cnts,key = cv2.contourArea, reverse=True)[:10]
screenCnt=None
flag_t=False
flag_s=False
for c in cnts:
	peri = cv2.arcLength(c,True)
	approx = cv2.approxPolyDP(c, 0.02 * peri, True)
	if len (approx)==3:
		triangle=approx
		print "triangle" 
		print triangle
		flag_t=True
        if len (approx)==4:
                square=approx
		print "square"
                print square
		flag_s=True
                break
	print "no square found"

	square
[[[485 293]]
 [[485 298]]
 [[487 298]]
 [[487 293]]]
