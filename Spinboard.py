import math
import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim
from Nail import Nail

class Spinboard:
    def __init__(self, goalImage, numNails):
        self.goalImage = cv2.imread(goalImage, cv2.IMREAD_UNCHANGED)
        self.numNails = numNails
        self.radius = int(self.goalImage.shape[0] / 2)
        self.nails = []
        self.currentNail = None
        self.image = np.zeros((self.radius*2, self.radius*2, 4), dtype=np.uint8)

        # init self.nails
        for i in range(0, numNails):
            self.nails.append(Nail(self.radius * 2, int(math.cos(math.radians(float(i) / numNails * 360)) * self.radius + self.radius), int(math.sin(math.radians(float(i) / numNails * 360)) * self.radius + self.radius)))
        self.currentNail = self.nails[0]

        # init the starting circle
        color = (255, 255, 255, 255)  # White color in RGBA format (full opacity)
        cv2.circle(self.image, (self.radius, self.radius), self.radius, color, thickness=-1)  # -1 for a filled circle

        # Draw the nails and add the lines to each nail
        color = (75, 75, 75, 255)
        for nail in self.nails:
            cv2.circle(self.image, (nail.x, nail.y), 3, color, thickness=-1)  # -1 for a filled circle
            for otherNail in self.nails:
                if nail == otherNail: continue
                nail.addLine(otherNail)

    def display(self):
        cv2.imwrite("Spinboard.png", self.image)

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
        # Create a mask for the circular region
        height, width, _ = image.shape
        x, y = np.meshgrid(np.arange(width), np.arange(height))
        mask = ((x - self.radius)**2 + (y - self.radius)**2) < self.radius**2

        # Extract the RGB channels from the images
        image_channels = image[:, :, :3]
        goal_image_channels = self.goalImage[:, :, :3]

        # Calculate the absolute difference for each channel
        abs_diff = np.abs(image_channels - goal_image_channels)

        # Apply the circular mask to the absolute difference
        abs_diff_masked = abs_diff[mask]

        # Calculate the mean of the masked absolute differences
        mean_diff = np.mean(abs_diff_masked)

        return mean_diff
        
    def getDifferenceSSIM(self, image):
        return ssim(image, self.goalImage, channel_axis=2)

spinboard = Spinboard("result.png", 100)
spinboard.drawLines(100000)
spinboard.display()