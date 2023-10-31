import math
import random
import numpy as np
import cv2
import time
import sys

'''
Progression:
 - Fix the Memory issue for starting with more nails

Easier:
 - Comments :)
 - Update UI
    - Add from existing order
    - Add Color option

Important Notes:
 - The amount that the line affects the image is related to the opacity of line, but more importantly the line shape itself
 - This also affects the line heuristic function interestingly enough
 - 
 - Color of thread shouldn't change the order that the threads are put on
'''
class Spinboard:
    def __init__(self, goalImage, numNails = None, nails = None, resultImage = "Spinboard.png", weightedImage = None, threadColor = (0, 0, 0, 60), replacedColor = (0, 0, 0)):
        self.goalImage = cv2.imread(goalImage, cv2.IMREAD_UNCHANGED)
        self.resultImage = resultImage
        self.weights = weightedImage
        self.width = self.goalImage.shape[0]
        self.height = self.goalImage.shape[1]
        self.radius = min(int(self.width / 2), int(self.height / 2))
        self.nails = nails
        self.numNails = 0
        self.currentNail = None
        self.image = np.ones((self.width, self.height, 4), dtype=np.uint8) * 255
        self.lines = {}
        self.order = []
        self.threadColor = threadColor
        self.display()


        self.initGoalImage(replacedColor)
        self.initWeights()
        self.initNails(nails, numNails)

    def initGoalImage(self, color):
        whiteImage = 255 * np.ones_like(self.goalImage)

        euclidean_distance = np.linalg.norm(self.goalImage[:, :, :3] - np.array(color), axis=-1)
        euclidean_distance /= np.max(euclidean_distance)
        euclidean_distance *= 255
                    
        self.goalImage = cv2.cvtColor(whiteImage, cv2.COLOR_BGR2BGRA)
        self.goalImage[:, :, 3] = 255 - euclidean_distance

    def initWeights(self):
        # Init the weightedImage/self.weights
        if (self.weights == None):
            self.weights = 255 * np.ones_like(self.goalImage)
        else:
            self.weights = cv2.imread(self.weights, cv2.IMREAD_UNCHANGED)
            white_image = 255 * np.ones_like(self.goalImage)
            bw_goal_image = cv2.cvtColor(self.weights, cv2.COLOR_BGR2GRAY)
            self.weights = cv2.cvtColor(white_image, cv2.COLOR_BGR2BGRA)
            self.weights[:, :, 3] = 255 - bw_goal_image
            cv2.imwrite("WeightedImage.png", self.weights)
        self.goalImage = self.goalImage * (self.weights / 255)

    def initNails(self, nails, numNails):
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

    def convertToMatrix(self, image):
        return image[:, :, 3]

    def convertToImage(self, matrix):
        height, width = matrix.shape
        image = np.full((height, width, 4), self.threadColor, dtype=np.uint8)
        image[:, :, 3] = matrix
        return image

    def display(self):
        cv2.imwrite(self.resultImage, self.image)

    def addNail(self, newNail, addLines = True):
        # Draw the nail
        color = (75, 75, 75, 255)
        cv2.circle(self.image, (newNail[0], newNail[1]), 3, color, thickness=-1)  # -1 for a filled circle

        # Calc the line and update it to self.lines
        if (addLines):
            for nail in self.nails:
                whiteImage = np.zeros((self.width, self.height, 4), dtype=np.uint8)

                thickness = 2
                color = tuple(value / 3 if i == 3 else value for i, value in enumerate(self.threadColor))
                lineImage = cv2.line(whiteImage, (nail[0], nail[1]), (newNail[0], newNail[1]), color, thickness)

                thickness = 1
                lineImage = cv2.line(whiteImage, (nail[0], nail[1]), (newNail[0], newNail[1]), self.threadColor, thickness)

                lineImage = self.convertToMatrix(lineImage)
                self.lines[((nail[0], nail[1]), (newNail[0], newNail[1]))] = lineImage
        self.nails.append(newNail)
        self.currentNail = newNail
        self.numNails += 1
        self.display()

    def drawLines(self, numLines):
        start = time.time()
        self.order.append(self.nails.index(self.currentNail))
        for i in range(numLines):
            if i % 100 == 0:
                print("iter:", i)
            self.display()
            self.order.append(self.nails.index(self.getNextNail()))
        end = time.time()
        print("Done!", end - start, "seconds")
        print("Order: ", self.order)
        return self.order

    def getNextNail(self):
        lines = [(key, line) for key, line in self.lines.items() if self.currentNail in key]
        bestLine = max(lines, key=self.getBestLine)
        self.image = self.drawLine(bestLine[1])
        self.goalImage = self.subtractLine(bestLine[1])
        if self.currentNail == bestLine[0][0]:
            self.currentNail = bestLine[0][1]
        else:
            self.currentNail = bestLine[0][0]
        return self.currentNail

    def getBestLine(self, line):
        # whiteImage = np.zeros((self.width, self.height, 4), dtype=np.uint8)
        # lineImage = cv2.line(whiteImage, (line[0][0][0], line[0][0][1]), (line[0][1][0], line[0][1][1]), (0, 0, 0, 64), 1)
        # lineImage = cv2.GaussianBlur(lineImage, (3, 3), 0)
        # lineImage = self.convertToMatrix(lineImage)

        return self.lineHeuristic(line[1])
        
    def lineHeuristic(self, line):
        alpha = line / 255
        goalAlpha = self.goalImage[:, :, 3] / 255
        # weightedAlpha = self.weights[:, :, 3] / 255

        return np.sum(alpha * goalAlpha) / alpha.size**2
    
    def subtractLine(self, line):
        alpha1 = self.goalImage[:, :, 3] / 255.0
        alpha2 = line / 255.0

        # resulting_alpha = alpha1 + alpha2 - (alpha1 * alpha2)     # This is "addition"
        resulting_alpha = alpha1 - alpha2 * .5
        resulting_alpha = np.maximum(resulting_alpha, 0)

        resulting_alpha *= 255
        resulting_alpha = resulting_alpha.astype(np.uint8)

        result = np.zeros((self.width, self.height, 4), dtype=np.uint8)
        result[:, :, :3] = self.goalImage[:, :, :3]
        result[:, :, 3] = resulting_alpha

        cv2.imwrite("EdittedGoalImage.png", result)
        return result

    def drawLine(self, line):
        line = line.astype(float)
        
        alpha = self.image[:, :, 3] / 255.0
        line_alpha = line / 255.0
        
        new_alpha = (alpha + line_alpha - alpha * line_alpha) * 255

        # Make sure that self.threadColor has the same number of channels as the image (BGRA)
        line_color = np.array(self.threadColor, dtype=np.uint8)
        new_pixels = (self.image[:, :, :3] * alpha[:, :, np.newaxis] * (1 - line_alpha[:, :, np.newaxis])) + (line_color[:3] * line_alpha[:, :, np.newaxis])

        result = np.zeros_like(self.image)
        result[:, :, :3] = new_pixels
        result[:, :, 3] = new_alpha
        
        return result.astype(np.uint8)

    def drawExisting(self, order, sizeFactor = 3):
        self.width = int(self.width * sizeFactor)
        self.height = int(self.height * sizeFactor)
        self.image = np.zeros((self.width, self.height, 4), dtype=np.uint8)
        color = (255, 255, 255, 255) 
        cv2.ellipse(self.image, (int(self.height / 2), int(self.width / 2)), (int(self.height / 2), int(self.width / 2)), 0, 0, 360, color, -1)
        
        self.lines = {}
        self.nails = []
        a = self.width / 2
        b = self.height / 2 

        for i in range(self.numNails):
            angle = 2 * math.pi * i / self.numNails
            x = b * math.cos(angle)
            y = a * math.sin(angle) 
            self.addNail((int(x + b), int(y + a)), False)
            self.numNails -= 1

        color = (0, 0, 0, 64)
        thickness = 1
        whiteImage = np.zeros((self.width, self.height, 4), dtype=np.uint8)
        for i in range(len(order) - 1):
            lineImage = cv2.line(whiteImage.copy(), (self.nails[order[i]][0], self.nails[order[i]][1]), (self.nails[order[i+1]][0], self.nails[order[i+1]][1]), color, thickness)
            lineImage = cv2.GaussianBlur(lineImage, (3, 3), 0)
            lineImage = self.convertToMatrix(lineImage)
            self.image = self.drawLine(lineImage)
            self.display()
        
        self.display()
            

