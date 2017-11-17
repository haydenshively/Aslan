#DENSE OPTICAL FLOW MAY PROVIDE SIMILAR RESULTS UNDER CERTAIN CIRCUMSTANCES
#this is really good at highlighting the contours of moving objects and ignoring background colors
"""Temporal Average Optical Flow"""
import cv2
from common import *
from initialization import Reel, motionCenter
from mosse import Tracker
from interface import DemoCube
from math import floor

#{SETUP CAMERA}
scene = cameraView(0)

image = scan(scene, "hsv", channel = 2)
image = shrink(image, amount = 3)

reel = Reel(10, image)

tracking = False
tracker = None

cube = DemoCube()
prevX, prevY = None, None

while scene.isOpened():
	image = scan(scene, "hsv", channel = 2)
	image = shrink(image, amount = 3)

	reel.append(image)

	vis = reel.temporalVariance
	center = motionCenter(vis)#TODO cannot just use motion center, because that includes body
	if center is not None:
		vis[int(center[1]), int(center[0])] = 255
		if not tracking:
			rectangle = (center[0] - 20, center[1] - 10, center[0] + 20, center[1] + 30)
			rectangle = (int(a) for a in rectangle)
			tracker = Tracker(image, rectangle)
			tracking = True

	if tracking:
		tracker.update(image)
		x, y = tracker.position
		vis[floor(y), floor(x)] = 255
		# cv2.imshow("test", tracker.visualizer)

		if prevX is not None:
			cube.adjustCamera((prevX - x)/6, (prevY - y)/6)
			cube.render()
		prevX, prevY = x, y

	cv2.imshow("vis", expand(vis.astype("uint8"), amount = 2))

	ch = 0xFF & cv2.waitKey(1)
	if ch == 27:
		break
	if ch == ord('n'):
		tracking = False
		print("refocusing")


scene.release()
cv2.destroyAllWindows()
