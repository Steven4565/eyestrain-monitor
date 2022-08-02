from tensorflow.python.ops.numpy_ops import np_config
from source.Database import database
from source.utils.Reminder import *
from source.utils.Config import AppConfig
from source.rotated_rect_crop import *
import math
import time
import cv2 as cv
import numpy as np
import mediapipe as mp
import tensorflow as tf
import tensorflow.keras as keras


np_config.enable_numpy_behavior()

faceMesh = mp.solutions.face_mesh.FaceMesh(
    max_num_faces=3, min_detection_confidence=0.5, min_tracking_confidence=0.5)
landmark_points = np.array([130, 133, 145, 159, 263, 362, 374, 386])

# change the height value of IMG_SIZE to change AI threshold
IMG_SIZE = (64, 30)
AI_INPUT_SIZE = (34, 26)
DEBUG = False

FONT_SIZE = 1
FONT_COLOR = (0, 0, 255)

model_new = keras.models.load_model('models/blinkdetection.h5')


def detect_blink(eye_img):
    pred_B = model_new(eye_img)
    status = pred_B[0][0]
    status = status*100
    status = round(status, 3)
    return status


class AILogic:
    def __init__(self):
        self.frame = None

        self.imgRGB = None
        self.results = []

        self.prev_rect = None
        self.cropped_eye = None

        # for counting blinks
        self.blink_count = []
        self.blink_count_buffer = 0
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

        # open filestream for saving data
        self.f = open("blink_data.csv", "a", newline="")

    def process_frame(self, frame) -> cv2.Mat:
        self.imgRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        self.last_frame_stamp = time.time()
        self.results = faceMesh.process(self.imgRGB)

        # face does not show on frame
        if not self.results.multi_face_landmarks:
            if (not self.since_face_left_frame):
                self.since_face_left_frame = time.time()
            # break starts
            if (time.time() - self.since_face_left_frame > AppConfig.cfg["activity"]["min_break"]):
                self.since_face_entered_frame = None
                self.start_timestamp = None

                # insert to database if session has already started for 2 minutes
                self.on_session_finish()
        # face shows on frame
        else:
            self.since_face_left_frame = None
            if (not self.since_face_entered_frame):
                self.since_face_entered_frame = time.time()
                self.start_timestamp = time.time()

            for faceLms in self.results.multi_face_landmarks:
                # get the eye coords from landmarks
                coords_left, coords_right = self.landmark_to_coords(
                    faceLms.landmark, self.imgRGB)

                # get bounding box and draw it
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
                if self.prediction_new < AppConfig.cfg["activity"]["ai_confidence_threshold"]:
                    self.blinked = True
                    break
                self.blinked = False

        # handle per minute blink frequency
        if (self.since_face_entered_frame):
            # timer every 60 seconds
            if (round(time.time() - self.start_timestamp) > 60):
                self.start_timestamp = time.time()
                date = time.strftime('%d', time.localtime())
                hour = time.strftime('%H', time.localtime())
                self.blink_count.append((date, hour, self.blink_count_buffer))
                print(self.blink_count)
                self.blink_count_buffer = 0

        # handle blinks
        if (self.blinked and self.prev_blink == False and self.blink_interval > 0.08):
            # TODO: add to blink count
            self.blink_count_buffer += 1
            self.prev_blink = True
            self.blink_interval = 0
            self.prev_time = time.time()

        # blink duration
        if(not self.blinked and not self.prev_blink):
            self.blink_interval = time.time() - self.prev_time

        # remind to blink after a few seconds of not blinking
        if (self.blink_interval > AppConfig.cfg["activity"]["max_blink_interval"]):
            self.blink_interval = 0
            self.prev_time = time.time()
            Reminder.remind_blink()

        # remind to take breaks
        if (self.since_face_entered_frame and time.time() - self.since_face_entered_frame > AppConfig.cfg["activity"]["max_session"] * self.break_reminder_count):
            self.break_reminder_count += 1
            Reminder.remind_break()

        exec_time = round((time.time() - self.last_frame_stamp), 5)

        if (AppConfig.cfg["video"]["debug_mode"]):
            cv.putText(self.imgRGB, 'percent opened ' + str(self.prediction_new), (10, 50),
                       cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)
            cv.putText(self.imgRGB, 'exec time: ' + str(exec_time) + 'ms', (10, 250),
                       cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)
        cv.putText(self.imgRGB, 'count: ' + str(self.blink_count_buffer) + ('+' if self.blinked else ''),
                   (10, 100), cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)
        if (self.since_face_entered_frame):
            cv.putText(self.imgRGB, 'session time: ' + str(round(time.time() - self.since_face_entered_frame)) + 's',
                       (10, 150), cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)
        if (self.since_face_left_frame):
            cv.putText(self.imgRGB, 'break time: {0}/{1}s'.format(str(round(time.time() - self.since_face_left_frame)), str(
                AppConfig.cfg["activity"]["min_break"])), (10, 200), cv.FONT_HERSHEY_SIMPLEX, FONT_SIZE, FONT_COLOR, 2)

        return self.imgRGB

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
        height = width * \
            AppConfig.cfg["activity"]["eye_crop_height"] / IMG_SIZE[0]

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

    def on_session_finish(self):
        if (len(self.blink_count) >= 1):
            self.blink_count = []
            database.insert_session_entries(self.blink_count)


AIInstance = AILogic()
