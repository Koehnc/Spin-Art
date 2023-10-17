import math
import random
import numpy as np
import cv2

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
        self.lines = {}
        self.display()

        # Init the goal image
        # (This becomes an all black photo where the alpha channel is a fxn of BW intensity. Basically more black = more opaque)
        black_image = 255 * np.ones_like(self.goalImage)
        bw_goal_image = cv2.cvtColor(self.goalImage, cv2.COLOR_BGR2GRAY)
        result_image = cv2.cvtColor(black_image, cv2.COLOR_BGR2BGRA)
        result_image[:, :, 3] = 255 - bw_goal_image
        self.goalImage = result_image

        # init self.nails
        if (nails == None):
            # init the starting circle
            self.image = np.zeros((self.width, self.height, 4), dtype=np.uint8)
            color = (255, 255, 255, 255)  # White color in RGBA format (full opacity)
            cv2.ellipse(self.image, (int(self.height / 2), int(self.width / 2)), (int(self.height / 2), int(self.width / 2)), 0, 0, 360, color, -1)

            self.nails = []
            if (numNails == None):
                numNails = 50
            self.nails = []
            a = self.width / 2  # Semi-major axis
            b = self.height / 2  # Semi-minor axis

            for i in range(numNails):
                angle = 2 * math.pi * i / numNails
                x = b * math.cos(angle)  # Calculate x-coordinate
                y = a * math.sin(angle)  # Calculate y-coordinate
                self.addNail((int(x + b), int(y + a)))
            self.currentNail = self.nails[0]
        else:
            self.nails = []
            for i in range(0, len(nails)):
                self.addNail((nails[i][0], nails[i][1]))
            self.numNails = len(self.nails)

        # print("Number of lines: ", len(self.lines), "Should be summation of digits up to numNails: ", self.numNails)
                

    def display(self):
        cv2.imwrite(self.resultImage, self.image)

    def addNail(self, newNail):
        # Draw the nail
        color = (75, 75, 75, 255)
        cv2.circle(self.image, (newNail[0], newNail[1]), 3, color, thickness=-1)  # -1 for a filled circle

        # Calc the line and update it to self.lines
        color = (0, 0, 0, 64)
        thickness = 1
        whiteImage = np.zeros((self.width, self.height, 4), dtype=np.uint8)
        for nail in self.nails:
            lineImage = cv2.line(whiteImage.copy(), (nail[0], nail[1]), (newNail[0], newNail[1]), color, thickness)
            lineImage = cv2.GaussianBlur(lineImage, (3, 3), 0)
            self.lines[((nail[0], nail[1]), (newNail[0], newNail[1]))] = lineImage
        self.nails.append(newNail)
        self.currentNail = newNail
        self.numNails += 1
        self.display()

    def getNumNails(self):
        return self.numNails

    def drawLines(self, numLines):
        for i in range(numLines):
            if i % 100 == 0:
                print("iter:", i)
            self.display()
            self.getNextNail()
        print("Done!")

    def getNextNail(self):
        lines = [(key, line) for key, line in self.lines.items() if self.currentNail in key]
        bestLine = max(lines, key=self.getBestLine)
        # bestLine = max(self.currentNail.lines, key=self.getBestLine)
        self.image = self.drawLine(bestLine[1])
        self.goalImage = self.subtractLine(bestLine[1])
        if self.currentNail == bestLine[0][0]:
            self.currentNail = bestLine[0][1]
        else:
            self.currentNail = bestLine[0][0]
        return self.lineHeuristic(self.image)

    def getBestLine(self, line):
        return self.lineHeuristic(line[1])
    
    def lineHeuristic(self, line):
        alpha = line[:, :, 3] / 255
        goalAlpha = self.goalImage[:, :, 3] / 255

        return np.sum(alpha * goalAlpha) / alpha.size**2
    
    def subtractLine(self, line):
        alpha1 = self.goalImage[:, :, 3] / 255.0
        alpha2 = line[:, :, 3] / 255.0

        # resulting_alpha = alpha1 + alpha2 - (alpha1 * alpha2)     # This is "addition"
        resulting_alpha = alpha1 - alpha2 * .7
        resulting_alpha = np.maximum(resulting_alpha, 0)

        resulting_alpha *= 255
        resulting_alpha = resulting_alpha.astype(np.uint8)

        result = np.zeros((self.width, self.height, 4), dtype=np.uint8)
        result[:, :, :3] = self.goalImage[:, :, :3]
        result[:, :, 3] = resulting_alpha

        cv2.imwrite("EdittedGoalImage.png", result)
        return result

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

# spinboard = Spinboard("images/result.png", nails=[])
# for i in range(50):
#     spinboard.addNail((random.randint(0, 360), random.randint(0, 360)))
# spinboard.drawLines(100000)
# spinboard.display()