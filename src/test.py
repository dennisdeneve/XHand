#!/usr/bin/env python3

import unittest
import main
import cv2
import numpy

class TestXhandCleaner(unittest.TestCase):

    def test_binarize_image(self):
        image = main.XhandCleaner(cv2.imread("../images/batch1/13894.png"))
        binary_image = image._binarize()
        self.assertEqual(len(binary_image.shape) == 2, True) # A binary image has two channels

    def test_normalization(self):
        image = main.XhandCleaner(cv2.imread("../images/batch1/13894.png"))
        normalized_image = image._normalize()
        self.assertEqual(type(normalized_image), numpy.ndarray)

class TestXhandAnalyzer(unittest.TestCase):

    def test_blob_extraction(self):
        image = main.XhandAnalyzer(cv2.imread("../images/batch1/13894.png"))
        blob_stats = image._blob_extraction()
        self.assertEqual(len(blob_stats), 4)

    def test_largest_CC(self):
        image = main.XhandAnalyzer(cv2.imread("../images/batch1/13894.png"))
        largest_CC = image.largest_CC()
        self.assertEqual(type(largest_CC), numpy.ndarray)

class TestXhandContoursExtractor(unittest.TestCase):

    def test_contours(self):
        image = main.XhandAnalyzer(cv2.imread("../images/batch1/13894.png"))
        largest_CC = image.largest_CC()
        contours = main.XhandContoursExtractor(largest_CC).get_contours()
        self.assertEqual(type(contours), tuple)

    def test_convex_hull(self):
        image = main.XhandAnalyzer(cv2.imread("../images/batch1/13894.png"))
        largest_CC = image.largest_CC()
        hull_list = main.XhandContoursExtractor(largest_CC).get_convex_hulls()
        self.assertEqual(type(hull_list), list)

class TestXhandDefectsExtractor(unittest.TestCase):

    def test_get_midpoint(self):
        image = main.XhandAnalyzer(cv2.imread("../images/batch1/13894.png"))
        largest_CC = image.largest_CC()
        contours = main.XhandContoursExtractor(largest_CC).get_contours()
        defects_extractor = main.XhandDefectsExtractor(contours)
        self.assertEqual(defects_extractor.get_mid_point(), (883, 723))

    def test_get_mid_finger(self):
        image = main.XhandAnalyzer(cv2.imread("../images/batch1/13894.png"))
        largest_CC = image.largest_CC()
        contours = main.XhandContoursExtractor(largest_CC).get_contours()
        defects_extractor = main.XhandDefectsExtractor(contours)
        self.assertEqual(defects_extractor.get_mid_finger(), (850, 153)) #This point was tested and found to be correct

    def test_get_external_points(self):
        image = main.XhandAnalyzer(cv2.imread("../images/batch1/13894.png"))
        largest_CC = image.largest_CC()
        contours = main.XhandContoursExtractor(largest_CC).get_contours()
        defects_extractor = main.XhandDefectsExtractor(contours)
        self.assertEqual(len(defects_extractor.get_finger_tips()), 7) # There are five finger tips and two wrist points.

    def test_get_internal_points(self):
        image = main.XhandAnalyzer(cv2.imread("../images/batch1/13894.png"))
        largest_CC = image.largest_CC()
        contours = main.XhandContoursExtractor(largest_CC).get_contours()
        defects_extractor = main.XhandDefectsExtractor(contours)
        self.assertEqual(len(defects_extractor.get_points()), 4) # There are only four inner points.
