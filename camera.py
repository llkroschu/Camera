import cv2
from pygrabber.dshow_graph import FilterGraph
import time
import os
import threading

# raspberry pi v2 12MP Camera resolutions:
supported_resolution_pi_v2 = [[4032, 3040], [3840, 2160], [2592, 1944], [2560, 1440], [1920, 1080], [1280, 720],
                              [640, 480]]


class Camera:
    HIGH_VALUE = 10000
    WIDTH = HIGH_VALUE
    HEIGHT = HIGH_VALUE

    def __init__(self, device_number, resolution):
        # creates capture Object for given device number
        self.device_number = device_number
        self.resolution = resolution
        self.__live_feed_running = False
        self.__thread = None
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
                display_text = f'fps:{int(fps)}, res:{self.resolution[0]} x {self.resolution[1]}'
                cv2.putText(fps_display_frame, display_text, (7, 25), font, 0.5, (100, 255, 0), 1)

                # display video
                cv2.imshow('image', fps_display_frame)

                # add a waitKey call
                if cv2.waitKey(1) and not self.__live_feed_running:
                    break

    def capture_image(self):
        # will save a picture in pictures folder:
        image_path = 'pictures'

        if not os.path.exists(image_path):
            os.makedirs(image_path)

        if self.__live_feed_running:
            # save image
            cv2.imwrite(f'{image_path}/image.png', self.frame)
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

    live_feed = CameraFeed(device_nr, supported_resolution_pi_v2[3])

    live_feed.start_camera_feed()
    time.sleep(3)
    live_feed.capture_image()
    time.sleep(3)
    live_feed.stop_camera()

