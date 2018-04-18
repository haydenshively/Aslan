if __name__ == '__main__':
	from time import sleep
	from numpy import zeros_like
	import cv2
	from mosse import Tracker

	# setup camera
	from FilmingStudio import *
	camera = camera(0)

	# setup TensorFlow thread
	from CustomThread import CustomThread
	from queue import Empty
	from ai import Faces
	thread_detector = CustomThread(Faces)
	thread_detector.start()

	# setup scene
	from scenes import STL#Grid3D#, DemoCube
	grid = STL('robot.stl')#Grid3D(12, 12, 12)#DemoCube()
	prevX, prevY = None, None


	tracking = False

	while camera.isOpened():
		try:
			image = scan(camera)
			image = shrink(image, amount = 1)
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

			box = None
			while True:
				try: box = Faces.queue_result.get_nowait()
				except Empty: break

			if box is not None:
				roi = zeros_like(box)# roi will be the same as box, but with x and y flipped
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
					grid.moveCameraBy((prevX - x)/24, (prevY - y)/24)
					grid.render()
				prevX, prevY = x, y

				# cv2.circle(image, (int(x), int(y)), 5, (255,0,0), -1)#VIS

			else: Faces.queue_image.put(image)# attempt to initialize tracking

			sleep(.03)
			# cv2.imshow("image", image)#VIS
			# ch = 0xFF & cv2.waitKey(1)
			# if ch == 27:
			# 	break

		except KeyboardInterrupt: break

	# close windows
	del grid.window
	cv2.destroyAllWindows()
	# stop tensorflow thread
	thread_detector.stop()
	Faces.queue_image.put('break')
	thread_detector.join()
	# release camera
	camera.release()
