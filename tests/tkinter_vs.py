import tkinter as tk
import cv2
import PIL.Image
import PIL.ImageTk


class App:
    def __init__(self, window, window_title, video_source=1):
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

        if success:
            self.photo = PIL.ImageTk.PhotoImage(
                image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.window.after(self.delay, self.update)


class VideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source, cv2.CAP_DSHOW)
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
        if not self.vid.isOpened():
            return (success, None)

        success, frame = self.vid.read()
        if not success:
            return (success, None)

        return (success, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            cv2.destroyAllWindows()


def main():
    App(tk.Tk(), 'Video Recorder')


main()
