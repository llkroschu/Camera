import cv2
import neoapi
import time
import os
import threading
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from datetime import datetime
from PIL import Image
from logWidget import LogWidget
import subprocess


class BaumerCamera(QObject):
    frame_signal = pyqtSignal(QPixmap)

    def __init__(self, device_number, resolution):
        super().__init__()
        self.device_number = device_number
        self.resolution = resolution
        self.frame = None
        self.__live_feed_running = False
        self.__thread = None
        self.logging = LogWidget
        self.make_camera_connectable()
        self.__capture = neoapi.Cam()
        self.ensure_camera_closed()
        try:
            self.__capture.Connect(self.device_number)
            self.__capture.f.Width.value = self.resolution[0]
            self.__capture.f.Height.value = self.resolution[1]
            self.__capture.f.ExposureTime.Set(15000)
            self.__capture.f.PixelFormat.value = neoapi.PixelFormat_BGR8
        except ValueError as e:
            self.__capture = neoapi.Cam()
            self.__capture.Connect()

    def ensure_camera_closed(self):
        """Close the camera if it's opened to ensure a clean startup."""
        if self.__capture.IsConnected():
            self.__capture.Disconnect()
            self.__live_feed_running = False

    def start_stream(self):
        self.__live_feed_running = True
        self.__thread = threading.Thread(target=self.__update_frame, args=())
        self.__thread.start()
        print(f'Camera feed thread started')

    def __update_frame(self):
        # this method starts the camera live feed
        if not self.__capture.IsConnected():
            raise Exception(f'Camera is not opened correctly')
        # getting everything we need for fps display
        prev_frame_time = 0

        while self.__capture.IsConnected():
            # Capture frame-by-frame
            self.frame = self.__capture.GetImage()

            if self.frame:
                new_frame_time = time.perf_counter()
                # calc frame per sec
                fps = 1 / (new_frame_time - prev_frame_time)
                prev_frame_time = new_frame_time
                width = self.frame.GetWidth()
                height = self.frame.GetHeight()
                pixelFormat = self.frame.GetPixelFormat()

                # put logging text:
                self.logging.remove()
                self.logging.set_info(f'Resolution: {width}x{height} at {int(fps)} fps')

                # Convert the frame to QImage and emit the signal
                bytes_per_line = 3 * width
                current_frame = self.frame.GetNPArray()
                q_img = QImage(current_frame, width, height, bytes_per_line, QImage.Format.Format_BGR888)
                self.frame_signal.emit(QPixmap.fromImage(q_img))

    def capture_image(self, camera_name):
        # will save a picture in pictures folder:
        image_path = 'pictures'

        if not os.path.exists(image_path):
            os.makedirs(image_path)

        if self.__live_feed_running:
            # save image
            now = datetime.now()
            image_name = f'{now.strftime("%Y%m%d_%H%M%S")}_{camera_name}_{self.resolution[0]}x{self.resolution[1]}.png'
            Image.fromarray(self.frame.GetNPArray()).save(f'{image_path}/{image_name}')
            print(f'{image_name}    --> saved successfully!')
        else:
            raise ValueError(f'unable to capture Image')

    def make_camera_connectable(self):
        cam_list = neoapi.CamInfoList_Get()
        cam_list.Refresh()
        for idx, cam_info in enumerate(cam_list):
            ip_adress = cam_info.GetGevIpAddress()
            if cam_info.GetModelName() == self.device_number and not cam_info.IsConnectable():
                print(f'Camera is not in the same subnet, current IP: {ip_adress} \t I will try to connect it ...')
                subprocess.run(['./source/tools/gevipconfig.exe', "-a"])
                cam_list.Refresh()
                ip_adress_new = cam_list[idx].GetGevIpAddress()
                print(f'new IP adress is now: {ip_adress_new}')
            else:
                continue

    def set_exposure(self, value):
        self.__capture.f.ExposureTime.Set(value)

    def set_gain(self, value):
        self.__capture.f.Gain.Set(value)

    def set_gamma(self, value):
        self.__capture.f.Gamma.Set(value)

    def set_exposure_off(self):
        self.__capture.f.ExposureAuto.Set(neoapi.ExposureAuto_Off)

    def set_exposure_once(self):
        self.__capture.f.ExposureAuto.Set(neoapi.ExposureAuto_Once)

    def set_exposure_continuous(self):
        self.__capture.f.ExposureAuto.Set(neoapi.ExposureAuto_Continuous)

    def stop_stream(self):
        # Use neoAPI methods to stop streaming
        self.__live_feed_running = False
        self.__thread.join()
        self.__capture.Disconnect()

    def close_camera(self):
        # Use neoAPI methods to stop streaming
        self.__live_feed_running = False
        self.__thread.join()
        self.__capture.Disconnect()


if __name__ == '__main__':
    cam_list = neoapi.CamInfoList_Get()

    # Refresh the camera list to reflect current system status
    cam_list.Refresh()

    # List to hold camera details
    cameras = []

    # Iterate over the camera list and retrieve details
    for idx, cam_info in enumerate(cam_list):
        camera_id = cam_info.GetId()
        camera_name = cam_info.GetModelName()
        conectable = cam_info.IsConnectable()
        ip_adress = cam_info.GetGevIpAddress()
        cameras.append((camera_id, camera_name))

