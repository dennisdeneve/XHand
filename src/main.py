import os
import math
import time
import numpy
import cv2

from multipledispatch import dispatch
from enum import Enum
from PIL import Image, ImageFilter
from rich.console import Console

CONSOLE = Console()

#################################################################################
#                                Color Class                                    #
#################################################################################
class RGBColor(Enum):
    RED     = (0, 0, 255)
    GREEN   = (0, 255, 0)
    BLUE    = (255, 0, 0)
    BRIGHT_TEAL = (0, 181, 184)
    ORANGE = (0, 165, 255)

#################################################################################
#                            Xhand Cleaner Class                                #
#################################################################################
class XhandCleaner:
    """
    This class cleans the image for the following image processes.
    """
    def __init__(self, ximage: numpy.ndarray, threshold: int = 30) -> None:
        self.image = ximage
        self.orig_image = self.image.copy()
        self.threshold = threshold
        self._crop()

    def _normalize(self) -> numpy.ndarray:
        return cv2.normalize(self.image, numpy.zeros(self.image.shape), 0, 255, cv2.NORM_MINMAX)

    def _binarize(self, ) -> numpy.ndarray:
        new_image = self._normalize()
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
        return cv2.threshold(cv2.GaussianBlur(new_image, (7, 7), 0), self.threshold, 255, cv2.THRESH_BINARY, dst=numpy.zeros(self.image.shape))[1]

    def _crop(self):
        shape = self.image.shape
        y, x = shape[0], shape[1]
        self.image = self.image[0:x-15, 0:y-15]
        self.orig_image = self.orig_image[0:x-15, 0:y-15]

#################################################################################
#                           Xhand Analyser Class                                #
#################################################################################
class XhandAnalyzer(XhandCleaner):
    """
    This class runs the connected components analysis and extracts the largest component.
    """
    def __init__(self, ximage: numpy.ndarray) -> None:
        super().__init__(ximage)

    def _blob_extraction(self, connectivity: int = 8) -> tuple:
        return cv2.connectedComponentsWithStats(self._binarize(), connectivity, cv2.CV_32S)

    def _stat_area(self, stats: numpy.ndarray) -> numpy.int32:
        return stats[1][cv2.CC_STAT_AREA]

    def largest_CC(self) -> numpy.ndarray:
        labelCount, label_ids, stats, centroids = self._blob_extraction()
        label, stat = max(enumerate(stats[1:], 1), key= self._stat_area)
        largest_cc = numpy.uint8(label_ids == label)*255
        ## creating image mask
        background = cv2.merge([largest_cc, largest_cc, largest_cc])
        self.image = cv2.bitwise_and(self.image, background)
        return largest_cc
    

#################################################################################
#                           Xhand Contours Extractor Class                      #
################################################################################
class XhandContoursExtractor:
    """
    This class takes in a numpy ndarray image and extracts drawable points for contours and convex hull.
    """
    def __init__(self, largest_CC, threshold: int=30) -> None:
        self.largest_CC = largest_CC
        self.threshold = threshold
        self.contours = self._contours()
        self.hulls = self._convex_hull()

    def _contours(self) -> tuple:
        ret, thresh = cv2.threshold(self.largest_CC, self.threshold, 255, 0)
        return cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]

    def _convex_hull(self, return_points: bool = True) -> list:
        return [cv2.convexHull(contour, return_points) for contour in self.contours]

    def get_contours(self):
        return self.contours

    def get_convex_hulls(self):
        return self.hulls

