import numpy as np
from cv2 import (
    warpAffine,
    getOptimalDFTSize,
    getRectSubPix,
    createHanningWindow,
    GaussianBlur,
    mulSpectrums,
    minMaxLoc,
    rectangle,
    dft,
    idft,
    BORDER_REFLECT,
    CV_32F,
    DFT_SCALE,
    DFT_REAL_OUTPUT,
    DFT_COMPLEX_OUTPUT,
)

def rnd_warp(a):
    height, width = a.shape[:2]
    T = np.zeros((2,3))
    coefficient = 0.2
    angle = (np.random.rand() - 0.5)*coefficient
    cos, sin = np.cos(angle), np.sin(angle)
    T[:2,:2] = [[cos, -sin], [sin, cos]]
    T[:2,:2] += (np.random.rand(2,2) - 0.5)*coefficient
    cos = (width/2, height/2)
    T[:, 2] = cos - np.dot(T[:2,:2], cos)
    return warpAffine(a, T, (width, height), borderMode = BORDER_REFLECT)

def divSpec(A, B):
    Ar, Ai = A[...,0], A[...,1]
    Br, Bi = B[...,0], B[...,1]
    C = (Ar + 1j*Ai)/(Br + 1j*Bi)
    return np.dstack([np.real(C), np.imag(C)]).copy()#TODO need copy()?

eps = 1e-5

class Tracker(object):
    def __init__(self, image, rectangle):
        x1, y1, x2, y2 = rectangle
        width, height = map(getOptimalDFTSize, [x2 - x1, y2 - y1])
        x1, y1 = (x1 + x2 - width)//2, (y1 + y2 - height)//2
        self.position = x, y = x1 + 0.5*(width - 1), y1 + 0.5*(height - 1)
        self.size = width, height
        roi = getRectSubPix(image, (width, height), (x, y))

        self.window = createHanningWindow((width, height), CV_32F)
        g = np.zeros((height, width), dtype = "float32")
        g[height//2, width//2] = 1
        g = GaussianBlur(g, (-1, -1), 2.0)
        g /= g.max()

        self.G = dft(g, flags = DFT_COMPLEX_OUTPUT)
        self.H1 = np.zeros_like(self.G)
        self.H2 = np.zeros_like(self.G)
        for i in range(128):
            a = self.preprocess(rnd_warp(roi))
            A = dft(a, flags = DFT_COMPLEX_OUTPUT)
            self.H1 += mulSpectrums(self.G, A, 0, conjB = True)
            self.H2 += mulSpectrums(     A, A, 0, conjB = True)
        self.update_kernel()
        self.update(image)

    @property
    def visualizer(self):
        f = idft(self.H, flags = DFT_SCALE | DFT_REAL_OUTPUT)
        height, width = f.shape
        f = np.roll(f, -height//2, 0)
        f = np.roll(f, -width//2, 1)
        kernel = (f - f.min())/(f.ptp()*255)
        resp = self.last_resp
        resp = np.clip(resp/resp.max(), 0, 1)*255
        return np.hstack([self.last_roi, kernel.astype("uint8"), resp.astype("uint8")])

    def preprocess(self, roi):
        roi = np.log(roi.astype("float32") + 1.0)
        roi = (roi - roi.mean())/(roi.std() + eps)
        return roi*self.window

    def correlate(self, roi):
        C = mulSpectrums(dft(roi, flags = DFT_COMPLEX_OUTPUT), self.H, 0, conjB = True)
        resp = idft(C, flags = DFT_SCALE | DFT_REAL_OUTPUT)
        height, width = resp.shape
        _, mval, _, (mx, my) = minMaxLoc(resp)
        resp_side = resp.copy()
        rectangle(resp_side, (mx - 5, my - 5), (mx + 5, my + 5), 0, -1)
        smean, sstd = resp_side.mean(), resp_side.std()
        psr = (mval - smean)/(sstd + eps)
        return resp, (mx - width//2, my - height//2), psr

    def update(self, image, rate = 0.125):
        (x, y), (width, height) = self.position, self.size
        self.last_roi = roi = getRectSubPix(image, (width, height), (x, y))
        roi = self.preprocess(roi)
        self.last_resp, (dx, dy), self.psr = self.correlate(roi)
        self.good = self.psr > 6.0
        if not self.good:
            return

        self.position = x + dx, y + dy
        self.last_roi = roi = getRectSubPix(image, (width, height), self.position)
        roi = self.preprocess(roi)

        A = dft(roi, flags = DFT_COMPLEX_OUTPUT)
        H1 = mulSpectrums(self.G, A, 0, conjB=True)
        H2 = mulSpectrums(     A, A, 0, conjB=True)
        self.H1 = self.H1*(1.0 - rate) + H1*rate
        self.H2 = self.H2*(1.0 - rate) + H2*rate
        self.update_kernel()

    def update_kernel(self):
        self.H = divSpec(self.H1, self.H2)
        self.H[...,1] *= -1
