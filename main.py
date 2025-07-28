#!/usr/bin/python3

### Patch note 
#     Mk1   Smooth contour detecting    IMPROVED
#           Smooth line moving          IMPROVED
#           Smooth rectangle drawing    ADDED
#           Right angle detecting       ADDED
#           Gaussianblur                ADDED
#           Offset calculating method   IMPROVED
#           Max Verstappen height       ADDED
#           Serial Open to Close        REMOVED
#           Line detecting method       IMPROVED



import numpy as np
import cv2
import serial



class Hubot:
    def __init__(self):
        # self.ser = serial.Serial(port="/dev/ttyUSB0",
        #                          baudrate=57600,
        #                          parity=serial.PARITY_NONE,
        #                          stopbits=serial.STOPBITS_ONE,
        #                          bytesize=serial.EIGHTBITS,
        #                          timeout=0)
        
        self.cap = cv2.VideoCapture(0)
        self.cam_w = 0
        self.cam_h = 0

        self.MIN_DETECT_WIDTH = 30
        self.MIN_DETECT_HEIGHT = 10
        self.MIN_RIGHT_WIDTH = 300
#       self.MAX_VERSTAPPEN_HEIGHT = 181

        # self.MIN_LINE_HSV = np.array([20, 35, 10])
        # self.MAX_LINE_HSV = np.array([75, 255, 220])

        self.MIN_LINE_HSV = np.array([20, 125, 50])
        self.MAX_LINE_HSV = np.array([75, 255, 220])
        self.MIN_OBJECT_HSV = np.array([100, 125, 50])
        self.MAX_OBJECT_HSV = np.array([160, 255, 150])

        self.LOWER_LINE_MASK_LIMIT = 1/2
        self.UPPER_LINE_MASK_LIMIT = 0
        self.CURRENT_LINE_POS = 3/4
        self.LOWER_OBJECT_MASK_LIMIT = 2/4
        self.UPPER_OBJECT_MASK_LIMIT = 1/8
    
        self.MAX_LINE_STACK = 10
        self.object_stack = []

        self.line_BGR = (0, 255, 255)
        self.object_BGR = (255, 255, 0)
        self.right_BGR = (191,84,45)

        self.ln_stack = ()
        self.ln_stackX1 = []
        self.ln_stackY1 = []
        self.ln_stackX2 = []
        self.ln_stackY2 = []
        self.ln_lineX = []

        self.obj_stackX1 = []
        self.obj_stackY1 = []
        self.obj_stackX2 = []
        self.obj_stackY2 = []
        self.obj_lineX = []



    # def serial_write(self, num):
    #     self.ser.write(bytearray([255, 85, num, 255-num, 0, 255]))



    def get_center(self, contours, dst, BGR):
        res = False
        cont_pos = []
        cont_x1 = 0
        cont_x2 = 0.
        inverted = False
        for contour in contours:
            rect_x1, rect_y1, rect_w, rect_h = cv2.boundingRect(contour)
            if rect_w > self.MIN_DETECT_WIDTH and rect_h > self.MIN_DETECT_HEIGHT:
                res = True
                center_x = int(rect_x1 + rect_w/2)
                center_y = int(rect_y1 + rect_h/2)
                rect_x2 = int(rect_x1 + rect_w)
                rect_y2 = int(rect_y1 + rect_h)

                if abs(rect_x1 -self.cam_w/2) < abs(rect_x2 -self.cam_w/2):
                    cont_x1 = rect_x1
                    cont_x2 = rect_x2
                else:
                    cont_x1 = rect_x2
                    cont_x2 = rect_x1
                    inverted = True

                if rect_w > self.MIN_RIGHT_WIDTH and BGR == self.line_BGR:
                    cont_pos.append((contour, (cont_x1, rect_y1), (cont_x2, rect_y2), (center_x, center_y), self.right_BGR))
                    continue
                cont_pos.append((contour, (cont_x1, rect_y1), (cont_x2, rect_y2), (center_x, center_y), BGR))

        if res == False:
            return res

        cont_pos.sort(key=lambda x:abs(x[1][0] - self.cam_w/2))

        self.draw(dst, cont_pos, inverted)

        return res



    def draw(self, dst, cont_pos ,inv):
        rect_pos = (0, 0, 0)

        # for conts in range(len(cont_pos)):
        #     if conts == 0:
        #         cv2.rectangle(dst, cont_pos[conts][1], cont_pos[conts][2], cont_pos[conts][4], 2)
        #         cv2.circle(dst, cont_pos[conts][3], 3, cont_pos[conts][4], -1)
        #         continue

        #     cv2.rectangle(dst, cont_pos[conts][1], cont_pos[conts][2], cont_pos[conts][4], 1)
        #     cv2.circle(dst, cont_pos[conts][3], 3, cont_pos[conts][4], 1)

        rect_pos = self.stacks(cont_pos[0], inv)

        cv2.line(dst, (int(self.cam_w/2), int(self.cam_h*self.CURRENT_LINE_POS)), rect_pos[2], cont_pos[0][4], 1, cv2.LINE_AA)

        cv2.rectangle(dst, rect_pos[0], rect_pos[1], cont_pos[0][4], 2)

        self.ln_stack = rect_pos[2]



    def stacks(self, rect_pos, inv):
        if rect_pos[4] == self.line_BGR or rect_pos[4] == self.right_BGR:
            return self.ln_stack_av(rect_pos, inv)
        else:
            return self.obj_stack_av(rect_pos, inv)



    def ln_stack_av(self, rect_pos, inv):
        ln_X1 = np.array([])
        ln_Y1 = np.array([])
        ln_X2 = np.array([])
        ln_Y2 = np.array([])
        ln_line = np.array([])
        weight = np.array([])

        avgX1 = 0
        avgY1 = 0
        avgX2 = 0
        avgY2 = 0
        avgLine = 0

        if len(self.ln_stackX1) > self.MAX_LINE_STACK:
            del self.ln_stackX1[:len(self.ln_stackX1)-self.MAX_LINE_STACK]
            del self.ln_stackY1[:len(self.ln_stackY1)-self.MAX_LINE_STACK]
            del self.ln_stackX2[:len(self.ln_stackX2)-self.MAX_LINE_STACK]
            del self.ln_stackY2[:len(self.ln_stackY2)-self.MAX_LINE_STACK]
            del self.ln_lineX[:len(self.ln_lineX)-self.MAX_LINE_STACK]

        if inv == False:
            self.ln_stackX1.append(rect_pos[1][0])
            self.ln_stackX2.append(rect_pos[2][0])
        else:
            self.ln_stackX1.append(rect_pos[2][0])
            self.ln_stackX2.append(rect_pos[1][0])
        self.ln_stackY1.append(rect_pos[1][1])
        self.ln_stackY2.append(rect_pos[2][1])

        if rect_pos[4] == self.right_BGR:
            self.ln_lineX.append(rect_pos[2][0])
        elif abs(rect_pos[1][0] -self.cam_w/2) < abs(rect_pos[3][0] -self.cam_w/2):
            self.ln_lineX.append(rect_pos[1][0])
        else:
            self.ln_lineX.append(rect_pos[3][0])

        ln_X1 = np.array(self.ln_stackX1)
        ln_Y1 = np.array(self.ln_stackY1)
        ln_X2 = np.array(self.ln_stackX2)
        ln_Y2 = np.array(self.ln_stackY2)
        ln_line = np.array(self.ln_lineX)

        for i in range(0, len(self.ln_stackX1)*5, 5):
            weight = np.append(weight, i+1)

        # print(ln_line)
        # print(weight)

        avgX1 = int(np.average(ln_X1, weights=weight))
        avgY1 = int(np.average(ln_Y1, weights=weight))
        avgX2 = int(np.average(ln_X2, weights=weight))
        avgY2 = int(np.average(ln_Y2, weights=weight))
        avgLine = int(np.average(ln_line, weights=weight))

        rect_pos1 = (avgX1, avgY1)
        rect_pos2 = (avgX2, avgY2)
        line_pos = (avgLine, avgY1)

        return rect_pos1, rect_pos2, line_pos



    def obj_stack_av(self, rect_pos, inv):
        obj_X1 = np.array([])
        obj_Y1 = np.array([])
        obj_X2 = np.array([])
        obj_Y2 = np.array([])
        obj_line = np.array([])
        weight = np.array([])

        avgX1 = 0
        avgY1 = 0
        avgX2 = 0
        avgY2 = 0
        avgLine = 0

        if len(self.obj_stackX1) > self.MAX_LINE_STACK:
            del self.obj_stackX1[:len(self.obj_stackX1)-self.MAX_LINE_STACK]
            del self.obj_stackY1[:len(self.obj_stackY1)-self.MAX_LINE_STACK]
            del self.obj_stackX2[:len(self.obj_stackX2)-self.MAX_LINE_STACK]
            del self.obj_stackY2[:len(self.obj_stackY2)-self.MAX_LINE_STACK]
            del self.obj_lineX[:len(self.obj_lineX)-self.MAX_LINE_STACK]

        if inv == False:
            self.obj_stackX1.append(rect_pos[1][0])
            self.obj_stackX2.append(rect_pos[2][0])
        else:
            self.obj_stackX1.append(rect_pos[2][0])
            self.obj_stackX2.append(rect_pos[1][0])
        self.obj_stackY1.append(rect_pos[1][1])
        self.obj_stackY2.append(rect_pos[2][1])

        if abs(rect_pos[1][0] -self.cam_w/2) < abs(rect_pos[2][0] -self.cam_w/2):
            if abs(rect_pos[1][0] -self.cam_w/2) < abs(rect_pos[3][0] -self.cam_w/2):
                self.obj_lineX.append(rect_pos[1][0])
            else:
                self.obj_lineX.append(rect_pos[3][0])
        else:
            if abs(rect_pos[2][0] -self.cam_w/2) < abs(rect_pos[3][0] -self.cam_w/2):
                self.obj_lineX.append(rect_pos[2][0])
            else:
                self.obj_lineX.append(rect_pos[3][0])

        obj_X1 = np.array(self.obj_stackX1)
        obj_Y1 = np.array(self.obj_stackY1)
        obj_X2 = np.array(self.obj_stackX2)
        obj_Y2 = np.array(self.obj_stackY2)
        obj_line = np.array(self.obj_lineX)

        for i in range(0, len(self.obj_stackX1)*5, 5):
            weight = np.append(weight, i+1)

        # print(obj_line)
        # print(weight)

        avgX1 = int(np.average(obj_X1, weights=weight))
        avgY1 = int(np.average(obj_Y1, weights=weight))
        avgX2 = int(np.average(obj_X2, weights=weight))
        avgY2 = int(np.average(obj_Y2, weights=weight))
        avgLine = int(np.average(obj_line, weights=weight))

        rect_pos1 = (avgX1, avgY1)
        rect_pos2 = (avgX2, avgY2)
        obj_pos = (avgLine, avgY1)

        return rect_pos1, rect_pos2, obj_pos



    def get_theta(self, pos1, pos2):
        return -np.degrees(np.arctan((pos1[0]-pos2[0]) / (pos1[1]-pos2[1])))



    def get_offset(self, theta, offset_limit =75):
        offset = int((theta ** 3) / (1024 * 2))
        if offset <= -offset_limit:
            return 0
        if offset >= offset_limit:
            return offset_limit * 2
        return offset +offset_limit



    def main(self):
        cam_res, dst = self.cap.read()
        if cam_res == False:
            print("CameraError: Cannot capture camera")
            return False
        
        dst = cv2.GaussianBlur(dst, (0, 0), 5)
        hsv = cv2.cvtColor(dst, cv2.COLOR_BGR2HSV)
        self.cam_h, self.cam_w = dst.shape[:2]

        line_mask = cv2.inRange(hsv, self.MIN_LINE_HSV, self.MAX_LINE_HSV)
        object_mask = cv2.inRange(hsv, self.MIN_OBJECT_HSV, self.MAX_OBJECT_HSV)

        line_mask[int(self.cam_h*self.LOWER_LINE_MASK_LIMIT):self.cam_h, :] = 0
        line_mask[0:int(self.cam_h*self.UPPER_LINE_MASK_LIMIT), :] = 0
        object_mask[int(self.cam_h*self.LOWER_OBJECT_MASK_LIMIT):self.cam_h, :] = 0
        object_mask[0:int(self.cam_h*self.UPPER_OBJECT_MASK_LIMIT), :] = 0

        line_res = self.get_center(cv2.findContours(line_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0], dst, self.line_BGR)
        object_res = self.get_center(cv2.findContours(object_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0], dst, self.object_BGR)

        cv2.rectangle(dst, (0, int(self.cam_h*self.UPPER_LINE_MASK_LIMIT)), (self.cam_w, int(self.cam_h*self.LOWER_LINE_MASK_LIMIT)), self.line_BGR, 1)
        cv2.rectangle(dst, (0, int(self.cam_h*self.UPPER_OBJECT_MASK_LIMIT)), (self.cam_w, int(self.cam_h*self.LOWER_OBJECT_MASK_LIMIT)), self.object_BGR, 1)

        cv2.imshow("dst", dst)
        cv2.waitKey(1)

        # Object detected
        if object_res == True:
            # self.serial_write(200)
            print("Object detected.\tWritten on Serial:", 200)
            return True

        # Line detected
        if line_res == True:
            theta = self.get_theta((int(self.cam_w/2), int(self.cam_h*self.CURRENT_LINE_POS)), self.ln_stack)
            offset = self.get_offset(theta)

            try:
                # self.serial_write(offset)
                print("Theta: ", theta, "\tWritten on serial:", offset)
                return True
            except Exception as e:
                print("SerialError:", str(e))
                return False

        # Line not detected
        else:
            print("Line not detected.")
            return True



    def run(self):
        try:
            while True:
                if self.main() == False:
                    break
        except KeyboardInterrupt:
            print("Pressed Ctrl+C")
        # except Exception as e:
        #     print("UnexpectedError:", str(e))
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            # self.ser.close()



if __name__ == "__main__":
    hubot = Hubot()
    hubot.run()