#################################################################################
#                           Xhand Defects Class                                #
################################################################################
class XhandDefectsExtractor:
    """
    This class uses contours list to determine convexity defects and use them to get finger tip and inner finger points.
    """
    def __init__(self, contours) -> None:
        self.contour_points = contours
        self.points, self.tips = self._defect_points()
        self.finger_tips = self._fingertips(self.tips)
        self.mid_finger = self.mid_finger(self.tips)
        self.mid_point = self.mid_point(self.points)

    def get_mid_point(self) -> tuple:
        """
        Returns the mid point between the opposite inner points of the middle finger.
        """
        return self.mid_point

    def mid_finger(self, tips: list) -> tuple:
        """
        Calculates and returns the coordinates of the tip of the middle finger.
        """
        tips.sort(key = lambda x: x[1])
        mid_finger = tips[0]
        return mid_finger

    def get_mid_finger(self) -> tuple:
        """
        Returns the coordinates of the tip of the middle finger.
        """
        return self.mid_finger

    def get_finger_tips(self):
        """
        Returns a list of finger tip coordinates.
        """
        return self.finger_tips

    def get_points(self):
        """
        Returns all convexity defects points.
        """
        return self.points

    def _defect_points(self) -> tuple:
        """
        This is a private method.
        It is relatively computationly heavy do not use it outside this class.
        Rather use accessor methods.
        """
        points, tips = [], []
        contours = self.contour_points
        for contour in contours:
            conv = cv2.convexHull(contour, returnPoints=False)
            defects = cv2.convexityDefects(contour, conv)
            if type(defects) != type(None):
                for j in range(defects.shape[0]):
                    try:
                        s, e, f, d = defects[j][0]
                        start = tuple(contour[s][0])
                        end = tuple(contour[e][0])
                        far = tuple(contour[f][0])
                        a = math.sqrt(
                            (end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2
                        )
                        b = math.sqrt(
                            (far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2
                        )
                        c = math.sqrt(
                            (end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2
                        )
                        angle = math.acos(
                            (b ** 2 + c ** 2 - a ** 2) / (2 * b * c )
                        )
                        if angle >= math.pi / 2:
                            tips.append(far)
                        else:
                            points.append(far)
                    except IndexError:
                        pass
        return (points, tips)#, mid_finger, mid_point)

    def _fingertips(self, tips) -> list:
        """
        This is a private mathod for getting fingertips.
        It is computationly heavy do not use it outside this class.
        Rather use accessor methods.
        """
        finaltips = []
        temptip = tips[0]
        tipgroup = []
        for tip in tips:
            if tip[0] >= temptip[0] -25 and tip[0] <= temptip[0] + 25:
                tipgroup.append(tip)
            else:
                if len(tipgroup) == 0:
                    tipgroup.append(temptip)
                tipgroup.sort()
                finaltips.append(tipgroup[len(tipgroup)//2] if len(tipgroup) > 2 else tipgroup[0])
                temptip = tip
                tipgroup = []
        return finaltips

    def mid_point(self, points : list) -> list:
        """
        Calculates the mid point between the opposite inner points around the middle finger.
        """
        points.sort()
        try:
            mid_finger = self.get_mid_finger()
            dists = [
                (
                    ind, math.hypot(
                        point[0]-mid_finger[0], point[1]-mid_finger[1]
                    )
                 )
                for ind, point in enumerate(points)
            ] ## getting distance from every point and the mid_finger and attaching the point index
            dists.sort(key=lambda x:x[1]) ## sorting by distance
            mid_points = [points[dists[0][0]], points[dists[1][0]]]
            mid_point = ((mid_points[0][0]+mid_points[1][0])//2, (mid_points[0][1]+mid_points[1][1])//2)
        except IndexError:
            #TODO: Sometimes there is only one point. Investigate on why this is and fix it.
            return points[0]
        return mid_point

#################################################################################
#                            Xhand Aligner Class                                #
#################################################################################
class XhandAligner:
    """
    This class contains a static align method.
    """

    @staticmethod
    def align(ximage: numpy.ndarray, mid_finger: tuple, mid_point: tuple) -> None:
        """
        This method calculates the angle an image needs to be rotated in order to align it.
        Then aligns the image.
        """
        ## line equation
        # gradient
        angle = numpy.rad2deg(
            numpy.arctan2(
                mid_finger[1] - mid_point[1], mid_finger[0]- mid_point[0])
        ) + 90

        (h, w) = ximage.shape[:2]
        matrix = cv2.getRotationMatrix2D(
            (w/2, h/2), angle, 1
        )
        return cv2.warpAffine(ximage, matrix, (w, h))

#################################################################################
#                            Xhand Drawer Class                                 #
#################################################################################
class XhandDrawer:

    @staticmethod
    def insert_contours(image, contours, contour_color: RGBColor, line_thickness: int):
        """
        Draws contours on the image given the list of contours, the colour of the contours and the thickness of the contour lines.
        """
        cv2.drawContours(image, contours, -1, contour_color.value, line_thickness)

    @staticmethod
    def insert_defect_points(image, tips, points, ext_defects_color:RGBColor, int_defects_color: RGBColor, defects_size: int, defects_thickness: int) -> None:
        """
        Inserts convexity defects on a given image, given the finger tips, points and colors for them respectively and the size and thickness of them.
        """
        for point in points:
            cv2.drawMarker(image, point, int_defects_color.value, cv2.MARKER_SQUARE, markerSize = defects_size, thickness = defects_thickness)
        for tip in tips:
            cv2.drawMarker(image, tip, ext_defects_color.value, cv2.MARKER_SQUARE, markerSize = defects_size, thickness = defects_thickness)

    @staticmethod
    def insert_convex_hull(image, hull_list, convex_hull_color: RGBColor = RGBColor.BLUE, line_thickness: int = 10, line_type: int = 8) -> None:
        """
        Draws the convex hull on a given image given the hull list and the color, thickness and line type of the convex hull.
        """
        num_hulls = len(hull_list)
        for i in range(num_hulls):
            cv2.drawContours(image, hull_list, i, convex_hull_color.value, line_thickness, line_type)

    @staticmethod
    def insert_straight_line(image, mid_finger, mid_point, line_color: RGBColor, thickness: int) -> None:
        """
        Draws a straign line given two points and the image to draw the line on. It also takes the thickness of that line.
        """
        cv2.line(image, mid_finger, mid_point, line_color.value, thickness=thickness)

#################################################################################
#                            XHandProcessor Class                               #
#################################################################################

class XhandProcessor(XhandAnalyzer, XhandDrawer, XhandAligner):
    def __init__(self, xImage: numpy.ndarray) -> None:
        super().__init__(xImage)
        self.largest_connected_component = self.largest_CC()
        self.lines_extractor = XhandContoursExtractor(self.largest_connected_component)
        self.contours = self.lines_extractor.get_contours()
        self.hulls = self.lines_extractor.get_convex_hulls()
        self.defects_extractor = XhandDefectsExtractor(self.contours)
        self.finger_tips = self.defects_extractor.get_finger_tips()
        self.points = self.defects_extractor.get_points()
        self.mid_finger = self.defects_extractor.get_mid_finger()
        self.mid_point = self.defects_extractor.get_mid_point()

    def draw_contours(self, contour_color: RGBColor = RGBColor.BRIGHT_TEAL, line_thickness: int = 3) -> None:
        self.insert_contours(self.image, self.contours, contour_color, line_thickness)

    def draw_defect_points(self, tips_color: RGBColor = RGBColor.GREEN, points_color: RGBColor = RGBColor.RED, size: int = 10, thickness: int = 16) -> None:
        self.insert_defect_points(self.image, self.finger_tips, self.points, tips_color, points_color, size, thickness)

    def draw_convex_hull(self, hull_color: RGBColor = RGBColor.BLUE, thickness: int = 10, line_type: int = 8) -> None:
        self.insert_convex_hull(self.image, self.hulls, hull_color, thickness, line_type)

    def draw_line(self, line_color: RGBColor = RGBColor.ORANGE, thickness: int = 10) -> None:
        self.insert_straight_line(self.image, self.mid_finger, self.mid_point, line_color, thickness)

    def rotate(self):
        self.image = self.align(self.image, self.mid_finger, self.mid_point)
        
    def overlay(self, ideal_image):
        self.image = cv2.resize(self.image, ideal_image.shape[1::-1])
        self.image = cv2.addWeighted(ideal_image, 0.85, self.image, 0.85, 0)

def draw(processed: numpy.ndarray, original: numpy.ndarray = numpy.array([])) -> None:
    cv2.namedWindow("Processed", cv2.WINDOW_NORMAL)
    if processed is not None:
        processed = cv2.resize(processed, (520, 540))
        if  original.size == 0:
            cv2.imshow("Processed", processed)
        else:
            stack = numpy.hstack((original, processed))
            cv2.imshow("Processed", stack)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        return