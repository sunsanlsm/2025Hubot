import cv2
import numpy as np
import params as p

def get_center(contours, dst, BGR):
    res = False
    cont_pos = []
    cont_x1 = 0
    cont_x2 = 0.
    inverted = False
    for contour in contours:
        rect_x1, rect_y1, rect_w, rect_h = cv2.boundingRect(contour)
        if rect_w > p.MIN_DETECT_WIDTH and rect_h > p.MIN_DETECT_HEIGHT:
            res = True
            center_x = int(rect_x1 + rect_w/2)
            center_y = int(rect_y1 + rect_h/2)
            rect_x2 = int(rect_x1 + rect_w)
            rect_y2 = int(rect_y1 + rect_h)

            if abs(rect_x1 -p.cam_w/2) < abs(rect_x2 -p.cam_w/2):
                cont_x1 = rect_x1
                cont_x2 = rect_x2
            else:
                cont_x1 = rect_x2
                cont_x2 = rect_x1
                inverted = True

            if rect_w > p.MIN_RIGHT_WIDTH and BGR == p.line_BGR:
                cont_pos.append((contour, (cont_x1, rect_y1), (cont_x2, rect_y2), (center_x, center_y), p.right_BGR))
                continue
            cont_pos.append((contour, (cont_x1, rect_y1), (cont_x2, rect_y2), (center_x, center_y), BGR))

    if res == False:
        return res

    cont_pos.sort(key=lambda x:abs(x[1][0] - p.cam_w/2))

    draw(dst, cont_pos, inverted)

    return res



def draw(dst, cont_pos ,inv):
    rect_pos = (0, 0, 0)

    # for conts in range(len(cont_pos)):
    #     if conts == 0:
    #         cv2.rectangle(dst, cont_pos[conts][1], cont_pos[conts][2], cont_pos[conts][4], 2)
    #         cv2.circle(dst, cont_pos[conts][3], 3, cont_pos[conts][4], -1)
    #         continue

    #     cv2.rectangle(dst, cont_pos[conts][1], cont_pos[conts][2], cont_pos[conts][4], 1)
    #     cv2.circle(dst, cont_pos[conts][3], 3, cont_pos[conts][4], 1)

    rect_pos = stacks(cont_pos[0], inv)

    cv2.line(dst, (int(p.cam_w/2), int(p.cam_h*p.CURRENT_LINE_POS)), rect_pos[2], cont_pos[0][4], 1, cv2.LINE_AA)
    cv2.rectangle(dst, rect_pos[0], rect_pos[1], cont_pos[0][4], 2)

    p.ln_stack = rect_pos[2]



def stacks(rect_pos, inv):
    if rect_pos[4] == p.line_BGR or rect_pos[4] == p.right_BGR:
        return ln_stack_av(rect_pos, inv)
    else:
        return obj_stack_av(rect_pos, inv)



