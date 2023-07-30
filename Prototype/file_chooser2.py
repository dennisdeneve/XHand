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

from xhand import *
import cv2 as cv

## Loading in Kivy file
Builder.load_file("file_chooser2.kv")

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

        self.file_chooser = FileChooserIconView(multiselect = True, dirselect = True)
        
        
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
        if len(self.file_chooser.selection) == 1:
            self.ids.filename.text = f"uploaded file: {self.file_chooser.selection[y]}"

            xImage = Xhand(self.file_chooser.selection[0])
            cv.imwrite("./ImagesRendered/resultsContour.png", xImage.getWithContours())
            self.ids.imageView.source = "ImagesRendered/resultsContour.png" 
            
        else:
            self.ids.filename.text = ""
        y+=1
        self.file_browser_popup.dismiss()

    def displayContourImage(self, instance):
        """
        This method simply displays the image after the contouring of the hand is done
        """
        y =0
        if len(self.file_chooser.selection) == 1:
            self.ids.filename.text = f"uploaded file: {self.file_chooser.selection[y]}"

            xImage = Xhand(self.file_chooser.selection[0])
            cv.imwrite("./ImagesRendered/resultsContour.png", xImage.getWithContours())
            self.ids.imageView.source = "ImagesRendered/resultsContour.png" 
            
        else:
            self.ids.filename.text = ""
        y+=1
        self.file_browser_popup.dismiss()

        #button.bind(on_press = self.displayContourImage)
        #close_button.bind(on_press = self.file_browser_popup.dismiss)

    def displayBinaryImage(self, instance):
        """
        This method simply displays the image after it has been converted to a 
        binary representation of the image 
        """
        y =0
        if len(self.file_chooser.selection) == 1:
            self.ids.filename.text = f"uploaded file: {self.file_chooser.selection[y]}"

            xImage = Xhand(self.file_chooser.selection[0])
            cv.imwrite("./ImagesRendered/resultsBinary.png", xImage.getBinary())
            self.ids.imageView.source = "ImagesRendered/resultsBinary.png"

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
        if len(self.file_chooser.selection) == 1:
            self.ids.filename.text = f"uploaded file: {self.file_chooser.selection[y]}"

            xImage = Xhand(self.file_chooser.selection[0])
            cv.imwrite("./ImagesRendered/resultsHist.png", xImage.normalizeContrast())
            self.ids.imageView.source ="ImagesRendered/resultsHist.png"

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
        if len(self.file_chooser.selection) == 1:
            self.ids.filename.text = f"uploaded file: {self.file_chooser.selection[y]}"

            xImage = Xhand(self.file_chooser.selection[0])
            cv.imwrite("./ImagesRendered/resultsConvexity.png", xImage.getWithConvexityDefects())
            self.ids.imageView.source ="ImagesRendered/resultsConvexity.png"

        else:
            self.ids.filename.text = ""
        y+=1
        self.file_browser_popup.dismiss()
    
   

class MyApplication(MDApp):
    def build(self):
        self.title = 'XHAND Application'
        return MyLayout()

if __name__ == "__main__":
    MyApplication().run()
