import cv2
from pygrabber.dshow_graph import FilterGraph
import time
import os
import threading
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from vimba import Vimba, VimbaCameraError, VimbaFeatureError, Camera, Frame
from datetime import datetime
from PIL import Image
import numpy as np

from VimbaPython.vimba import intersect_pixel_formats, OPENCV_PIXEL_FORMATS, PixelFormat
from logWidget import LogWidget


class AlliedVisionCamera(QObject):
    frame_signal = pyqtSignal(QPixmap)

    def __init__(self, device_number, resolution):
        super().__init__()
        self.vimba = Vimba.get_instance()
        self.vimba._startup()
        self.__live_feed_running = False
        self.latest_frame_data = []
        with self.vimba:
            if device_number:
                self.cam = self.vimba.get_camera_by_id(device_number)
            else:
                self.cam = self.vimba.get_all_cameras()[0]  # Default to the first camera
            self.resolution = resolution
            self.stream_thread = None
            self.shutdown_event = threading.Event()
            self.setup_camera()

    def setup_camera(self):
        with self.cam:
            # Placeholder for any initial setup or settings
            self.set_resolution(self.resolution[0], self.resolution[1])
            # opencv_formats = self.show_formats()
            # self.cam.set_pixel_format(opencv_formats[1])

    def show_features(self):
        features = []
        for feature in self.cam.get_all_features():
            try:
                value = feature.get()
            except (AttributeError, VimbaFeatureError):
                value = None
            feature_info = {
                'feature_name': feature.get_name(),
                'display_name': feature.get_display_name(),
                'value': value
            }
            features.append(feature_info)
        return features

    def show_formats(self):
        with self.cam:
            formats = self.cam.get_pixel_formats()
            opencv_formats = intersect_pixel_formats(formats, OPENCV_PIXEL_FORMATS)
        return opencv_formats

    def frame_handler(self, cam: Camera, frame: Frame):
        try:
            # Check if the frame's pixel format is 'Rgb8'
            if frame.get_pixel_format() == PixelFormat.Rgb8:
                img_data = frame.as_numpy_ndarray()
                q_img = QImage(img_data, frame.get_width(), frame.get_height(), QImage.Format.Format_RGB888)
                # Store the latest frame data as a numpy ndarray
                self.latest_frame_data = frame.as_numpy_ndarray()
            else:
                # If not 'Rgb8', try to use the built-in conversion method
                q_img = QImage(frame.as_opencv_image().data, frame.get_width(), frame.get_height(),
                               QImage.Format.Format_RGB888)
                # Store the latest frame data as a numpy ndarray
                self.latest_frame_data = frame.as_numpy_ndarray()

            self.frame_signal.emit(QPixmap.fromImage(q_img))
            cam.queue_frame(frame)
        except Exception as e:
            print(f"Error in frame_handler: {e}")

        # q_img = QImage(frame.as_opencv_image().data, frame.get_width(), frame.get_height(),
        #                QImage.Format.Format_BGR888)
        # self.frame_signal.emit(QPixmap.fromImage(q_img))
        # cam.queue_frame(frame)

    def ensure_camera_closed(self):
        """Close the camera if it's opened to ensure a clean startup."""
        with self.vimba:
            with self.cam:
                if self.cam.is_streaming():
                    self.cam.stop_streaming()
                    self.cam._close()
                    self.__live_feed_running = False

    def start_stream(self):
        self.ensure_camera_closed()
        self.shutdown_event.clear()
        self.stream_thread = threading.Thread(target=self._stream)
        self.stream_thread.start()
        self.__live_feed_running = True

    def _stream(self):
        NUM_FRAMES_TO_QUEUE = 5  # This number can be adjusted based on performance and requirements

        with self.vimba:
            with self.cam:
                # Allocate and queue frames
                frames = [self.cam.get_frame() for _ in range(NUM_FRAMES_TO_QUEUE)]
                for frame in frames:
                    self.cam.queue_frame(frame)  # Queue the frame without callback

                # Start asynchronous image acquisition with frame_handler as the callback
                self.cam.start_streaming(self.frame_handler)

                # Wait until the shutdown event is set
                self.shutdown_event.wait()

    def stop_stream(self):
        if self.stream_thread:
            with self.vimba:
                with self.cam:
                    self.shutdown_event.set()  # Signal the stream thread to stop
                    self.stream_thread.join()  # Wait for the stream thread to finish
                    self.cam.stop_streaming()
                    self.stream_thread = None
                    self.shutdown()
                    self.__live_feed_running = False

    def close_camera(self):
        if self.cam:
            self.cam.stop_streaming()
            self.cam._close()

    def set_resolution(self, width: int, height: int):
        self.cam.Width.set(width)
        self.cam.Height.set(height)

    def set_exposure(self, value: float):
        exposure_time = self.cam.ExposureTime
        exposure_time.set(value)

    def shutdown(self):
        self.vimba._shutdown()  # Shutdown the Vimba system

    def capture_image(self, camera_name: str):
        """
        Captures the current frame and saves it as an image.

        Parameters:
            - camera_name: Name of the camera (to be used in the saved filename).
        """
        # Path to save the images
        image_path = 'pictures'

        # Create the directory if it doesn't exist
        if not os.path.exists(image_path):
            os.makedirs(image_path)

        # Check if the live feed is running
        if self.__live_feed_running:
            # Check if we have frame data
            if self.latest_frame_data is not None:
                # Construct the image filename
                now = datetime.now()
                image_name = f'{now.strftime("%Y%m%d_%H%M%S")}_{camera_name}_{self.resolution[0]}x{self.resolution[1]}.png'

                # Convert the numpy array frame data to an image and save
                Image.fromarray(self.latest_frame_data).save(f'{image_path}/{image_name}')

                print(f'{image_name}    --> saved successfully!')

            else:
                raise ValueError('Unable to capture Image: No frame data available.')

        else:
            raise ValueError('Unable to capture Image: Live feed is not running.')