def ln_stack_av(rect_pos, inv):
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

    if len(p.ln_stackX1) > p.MAX_LINE_STACK:
        del p.ln_stackX1[:len(p.ln_stackX1)-p.MAX_LINE_STACK]
        del p.ln_stackY1[:len(p.ln_stackY1)-p.MAX_LINE_STACK]
        del p.ln_stackX2[:len(p.ln_stackX2)-p.MAX_LINE_STACK]
        del p.ln_stackY2[:len(p.ln_stackY2)-p.MAX_LINE_STACK]
        del p.ln_lineX[:len(p.ln_lineX)-p.MAX_LINE_STACK]

    if inv == False:
        p.ln_stackX1.append(rect_pos[1][0])
        p.ln_stackX2.append(rect_pos[2][0])
    else:
        p.ln_stackX1.append(rect_pos[2][0])
        p.ln_stackX2.append(rect_pos[1][0])
    p.ln_stackY1.append(rect_pos[1][1])
    p.ln_stackY2.append(rect_pos[2][1])

    if rect_pos[4] == p.right_BGR:
        p.ln_lineX.append(rect_pos[2][0])
    elif abs(rect_pos[1][0] -p.cam_w/2) < abs(rect_pos[3][0] -p.cam_w/2):
        p.ln_lineX.append(rect_pos[1][0])
    else:
        p.ln_lineX.append(rect_pos[3][0])

    ln_X1 = np.array(p.ln_stackX1)
    ln_Y1 = np.array(p.ln_stackY1)
    ln_X2 = np.array(p.ln_stackX2)
    ln_Y2 = np.array(p.ln_stackY2)
    ln_line = np.array(p.ln_lineX)

    for i in range(0, len(p.ln_stackX1)*5, 5):
        weight = np.append(weight, i+1)

    avgX1 = int(np.average(ln_X1, weights=weight))
    avgY1 = int(np.average(ln_Y1, weights=weight))
    avgX2 = int(np.average(ln_X2, weights=weight))
    avgY2 = int(np.average(ln_Y2, weights=weight))
    avgLine = int(np.average(ln_line, weights=weight))

    rect_pos1 = (avgX1, avgY1)
    rect_pos2 = (avgX2, avgY2)
    line_pos = (avgLine, avgY1)

    return rect_pos1, rect_pos2, line_pos



def obj_stack_av(rect_pos, inv):
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

    if len(p.obj_stackX1) > p.MAX_LINE_STACK:
        del p.obj_stackX1[:len(p.obj_stackX1)-p.MAX_LINE_STACK]
        del p.obj_stackY1[:len(p.obj_stackY1)-p.MAX_LINE_STACK]
        del p.obj_stackX2[:len(p.obj_stackX2)-p.MAX_LINE_STACK]
        del p.obj_stackY2[:len(p.obj_stackY2)-p.MAX_LINE_STACK]
        del p.obj_lineX[:len(p.obj_lineX)-p.MAX_LINE_STACK]

    if inv == False:
        p.obj_stackX1.append(rect_pos[1][0])
        p.obj_stackX2.append(rect_pos[2][0])
    else:
        p.obj_stackX1.append(rect_pos[2][0])
        p.obj_stackX2.append(rect_pos[1][0])
    p.obj_stackY1.append(rect_pos[1][1])
    p.obj_stackY2.append(rect_pos[2][1])

    if abs(rect_pos[1][0] -p.cam_w/2) < abs(rect_pos[2][0] -p.cam_w/2):
        if abs(rect_pos[1][0] -p.cam_w/2) < abs(rect_pos[3][0] -p.cam_w/2):
            p.obj_lineX.append(rect_pos[1][0])
        else:
            p.obj_lineX.append(rect_pos[3][0])
    else:
        if abs(rect_pos[2][0] -p.cam_w/2) < abs(rect_pos[3][0] -p.cam_w/2):
            p.obj_lineX.append(rect_pos[2][0])
        else:
            p.obj_lineX.append(rect_pos[3][0])

    obj_X1 = np.array(p.obj_stackX1)
    obj_Y1 = np.array(p.obj_stackY1)
    obj_X2 = np.array(p.obj_stackX2)
    obj_Y2 = np.array(p.obj_stackY2)
    obj_line = np.array(p.obj_lineX)

    for i in range(0, len(p.obj_stackX1)*5, 5):
        weight = np.append(weight, i+1)

    avgX1 = int(np.average(obj_X1, weights=weight))
    avgY1 = int(np.average(obj_Y1, weights=weight))
    avgX2 = int(np.average(obj_X2, weights=weight))
    avgY2 = int(np.average(obj_Y2, weights=weight))
    avgLine = int(np.average(obj_line, weights=weight))

    rect_pos1 = (avgX1, avgY1)
    rect_pos2 = (avgX2, avgY2)
    obj_pos = (avgLine, avgY1)

    return rect_pos1, rect_pos2, obj_pos