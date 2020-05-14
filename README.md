# Aslan  
Aslan combines Visual Toolkit (VTK) Python bindings with Google’s TensorFlow Object Detection library to create the
illusion of 3D on a 2D screen.
  
Since I wrote most of this code in early 2018, the SOTA model for fast object tracking was MobileNet(V1)-SSD. To make
Aslan, I retrained Google's model on the FDDB faces dataset. Since my laptop didn't have a GPU, this model was unable to
process images from the webcam feed in real time. To fix that, I designed a queue-based multi-threaded framework that
combines ML with a traditional Mosse tracker. Whenever Mosse loses accuracy, its bounding box is reinitialized from the
MobileNet predictions. This allows Aslan to run in real time, even on older hardware.  
  
Once the face's location is known, I use VTK to re-position the camera (with off-axis projection) such that everything
looks 3-Dimensional to the user. This can be done with any VTK scene; I've provided a few demos, including one which displays .STL
CAD files.
  
Demo video available here: https://www.haydenshively.info/aslan
  
## Usage
1. Install requirements from `environment.yml` using Anaconda
2. Run `python main.py`
3. To try out different scenes, modify lines 19 and 20 of `main.py`. If you're using a .STL file and the scale doesn't
look right, try modifying line 176 of `scenes.py` (`stl_actor.Set_Scale(...)`)
  
Traditionally, VTK for Python is pretty poorly documented, so if you're having issues, let me know directly. You're
unlikely to find answers in forums.
  
## Future Updates
If this repo ever gets any stars, I'll try to update it with command line arguments for STL file usage.