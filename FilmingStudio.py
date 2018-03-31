import cv2

def scan(scene, color = "bgr", channel = "all"):
    scan = scene.read()[1]
    if color is "hsv": scan = cv2.cvtColor(scan, cv2.COLOR_BGR2HSV)
    elif color is "luv": scan = cv2.cvtColor(scan, cv2.COLOR_BGR2LUV)
    elif color is "lab": scan = cv2.cvtColor(scan, cv2.COLOR_BGR2LAB)
    elif color is "gray": scan = cv2.cvtColor(scan, cv2.COLOR_BGR2GRAY)
    elif color is "bgr": pass
    else: print("Specified color unavailable - fallback is bgr")

    if channel is not "all": return scan[:,:,channel]
    else: return scan

def shrink(image, amount = 1):
    for i in range(amount): image = cv2.pyrDown(image)
    return image

def expand(image, amount = 1):
    for i in range(amount): image = cv2.pyrUp(image)
    return image

def camera(identifier, width = 1920, height = 1080):
    camera = cv2.VideoCapture(identifier)
    camera.set(3, width)
    camera.set(4, height)
    return camera
