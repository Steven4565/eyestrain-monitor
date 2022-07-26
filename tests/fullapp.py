import math
import time
import cv2 as cv
import numpy as np
import seaborn as sns
import mediapipe as mp
import tensorflow as tf
import matplotlib.pyplot as plt
import tensorflow.keras as keras

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

import pygame
from pygame import mixer

from rotated_rect_crop import *

MAX_SESSION = 1200  # max screen time in seconds
MIN_BREAK = 20  # min break (minimum face not detected time for timer to reset)
MAX_BLINK_INTERVAL = 10  # max time for not blinking in seconds
CAMERA_INDEX = 1

EXIT_KEY = 'q'
TOGGLE_DEBUG_KEY = 'd'
VOICE_CHANGE_KEY = 'v'
FONT_SIZE = 1
FONT_COLOR = (0, 0, 255)

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

SHORT_VOICEOVER = True


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


cap = cv.VideoCapture(CAMERA_INDEX)
mpFaceMesh = mp.solutions.face_mesh
faceMesh = mpFaceMesh.FaceMesh(
    max_num_faces=3, min_detection_confidence=0.5, min_tracking_confidence=0.5)
landmark_points = np.array([130, 133, 145, 159, 263, 362, 374, 386])
prev_rect = None

# for counting blinks
blink_count = []
prev_blink = False
blinked = False

# counting time interval between blinks
blink_interval = 0
prev_time = time.time()
start_timestamp = time.strftime('%M %S', time.gmtime())

# counting screen time
break_time = 0
screen_time = 0
temp_screen_time = 0
latest_face_undetected = time.time()
latest_face_detected = None
transition_face_detected_timestamp = None

# for repeating break reminders
break_reminder_count = 1

# fps counter
last_frame_stamp = 0
fps = 0

show_debug = True


while cap.isOpened():
    success, image = cap.read()  # read image
    if not success:
        print("Ignoring empty camera frame.")
        continue
    height, width, _ = image.shape
    imgRGB = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    last_frame_stamp = time.time()
    results = faceMesh.process(imgRGB)

    if not results.multi_face_landmarks:
        prev_time = time.time()
        blink_interval = 0
        if (latest_face_detected):
            # set
            transition_face_detected_timestamp = time.time()
            screen_time += temp_screen_time
            # reset
            temp_screen_time = 0
            latest_face_detected = None

        # if break is more than 30s
        if (transition_face_detected_timestamp):
            break_time = time.time() - transition_face_detected_timestamp
            if (time.time() - transition_face_detected_timestamp > MIN_BREAK):
                screen_time = 0
                break_time = 0
                transition_face_detected_timestamp = None

        latest_face_undetected = time.time()
    else:
        break_time = 0
        latest_face_detected = time.time()
        temp_screen_time = latest_face_detected - latest_face_undetected

        for faceLms in results.multi_face_landmarks:
            # get the eye landmarks
            coords_i = []
            coords_a = []
            for id, lm in enumerate(faceLms.landmark):
                for idx in range(len(landmark_points)):
                    if id == landmark_points[idx]:
                        ih, iw, ic = imgRGB.shape
                        x, y = int(lm.x*iw), int(lm.y*ih)
                        if (idx < 4):
                            coords_i.append([int(x), int(y)])
                        else:
                            coords_a.append([int(x), int(y)])

            # get the angle of the eyes
            m = (coords_i[0][1]-coords_a[0][1])/(coords_i[0][0]-coords_a[0][0])
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

            if (prev_rect and abs(prev_rect[0][0] - temp_rect[0][0]) < 2 and abs(prev_rect[0][1] - temp_rect[0][1]) < 2 and abs(prev_rect[1][0] - temp_rect[1][0]) < 2 and abs(prev_rect[1][1] - temp_rect[1][1]) < 2 and abs(prev_rect[2] - temp_rect[2]) < 10):
                rect = prev_rect
            else:
                rect = temp_rect
                prev_rect = rect

            # crop the eyes
            processed_images = []
            box = np.int0(cv.boxPoints(rect))
            try:
                if (show_debug):
                    cv.drawContours(image, [box], 0, (255, 255, 255), 1)
                image_cropped = cv.resize(
                    crop_rotated_rectangle(imgRGB, rect), (24, 24))
                image_cropped = cv.cvtColor(image_cropped, cv.COLOR_BGR2GRAY)
                image_cropped = cv.cvtColor(image_cropped, cv.COLOR_GRAY2BGR)
                image_cropped = enlighten_image(image_cropped)
                image_cropped = tf.keras.applications.vgg19.preprocess_input(
                    image_cropped)
                processed_images.append(image_cropped)
            except:
                continue

            # predict the blink
            predictions = model.predict(np.array(processed_images))
            prev_blink = blinked
            for prediction in predictions:
                if np.ceil(prediction):
                    blinked = True
                    break
                blinked = False

    # handle per minute blink frequency
    if (start_timestamp != time.strftime('%M', time.gmtime())):
        start_timestamp = time.strftime('%M', time.gmtime())
        blink_count.append(0)

    # handle blinks
    if (blinked and prev_blink == False and blink_interval > 0.08):
        blink_count[len(blink_count)-1] += 1
        prev_blink = True
        blink_interval = 0
        prev_time = time.time()

    # blink duration
    if(not blinked and not prev_blink):
        blink_interval = time.time() - prev_time

    # remind to blink after a few seconds of not blinking
    if (blink_interval > MAX_BLINK_INTERVAL):
        blink_interval = 0
        prev_time = time.time()
        playBlink()

    # remind to take breaks
    if (screen_time + temp_screen_time > MAX_SESSION * break_reminder_count):
        playBreak()
        break_reminder_count += 1

    fps = round(1/(time.time() - last_frame_stamp), 5)

    cv.imshow("Image", image)

    pressed_key = cv.waitKey(1) & 0xFF
    if pressed_key == ord(EXIT_KEY):
        cv.destroyAllWindows()
        break
    elif (pressed_key == ord(TOGGLE_DEBUG_KEY)):
        show_debug = not show_debug
    elif (pressed_key == ord(VOICE_CHANGE_KEY)):
        SHORT_VOICEOVER = not SHORT_VOICEOVER
cap.release()

plt.plot(range(len(blink_count)), blink_count)
plt.title('Blink Per Minute Frequency')
plt.xlabel('Time (minutes)')
plt.ylabel('Blink Frequency')
