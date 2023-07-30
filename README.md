# Project overview:

This group project involved pre-processing hand X-ray images using Python and OpenCV. Myself and 2 other students in the computer science department completed this project as part of our Capstone project towards the end of our third year at UCT. The input images are provided in PNG format, and Python libraries like imageio and matplotlib can be used to read and display the images. Numpy arrays are preferred over native Python lists for image processing due to their efficiency.


## Strategy followed:


- Histogram normalization to enhance the contrast between the hand and background.
- Thresholding to create a binary image where the hand is represented as white pixels and background clutter as black pixels. Adaptive thresholding can also be explored.
- Connected components analysis to identify the largest component representing the hand.
- Extracting the hand contour using OpenCV's findContours method.
- Computing a convex hull to tightly fit the hand, including fingertip points.
- Identifying convexity defects, points on the contour where it is highly concave, such as the finger-palm junctions.
- After extracting the hand contour and relevant points, alignment of the image is performed. The orientation of the hand is determined by connecting the middle fingertip with the two defect points on either side, and the rotation angle required to align this vector with the y-axis is computed. The image is then rotated accordingly, roughly aligning the hand.

## Evaluation

To evaluate the alignment accuracy, a color-coded overlay of the aligned binary hand image onto the target image is created. Additionally, hand boundary curves can be used to compute the error between aligned images, helping to identify differences across the population.


## Extra credit

For extra credit, various metrics can be computed based on differences between the current and target shapes. Hand feature vectors can be generated, serving as descriptors for each hand, which can be used for clustering similar hands. This clustering approach may create a hand database lookup system.

## Code structure

In terms of code structure, it is essential to modularize the code into separate components that form a pipeline for each stage of the image processing. This modularity allows for flexibility in changing certain parts of the pipeline. Appropriate data structures like Numpy arrays and dictionaries should be used to handle image points and images efficiently.

