import PIL.ImageTk
import PIL.Image
import tkinter as tk
from rotated_rect_crop import *
from pygame import mixer
import pygame
import csv
import math
import time
import cv2 as cv
import numpy as np
import mediapipe as mp
import tensorflow.keras as keras

from tensorflow.python.ops.numpy_ops import np_config
np_config.enable_numpy_behavior()

MAX_SESSION = 1200  # max screen time in seconds
MIN_BREAK = 20  # min break (minimum face not detected time for timer to reset)
MAX_BLINK_INTERVAL = 10  # max time for not blinking in seconds
CAMERA_INDEX = 1

# change the height value of IMG_SIZE to change AI threshold
IMG_SIZE = (64, 30)
AI_INPUT_SIZE = (34, 26)
DEBUG = False

FONT_SIZE = 1
FONT_COLOR = (0, 0, 255)

SHORT_VOICEOVER = True

model_new = keras.models.load_model('models/blinkdetection.h5')


def detect_blink(eye_img):
    # pred_B = model_new.predict(eye_img)
    pred_B = model_new(eye_img)
    status = pred_B[0][0]
    status = status*100
    status = round(status, 3)
    return status


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
    def __init__(self, window, window_title, video_source=0):

        # ============================== AI vars ==============================

        self.imgRGB = None
        self.results = []

        self.prev_rect = None
        self.cropped_eye = None

        # for counting blinks
        self.blink_count = [0]
        self.prev_blink = False
        self.blinked = False
        self.prediction_new = 0

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

        # Creates a custom routine based on the delay
        self.delay = 17  # 33ms delay for 30 fps
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

    def landmark_to_coords(self, face_landmarks, image):
        coords_left = []  # left eye coords
        coords_right = []  # right eye coords
        for id, lm in enumerate(face_landmarks):
            for idx in range(len(landmark_points)):
                if id == landmark_points[idx]:
                    ih, iw, ic = image.shape
                    x, y = int(lm.x*iw), int(lm.y*ih)
                    if (idx < 4):
                        coords_left.append([int(x), int(y)])
                    else:
                        coords_right.append([int(x), int(y)])

        return (coords_left, coords_right)

    def get_bb(self, coords_left, coords_right):
        # get the angle of the eyes
        m_left_x, m_left_y = coords_left[0]
        m_right_x, m_right_y = coords_right[0]
        m = (m_left_y-m_right_y) / (m_left_x-m_right_x)
        angle_in_degrees = math.degrees(math.atan(m))

        # get width of left eye and right eye
        width_left = abs(coords_left[0][0]-coords_left[1][0])
        width_right = abs(coords_right[0][0]-coords_right[1][0])

        # get the biggest rectangle
        biggest_width = max(width_left, width_right)
        coords = coords_left if width_left > width_right else coords_right

        width = biggest_width * 1.2
        height = width * IMG_SIZE[1] / IMG_SIZE[0]

        rect = (((coords[0][0]+coords[1][0])//2, (coords[0][1]+coords[1]
                [1])//2), (int(width), int(height)), angle_in_degrees)

        # compare with previous rect, if difference is negligable, keep the old one for stabilizing purposes
        if (self.prev_rect and abs(self.prev_rect[0][0] - rect[0][0]) < 2 and abs(self.prev_rect[0][1] - rect[0][1]) < 2 and abs(self.prev_rect[1][0] - rect[1][0]) < 2 and abs(self.prev_rect[1][1] - rect[1][1]) < 2 and abs(self.prev_rect[2] - rect[2]) < 10):
            rect = self.prev_rect
        else:
            self.prev_rect = rect

        # draw bounding box
        box = np.int0(cv.boxPoints(rect))
        cv.drawContours(self.imgRGB, [box], 0, (255, 255, 255), 1)

        return rect

    def try_processing_eyes(self, rect, imgRGB):
        # crop the eyes
        try:
            image_cropped = cv.resize(crop_rotated_rectangle(
                imgRGB, rect), (AI_INPUT_SIZE[0], AI_INPUT_SIZE[1]))
            image_cropped = cv.cvtColor(
                image_cropped, cv.COLOR_BGR2GRAY)
            return image_cropped
        except:
            return None

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
            self.since_face_left_frame = None
            if (not self.since_face_entered_frame):
                self.since_face_entered_frame = time.time()
                self.start_timestamp = time.time()

            for faceLms in self.results.multi_face_landmarks:
                # get the eye coords from landmarks
                coords_left, coords_right = self.landmark_to_coords(
                    faceLms.landmark, self.imgRGB)

                # ger bounding box and draw it
                rect = self.get_bb(coords_left, coords_right)

                processed_image = self.try_processing_eyes(rect, self.imgRGB)
                if processed_image is not None:
                    self.cropped_eye = processed_image
                else:
                    continue

                # predict the blink
                self.prediction_new = detect_blink(
                    np.array([processed_image]).astype(np.float32)/255)
                self.prev_blink = self.blinked
                if self.prediction_new < 0.9:
                    self.blinked = True
                    break
                self.blinked = False

            if(DEBUG):
                cv.imshow('eye', self.cropped_eye)
                cv.waitKey(0)
                cv.destroyAllWindows()

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
            self.blink_count = [0]

        # blink duration
        if(not self.blinked and not self.prev_blink):
            self.blink_interval = time.time() - self.prev_time

        # remind to blink after a few seconds of not blinking
        if (self.blink_interval > MAX_BLINK_INTERVAL):
            self.blink_interval = 0
            self.prev_time = time.time()
            # playBlink()

        fps = round(1/(time.time() - self.last_frame_stamp), 5)

        cv.putText(self.imgRGB, 'percent opened ' + str(self.prediction_new), (10, 50),
                   cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)
        cv.putText(self.imgRGB, 'count: ' + str(int(sum(self.blink_count))) + ('+' if self.blinked else ''),
                   (10, 100), cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)
        if (self.since_face_entered_frame):
            cv.putText(self.imgRGB, 'session time: ' + str(round(time.time() - self.since_face_entered_frame)) + 's',
                       (10, 150), cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)
        if (self.since_face_left_frame):
            cv.putText(self.imgRGB, 'break time: ' + str(round(time.time() - self.since_face_left_frame)) + '/' + str(MIN_BREAK) +
                       's', (10, 200), cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)
        cv.putText(self.imgRGB, 'fps: ' + str(fps), (10, 250),
                   cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)

    def write_to_file(self, array):
        csv.writer(self.f, delimiter=',').writerows(array)


class VideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        res = (1280, 720)
        # set video source width and height
        self.vid.set(3, res[0])
        self.vid.set(4, res[1])
        self.vid.set(cv.CAP_PROP_FPS, 90)

        # Get video source width and height
        self.width, self.height = res

    # To get frames

    def get_frame(self):
        success, image = self.vid.read()  # read image
        if not self.vid.isOpened():
            return (success, None)

        if not success:
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
