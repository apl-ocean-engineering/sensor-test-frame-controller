import serial


i = 0

with serial.Serial("/dev/ttyO1", 115200, timeout = 1) as ser:
    while True:
        x = ser.write(b':0\n')
        s = ser.readline()
        print(s)

        i = i+1
