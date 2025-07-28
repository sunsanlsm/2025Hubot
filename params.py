import numpy as np

cam_w = 0
cam_h = 0

MIN_DETECT_WIDTH = 30
MIN_DETECT_HEIGHT = 10
MIN_RIGHT_WIDTH = 300
MAX_VERSTAPPEN_HEIGHT = 181

min_line_HSV = np.array([20, 125, 50])
max_line_HSV = np.array([100, 255, 220])
min_object_HSV = np.array([120, 125, 50])
max_object_HSV = np.array([160, 255, 150])

LOWER_LINE_MASK_LIMIT = 0.6
UPPER_LINE_MASK_LIMIT = 0.25
CURRENT_LINE_POS = 0.75
LOWER_OBJECT_MASK_LIMIT = 0.5
UPPER_OBJECT_MASK_LIMIT = 0.125

MAX_LINE_STACK = 10
TURNING_POWER = 3

line_BGR = (0, 255, 255)
object_BGR = (255, 255, 0)
right_BGR = (191,84,45)

ln_stack = ()
ln_stackX1 = []
ln_stackY1 = []
ln_stackX2 = []
ln_stackY2 = []
ln_lineX = []

obj_stackX1 = []
obj_stackY1 = []
obj_stackX2 = []
obj_stackY2 = []
obj_lineX = []

mouse_press = False