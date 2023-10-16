import cv2
import numpy as np
import math

'''
This class is only meant to edit the output image into a black and white
circle that can be used to compare in the Spinboard class
'''
class ImageEdittor:
    def __init__(self, image, output = "images/result.png"):
        self.name = output
        self.image = cv2.imread(image, cv2.IMREAD_UNCHANGED)
        self.height, self.width, _ = self.image.shape

    def getImage(self):
        return self.image

    def addBackground(self):
        for row in range(len(self.image)):
            for pixel in range(len(self.image[row])):
                if self.image[row][pixel][3] == 0:
                    self.image[row][pixel] = [255, 255, 255, 255]
        cv2.imwrite(self.name, self.image)

    def blackAndWhite(self):
        for row in range(len(self.image)):
            for pixel in range(len(self.image[row])):
                avg = int((int(self.image[row][pixel][0]) + int(self.image[row][pixel][1]) + int(self.image[row][pixel][2])) / 3)
                if len(self.image[row][pixel]) == 3:   
                    self.image[row][pixel] = [avg, avg, avg]
                else:
                    self.image[row][pixel] = [avg, avg, avg, self.image[row][pixel][3]]
        cv2.imwrite(self.name, self.image)

    def invert(self):
        for row in range(len(self.image)):
            for pixel in range(len(self.image[row])):
                avg = int((int(self.image[row][pixel][0]) + int(self.image[row][pixel][1]) + int(self.image[row][pixel][2])) / 3)
                if len(self.image[row][pixel]) == 3:   
                    self.image[row][pixel] = [abs(avg - 255), abs(avg - 255), abs(avg - 255)]
                else:
                    self.image[row][pixel] = [abs(avg - 255), abs(avg - 255), abs(avg - 255), self.image[row][pixel][3]]
        cv2.imwrite(self.name, self.image)

    '''
    Max circle crop is when radius = half the height or width obviously
    '''
    def cropCircle(self, radius = None, center = None):
        # Default for value dependent on self
        if radius == None: radius = self.width / 2
        if center == None: center = (self.width / 2, self.height / 2)

        for row in range(len(self.image)):
            for pixel in range(len(self.image[row])):
                y = row - center[1]
                x = pixel - center[0]
                if (math.sqrt(x**2 + y**2) > radius):
                    if len(self.image[row][pixel]) == 3:   
                        self.image[row][pixel] = [0, 0, 0]
                    else:
                        self.image[row][pixel] = [0, 0, 0, 0]
        cv2.imwrite(self.name, self.image)
        return radius

edit = ImageEdittor("images/CreepyWitch.png")
# edit.addBackground()
edit.blackAndWhite()
# edit.invert()
# edit.cropCircle(100, (180, 130))
# edit.cropCircle()