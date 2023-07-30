import sys
import os
import random

from enum import Enum
import imageio.v3 as imgio
import cv2 as cv
import numpy as np

IMAGES="../images/"

class Batch(Enum):
    ONE = "batch1"
    TWO = "batch2"

class RGBColor(Enum):
    RED     = (0, 0, 255)
    GREEN   = (0, 255, 0)
    BLUE    = (255, 0, 0)
    BRIGHT_TEAL = (0, 181, 184)

def getRandomImagePath(batch :Batch = Batch.ONE) -> str:
    "Gets a random image from batch 1 if batch is not specified."
    return IMAGES+batch.value+"/"+random.choice(os.listdir(IMAGES+batch.value))

def getImagePath(batch: str=Batch.ONE, index: int=0) -> str:
    "Gets the first image from batch 1 if batch and index are not specified."
    return IMAGES+batch.value+"/"+os.listdir(IMAGES+batch.value)[index]

class Xhand:
    def __init__(self, path: str = getRandomImagePath()):
        self.pure_image = cv.imread(path)

    def getOriginal(self) -> np.ndarray:
        return self.pure_image

    def getShape(self):
        return self.pure_image.shape

    def normalizeContrast(self) -> np.ndarray:
        """Takes in an image read by cv2.imread(path, 0) or imageio.imread(path)
        Changes the contrast by making sure the background is very dark and
        the foreground is very bright"""
        return cv.normalize(self.pure_image, np.zeros(self.pure_image.shape), 0, 255, cv.NORM_MINMAX)

    def getBinary(self, threshold_value: int = 23) -> np.ndarray:
        """
        This returns a binary image after performing thresholding.
        Threshold value is the value used to classify the pixel values.
        """
        img_grayscale = cv.cvtColor(self.pure_image, cv.COLOR_BGR2GRAY)
        threshold, binaryImg = cv.threshold(img_grayscale, threshold_value, 255, cv.THRESH_BINARY, dst=np.zeros(self.getShape()))
        return binaryImg

    def runBlobEtraction(self, connect:int = 4):
       """ returns (labelsCount, label_ids, stats, centroids)"""
       return cv.connectedComponentsWithStats(self.getBinary(), connect, cv.CV_32S)

    def getStatArea(self, stats):
        return stats[1][cv.CC_STAT_AREA]

    def getLargerstCC(self):
        labelsCount, label_ids, stats, centroids = self.runBlobEtraction()
        label, stat = max(enumerate(stats[1:], 1), key=self.getStatArea)
        return np.uint8(label_ids == label)*255

    def extractContours(self, threshold_value: int = 23):
        ret, thresh = cv.threshold(self.getLargerstCC(), threshold_value, 255, 0)
        contours, heirarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
        return contours

    def getWithContours(self, contorColor: RGBColor = RGBColor.BRIGHT_TEAL, indexOfContours: int = -1):
        newImage = self.getOriginal().copy()

        cv.drawContours(newImage, self.extractContours(), indexOfContours, contorColor.value, 2)
        return newImage

    def getConvexHull(self, returnPoints=True):
        hull = []
        contours = self.extractContours()

        for i in range(len(contours)):
            hull.append(cv.convexHull(contours[i], returnPoints))

        return hull

    def getWithConvexHull(self, hullColor: RGBColor = RGBColor.BLUE):
        newImage = self.getWithContours()
        hull = self.getConvexHull()
        contours = self.extractContours()

        for i in range(len(contours)):
            cv.drawContours(newImage, hull,i,hullColor.value, 1, 8)

        return newImage

    def getWithConvexityDefects(self, defectsColor: RGBColor = RGBColor.RED):
        contours = self.extractContours()
        points = []
        convexHulled = self.getWithConvexHull()

        for i in range(len(contours)):
            conv = cv.convexHull(contours[i], returnPoints=False)
            defects = cv.convexityDefects(contours[i], conv)
            if type(defects) != type(None):
                for j in range(defects.shape[0]):
                    try:
                        s,e,f,d = defects[j][0]
                        far = tuple(contours[i][f][0])
                        points.append(far)
                    except IndexError:
                        pass

        for point in points:
            cv.drawMarker(convexHulled, point, defectsColor.value, cv.MARKER_SQUARE)
        return convexHulled

def draw(processed: np.ndarray, original: np.ndarray = np.array([])) -> None:
    if  original.size == 0:
        cv.imshow("Processed", processed)
    else:
        stack = np.hstack((original, processed))
        cv.imshow("Processed", stack)
    cv.waitKey(0)
    cv.destroyAllWindows()

#try:
#    xImage = Xhand()
#    res = xImage.runBlobEtraction()
#    draw(xImage.getWithConvexityDefects())
#except Exception:
#    CONSOLE.print_exception(show_locals=True)
