# Aslan  
Aslan combines Visual Toolkit (VTK) Python bindings with Google’s TensorFlow Object Detection library to create the illusion of 3D on a 2D screen.
  
First, the object detector was retrained using the FDDB faces dataset. When I wrote this code, however, my computer was too slow to run ML on every frame of webcam video, so I designed a queue-based multithreaded framework that combines ML with a traditional Mosse tracker. Whenever Mosse loses accuracy, the bounding box is reinitialized from the ML code. This allows Aslan to run in real time.  
  
Demo video available here: https://www.haydenshively.info/aslan