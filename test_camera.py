from vimba import *
import cv2
import numpy as np


def show_features(cam):
    for feature in cam.get_all_features():
        try:
            value = feature.get()
        except (AttributeError, VimbaFeatureError):
            value = None
        print(f"Feature name: {feature.get_name()}")
        print(f"Display name: {feature.get_display_name()}")
        if not value == None:
            if not feature.get_unit() == '':
                print(f"Unit: {feature.get_unit()}", end=' ')
                print(f"value={value}")
            else:
                print(f"Not set")
                print("--------------------------------------------")


def show_formats(cam):
    with cams[0] as cam:
        formats = cam.get_pixel_formats()
        opencv_formats = intersect_pixel_formats(formats, OPENCV_PIXEL_FORMATS)
        print(f"Available formats:")
        for i, format in enumerate(formats):
            print(i, format)
        print(f"\nOpencv compatible formats:")
        for i, format in enumerate(opencv_formats):
            print(i, format)

    return opencv_formats


with Vimba.get_instance() as vimba:
    cams = vimba.get_all_cameras()
    cam = cams[0]
    print(cam._Camera__info.cameraName)
    with cam:
        show_features(cam)
        opencv_formats = show_formats(cam)
        cam.set_pixel_format(opencv_formats[1])

        # change exposure
        exposure_time = cam.ExposureTime
        exposure_time.set(7000)
        print(f"Exposure changed to: {(exposure_time.get() / 1000):.0f} ms")

        width = cam.Width.get()
        height = cam.Height.get()

        width_values = range(8, 2592, 8)
        height_values = range(8, 1944, 8)
        cam.Width.set(width_values[150])
        cam.Height.set(height_values[140])

        print(f'Resolution: {cam.Width.get()}x{cam.Height.get()}')

        print(f'Name = {cam.DeviceModelName.get()}')
        print(f'exposureAutoMode {cam.ExposureAuto.get()}')
        cam.ExposureAuto.set('Once')

        # Optionally set the camera to FreeRun mode (if supported)
        # cam.AcquisitionMode.set('FreeRun')

        # Start the acquisition
        # cam.start_continuous_image_acquisition()

        try:
            while True:
                # Get the frame
                frame = cam.get_frame().as_opencv_image()

                # Display the frame
                cv2.imshow('Camera Feed', frame)

                # Break the loop if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            # Stop the acquisition and close the window
            cv2.destroyAllWindows()


