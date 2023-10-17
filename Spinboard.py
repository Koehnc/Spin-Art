import math
import random
import numpy as np
import cv2

'''
Progression:
 - Implement Weighting certain parts of the image
    - Start with blank image of that size, 128 is nothing, white is negative, black is positive, (-.5 during calc will be perfect)
 - Fix the Memory issue for starting with more nails
 - Implement multiple colors

Easier:
 - Comments :)
'''
class Spinboard:
    def __init__(self, goalImage, numNails = None, nails = None, resultImage = "Spinboard.png"):
        self.goalImage = cv2.imread(goalImage, cv2.IMREAD_UNCHANGED)
        self.resultImage = resultImage
        # radius * 2 is the same as the width and height for a square
        self.width = self.goalImage.shape[0]
        self.height = self.goalImage.shape[1]
        self.radius = min(int(self.width / 2), int(self.height / 2))
        self.nails = nails
        self.numNails = 0
        self.currentNail = None
        self.image = np.ones((self.width, self.height, 4), dtype=np.uint8) * 255
        self.lines = {}
        self.order = []
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
            if (numNails == 0):
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

    def addNail(self, newNail, addLines = True):
        # Draw the nail
        color = (75, 75, 75, 255)
        cv2.circle(self.image, (newNail[0], newNail[1]), 3, color, thickness=-1)  # -1 for a filled circle

        # Calc the line and update it to self.lines
        if (addLines):
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

    def drawLines(self, numLines):
        self.order.append(self.nails.index(self.currentNail))
        for i in range(numLines):
            if i % 100 == 0:
                print("iter:", i)
            self.display()
            self.order.append(self.nails.index(self.getNextNail()))
        print("Done!")
        print("Order: ", self.order)
        return self.order

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
        return self.currentNail

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

    def drawExisting(self, order, sizeFactor = 3):
        self.width = int(self.width * sizeFactor)
        self.height = int(self.height * sizeFactor)
        self.image = np.zeros((self.width, self.height, 4), dtype=np.uint8)
        color = (255, 255, 255, 255)  # White color in RGBA format (full opacity)
        cv2.ellipse(self.image, (int(self.height / 2), int(self.width / 2)), (int(self.height / 2), int(self.width / 2)), 0, 0, 360, color, -1)
        
        self.lines = {}
        self.nails = []
        a = self.width / 2  # Semi-major axis
        b = self.height / 2  # Semi-minor axis

        for i in range(self.numNails):
            angle = 2 * math.pi * i / self.numNails
            x = b * math.cos(angle)  # Calculate x-coordinate
            y = a * math.sin(angle)  # Calculate y-coordinate
            self.addNail((int(x + b), int(y + a)), False)
            self.numNails -= 1

        color = (0, 0, 0, 64)
        thickness = 1
        whiteImage = np.zeros((self.width, self.height, 4), dtype=np.uint8)
        for i in range(len(order) - 1):
            lineImage = cv2.line(whiteImage.copy(), (self.nails[order[i]][0], self.nails[order[i]][1]), (self.nails[order[i+1]][0], self.nails[order[i+1]][1]), color, thickness)
            lineImage = cv2.GaussianBlur(lineImage, (3, 3), 0)
            self.image = self.drawLine(lineImage)
            self.display()
        
        self.display()
            


