import serial

ser = None

def ser_init():
    try:
        ser = serial.Serial(port="/dev/ttyUSB0",
                                baudrate=57600,
                                parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_ONE,
                                bytesize=serial.EIGHTBITS,
                                timeout=0)
    except serial.SerialException as e:
        print("Failed to open serial port: ", str(e))



def serial_write(num):
    if ser == None:
        # print("Failed to serial write:", "Serial port is disabled")
        return
    if num < 0 or num > 255:
        print("Failed to serial write:", "number to write is out of range(0-255)")
        return
    
    try:
        ser.write(bytearray([255, 85, num, 255-num, 0, 255]))
    except serial.SerialException as e:
        print("SerialException:", str(e))
    except Exception as e:
        print("Unexpected Error:", str(e))