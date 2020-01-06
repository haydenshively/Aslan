if __name__ == '__main__':
	from time import sleep
	from numpy import zeros_like
	import cv2
	from mosse import Tracker

	# setup camera
	from filming_studio import *
	camera = camera(0)

	# setup TensorFlow thread
	from custom_thread import CustomThread
	from queue import Empty
	from ai import Faces
	thread_detector = CustomThread(Faces)
	thread_detector.start()

	# setup scene
	from scenes import Grid3D#STL#DemoCube#
	grid = Grid3D(10, 10, 5)#STL('teapot.stl')#DemoCube()#
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

				# Webcam Visualization/Debugging
				"""
				x1, y1, x2, y2 = roi
				cv2.rectangle(image, (x1, y1), (x2, y2), (0,0,255), 5)
				"""

			if tracking:
				tracker.update(gray)
				x, y = tracker.position

				if prevX is not None:
					if prevX == x: Faces.queue_image.put(image)# attempt to re-initialize tracking

					"""UPDATE GRAPHICS"""
					"""
					Here, delta_ is some number (of camera pixels) that *represents*
					the distance traveled by the face in its own plane.
					"""
					deltaX = prevX - x
					deltaY = prevY - y
					"""
					We need to scale that number so that it's measured in display
					pixels. Assume we have a 16" Macbook Pro (3072x1920). Let's
					say that the screen's width (in inches) is W. To reach the
					user's face, we walk a distance ~=W along the screen's normal.

					We also know that the built-in webcam has a resolution of
					1080x720. In the face's plane,
					the horizontal field-of-view captures ~2*W, and the vertical
					field-of-view captures ~1*W.

					After the math, delta_ is some number (of display pixels) which
					is *equal* to the distance traveled by the face in its own plane.
					(subject to the assumptions listed above)
					"""
					# W is supposed to be the width of the screen in inches, but it divides out.
					# This means it's arbitrary, but we keep it for math clarity.
					W = 1.0
					#                 2 * W * (VAL BETWEEN 0 and 1) / W = fraction
					deltaX = 3072.0 * 2 * W * (deltaX/(1080.0)) / W
					deltaY = 1920.0 * 1 * W * (deltaY/(720.00)) / W

					# Now that the math is done, we divide by 2.0 simply because it
					# looks better. Some of our assumptions were probably off.
					grid.moveCameraBy(deltaX/2.0, deltaY/2.0)
					grid.render()
					"""END UPDATE GRAPHICS"""

				prevX, prevY = x, y

				# Webcam Visualization/Debugging
				"""
				cv2.circle(image, (int(x), int(y)), 10, (255,0,0), -1)
				"""

			else: Faces.queue_image.put(image)# attempt to initialize tracking

			sleep(0.03)
			# Webcam Visualization/Debugging
			"""
			cv2.imshow("image", image)
			ch = 0xFF & cv2.waitKey(1)
			if ch == 27:
				break
			"""

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
