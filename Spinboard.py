import math
import random
import numpy as np
import cv2
from Nail import Nail

class Spinboard:
    def __init__(self, goalImage, numNails = None, nails = None, resultImage = "Spinboard.png"):
        self.goalImage = cv2.imread(goalImage, cv2.IMREAD_UNCHANGED)
        self.resultImage = resultImage
        # radius * 2 is the same as the width and height for a square
        self.width = self.goalImage.shape[0]
        self.height = self.goalImage.shape[1]
        self.radius = min(int(self.width / 2), int(self.height / 2))
        self.nails = nails
        self.numNails = numNails
        self.currentNail = None
        self.image = np.ones((self.width, self.height, 4), dtype=np.uint8) * 255
        self.display()

        # init self.nails
        if (nails == None):
            # init the starting circle
            self.image = np.zeros((self.width, self.height, 4), dtype=np.uint8)
            color = (255, 255, 255, 255)  # White color in RGBA format (full opacity)
            # cv2.circle(self.image, (self.radius, self.radius), self.radius, color, thickness=-1)  # -1 for a filled circle
            cv2.ellipse(self.image, (int(self.height / 2), int(self.width / 2)), (int(self.height / 2), int(self.width / 2)), 0, 0, 360, color, -1)

            self.nails = []
            if (self.numNails == None):
                self.numNails = 50
            self.nails = []
            a = self.width / 2  # Semi-major axis
            b = self.height / 2  # Semi-minor axis

            for i in range(self.numNails):
                angle = 2 * math.pi * i / self.numNails
                x = b * math.cos(angle)  # Calculate x-coordinate
                y = a * math.sin(angle)  # Calculate y-coordinate
                self.addNail((int(x + b), int(y + a)))  # Offset by the center of the rectangle
                self.numNails -= 1
            self.currentNail = self.nails[0]
        else:
            self.nails = []
            for i in range(0, len(nails)):
                self.addNail((nails[i][0], nails[i][1]))
            self.numNails = len(self.nails)

    def display(self):
        cv2.imwrite(self.resultImage, self.image)

    def addNail(self, newNailTuple):
        newNail = Nail(self.width, self.height, newNailTuple[0], newNailTuple[1])
        if (self.nails.count(newNail) > 0):
            return
        color = (75, 75, 75, 255)
        cv2.circle(self.image, (newNail.x, newNail.y), 3, color, thickness=-1)  # -1 for a filled circle
        # Draw the nails and add the lines to each nail
        for nail in self.nails:
            # This only adds the line if the pixels are too close, which could fuck up none circle/ellipse
            if math.sqrt((nail.x - newNail.x) ** 2 + (nail.y - newNail.y) ** 2) > 20:
                nail.addLine(newNail)
                newNail.addLine(nail)
        self.nails.append(newNail)
        self.currentNail = newNail
        self.numNails += 1
        self.display()

    def getNumNails(self):
        return self.numNails

    def drawLines(self, numLines):
        for i in range(numLines):
            print(self.getNextNail())
            self.display()

    def getNextNail(self):
        bestLine = min(self.currentNail.lines, key=self.getBestLine)
        self.image = self.drawLine(bestLine[1])
        self.currentNail = bestLine[0]
        return self.getDifferenceMean(self.image)

    def getBestLine(self, line):
        return self.getDifferenceMean(self.drawLine(line[1]))

    def drawLine(self, line):
        image = self.image.copy().astype(float)
        line = line.astype(float)
        
        alpha = image[:, :, 3] / 255
        line_alpha = line[:, :, 3] / 255
        
        new_alpha = (alpha + line_alpha - alpha * line_alpha) * 255
        new_pixels = (image[:, :, :3] * alpha[:, :, np.newaxis] * (1 - line_alpha[:, :, np.newaxis]) + line[:, :, :3] * line_alpha[:, :, np.newaxis])
        
        result = np.zeros_like(image)
        result[:, :, :3] = new_pixels
        result[:, :, 3] = new_alpha
        
        return result.astype(np.uint8)
        
    '''
    Gets the difference/error from the given image to the goalImage that is a
    class attribute
    '''
    def getDifferenceMean(self, image):
        # Extract the RGB channels from the images
        image_channels = image[:, :, :3]
        goal_image_channels = self.goalImage[:, :, :3]

        # Calculate the absolute difference for each channel
        abs_diff = np.abs(image_channels - goal_image_channels)

        # Calculate the mean of the masked absolute differences
        mean_diff = np.mean(abs_diff)

        return mean_diff

# spinboard = Spinboard("images/result.png", nails=[])
# for i in range(50):
#     spinboard.addNail((random.randint(0, 360), random.randint(0, 360)))
# spinboard.drawLines(100000)
# spinboard.display()