import cv2
import params as p

def mouse_event(p, event, x, y, _, dst):
    if event == cv2.EVENT_LBUTTONDOWN:
        if p.mouse_press == False:
            p.mouse_press = True
            print('LB pressed!')
            picked = dst[y, x]
            print('\n', picked)
            p.leftB(picked)
        else:
            print('Other eventis continuing yet!')
            return
        
    elif event == cv2.EVENT_LBUTTONDOWN:
        if p.mouse_press == False:
            p.mouse_press = True
            print('RB pressed!')
            picked = dst[y, x]
            print('\n', picked)
            p.rightB(picked)
        else:
            print('Other event is continuing yet!')
            return

    else:
        p.mouse_press = False
        pass


def leftB(p, picked):
    keybound = cv2.waitKey(0)

    if keybound == ord('l'):
        # latest = c.copy(p.min_line_HSV)
        print(p.min_line_HSV)

        for i in range(3):
            if picked[i] < p.min_line_HSV[i]:
                p.min_line_HSV[i] = picked[i]

        # msg = 'min_ln_HSV was Changed from', latest, 'to', p.min_line_HSV, '!'
        msg = 'min_ln_HSV was Changed to', p.min_line_HSV,'!'
        print(msg)

    elif keybound == ord('o'):
        # latest = c.copy(p.min_object_HSV)
        print(p.min_object_HSV)

        for i in range(3):
            if picked[i] < p.min_object_HSV[i]:
                p.min_object_HSV[i] = picked[i]

        # msg = 'min_obj_HSV was Changed from', latest, 'to', p.min_object_HSV, '!'
        msg = 'min_obj_HSV was Changed to', p.min_object_HSV,'!'

        print(msg)

    else:
        print('Press "L" for line or "O" for object!')
        p.mouse_press = False


def rightB(p, picked):
    keybound = cv2.waitKey(0)

    if keybound == ord('l'):
        # latest = c.copy(p.max_line_HSV)
        print(p.max_line_HSV)

        for i in range(3):
            if picked[i] > p.max_line_HSV[i]:
                p.max_line_HSV[i] = picked[i]

        # msg = 'max_ln_HSV was Changed from', latest, 'to', p.max_line_HSV,'!'
        msg = 'max_ln_HSV was Changed to', p.max_line_HSV,'!'
        print(msg)

    elif keybound == ord('o'):
        # latest = c.copy(p.max_object_HSV)
        print(p.max_object_HSV)

        for i in range(3):
            if picked[i] > p.max_object_HSV[i]:
                p.max_object_HSV[i] = picked[i]

        # msg = 'max_obj_HSV was Changed from', latest, 'to', p.max_object_HSV, '!'
        msg = 'max_obj_HSV was Changed to', p.max_line_HSV,'!'
        print(msg)

    else:
        print('Press "L" for line or "O" for object!')

    p.mouse_press = False