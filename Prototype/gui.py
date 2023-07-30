from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivy.uix.filechooser import FileChooserIconView, FileChooserListView
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy import clock

from main import *
import cv2 as cv

import os

from rich.console import Console

CONSOLE = Console()

## Loading in Kivy file
Builder.load_file("gui.kv")

class MyLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_chooser = ObjectProperty()
        self.file_browser_popup = ObjectProperty()
        

    def choose_file(self):
        """
        This method contains all the buttons to perform the various analysis steps
        on the image for the pre-processing
        """

        layout = BoxLayout(orientation = "vertical", spacing=20)
        label = MDLabel(text = "Choose a file to upload :", halign="center")
        
        button = MDRaisedButton(text = "Display natural image", pos_hint = {"center_x":0.5})
        button2 = MDRaisedButton(text = "Display contour Image", pos_hint = {"center_x":0.5})
        button3 = MDRaisedButton(text = "Display binary image", pos_hint = {"center_x":0.5})
        button4 = MDRaisedButton(text = "Display histogram normalized image", pos_hint = {"center_x":0.5})
        button5 = MDRaisedButton(text = "Display convexity defects", pos_hint = {"center_x":0.5})

        #TODO: instead of using path='../' research on how to use pathlib. I am afraid we might have problems with this once we package the application
        self.file_chooser = FileChooserIconView(dirselect = True, path="../")
        
        
        close_button = MDRaisedButton(text = "Cancel", pos_hint = {"center_x":0.5})
        
        layout.add_widget(self.file_chooser)
        layout.add_widget(button)
        layout.add_widget(button2)
        layout.add_widget(button3)
        layout.add_widget(button4)
        layout.add_widget(button5)
    
        layout.add_widget(close_button)

        self.file_browser_popup = Popup(title = "File Explorer", content = layout)
        self.file_browser_popup.open()

        button.bind(on_press = self.displayNaturalImage)
        button2.bind(on_press = self.displayContourImage)
        button3.bind(on_press = self.displayBinaryImage)
        button4.bind(on_press = self.displayHistogramNormalized)
        button5.bind(on_press = self.displayConvexHull)
        close_button.bind(on_press = self.file_browser_popup.dismiss)

    def displayNaturalImage(self, instance):
        """
        This method simply displays the natural image before all processing is done
        """
        y =0
        if len(self.file_chooser.selection) == True:
            self.ids.filename.text = f"uploaded file: {self.file_chooser.selection[y]}"
            xImage = XhandProcessor(Xhand(self.file_chooser.selection[0]))
            cv.imwrite("resultNatural.png", xImage.get_original())
            self.ids.imageView.source = "resultNatural.png"
            
        else:
            self.ids.filename.text = ""
        y+=1
        self.file_browser_popup.dismiss()

    def displayContourImage(self, instance):
        """
        This method simply displays the image after the contouring of the hand is done
        """
        y =0
        if len(self.file_chooser.selection) == True:
            self.ids.filename.text = f"uploaded file: {self.file_chooser.selection[y]}"
            xImage = XhandProcessor(XhandProcessor(self.file_chooser.selection[0]))
            cv.imwrite("./ImagesRendered/Contour/resultsContour{}.png".format(y), xImage.get_with_contours())
            self.ids.imageView.source = "ImagesRendered/resultsContour{}.png".format(y)
            
        else:
            self.ids.filename.text = ""
        y+=1
        self.file_browser_popup.dismiss()


    def displayBinaryImage(self, instance):
        """
        This method simply displays the image after it has been converted to a 
        binary representation of the image 
        """
        y =0
        if len(self.file_chooser.selection) == True:
            self.ids.filename.text = f"uploaded file: {self.file_chooser.selection[y]}"
            xImage = XhandProcessor(Xhand(self.file_chooser.selection[0]))

            cv.imwrite("./ImagesRendered/Binary/resultsBinary{}.png".format(y), xImage.get_binary())
            self.ids.imageView.source = "ImagesRendered/Binary/resultsBinary{}.png".format(y)
            cv.imwrite("resultsBinary.png", xImage.get_binary())
            self.ids.imageView.source = "resultsBinary.png"

        else:
            self.ids.filename.text = ""
        y+=1
        self.file_browser_popup.dismiss()

    def displayHistogramNormalized(self, instance):
        """
        This method simply displays the image after the histogram normalization has 
        been implemented on the image to remove background clutter
        """
        y =0
        if len(self.file_chooser.selection) == True:
            self.ids.filename.text = f"uploaded file: {self.file_chooser.selection[y]}"
            xImage = XhandProcessor(Xhand(self.file_chooser.selection[0]))

            cv.imwrite("./ImagesRendered/Hist/resultsHist{}.png".format(y), xImage.normalize_contrast())
            self.ids.imageView.source ="ImagesRendered/Hist/resultsHist{}.png".format(y)
            cv.imwrite("resultsHist.png", xImage.normalize_contrast())
            self.ids.imageView.source ="resultsHist.png"


        else:
            self.ids.filename.text = ""
        y+=1
        self.file_browser_popup.dismiss()

    def displayConvexHull(self, instance):
        """
        This method simply displays the image after the convexity defects have  
        been computed on the image 
        """
        y =0

        if len(self.file_chooser.selection) == True:

            self.ids.filename.text = f"uploaded file: {self.file_chooser.selection[y]}"
            xImage = XhandProcessor(Xhand(self.file_chooser.selection[0]))

            cv.imwrite("./ImagesRendered/Convex/resultsConvexity{}.png".format(y), xImage.get_with_convexity_defects())
            self.ids.imageView.source ="./ImagesRendered/Convex/resultsConvexity{}.png".format(y)
            cv.imwrite("resultsConvexity.png", xImage.get_with_convexity_defects())
            self.ids.imageView.source ="resultsConvexity.png"

        else:
            self.ids.filename.text = ""
        y+=1
        self.file_browser_popup.dismiss()
    
   

class MyApplication(MDApp):
    def build(self):
        self.title = 'XHAND Application'
        return MyLayout()

if __name__ == "__main__":
    try:
        MyApplication().run()
    except:
        CONSOLE.print_exception()
