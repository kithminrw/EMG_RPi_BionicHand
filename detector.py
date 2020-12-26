import time
import picamera
# import the necessary packages
import numpy as np
import argparse
import cv2


# Explicitly open a new file called my_image.jpg
my_file = open('stream2.jpg', 'wb')
with picamera.PiCamera() as camera:
    camera.start_preview()
    time.sleep(2)
    camera.capture(my_file)
# At this point my_file.flush() has been called, but the file has
# not yet been closed
my_file.close()

# load the image
#image = cv2.imread(args["image"])
image = cv2.imread('stream2.jpg')

# find all the 'black' shapes in the image
#lower = np.array([0, 140, 255])
#upper = np.array([80, 127, 255])
upper = np.array([90, 110, 200])
lower = np.array([30, 50, 130])
shapeMask = cv2.inRange(image, lower, upper)
new_file=open('filtered2.jpg','wb')
cv2.imwrite('filtered2.jpg',shapeMask)
new_file.close()
#cv2.imshow("Mask", shapeMask)

#Turn into gray scale
#image = cv2.imread('stream.jpg')
#gray_image=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#gray_file=open('gray.jpg','wb')
#cv2.imwrite('gray.jpg',gray_image)
#gray_file.close()

#ret,thresh = cv2.threshold(shapeMask,217,255,1)#filter again
#contours,h = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)#find contours
#print len(contours)
#cnt= contours[0]
#print contours[0]
#M = cv2.moments(cnt)
#print M

gray=cv2.bilateralFilter(shapeMask,11,17,17)
edged=cv2.Canny(gray,30,200)
gray_file=open('edge2.jpg','wb')
cv2.imwrite('edge2.jpg',edged)
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


#Draw square

if flag_t==True:
	cv2.drawContours(shapeMask, [triangle], -1, (0,255,0), 3)

if flag_s==True:
        cv2.drawContours(shapeMask, [square], -1, (0,255,0), 3)

 
#cv2.imshow("Arrow", shapeMask)

fin=open('fin2.jpg','wb')
cv2.imwrite('fin2.jpg',shapeMask)
fin.close()

