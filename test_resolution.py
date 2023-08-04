import cv2
from pygrabber.dshow_graph import FilterGraph

graph = FilterGraph()
print(graph.get_input_devices())
w = 4100
h = 3100
width_old = 4100
hight_old = 3100

while True:

    capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    ret, frame = capture.read()
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if width < width_old:
        print(f'{width}, {height}')
        width_old = width
    w -= 50
    h -= 50

    capture.release()