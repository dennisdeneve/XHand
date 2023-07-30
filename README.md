
# Table of Contents

1.  [About](#org9c40fe0)
2.  [Installing And Running](#orgaedc806)
3.  [Packages](#org67a8b20)
4.  [Coding Convention Used](#org729d42a)
5.  [Hand x-ray image pre-processing](#org43f188f)
6.  [Imports](#org5b887b3)
7.  [Debug helper](#org557433c)
8.  [Enum Class](#org5b835ac)
    1.  [Color Class](#orgfd4eb1e)
9.  [Segmenting and aligning the image.](#orgd9f56ba)
    1.  [Xhand Image Cleaner](#orgbb1e63c)
    2.  [Xhand Analyzer](#org4166443)
        1.  [Preparation](#org4fb9c6f)
        2.  [Analysis](#org17138b9)
    3.  [Xhand Contours Extraction](#org6c7a21f)
        1.  [Contours](#org2bd22c3)
        2.  [Convex Hull](#org27656b1)
    4.  [Defects Extraction](#org65e9c77)
10. [Xhand Aligner](#org89cbf48)
    1.  [Align](#org6ee59b4)
11. [XhandDrawer](#org2413342)
12. [Xhand Processor](#orgd372af2)
    1.  [XhandAnalyzer](#org192b3f0)
    2.  [XhandDrawer](#orgcbf2b10)
    3.  [XhandAligner](#org5372fb3)



<a id="org9c40fe0"></a>

# About

-   TODO: Describe what this software does.


<a id="orgaedc806"></a>

# Installing And Running

-   TODO: Add an installation description and how to run this application.


<a id="org67a8b20"></a>

# Packages

-   **Python 3.9+**
-   Numpy
-   OpenCV


<a id="org729d42a"></a>

# Coding Convention Used

-   [PEP 8](https://peps.python.org/pep-0008/)


<a id="org43f188f"></a>

# Hand x-ray image pre-processing

-   A set of images where provided in PNG format.
-   We used python for this project.
-   imageio is used to read and display the images.


<a id="org5b887b3"></a>

# Imports

    import os
    import math
    import time
    
    from multipledispatch import dispatch
    
    from enum import Enum
    
    import numpy
    import cv2


<a id="org557433c"></a>

# Debug helper

-   TODO: Delete this before submitting the main code.

    from rich.console import Console
    
    CONSOLE = Console()


<a id="org5b835ac"></a>

# Enum Class

-   This is the class color for contours, defects, etc.


<a id="orgfd4eb1e"></a>

## Color Class

    #################################################################################
    #                                Color Class                                    #
    #################################################################################
    class RGBColor(Enum):
        RED     = (0, 0, 255)
        GREEN   = (0, 255, 0)
        BLUE    = (255, 0, 0)
        BRIGHT_TEAL = (0, 181, 184)
        ORANGE = (0, 165, 255)


<a id="orgd9f56ba"></a>

# Segmenting and aligning the image.

-   In this project, we are using python binding for openCV to segment and align the xhand images.


<a id="orgbb1e63c"></a>

## Xhand Image Cleaner

-   This is the root class in our pip and filter architecture.
-   This is the first process the image goes through before it can under go other processes.
-   It has the following methods:

1.  Normalize

    -   This method is used to change the intensity level of pixels, i.e. to change the image to a better contrast due to poor lighting conditions.
    -   We used the lower range **0** and the upper range **255** in order to makesure the background is very dark, and the foreground (hand, bones etc) is very bright.
    
    **\*\***

2.  Binarize

    -   This method thresholds the image to produce a binary image.
    -   Firstly, normalizes the image.
    -   Converts it to grayscale.
    -   Blurs it using the guassian blur with a 7 x 7 window.
    -   Then thresholds the image.
    
        #################################################################################
        #                            Xhand Cleaner Class                                #
        #################################################################################
        class XhandCleaner:
            """
            This class cleans the image for the following image processes.
            """
            def __init__(self, ximage: numpy.ndarray, threshold: int = 30) -> None:
                self.image = ximage
                self.threshold = threshold
        
            def _normalize(self) -> numpy.ndarray:
                return cv2.normalize(self.image, numpy.zeros(self.image.shape), 0, 255, cv2.NORM_MINMAX)
        
            def _binarize(self, ) -> numpy.ndarray:
                new_image = self._normalize()
                new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
                return cv2.threshold(cv2.GaussianBlur(new_image, (7, 7), 0), self.threshold, 255, cv2.THRESH_BINARY, dst=numpy.zeros(self.image.shape))[1]


<a id="org4166443"></a>

## Xhand Analyzer

-   This class run connected components analysis on the thresholded binary image
-   Connected components analysis is the extraction of important components from the image.


<a id="org4fb9c6f"></a>

### Preparation

-   We first convert the image to grayscale image  to make the algorithm more accurate and efficient.
-   After that we apply a 7 x 7 Gausian blur to help remove unwanted edges and help with overal segmentation.
-   All this preparation will be done with the help of the **XhandCleaner** class


<a id="org17138b9"></a>

### Analysis

-   The following methods help with our connected components analysis.

1.  Blob Extraction

    -   AKA connected components analysis
    -   This method binarizes the image first using the method in the **XhandCleaner** class.
    -   It then applies the connectedComponentsWithStats algorithm to the binary image.
    
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
                print("getting largest cc")
                labelCount, label_ids, stats, centroids = self._blob_extraction()
                label, stat = max(enumerate(stats[1:], 1), key= self._stat_area)
                return numpy.uint8(label_ids == label)*255


<a id="org6c7a21f"></a>

## Xhand Contours Extraction

-   This class extracts points from the image for contour and convex hull drawing.


<a id="org2bd22c3"></a>

### Contours

-   Contours are curve joining all the continours points along the boundary of the largest component in this project (the x-ray hand)
-   For accuracy we use binary images.
-   TODO: try canny edge detection instead of thresholding


<a id="org27656b1"></a>

### Convex Hull

-   This is a tight fitting convex boundary around the points of the largest component (x-ray hand )
-   This method uses the \_extract\_contours method to get the list of contours
-   Then iterates over these contours applying the convexHull opencv function to each contour.
-   Save the results of the convexHull function in an array.
-   Returns a list of convexhull that can be drawn on an image.

    #################################################################################
    #                           Xhand Analyser Class                                #
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
            print("extracting contours")
            ret, thresh = cv2.threshold(self.largest_CC, self.threshold, 255, 0)
            return cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
    
        def _convex_hull(self, return_points: bool = True) -> list:
            print("getting convext hull points")
            return [cv2.convexHull(contour, return_points) for contour in self.contours]
    
        def get_contours(self):
            return self.contours
    
        def get_convex_hulls(self):
            return self.hulls


<a id="org65e9c77"></a>

## Defects Extraction

-   This class uses the contour list to calculate convexity defects.
-   With convexity defects points it then determines finger tips -> by extension -> the middle finger.

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
    
        def get_mid_point(self) -> None:
            """
            Returns the mid point between the opposite inner points of the middle finger.
            """
            print("getting mid point")
            return self.mid_point
    
        def mid_finger(self, tips: list) -> tuple:
            """
            Calculates and returns the coordinates of the tip of the middle finger.
            """
            print("computing mid finger")
            tips.sort(key = lambda x: x[1])
            mid_finger = tips[0]
            return mid_finger
    
        def get_mid_finger(self) -> tuple:
            """
            Returns the coordinates of the tip of the middle finger.
            """
            print("getting mid finger")
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
            print("gettiing defect points")
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
    
        def _fingertips(self, tips) -> None:
            """
            This is a private mathod for getting fingertips.
            It is computationly heavy do not use it outside this class.
            Rather use accessor methods.
            """
            print("computing fingertips")
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
    
        def mid_point(self, points : list) -> None:
            """
            Calculates the mid point between the opposite inner points around the middle finger.
            """
            print("computing mid_point")
            print("Points: ", points)
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
                print("distance: ", dists)
                mid_points = [points[dists[0][0]], points[dists[1][0]]]
                mid_point = ((mid_points[0][0]+mid_points[1][0])//2, (mid_points[0][1]+mid_points[1][1])//2)
            except:
                #TODO: Sometimes there is only one point. Investigate on why this is and fix it.
                return points[0]
            return mid_point


<a id="org89cbf48"></a>

# Xhand Aligner

-   This class has an align static method.


<a id="org6ee59b4"></a>

## Align

-   This method takes a middle finger point and a mid point between the inner points around the middle finger.
-   Calculates the angle the image needs to be rotated by then rotate it.

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
            print("Aligning")
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


<a id="org2413342"></a>

# XhandDrawer

-   This class only has static methods to draw points on the image.

    #################################################################################
    #                            Xhand Drawer Class                                 #
    #################################################################################
    class XhandDrawer:
    
        @staticmethod
        def insert_contours(image, contours, contour_color: RGBColor, line_thickness: int):
            """
            Draws contours on the image given the list of contours, the colour of the contours and the thickness of the contour lines.
            """
            print("Drawing contours")
            cv2.drawContours(image, contours, -1, contour_color.value, line_thickness)
    
        @staticmethod
        def insert_defect_points(image, tips, points, ext_defects_color:RGBColor, int_defects_color: RGBColor, defects_size: int, defects_thickness: int) -> None:
            """
            Inserts convexity defects on a given image, given the finger tips, points and colors for them respectively and the size and thickness of them.
            """
            print("Drawing Defect points")
            for point in points:
                cv2.drawMarker(image, point, int_defects_color.value, cv2.MARKER_SQUARE, markerSize = defects_size, thickness = defects_thickness)
            for tip in tips:
                cv2.drawMarker(image, tip, ext_defects_color.value, cv2.MARKER_SQUARE, markerSize = defects_size, thickness = defects_thickness)
    
        @staticmethod
        def insert_convex_hull(image, hull_list, convex_hull_color: RGBColor = RGBColor.BLUE, line_thickness: int = 10, line_type: int = 8) -> None:
            """
            Draws the convex hull on a given image given the hull list and the color, thickness and line type of the convex hull.
            """
            print("Drawing convex hull")
            num_hulls = len(hull_list)
            for i in range(num_hulls):
                cv2.drawContours(image, hull_list, i, convex_hull_color.value, line_thickness, line_type)
    
        @staticmethod
        def insert_straight_line(image, mid_finger, mid_point, line_color: RGBColor, thickness: int) -> None:
            """
            Draws a straign line given two points and the image to draw the line on. It also takes the thickness of that line.
            """
            cv2.line(image, mid_finger, mid_point, line_color.value, thickness=thickness)


<a id="orgd372af2"></a>

# Xhand Processor

-   This is our main processor class.
-   In inherites from the following classes:


<a id="org192b3f0"></a>

## XhandAnalyzer

-   This class analyzes the image to get the largest connected componed after doing the necessery operation to the image.


<a id="orgcbf2b10"></a>

## XhandDrawer

-   We inherite the draw methods from this class.


<a id="org5372fb3"></a>

## XhandAligner

-   We inherite the align method from this class.

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
            print("Rotating the image")
            self.align(self.image, self.mid_finger, self.mid_point)

    
    def draw(processed: numpy.ndarray, original: numpy.ndarray = numpy.array([])) -> None:
        print("Main Draw function")
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
            print("processor.image returned None!")
    
    try:
        for file in os.listdir("../images/batch1"):
            if file.endswith("png"):
                try:
                    processor = XhandProcessor(cv2.imread(f"../images/batch1/{file}"))
                    processor.draw_contours()
                    processor.draw_defect_points()
                    processor.draw_convex_hull()
                    processor.draw_line()
                    draw(processor.image)
                    processor.rotate()
                    draw(processor.image)
                except Exception:
                    CONSOLE.print_exception(show_locals=True)
                    with open("logs.txt", "a") as logs:
                        logs.write(f"{file} caused an error.\n")
        #draw(cleaner.draw_contours(3))
        #draw(cleaner.draw_line())
    except Exception:
        CONSOLE.print_exception(show_locals=True)