# spinboard = Spinboard("images/Monroe_crop.png", 300)
# # order = spinboard.drawLines(1250)
# spinboard.drawExisting([0, 151, 298, 163, 291, 160, 28, 106, 201, 101, 193, 97, 197, 99, 191, 93, 185, 95, 199, 97, 22, 101, 33, 110, 37, 113, 41, 117, 44, 109, 39, 120, 215, 85, 176, 89, 180, 91, 223, 73, 264, 65, 260, 61, 256, 57, 251, 66, 243, 53, 126, 285, 154, 2, 124, 55, 253, 65, 267, 70, 242, 68, 249, 58, 129, 10, 166, 37, 137, 26, 103, 209, 82, 231, 78, 191, 103, 202, 74, 241, 55, 261, 57, 124, 51, 128, 284, 155, 292, 147, 295, 159, 274, 182, 87, 218, 84, 207, 93, 178, 115, 35, 99, 195, 103, 30, 134, 18, 98, 39, 103, 189, 79, 239, 71, 248, 62, 270, 56, 252, 46, 257, 66, 190, 140, 185, 276, 165, 279, 122, 5, 125, 183, 114, 203, 99, 247, 2, 243, 63, 268, 174, 91, 19, 131, 63, 232, 76, 207, 87, 178, 267, 44, 261, 170, 13, 168, 274, 137, 187, 85, 229, 80, 210, 109, 174, 117, 57, 239, 75, 234, 72, 245, 297, 241, 69, 130, 288, 159, 25, 106, 194, 77, 220, 272, 55, 257, 174, 126, 65, 137, 180, 117, 170, 251, 1, 254, 62, 245, 52, 113, 215, 106, 38, 93, 226, 81, 188, 107, 201, 94, 26, 89, 205, 98, 20, 263, 218, 276, 152, 282, 163, 120, 7, 265, 215, 87, 175, 113, 187, 132, 170, 270, 223, 83, 219, 259, 45, 97, 24, 140, 178, 104, 201, 65, 276, 44, 263, 54, 275, 224, 280, 184, 143, 199, 110, 31, 93, 41, 101, 211, 287, 126, 160, 263, 10, 249, 295, 237, 81, 15, 132, 191, 279, 141, 174, 120, 66, 247, 211, 69, 269, 202, 101, 192, 108, 176, 115, 165, 247, 13, 93, 229, 274, 15, 85, 216, 256, 0, 239, 67, 135, 185, 260, 59, 250, 3, 157, 122, 37, 87, 28, 130, 72, 237, 97, 207, 243, 
# 293, 253, 28, 95, 228, 76, 233, 285, 144, 174, 124, 191, 135, 16, 99, 213, 88, 192, 63, 138, 5, 270, 42, 85, 32, 129, 165, 11, 118, 213, 260, 22, 95, 146, 189, 111, 68, 245, 20, 271, 201, 140, 160, 241, 294, 259, 224, 253, 48, 93, 24, 135, 171, 126, 35, 168, 9, 276, 7, 124, 68, 189, 280, 207, 235, 74, 128, 286, 157, 15, 272, 231, 79, 24, 104, 199, 148, 183, 115, 68, 132, 21, 103, 216, 249, 203, 266, 215, 243, 5, 162, 284, 201, 274, 67, 140, 163, 37, 82, 220, 47, 255, 176, 95, 36, 140, 168, 120, 186, 282, 20, 267, 226, 109, 197, 91, 53, 107, 205, 78, 16, 150, 299, 259, 27, 76, 222, 279, 194, 111, 171, 15, 287, 10, 122, 160, 137, 181, 251, 65, 235, 215, 185, 99, 18, 276, 227, 263, 40, 117, 163, 201, 90, 41, 280, 7, 138, 39, 165, 111, 72, 203, 235, 270, 134, 194, 247, 207, 67, 250, 51, 85, 203, 95, 188, 113, 46, 258, 30, 285, 213, 243, 69, 97, 145, 91, 195, 105, 176, 267, 297, 253, 178, 151, 115, 3, 239, 218, 78, 41, 272, 293, 162, 27, 91, 238, 207, 174, 272, 26, 265, 180, 126, 157, 199, 84, 57, 10, 290, 265, 232, 260, 203, 247, 60, 258, 106, 70, 205, 43, 265, 293, 39, 130, 160, 186, 249, 103, 143, 170, 16, 122, 183, 97, 21, 111, 200, 93, 70, 18, 285, 39, 87, 208, 232, 92, 222, 243, 197, 165, 281, 121, 43, 82, 234, 259, 13, 290, 276, 24, 87, 256, 235, 215, 191, 263, 157, 135, 271, 51, 10, 124, 219, 55, 85, 65, 208, 278, 118, 187, 165, 180, 111, 59, 237, 153, 21, 89, 33, 134, 18, 160, 140, 276, 290, 130, 9, 290, 209, 180, 20, 115, 172, 13, 158, 235, 256, 209, 194, 95, 24, 120, 135, 174, 160, 201, 263, 57, 113, 97, 189, 53, 242, 15, 279, 265, 49, 117, 282, 221, 207, 191, 109, 93, 82, 195, 12, 24, 10, 287, 276, 265, 230, 89, 47, 170, 185, 174, 163, 124, 181, 100, 261, 243, 259, 247, 235, 211, 45, 261, 291, 192, 56, 81, 204, 109, 93, 15, 128, 140, 280, 290, 276, 265, 33, 117, 126, 137, 189, 203, 215, 203, 191, 174, 163, 174, 185, 174, 111, 143, 163, 296, 110, 97, 85, 93, 217, 29, 235, 247, 259, 63, 240, 70, 197, 274, 24, 10, 44, 57, 41, 53, 261, 194, 122, 276, 265, 189, 160, 82, 93, 109, 97, 109, 228, 243, 235, 243, 253, 243, 205, 257, 295, 149, 95, 196, 60, 186, 174, 163, 174, 185, 174, 163, 117, 126, 137, 126, 115, 126, 137, 28, 84, 65, 57, 41, 199, 113, 66, 200, 215, 207, 215, 207, 197, 207, 215, 235, 243, 259, 247, 28, 15, 24, 13, 7, 20, 249, 259, 247, 47, 272, 285, 276, 265, 276, 287, 276, 265, 276, 187, 203, 191, 203, 103, 114, 126, 137, 160, 299, 134, 32, 282, 141, 178, 262, 105, 187, 247, 259, 247, 237, 243, 235, 243, 211, 49, 87, 93, 85, 93, 109, 97, 57, 65, 53, 41, 24, 13, 290, 280, 290, 165, 174, 185, 174, 163, 174, 185, 174, 163, 156, 39, 24, 211, 94, 264, 253, 264, 276, 287, 276, 265, 276, 167, 14, 137, 126, 115, 126, 137, 144, 137, 126, 55, 254, 263, 172, 249, 261, 9, 59, 128, 34, 24, 13, 20, 10, 20, 13, 7, 185, 191, 203, 215, 207, 197, 186, 218, 207, 215, 207, 197, 187, 178, 185, 174, 163, 156, 163, 174, 185, 191, 203, 191, 185, 174, 163, 113, 103, 114, 103, 93, 85, 93, 85, 93, 109, 97, 109, 97, 231, 243, 247, 243, 235, 243, 247, 259, 247, 259, 265, 276, 287, 293, 287, 276, 265, 276, 285, 276, 265, 256, 247, 243, 235, 243, 247, 75, 111, 120, 111, 46, 37, 47, 57, 53, 41, 53, 57, 65, 57, 53, 41, 24, 35, 24, 15, 24, 287, 205, 89, 225])

# spinboard = Spinboard("images/Butterfly.png", 100, weightedImage="images/Butterfly_weights.png")
# order = spinboard.drawLines(2500)

# zombieEyes = Spinboard("images/zombie.png", numNails=100, weightedImage="images/zombieEyesWeight.png", threadColor=(210, 118, 25, 30), replacedColor=(0, 200, 255))
# order = zombieEyes.drawLines(300)
# cv2.imwrite("ZombieEyes.png", zombieEyes.image)
zombieFace = Spinboard("images/Butterfly_small.png", numNails=100, weightedImage="images/Butterfly_small_weights.png", threadColor=(0, 0, 0, 30), replacedColor=(0, 0, 0))
order = zombieFace.drawLines(700)
# cv2.imwrite("ZombieFace.png", zombieFace.image)
# cv2.imwrite("ZombieArt_Spinboard.png", cv2.addWeighted(cv2.imread("ZombieEyes.png"), .2, cv2.imread("ZombieFace.png"), .8, 0))