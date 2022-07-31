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

    # Get all the available cameras
    # https://stackoverflow.com/a/62639343
    @staticmethod
    def get_cameras():
        non_working_ports = []
        dev_port = 0
        working_ports: list[int] = []
        available_ports = []
        # if there are more than 5 non working ports stop the testing.
        while len(non_working_ports) < 6:
            camera = cv2.VideoCapture(dev_port)
            if not camera.isOpened():
                non_working_ports.append(dev_port)
                print("Port %s is not working." % dev_port)
            else:
                is_reading, img = camera.read()
                w = camera.get(3)
                h = camera.get(4)
                if is_reading:
                    print("Port %s is working and reads images (%s x %s)" %
                          (dev_port, h, w))
                    working_ports.append(dev_port)
                else:
                    print("Port %s for camera ( %s x %s) is present but does not reads." % (
                        dev_port, h, w))
                    available_ports.append(dev_port)
            dev_port += 1
        return working_ports

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
