#DENSE OPTICAL FLOW MAY PROVIDE SIMILAR RESULTS UNDER CERTAIN CIRCUMSTANCES
#this is really good at highlighting the contours of moving objects and ignoring background colors
"""Temporal Average Optical Flow"""
import cv2
import numpy as np
from common import *
from Mosse import Tracker
from Visuals import Grid3D#, DemoCube

# setup TensorFlow thread
from CustomThread import CustomThread
from queue import Empty
from TensorFlow import Faces
thread_detector = CustomThread(Faces)
thread_detector.start()

#{SETUP CAMERA}
scene = cameraView(0)

tracking = False

cube = Grid3D(12, 12, 12)#DemoCube()
prevX, prevY = None, None

while scene.isOpened():
	image = scan(scene)
	image = shrink(image, amount = 1)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	box = None
	while True:
		try:
			box = Faces.queue_result.get_nowait()
		except Empty:
			break

	if box is not None:
		roi = np.zeros_like(box)# roi will be the same as box, but with x and y flipped
		roi[0::2] = box[1::2]
		roi[1::2] = box[0::2]
		roi = roi.tolist()

		tracker = Tracker(gray, roi)
		tracking = True

		# x1, y1, x2, y2 = roi#VIS
		# cv2.rectangle(image, (x1, y1), (x2, y2), (0,0,255), 1)#VIS

	if tracking:
		tracker.update(gray)
		x, y = tracker.position

		if prevX is not None:
			if prevX == x: Faces.queue_image.put(image)# attempt to re-initialize tracking
			cube.adjustCamera((prevX - x)/24, (prevY - y)/24)
			cube.render()
		prevX, prevY = x, y

		# cv2.circle(image, (int(x), int(y)), 5, (255,0,0), -1)#VIS

	else: Faces.queue_image.put(image)# attempt to initialize tracking

	cv2.imshow("image", image)

	ch = 0xFF & cv2.waitKey(1)
	if ch == 27:
		break

# close windows
del cube.window
cv2.destroyAllWindows()
# stop tensorflow thread
thread_detector.stop()
Faces.queue_image.put('break')
thread_detector.join()
# release camera
scene.release()
