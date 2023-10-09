import numpy as np
import cv2

class Nail:
    def __init__(self, size, x, y):
        self.height = size
        self.width = size
        self.x = x
        self.y = y
        self.lines = []
    
    def addLine(self, toNail, color = (0, 0, 0, 128), thickness = 1):
        x = toNail.x
        y = toNail.y
        lineImage = np.zeros((self.width, self.height, 4), dtype=np.uint8)
        lineImage = cv2.line(lineImage, (self.x, self.y), (x, y), color, thickness)
        # lineImage = cv2.GaussianBlur(lineImage, (3, 3), 0)
        self.lines.append((toNail, lineImage))