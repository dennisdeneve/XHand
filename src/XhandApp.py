import os
import cv2 as cv

from main import XhandProcessor
from PIL import Image

from kivy.core.window import Window
from kivymd.uix.button import MDFlatButton
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.dialog import MDDialog
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from kivy.graphics.texture import Texture
from kivy.lang import Builder

KV = '''
<TooltipMDIconButton@MDIconButton+MDTooltip>

<FullScreen>
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "450dp"
    md_bg_color: "#8080ff"

    MDCard:
        id: final_image_card
        line_color: (0.2, 0.2, 0.2, 0.8)
        radius: 36
        style: "filled"
        padding: "2dp"
        size_hint: (None, None)
        size: ("450dp", "450dp")
        md_bg_color: "#e0e6e3"

        MDRelativeLayout:
            FitImage:
                id: final_image
                size_hit_y: 3
                source: '../assets/xray-img.png'
                radius: 20, 20, 25, 25


MDScreenManager:
    id: screen_manager
    screen1: screen1

    MDScreen:
        id: screen1
        name: 'screen1'

        MDBoxLayout:
            orientation: "vertical"
            id: box

            MDTopAppBar:
                title: "XhandApp"
                right_action_items: [["folder", lambda x: app.shelf()], ["home", lambda x: app.home()]]

            MDGridLayout:
                id: main
                cols: 2

                ScrollView:
                    GridLayout:
                        id: screen
                        cols: 3
                        padding: "10dp"

                        MDCard:
                            line_color: (0.2, 0.2, 0.2, 0.8)
                            radius: 36
                            style: "filled"
                            padding: "4dp"
                            size_hint: (None, None)
                            size: ("350dp", "350dp")
                            md_bg_color: "#ffffff"

                            MDRelativeLayout:
                                FitImage:
                                    id: original
                                    size_hit_y: 3
                                    source: '../assets/xray-img.png'
                                    radius: 20, 20, 25, 25

                                MDLabel:
                                    text: "Original"
                                    adaptive_size:True
                                    color:"cyan"
                                    pos:("12dp", "12dp")

                        MDCard:
                            line_color: (0.2, 0.2, 0.2, 0.8)
                            radius: 36
                            style: "filled"
                            padding: "4dp"
                            size_hint: (None, None)
                            size: ("350dp", "350dp")
                            md_bg_color: "#ffffff"

                            MDRelativeLayout:
                                FitImage:
                                    id: ideal
                                    size_hit_y: 3
                                    source: '../images/batch1/13925.png'
                                    radius: 20, 20, 25, 25
                                
                                MDLabel:
                                    id: ideal_label
                                    text: 'Ideal Image'
                                    adaptive_size:True
                                    color:"cyan"
                                    pos:("12dp", "12dp")
                                

                        MDCard:
                            line_color: (0.2, 0.2, 0.2, 0.8)
                            radius: 36
                            style: "filled"
                            padding: "4dp"
                            size_hint: (None, None)
                            size: ("350dp", "350dp")
                            md_bg_color: "#ffffff"

                            MDRelativeLayout:
                                FitImage:
                                    id: contours
                                    size_hit_y: 3
                                    source: '../assets/xray-img.png'
                                    radius: 20, 20, 25, 25

                                MDLabel:
                                    text: "Contours"
                                    adaptive_size:True
                                    color:"cyan"
                                    pos:("12dp", "12dp")

                        MDCard:
                            line_color: (0.2, 0.2, 0.2, 0.8)
                            radius: 36
                            style: "filled"
                            padding: "4dp"
                            size_hint: (None, None)
                            size: ("350dp", "350dp")
                            md_bg_color: "#ffffff"

                            MDRelativeLayout:
                                FitImage:
                                    id: convex_hull
                                    size_hit_y: 3
                                    source: '../assets/xray-img.png'
                                    radius: 20, 20, 25, 25

                                MDLabel:
                                    text: "Convex Hull"
                                    adaptive_size:True
                                    color:"cyan"
                                    pos:("12dp", "12dp")

                        MDCard:
                            line_color: (0.2, 0.2, 0.2, 0.8)
                            radius: 36
                            style: "filled"
                            padding: "4dp"
                            size_hint: (None, None)
                            size: ("350dp", "350dp")
                            md_bg_color: "#ffffff"

                            MDRelativeLayout:
                                FitImage:
                                    id: convexity_defects
                                    size_hit_y: 3
                                    source: '../assets/xray-img.png'
                                    radius: 20, 20, 25, 25

                                MDLabel:
                                    text: "Convexity Defects"
                                    adaptive_size:True
                                    color:"cyan"
                                    pos:("12dp", "12dp")

                        MDCard:
                            line_color: (0.2, 0.2, 0.2, 0.8)
                            radius: 36
                            style: "filled"
                            padding: "4dp"
                            size_hint: (None, None)
                            size: ("350dp", "350dp")
                            md_bg_color: "#ffffff"

                            MDRelativeLayout:
                                FitImage:
                                    id: alignment
                                    size_hit_y: 3
                                    source: '../assets/xray-img.png'
                                    radius: 20, 20, 25, 25

                                MDLabel:
                                    text: "Aligned"
                                    adaptive_size:True
                                    color:"cyan"
                                    pos:("12dp", "12dp")


                MDGridLayout:
                    id: controls
                    cols: 1
                    adaptive_width: True
                    padding: "6dp"

                    MDCard:
                        line_color: (0.2, 0.2, 0.2, 0.8)
                        radius: 36
                        style: "filled"
                        padding: "14dp"
                        size_hint: (None, None)
                        size: ("280dp", "180dp")
                        md_bg_color: "#ffffff"

                        MDRelativeLayout:
                            FitImage:
                                size_hit_y: 3
                                source: '../assets/hand-xray.png'
                                radius: 45, 45, 45, 45

                    MDCard:
                        line_color: (0.2, 0.2, 0.2, 0.8)
                        radius: 36
                        style: "filled"
                        padding: "4dp"
                        size_hint: (None, None)
                        size: ("250dp", "180dp")
                        md_bg_color: "#ffffff"

                        MDRelativeLayout:
                            TooltipMDIconButton:
                                id: fullscreen
                                icon: 'fullscreen'
                                tooltip_text: "Full Screen"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                md_bg_color: "#00ffff"
                                on_release: app.full_screen()
                                disabled: True
                        
                        MDRelativeLayout:
                            TooltipMDIconButton:
                                id: next_btn
                                icon: 'skip-next'
                                tooltip_text: "Next Image"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                md_bg_color: "#00ffff"
                                on_release: app.next_image()
                                disabled: True

                        MDRelativeLayout:
                            TooltipMDIconButton:
                                id: process
                                icon:'skip-previous'
                                icon: 'fast-forward'
                                tooltip_text: "Process Batch"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                md_bg_color: "#00ffff"
                                on_release: app.batch_process()
                                disabled: True

                    MDCard:
                        line_color: (0.2, 0.2, 0.2, 0.8)
                        radius: 20
                        style: "filled"
                        padding: "20dp"
                        size_hint: (None, None)
                        size: ("275dp", "325dp")
                        md_bg_color: "#000000"

                        MDLabel:
                            id: output
                            radius: 20
                            text: "XhandApp: Waiting for image batch to be uploaded..."
                            color:"cyan"
                            size_hint: (None, None)
                            size: ("245dp", "320dp")
                            # pos:("12dp", "12dp")
                            pos_hint: {"center_x": .5, "center_y":.5}

            MDBottomAppBar:
                MDTopAppBar:
                    icon: "license"
                    elevation: 4
                    type: "bottom"
                    mode: "end"
                    on_action_button: app.license()
                    

'''

