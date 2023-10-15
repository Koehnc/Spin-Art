import math
import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim
from Nail import Nail

class Spinboard:
    def __init__(self, goalImage, numNails = None, nails = None, resultImage = "Spinboard.png"):
        self.goalImage = cv2.imread(goalImage, cv2.IMREAD_UNCHANGED)
        self.resultImage = resultImage
        # radius * 2 is the same as the width and height for a square
        self.radius = int(self.goalImage.shape[0] / 2)
        self.nails = nails
        self.numNails = numNails
        self.currentNail = None
        self.image = np.zeros((self.radius*2, self.radius*2, 4), dtype=np.uint8)

        # Reset the result image
        height, width, _ = cv2.imread(self.resultImage).shape  # Get the dimensions of the original image
        transparent_background = np.zeros((height, width, 4), dtype=np.uint8)  # Create an RGBA image (4 channels) with all zeros
        cv2.imwrite(resultImage, transparent_background)  # Save the result to a new image file

        # init self.nails
        if (nails == None):
            # init the starting circle
            color = (255, 255, 255, 255)  # White color in RGBA format (full opacity)
            cv2.circle(self.image, (self.radius, self.radius), self.radius, color, thickness=-1)  # -1 for a filled circle

            self.nails = []
            if (self.numNails == None):
                self.numNails = 50
            for i in range(0, self.numNails):
                self.nails.append(Nail(self.radius * 2, int(math.cos(math.radians(float(i) / self.numNails * 360)) * self.radius + self.radius), int(math.sin(math.radians(float(i) / self.numNails * 360)) * self.radius + self.radius)))
            self.currentNail = self.nails[0]
        else:
            self.nails = []
            for i in range(0, len(nails)):
                self.nails.append(Nail(self.radius * 2, nails[i][0], nails[i][1]))
            self.numNails = len(self.nails)


        # Draw the nails and add the lines to each nail
        color = (75, 75, 75, 255)
        for nail in self.nails:
            cv2.circle(self.image, (nail.x, nail.y), 3, color, thickness=-1)  # -1 for a filled circle
            for otherNail in self.nails:
                if nail == otherNail: continue
                nail.addLine(otherNail)

    def display(self):
        cv2.imwrite(self.resultImage, self.image)

    def addNail(self, newNailTuple):
        newNail = Nail(self.radius * 2, newNailTuple[0], newNailTuple[1])
        if (self.nails.count(newNail) > 0):
            return
        color = (75, 75, 75, 255)
        cv2.circle(self.image, (newNail.x, newNail.y), 3, color, thickness=-1)  # -1 for a filled circle
        # Draw the nails and add the lines to each nail
        for nail in self.nails:
            nail.addLine(newNail)
            newNail.addLine(nail)
        self.nails.append(newNail)
        self.numNails += 1
        self.currentNail = newNail
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

# spinboard = Spinboard("images/result.png", nails=[])
# spinboard.drawLines(100000)
# spinboard.display()