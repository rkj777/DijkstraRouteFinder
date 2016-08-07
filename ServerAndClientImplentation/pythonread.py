import serial
ser = serial.Serial('/dev/ttyACM0', 9600)
counter = 0

def read_points():
    while 1:
        line1 = ser.readline().decode('ASCII')
        line2 = ser.readline().decode('ASCII')
        elements1 = line1.split(", ")
        elements2 = line2.split(", ")
        lat1 = elements1[-1].rstrip()
        lat2 = elements2[-1].rstrip()
        lon1 = elements1[0]
        lon2 = elements2[0]
        ard_vert = lat1 +", "+ lon1 +", "+ lat2 +", "+ lon2
        """ print(ard_vert)
        print(lat1)"""
        return ard_vert
        break

