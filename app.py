import math
import time
import cv2 as cv
import numpy as np
import seaborn as sns
import mediapipe as mp
import tensorflow as tf
import matplotlib.pyplot as plt
import tensorflow.keras as keras

import pygame
from pygame import mixer

from source.rotated_rect_crop import *

# Tkinter imports
import tkinter as tk
from tkinter.ttk import Notebook, Style
import PIL.Image
import PIL.ImageTk
import customtkinter
from source.customWidgets import *


MAX_SESSION = 1200  # max screen time in seconds
MIN_BREAK = 20  # min break (minimum face not detected time for timer to reset)
MAX_BLINK_INTERVAL = 10  # max time for not blinking in seconds
CAMERA_INDEX = 1

FONT_SIZE = 1
FONT_COLOR = (0, 0, 255)

SHORT_VOICEOVER = True


model = tf.keras.models.Sequential([
    # The first convolution
    tf.keras.layers.Conv2D(16, (3, 3), activation='relu',
                           input_shape=(24, 24, 3)),
    tf.keras.layers.MaxPooling2D(2, 2),
    # The second convolution
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2, 2),
    # The third convolution
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2, 2),
    # Flatten the results to feed into a DNN
    tf.keras.layers.Flatten(),
    # 512 neuron hidden layer
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')])

model.compile(loss="binary_crossentropy",
              optimizer=keras.optimizers.Adam(learning_rate=0.001),
              metrics=["accuracy"])
model.load_weights("./model.h5")

pygame.init()

short_sound_blink = mixer.Sound("./sounds/short_blink.wav")
short_sound_break = mixer.Sound("./sounds/short_break.wav")
long_sound_blink = mixer.Sound("./sounds/voiceover_blink.wav")
long_sound_break = mixer.Sound("./sounds/voiceover_break.wav")


def playBlink():
    if SHORT_VOICEOVER:
        short_sound_blink.play()
    else:
        long_sound_blink.play()


def playBreak():
    if SHORT_VOICEOVER:
        short_sound_break.play()
    else:
        long_sound_break.play()


def enlighten_image(bgrImage):
    enlightened = cv.cvtColor(bgrImage, cv.COLOR_BGR2YUV)
    enlightened[:, :, 0] = cv.equalizeHist(enlightened[:, :, 0])
    return cv.cvtColor(enlightened, cv.COLOR_YUV2BGR)


faceMesh = mp.solutions.face_mesh.FaceMesh(
    max_num_faces=3, min_detection_confidence=0.5, min_tracking_confidence=0.5)
landmark_points = np.array([130, 133, 145, 159, 263, 362, 374, 386])