# spinboard = Spinboard("images/Monroe_big.png", 100)
# # order = spinboard.drawLines(1250)
# spinboard.drawExisting([0, 50, 99, 54, 97, 53, 96, 43, 19, 85, 20, 86, 21, 87, 22, 88, 21, 84, 19, 86, 22, 63, 32, 64, 33, 66, 32, 65, 33, 67, 34, 64, 31, 62, 32, 61, 30, 60, 31, 63, 33, 8, 34, 66, 31, 61, 29, 59, 30, 64, 29, 
# 60, 32, 7, 33, 9, 35, 67, 36, 11, 37, 12, 36, 13, 38, 14, 39, 13, 37, 14, 36, 10, 35, 70, 27, 69, 26, 63, 25, 68, 35, 12, 38, 15, 39, 12, 34, 65, 31, 59, 28, 58, 29, 73, 30, 74, 24, 88, 23, 81, 18, 83, 19, 87, 23, 89, 22, 81, 21, 85, 23, 80, 18, 42, 95, 51, 0, 55, 3, 43, 20, 87, 24, 84, 18, 41, 17, 42, 94, 51, 92, 53, 9, 36, 70, 34, 7, 44, 5, 57, 29, 65, 35, 11, 45, 6, 33, 62, 30, 66, 35, 13, 40, 14, 39, 17, 80, 22, 84, 20, 89, 21, 82, 18, 79, 28, 71, 35, 8, 32, 67, 24, 80, 26, 68, 38, 59, 29, 72, 40, 15, 37, 67, 22, 82, 24, 63, 21, 90, 22, 83, 23, 77, 27, 65, 26, 77, 25, 81, 19, 88, 18, 85, 22, 79, 26, 64, 32, 9, 34, 63, 30, 58, 31, 75, 30, 60, 39, 16, 41, 94, 50, 99, 49, 98, 52, 95, 43, 9, 31, 76, 27, 64, 35, 69, 33, 12, 46, 13, 34, 68, 36, 65, 23, 90, 19, 42, 2, 54, 92, 61, 39, 59, 89, 58, 27, 78, 28, 70, 37, 11, 34, 69, 25, 82, 
# 23, 86, 18, 87, 21, 91, 53, 88, 20, 42, 4, 56, 3, 42, 96, 51, 93, 47, 92, 62, 25, 75, 28, 60, 38, 71, 34, 14, 41, 19, 82, 33, 13, 32, 6, 30, 57, 28, 77, 32, 63, 23, 79, 21, 83, 1, 52, 96, 49, 97, 43, 18, 89, 24, 78, 26, 74, 29, 69, 24, 81, 20, 83, 15, 84, 23, 78, 29, 63, 47, 62, 46, 8, 45, 12, 56, 14, 87, 15, 85, 24, 79, 17, 81, 0, 82, 1, 41, 12, 55, 92, 22, 43, 21, 45, 90, 60, 91, 19, 79, 25, 67, 35, 60, 41, 20, 44, 62, 34, 10, 54, 93, 63, 27, 68, 39, 58, 37, 66, 33, 11, 31, 7, 45, 61, 38, 58, 86, 16, 85, 1, 55, 91, 23, 70, 26, 76, 25, 83, 34, 72, 28, 64, 33, 59, 42, 21, 80, 99, 81, 1, 51, 91, 22, 45, 59, 30, 8, 53, 90, 24, 
# 77, 29, 6, 31, 62, 94, 54, 88, 15, 36, 73, 25, 65, 30, 9, 54, 98, 79, 20, 63, 35, 9, 46, 61, 41, 2, 40, 93, 74, 91, 61, 42, 58, 85, 13, 41, 6, 44, 21, 78, 25, 88, 57, 39, 18, 37, 71, 40, 12, 32, 76, 36, 72, 38, 
# 69, 32, 81, 27, 71, 39, 62, 45, 58, 90, 73, 89, 15, 86, 1, 84, 0, 80, 19, 92, 46, 60, 40, 21, 77, 31, 13, 55, 4, 56, 83, 17, 82, 99, 83, 24, 73, 35, 74, 92, 23, 44, 10, 33, 14, 89, 60, 43, 2, 52, 4, 43, 23, 93, 
# 22, 46, 65, 28, 68, 33, 7, 30, 12, 37, 9, 29, 56, 86, 24, 75, 36, 64, 48, 95, 41, 57, 84, 16, 88, 73, 26, 75, 92, 56, 36, 69, 28, 82, 2, 87, 52, 94, 65, 47, 61, 40, 63, 28, 8, 31, 5, 32, 59, 41, 93, 55, 82, 20, 
# 78, 17, 37, 10, 85, 0, 83, 3, 41, 56, 5, 53, 1, 80, 98, 81, 33, 15, 35, 84, 17, 43, 12, 47, 66, 21, 93, 59, 35, 62, 32, 11, 46, 7, 35, 55, 84, 99, 79, 0, 54, 81, 2, 88, 72, 41, 21, 46, 91, 75, 27, 66, 48, 62, 20, 80, 31, 12, 29, 8, 34, 67, 38, 55, 43, 24, 76, 18, 36, 74, 90, 15, 79, 97, 44, 63, 48, 61, 30, 13, 86, 0, 41, 73, 92, 40, 1, 39, 77, 22, 40, 57, 4, 84, 6, 51, 79, 32, 49, 31, 74, 94, 70, 33, 78, 18, 83, 14, 31, 10, 32, 78, 39, 63, 46, 58, 36, 67, 21, 64, 93, 19, 45, 57, 37, 68, 91, 76, 90, 61, 33, 83, 98, 82, 27, 59, 44, 22, 42, 7, 88, 1, 83, 7, 51, 38, 1, 87, 71, 85, 2, 53, 6, 28, 9, 86, 73, 15, 91, 24, 66, 46, 23, 
# 40, 68, 23, 42, 57, 34, 6, 87, 59, 47, 94, 22, 69, 95, 54, 42, 12, 36, 19, 85, 72, 89, 4, 31, 64, 45, 66, 89, 1, 81, 29, 71, 86, 14, 30, 79, 52, 85, 25, 45, 9, 42, 73, 38, 18, 73, 91, 5, 30, 11, 55, 41, 65, 48, 
# 60, 37, 76, 93, 61, 25, 74, 87, 10, 36, 8, 27, 72, 84, 98, 44, 96, 71, 36, 66, 23, 95, 77, 93, 49, 63, 19, 89, 6, 57, 46, 2, 86, 7, 29, 13, 39, 70, 95, 22, 76, 30, 48, 67, 31, 69, 93, 75, 35, 14, 55, 28, 5, 43, 
# 54, 3, 82, 56, 40, 62, 24, 42, 60, 47, 23, 94, 63, 38, 21, 62, 87, 0, 88, 75, 94, 39, 11, 47, 64, 19, 77, 92, 24, 46, 59, 91, 45, 20, 86, 74, 89, 67, 49, 33, 65, 45, 60, 34, 84, 10, 30, 69, 81, 5, 58, 48, 29, 14, 32, 7, 91, 56, 13, 83, 71, 88, 10, 28, 12, 54, 39, 93, 6, 43, 73, 93, 42, 8, 52, 40, 24, 44, 4, 87, 72, 24, 94, 55, 97, 80, 15, 78, 99, 44, 61, 49, 62, 26, 83, 29, 5, 92, 63, 18, 35, 61, 31, 48, 96, 23, 38, 17, 76, 89, 2, 39, 69, 15, 41, 53, 80, 70, 84, 7, 26, 84, 73, 34, 64, 25, 87, 99, 85, 5, 27, 57, 38, 54, 28, 73, 17, 33, 6, 58, 93, 62, 86, 4, 90, 67, 23, 45, 56, 15, 94, 61, 43, 25, 84, 14, 43, 94, 77, 16, 40, 73, 83, 55, 81, 70, 86, 98, 79, 27, 12, 85, 11, 29, 55, 37, 59, 48, 32, 18, 75, 15, 81, 6, 52, 41, 62, 29, 70, 32, 52, 3, 88, 65, 22, 37, 65, 49, 59, 43, 8, 82, 34, 19, 62, 91, 2, 90, 0, 38, 93, 10, 89, 63, 36, 17, 40, 9, 27, 6, 85, 74, 20, 66, 85, 29, 80, 13, 57, 47, 8, 26, 67, 47, 22, 36, 50, 63, 33, 67, 88, 6, 94, 66, 50, 38, 11, 86, 72, 83, 70, 93, 2, 84, 13, 45, 97, 81, 71, 15, 57, 44, 25, 40, 59, 36, 23, 71, 82, 14, 28, 66, 91, 1, 54, 6, 50, 61, 36, 11, 42, 53, 93, 24, 68, 14, 69, 79, 16, 42, 62, 22, 38, 20, 33, 60, 24, 64, 92, 76, 88, 98, 85, 9, 94, 48, 69, 94, 5, 83, 11, 41, 68, 90, 77, 91, 39, 19, 35, 72, 91, 9, 47, 56, 28, 7, 87, 70, 85, 35, 23, 73, 82, 30, 49, 58, 41, 63, 95, 62, 18, 74, 21, 37, 69, 47, 3, 89, 99, 53, 43, 13, 88, 5, 45, 55, 2, 92, 57, 83, 74, 38, 13, 27, 14, 79, 33, 8, 87, 30, 4, 41, 66, 52, 39, 72, 33, 23, 5, 86, 75, 14, 54, 34, 49, 66, 29, 10, 78, 0, 89, 56], 1/3)