Window.size = (1350, 1000)

class FullScreen(BoxLayout):
    pass

class XhandImages:
    """
    X hand images class
    """
    def tmpsave(self, filename, img):
        img = Image.fromarray(img)
        img.save(f"/tmp/{filename}")
        return f"/tmp/{filename}"

    def disksave(self, folder, filename, img):
        img = Image.fromarray(img)
        img.save(f"{folder}/output/{filename}")


class XhandApp(MDApp, XhandImages):
    """
    Main Application
    """
    screen_manager = ObjectProperty(None)
    dialog = None
    error_dialog = None
    msg_dialog = None
    error_folder = None
    folder_path = None
    index = 0
    processor = None
    max_line = 12
    full_screen_image = None
    current_path = None
    image_no = 0
    LICENSE_DIALOG = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_manager_obj = MDFileManager(
            select_path=self.select_path,
            exit_manager=self.exit_file_manager,
            selector='folder',
        )

    def select_path(self, path: str) -> None:

        self.folder_path = path

        if os.path.exists(self.folder_path):
            self.current_path = self.folder_path + "/" + \
                os.listdir(self.folder_path)[self.index]
            if self.is_image(self.current_path):
                try:
                    image = cv.imread(self.current_path)
                    self.processor = XhandProcessor(image)
                    self.render_images(self.current_path)
                    self.root.ids.next_btn.disabled = False
                    self.root.ids.fullscreen.disabled = False
                    self.root.ids.process.disabled = False
                except:
                    self.error_dialog = MDDialog(
                    text=f"Can not process this image at: {self.current_path}",
                    radius=[20, 7, 20, 7],
                    )
                    self.error_dialog.open()

                
            else:
                self.error_folder()
        else:
            self.error(self)
        self.index += 1
        self.exit_file_manager()

        if not self.error_dialog:
            self.error_dialog = MDDialog(
                text="Picking the first image to show operations that can be applied to it.",
                radius=[20, 7, 20, 7],
            )
        self.error_dialog.open()

    def error_folder(self):
        if not self.error_dialog:
            self.error_dialog = MDDialog(
                text="No images were detected in the picked directory.",
                radius=[20, 7, 20, 7],
            )
        self.error_dialog.open()

    def is_image(self, path):
        return path.endswith('.png')

    def exit_file_manager(self, value: int = 1) -> None:
        self.file_manager_obj.close()

    def render_images(self, current_path):
        self.root.ids.original.source = current_path
        self.root.ids.original.reload()
        self.add_text(f"Loaded img: {current_path}")
        
        self.processor.draw_contours()
        self.root.ids.contours.source = self.tmpsave("contours.png", self.processor.image)
        self.root.ids.contours.reload()
        self.add_text(f"Contours: SUCCESSFUL")

        self.processor.draw_convex_hull()
        self.root.ids.convex_hull.source = self.tmpsave("convex.png", self.processor.image)
        self.root.ids.convex_hull.reload()
        self.add_text(f"Convex hull: SUCCESSFUL")

        self.processor.draw_defect_points()
        self.root.ids.convexity_defects.source = self.tmpsave("convexity.png", self.processor.image)
        self.root.ids.convexity_defects.reload()
        self.add_text(f"Convexity Defects: SUCCESSFUL")

        self.processor.draw_line()
        self.processor.rotate()
        self.root.ids.alignment.source = self.tmpsave("aligned.png", self.processor.image)
        self.root.ids.alignment.reload()
        self.add_text(f"alignment: SUCCESSFUL")

    def shelf(self):
        self.file_manager_obj.show("../")

    def license(self):
        if not self.LICENSE_DIALOG:
            self.LICENSE_DIALOG = MDDialog(
                title = "MIT License",
                text = self.get_license()
            )

        self.LICENSE_DIALOG.open()

    def get_license(self):
        license = ""
        try:
            with open("license.txt", "r") as file:
                for line in file:
                    license += line
        except Exception as e:
            license = "There is no license."    
            print(e)    
        return license

    def home(self):
        self.root.ids.original.source = "../assets/xray-img.png"
        self.root.ids.contours.source = "../assets/xray-img.png"
        self.root.ids.convex_hull.source = "../assets/xray-img.png"
        self.root.ids.convexity_defects.source = "../assets/xray-img.png"
        self.root.ids.alignment.source = "../assets/xray-img.png"
        self.screen.ids.output.text = self.screen.ids.output.text.split("\n")[0]
        self.current_path = None
        self.folder_path = None
        self.root.ids.next_btn.disabled = True
        self.root.ids.fullscreen.disabled = True
        self.root.ids.process.disabled = True      

    def full_screen(self):
        if not self.full_screen_image:
            ideal_image = cv.imread(self.current_path)
            full_screen_processor = XhandProcessor(ideal_image)
            full_screen_processor.draw_contours()
            full_screen_processor.draw_convex_hull()
            full_screen_processor.draw_defect_points()
            full_screen_processor.draw_line()
            full_screen_processor.rotate()
            full_screen_processor.overlay(ideal_image)
            self.full_screen_container = FullScreen()
            self.full_screen_container.ids.final_image.source = self.tmpsave("overlay.png", full_screen_processor.image)
            self.add_text(" Overlay: SUCCESSFUL ")
            self.full_screen_image = MDDialog(
                title= "Final Image",
                md_bg_color = "#e0e6e3",
                size_hint=(None, None),
                width=500,
                type = "custom",
                content_cls=self.full_screen_container,
                buttons = [
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.cancel
                    ),
                    MDFlatButton(
                        text="SAVE",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.save
                    )
                ]
            )
        self.full_screen_image.open()
        

    def save(self, button):
        self.disksave(self.folder_path, f"overlay_{os.listdir(self.folder_path)[self.index]}", self.processor.image)
        self.full_screen_image.dismiss()

    def cancel(self, button):
        self.full_screen_image.dismiss()

    def next_image(self):
        try:
            self.full_screen_image = None
            self.full_screen_container.clear_widgets()
        except:
            pass

        self.add_text("Showing next Image.")
        self.current_path = self.folder_path + "/" + os.listdir(self.folder_path)[self.index]
        if self.is_image(self.current_path):                    
            try:
                image = cv.imread(self.current_path)
                self.processor = XhandProcessor(image)
                self.render_images(self.current_path) 
            except:
                self.error_dialog = MDDialog(
                text=f"Can not process this image at: {self.current_path}",
                radius=[20, 7, 20, 7],
                )
                self.error_dialog.open()
               
        else:
            self.add_text("End Of Folder Reached")
            self.error_dialog = MDDialog(
                text="You have reached the end of the folder",
                radius=[20, 7, 20, 7],
            )
            self.error_dialog.open()
            self.root.ids.next_btn.disabled = True

        self.index += 1

    def batch_process(self):
        self.add_text("Processing Images...")
        try:
            for file in os.listdir(self.folder_path):
                if self.is_image(file):
                    try:
                        image = cv.imread(self.folder_path + "/" + file)
                        self.processor = XhandProcessor(image)
                        self.processor.draw_contours()
                        self.processor.draw_defect_points()
                        self.processor.draw_convex_hull()
                        self.processor.draw_line()
                        self.processor.rotate()

                        self.disksave(self.folder_path, file, self.processor.image)
                    except IndexError:
                        continue
            self.error_dialog = MDDialog(
                text="Folder Batch Successfully Processed",
                radius=[20, 7, 20, 7],
            )
            self.error_dialog.open()
        except Exception as e:
            self.error_dialog = MDDialog(
                text=f"ERROR: {e}",
                radius=[20, 7, 20, 7],
            )
            self.error_dialog.open()

    def add_text(self, text):
        lines = self.screen.ids.output.text.split("\n")
        if len(lines) > self.max_line - 1:
            lines = lines[0:1]+lines[2:]
            lines.append("> " + text)
            self.screen.ids.output.text = "\n".join(lines)
        else:
            self.screen.ids.output.text += f"\n> {text}"

    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.primary_palette = "LightBlue"
        self.screen = Builder.load_string(KV)
        return self.screen

XhandApp().run()