class App:
    def __init__(self, window_title, video_source=0):

        # ============================== AI vars ==============================

        self.imgRGB = None
        self.results = []

        self.prev_rect = None

        # for counting blinks
        self.blink_count = []
        self.prev_blink = False
        self.blinked = False

        # counting time interval between blinks
        self.blink_interval = 0
        self.prev_time = time.time()
        self.start_timestamp = time.strftime('%M %S', time.gmtime())

        # counting screen time
        self.break_time = 0
        self.screen_time = 0
        self.temp_screen_time = 0
        self.latest_face_undetected = time.time()
        self.latest_face_detected = None
        self.transition_face_detected_timestamp = None

        # for repeating break reminders
        self.break_reminder_count = 1

        # fps counter
        self.last_frame_stamp = 0
        self.fps = 0

        self.show_debug = True

        # ============================= GUI stuff ==============================
        self.video_source = video_source

        # open video source
        self.vid = VideoCapture(self.video_source)

        # =========== Main Window ===========

        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("blue")

        self.root_tk = customtkinter.CTk()
        self.root_tk.geometry("800x500")
        self.root_tk.title(window_title)
        self.root_tk.grid_rowconfigure(1, weight=1)
        self.root_tk.grid_columnconfigure(0, weight=1)

        self.Menu = customtkinter.CTkFrame(
            master=self.root_tk, width=800, height=75, corner_radius=0, fg_color="#212325")
        self.Menu.grid(row=0, column=0, sticky="NEWS")

        self.Menu.grid_columnconfigure(0, weight=1)
        self.Menu.grid_columnconfigure(1, weight=1)
        self.Menu.grid_columnconfigure(2, weight=1)

        self.ActivityButton = MenuButton(self.Menu, 'Activity', 'Helvetica 16 bold',
                                         lambda: self.note.select(0)).grid(column=0, row=0)
        self.StartButton = MenuButton(self.Menu, 'Start', 'Helvetica 16 bold',
                                      lambda: self.note.select(1)).grid(column=1, row=0)
        self.SettingsButton = MenuButton(self.Menu, 'Settings', 'Helvetica 16 bold',
                                         lambda: self.note.select(2)).grid(column=2, row=0)

        noteStyle = Style()
        noteStyle.theme_use('default')
        noteStyle.layout('TNotebook.Tab', [])
        noteStyle.configure("TNotebook", background="#212325", borderwidth=0)
        noteStyle.configure(
            "TNotebook.Tab", background="#212325", borderwidth=0)
        noteStyle.map("TNotebook", background=[("selected", "#212325")])

        self.note = Notebook(self.root_tk, padding=25)
        self.note.grid(column=0, row=1, stick="NEWS")

        # =========== Activity Page ===========
        ActivityPage = customtkinter.CTkFrame(master=self.note,
                                              width=200,
                                              height=200,
                                              corner_radius=10)
        customtkinter.CTkLabel(ActivityPage, text="activity page").grid()
        self.note.add(ActivityPage)

        # =========== Start Page ===========

        StartPage = customtkinter.CTkFrame(master=self.note,
                                           width=200,
                                           height=200,
                                           corner_radius=10)
        customtkinter.CTkLabel(StartPage, text="start page").grid()
        self.note.add(StartPage)

        # =========== Settings Page ===========

        SettingsPage = customtkinter.CTkFrame(master=self.note,
                                              width=200,
                                              height=200,
                                              corner_radius=10)
        self.note.add(SettingsPage)

        # Create a canvas that can fit the above video source size
        self.scrollbar = customtkinter.CTkScrollbar()
        self.canvas = customtkinter.CTkCanvas(
            StartPage, width=self.vid.width, height=self.vid.height)
        self.canvas.grid(column=0, row=0, sticky="news")

        self.scrollbar = customtkinter.CTkScrollbar(
            StartPage, command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)


        # Creates a custom routine based on the delay
        self.delay = 30  # 33ms delay for 30 fps
        self.update()

        self.root_tk.mainloop()

    def update(self):
        success, frame = self.vid.get_frame()
        # process ai here
        self.process_frame(frame)

        if success:
            self.photo = PIL.ImageTk.PhotoImage(
                image=PIL.Image.fromarray(self.imgRGB))  # process the image here
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.root_tk.after(self.delay, self.update)

    def process_frame(self, frame):
        self.imgRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        self.last_frame_stamp = time.time()
        self.results = faceMesh.process(self.imgRGB)

        if not self.results.multi_face_landmarks:
            self.prev_time = time.time()
            self.blink_interval = 0
            if (self.latest_face_detected):
                # set
                self.transition_face_detected_timestamp = time.time()
                self.screen_time += self.temp_screen_time
                # reset
                self.temp_screen_time = 0
                self.latest_face_detected = None

            # if break is more than 30s
            if (self.transition_face_detected_timestamp):
                self.break_time = time.time() - self.transition_face_detected_timestamp
                if (time.time() - self.transition_face_detected_timestamp > MIN_BREAK):
                    self.screen_time = 0
                    self.break_time = 0
                    self.transition_face_detected_timestamp = None

            self.latest_face_undetected = time.time()
        else:
            self.break_time = 0
            self.latest_face_detected = time.time()
            self.temp_screen_time = self.latest_face_detected - self.latest_face_undetected

            for faceLms in self.results.multi_face_landmarks:
                # get the eye landmarks
                coords_i = []
                coords_a = []
                for id, lm in enumerate(faceLms.landmark):
                    for idx in range(len(landmark_points)):
                        if id == landmark_points[idx]:
                            ih, iw, ic = self.imgRGB.shape
                            x, y = int(lm.x*iw), int(lm.y*ih)
                            if (idx < 4):
                                coords_i.append([int(x), int(y)])
                            else:
                                coords_a.append([int(x), int(y)])

                # get the angle of the eyes
                m = (coords_i[0][1]-coords_a[0][1]) / \
                    (coords_i[0][0]-coords_a[0][0])
                angle_in_degrees = math.degrees(math.atan(m))

                # get the cropped rectangle coordinates
                rect = None
                temp_rect = None
                padding = 10
                width_i = max(abs(coords_i[0][0]-coords_i[1][0]),
                              abs(coords_i[2][1]-coords_i[3][1])) + padding
                width_a = max(abs(coords_a[0][0]-coords_a[1][0]),
                              abs(coords_a[2][1]-coords_a[3][1])) + padding
                # get the biggest rectangle
                if (width_a >= width_i):
                    temp_rect = (((coords_a[0][0]+coords_a[1][0])//2, (coords_a[0]
                                                                       [1]+coords_a[1][1])//2), (width_a, width_a), angle_in_degrees)
                else:
                    temp_rect = (((coords_i[0][0]+coords_i[1][0])//2, (coords_i[0]
                                                                       [1]+coords_i[1][1])//2), (width_i, width_i), angle_in_degrees)

                if (self.prev_rect and abs(self.prev_rect[0][0] - temp_rect[0][0]) < 2 and abs(self.prev_rect[0][1] - temp_rect[0][1]) < 2 and abs(self.prev_rect[1][0] - temp_rect[1][0]) < 2 and abs(self.prev_rect[1][1] - temp_rect[1][1]) < 2 and abs(self.prev_rect[2] - temp_rect[2]) < 10):
                    rect = self.prev_rect
                else:
                    rect = temp_rect
                    self.prev_rect = rect

                # crop the eyes
                processed_images = []
                box = np.int0(cv.boxPoints(rect))
                try:
                    if (self.show_debug):
                        cv.drawContours(
                            self.imgRGB, [box], 0, (255, 255, 255), 1)
                    image_cropped = cv.resize(
                        crop_rotated_rectangle(self.imgRGB, rect), (24, 24))
                    image_cropped = cv.cvtColor(
                        image_cropped, cv.COLOR_BGR2GRAY)
                    image_cropped = cv.cvtColor(
                        image_cropped, cv.COLOR_GRAY2BGR)
                    image_cropped = enlighten_image(image_cropped)
                    image_cropped = tf.keras.applications.vgg19.preprocess_input(
                        image_cropped)
                    processed_images.append(image_cropped)
                except:
                    continue

                # predict the blink
                predictions = model.predict(np.array(processed_images))
                self.prev_blink = self.blinked
                for prediction in predictions:
                    if np.ceil(prediction):
                        self.blinked = True
                        break
                    self.blinked = False

        # handle per minute blink frequency
        if (self.start_timestamp != time.strftime('%M', time.gmtime())):
            self.start_timestamp = time.strftime('%M', time.gmtime())
            self.blink_count.append(0)

        # handle blinks
        if (self.blinked and self.prev_blink == False and self.blink_interval > 0.08):
            self.blink_count[len(self.blink_count)-1] += 1
            self.prev_blink = True
            self.blink_interval = 0
            self.prev_time = time.time()

        # blink duration
        if(not self.blinked and not self.prev_blink):
            self.blink_interval = time.time() - self.prev_time

        # remind to blink after a few seconds of not blinking
        if (self.blink_interval > MAX_BLINK_INTERVAL):
            self.blink_interval = 0
            self.prev_time = time.time()
            playBlink()

        # remind to take breaks
        if (self.screen_time + self.temp_screen_time > MAX_SESSION * self.break_reminder_count):
            playBreak()
            self.break_reminder_count += 1

        fps = round(1/(time.time() - self.last_frame_stamp), 5)

        cv.putText(self.imgRGB, 'count: ' + str(int(sum(self.blink_count))) + ('+' if self.blinked else ''),
                   (10, 50), cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)
        cv.putText(self.imgRGB, 'session time: ' + str(round(self.screen_time + self.temp_screen_time)) + 's',
                   (10, 100), cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)
        cv.putText(self.imgRGB, 'blink interval: ' + str(round(self.blink_interval, 2)) + 's',
                   (10, 150), cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)
        cv.putText(self.imgRGB, 'break reminder: ' + str(round(self.screen_time + self.temp_screen_time)) + 's',
                   (10, 200), cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)
        cv.putText(self.imgRGB, 'break time: ' + str(round(self.break_time)) + '/' + str(MIN_BREAK) +
                   's', (10, 250), cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)
        cv.putText(self.imgRGB, 'fps: ' + str(fps), (10, 300),
                   cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)


class VideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        res = (640, 480)
        # set video source width and height
        self.vid.set(3, res[0])
        self.vid.set(4, res[1])

        # Get video source width and height
        self.width, self.height = res

    # To get frames

    def get_frame(self):
        success, image = self.vid.read()  # read image
        if not self.vid.isOpened():
            return (success, None)

        if not success:
            print("Ignoring empty camera frame.")
            return (success, None)

        return (success, image)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            cv2.destroyAllWindows()


def main():
    App('Eye Strain Monitor', CAMERA_INDEX)


main()
