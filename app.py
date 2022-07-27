import csv
import math
import time
import cv2 as cv
import numpy as np
import mediapipe as mp
import tensorflow as tf
import tensorflow.keras as keras

import pygame
from pygame import mixer

from rotated_rect_crop import *

# Tkinter imports
import tkinter as tk
import PIL.Image
import PIL.ImageTk


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


# Tkinter -------------------------------------

class App:
    def __init__(self, window, window_title, video_source=1):

        # ============================== AI vars ==============================

        self.imgRGB = None
        self.results = []

        self.prev_rect = None

        # for counting blinks
        self.blink_count = [0]
        self.prev_blink = False
        self.blinked = False

        # counting time interval between blinks
        self.blink_interval = 0
        self.prev_time = time.time()

        # counting screen time
        self.since_face_left_frame = time.time()
        self.since_face_entered_frame = None
        # same as since_face_entered_frame but will be reset every 60 seconds for the graph
        self.start_timestamp = None

        # for repeating break reminders
        self.break_reminder_count = 1

        # fps counter
        self.last_frame_stamp = 0
        self.fps = 0

        self.show_debug = True

        self.f = open("blink_data.csv", "a", newline="")

        # ============================= GUI stuff ==============================
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source

        # open video source (by default this will try to open the computer webcam)
        self.vid = VideoCapture(self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(
            window, width=self.vid.width, height=self.vid.height)
        self.canvas.pack()

        # quit button
        self.btn_quit = tk.Button(window, text='QUIT', command=quit)
        self.btn_quit.pack(side=tk.LEFT)

        # Creates a custom routine based on the delay
        self.delay = 30  # 33ms delay for 30 fps
        self.update()

        self.window.mainloop()

    def update(self):
        success, frame = self.vid.get_frame()
        # process ai here
        self.process_frame(frame)

        if success:
            self.photo = PIL.ImageTk.PhotoImage(
                image=PIL.Image.fromarray(self.imgRGB))  # process the image here
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.window.after(self.delay, self.update)

    def process_frame(self, frame):
        self.imgRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        self.last_frame_stamp = time.time()
        self.results = faceMesh.process(self.imgRGB)

        # face does not show on frame
        if not self.results.multi_face_landmarks:
            if (not self.since_face_left_frame):
                self.since_face_left_frame = time.time()
            if (time.time() - self.since_face_left_frame > 10):
                self.since_face_entered_frame = None
                self.start_timestamp = None
        # face shows on frame
        else:
            if (self.since_face_left_frame and time.time() - self.since_face_left_frame > 10):
                self.write_to_file(
                    [[time.strftime('%H:%M', time.localtime()), 'break', round(time.time() - self.since_face_left_frame)]])
                print([time.strftime('%H:%M', time.localtime()), 'break',
                      round(time.time() - self.since_face_left_frame)])
            self.since_face_left_frame = None
            if (not self.since_face_entered_frame):
                self.since_face_entered_frame = time.time()
                self.start_timestamp = time.time()

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
        if (self.since_face_entered_frame):
            if (round(time.time() - self.start_timestamp) > 60):
                self.start_timestamp = time.time()
                self.blink_count.append(0)

        # handle blinks
        if (self.blinked and self.prev_blink == False and self.blink_interval > 0.08):
            self.blink_count[len(self.blink_count)-1] += 1
            self.prev_blink = True
            self.blink_interval = 0
            self.prev_time = time.time()

        # write session data to file
        if (len(self.blink_count) > 5):
            self.write_to_file(
                [[time.strftime('%H:%M', time.localtime()), 'session', *self.blink_count[0:-1]]])
            print([time.strftime('%H:%M', time.localtime()),
                  'session', *self.blink_count[0:-1]])
            self.blink_count = [0]

        # blink duration
        if(not self.blinked and not self.prev_blink):
            self.blink_interval = time.time() - self.prev_time

        # remind to blink after a few seconds of not blinking
        if (self.blink_interval > MAX_BLINK_INTERVAL):
            self.blink_interval = 0
            self.prev_time = time.time()
            # playBlink()

        # remind to take breaks
        # if (self.screen_time + self.temp_screen_time > MAX_SESSION * self.break_reminder_count):
        #     playBreak()
        #     self.break_reminder_count += 1

        fps = round(1/(time.time() - self.last_frame_stamp), 5)

        cv.putText(self.imgRGB, 'count: ' + str(int(sum(self.blink_count))) + ('+' if self.blinked else ''),
                   (10, 50), cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)
        if (self.since_face_entered_frame):
            cv.putText(self.imgRGB, 'session time: ' + str(round(time.time() - self.since_face_entered_frame)) + 's',
                       (10, 100), cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)
        # cv.putText(self.imgRGB, 'break reminder: ' + str(round(self.screen_time + self.temp_screen_time)) + 's',
        #            (10, 200), cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)
        if (self.since_face_left_frame):
            cv.putText(self.imgRGB, 'break time: ' + str(round(time.time() - self.since_face_left_frame)) + '/' + str(MIN_BREAK) +
                       's', (10, 250), cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)
        cv.putText(self.imgRGB, 'fps: ' + str(fps), (10, 300),
                   cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)

    def write_to_file(self, array):
        csv.writer(self.f, delimiter=',').writerows(array)


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
    App(tk.Tk(), 'Video Recorder', 1)


main()
