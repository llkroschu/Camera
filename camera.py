import cv2
from pygrabber.dshow_graph import FilterGraph
import time
import os
import threading
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from datetime import datetime
from PIL import Image
from logWidget import LogWidget

# raspberry pi v2 12MP Camera resolutions:
supported_resolution_pi_v2 = [[4032, 3040], [3840, 2160], [2592, 1944], [2560, 1440], [1920, 1080], [1280, 720],
                              [640, 480]]


class Camera(QObject):
    frame_signal = pyqtSignal(QPixmap)

    def __init__(self, device_number, resolution):
        super().__init__()
        # creates capture Object for given device number
        self.device_number = device_number
        self.resolution = resolution
        # self.frame_signal = pyqtSignal(QPixmap)
        self.__live_feed_running = False
        self.__thread = None
        self.logging = LogWidget
        try:
            self.__capture = cv2.VideoCapture(self.device_number, cv2.CAP_DSHOW)
            self.__capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.__capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])

        except ValueError as e:
            self.__capture = cv2.VideoCapture(0)

    def start_camera_feed(self):
        self.__live_feed_running = True
        self.__thread = threading.Thread(target=self.__update_frame, args=())
        self.__thread.start()
        print(f'Camera feed thread started')

    def __update_frame(self):
        # this method starts the camera live feed
        if not self.__capture.isOpened():
            raise Exception(f'Camera is not opened correctly')
        # getting everything we need for fps display
        prev_frame_time = 0
        font = cv2.FONT_HERSHEY_SIMPLEX

        while self.__capture.isOpened():
            # Capture frame-by-frame
            return_value, self.frame = self.__capture.read()
            if return_value:
                new_frame_time = time.perf_counter()
                # calc frame per sec
                fps = 1 / (new_frame_time - prev_frame_time)
                prev_frame_time = new_frame_time
                # write fps
                fps_display_frame = self.frame.copy()
                height, width, channel = fps_display_frame.shape

                # put logging text:
                self.logging.remove()
                self.logging.set_info(f'Resolution: {width}x{height} at {int(fps)} fps')

                # Convert the frame to QImage and emit the signal
                bytes_per_line = 3 * width
                q_img = QImage(fps_display_frame.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
                self.frame_signal.emit(QPixmap.fromImage(q_img))

                # add a waitKey call
                if cv2.waitKey(1) and not self.__live_feed_running:
                    break

    def capture_image(self, camera_name):
        # will save a picture in pictures folder:
        image_path = 'pictures'

        if not os.path.exists(image_path):
            os.makedirs(image_path)

        if self.__live_feed_running:
            # save image
            now = datetime.now()
            image_name = f'{now.strftime("%Y%m%d_%H%M%S")}_{camera_name}_{self.resolution[0]}x{self.resolution[1]}.png'
            Image.fromarray(self.frame).save(f'{image_path}/{image_name}')
            print(f'{image_name}    --> saved successfully!')
        else:
            raise ValueError(f'unable to capture Image')

    def stop_camera(self):
        # close the live feed
        self.__live_feed_running = False
        self.__thread.join()
        self.__capture.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    graph = FilterGraph()
    print(graph.get_input_devices())

    device_nr = graph.get_input_devices().index('Arducam IMX477 HQ Camera')

    live_feed = Camera(device_nr, supported_resolution_pi_v2[3])

    live_feed.start_camera_feed()
    time.sleep(3)
    live_feed.capture_image()
    time.sleep(3)
    live_feed.stop_camera()

