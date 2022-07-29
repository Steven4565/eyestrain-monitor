import cv2


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

    def get_fps(self):
        return self.vid.get(cv2.CAP_PROP_FPS)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            cv2.destroyAllWindows()
