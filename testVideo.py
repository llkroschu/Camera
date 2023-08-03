import cv2
import os
import v4l2
import fcntl
import logging


def get_available_cameras():
    camera_devices = []
    for device in os.listdir("/dev"):
        if device.startswith("video"):
            path = f'/dev/{device}'
            with open(path, 'r') as vd:
                device_number = path.split('video')
                cp = v4l2.v4l2_capability()
                result = fcntl.ioctl(vd, v4l2.VIDIOC_QUERYCAP, cp)
                try:
                    fmt = v4l2.v4l2_format()
                    fmt.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
                    result = fcntl.ioctl(vd, v4l2.VIDIOC_G_FMT, fmt)
                    if result != 0 or cp.card.decode('utf-8') != "Integrated RGB Camera: Integrat":
                        print(cp.card.decode('utf-8'))
                        camera_devices.append({"device number": device_number[-1],
                                               "camera name ": cp.card.decode('utf-8')})

                except Exception as e:
                    print(e)


class VideoWidget:
    HIGH_VALUE = 10000
    WIDTH = HIGH_VALUE
    HEIGHT = HIGH_VALUE
    def __init__(self, device_number ):
        self.__capture = cv2.VideoCapture(device_number)
        # fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.__capture.set(cv2.CAP_PROP_FRAME_WIDTH, VideoWidget.WIDTH)
        self.__capture.set(cv2.CAP_PROP_FRAME_HEIGHT, VideoWidget.HEIGHT)

        width = int(self.__capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.__capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(width, height)




# Create a VideoCapture object
cap = cv2.VideoCapture(4)

# Check if camera opened successfully
if not cap.isOpened():
    print("Error opening video stream or file")

while cap.isOpened():
    # Capture frame-by-frame
    ret, frame = cap.read()
    if ret:
        # Display the resulting frame
        cv2.imshow('Frame', frame)

        # Press 'c' on the keyboard to capture a picture
        if cv2.waitKey(1) & 0xFF == ord('c'):
            cv2.imwrite('capture.png', frame)
            print("Image captured")

        # Press 'q' on the keyboard to exit the program
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# When everything is done, release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()