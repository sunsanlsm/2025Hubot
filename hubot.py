import cv2
# import mouse as me
import selector as sel
import pathfinder as gp
import params as p
import serials as s

class Hubot:
    def __init__(self):
        s.ser_init()
        self.cap = cv2.VideoCapture(0)



    def main(self):
        cam_res, dst = self.cap.read()
        if cam_res == False:
            print("CameraError: Failed to capture camera")
            return False
        
        dst = cv2.GaussianBlur(dst, (0, 0), 2)
        hsv = cv2.cvtColor(dst, cv2.COLOR_BGR2HSV)
        p.cam_h, p.cam_w = dst.shape[:2]

        line_mask = cv2.inRange(hsv, p.min_line_HSV, p.max_line_HSV)
        object_mask = cv2.inRange(hsv, p.min_object_HSV, p.max_object_HSV)
        line_mask[int(p.cam_h*p.LOWER_LINE_MASK_LIMIT):p.cam_h, :] = 0
        line_mask[0:int(p.cam_h*p.UPPER_LINE_MASK_LIMIT), :] = 0
        object_mask[int(p.cam_h*p.LOWER_OBJECT_MASK_LIMIT):p.cam_h, :] = 0
        object_mask[0:int(p.cam_h*p.UPPER_OBJECT_MASK_LIMIT), :] = 0

        line_res = sel.get_center(cv2.findContours(line_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0], dst, p.line_BGR)
        object_res = sel.get_center(cv2.findContours(object_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0], dst, p.object_BGR)

        cv2.rectangle(dst, (0, int(p.cam_h*p.UPPER_LINE_MASK_LIMIT)), (p.cam_w, int(p.cam_h*p.LOWER_LINE_MASK_LIMIT)), p.line_BGR, 1)
        cv2.rectangle(dst, (0, int(p.cam_h*p.UPPER_OBJECT_MASK_LIMIT)), (p.cam_w, int(p.cam_h*p.LOWER_OBJECT_MASK_LIMIT)), p.object_BGR, 1)

        cv2.imshow('dst', dst)
        cv2.imshow('line',line_mask)
        cv2.imshow('object', object_mask)
        key = cv2.waitKey(1)
        if key == ord('q'):
            print("Pressed Q")
            return False

        # cv2.setMouseCallback('dst', me.mouse_event, dst)

        # Object detected
        if object_res == True:
            s.serial_write(200)
            print('Object detected.\tWritten on Serial:', 200)
            return True

        # Line detected
        if line_res == True:
            theta = gp.get_theta((int(p.cam_w/2), int(p.cam_h*p.CURRENT_LINE_POS)), p.ln_stack)
            offset = gp.get_offset(theta)

            try:
                s.serial_write(offset)
                print('Theta: ', theta, '\tWritten on serial:', offset)
                return True
            except Exception as e:
                print('SerialError:', str(e))
                return False

        # Line not detected
        else:
            # print('Line not detected.')
            return True



    def run(self):
        try:
            while True:
                if self.main() == False:
                    break
        except KeyboardInterrupt:
            print('Pressed Ctrl+C')
        except Exception as e:
            print('UnexpectedError:', str(e))
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            if s.ser != None:
                s.ser.close()