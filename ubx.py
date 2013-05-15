#uBlox flight mode code

import serial
import time
import sys
import time as time_
gps_set_sucess = False
ser = serial.Serial("/dev/ttyACM0", 9600) #ACM gps AMA gpio
setNav = bytearray.fromhex("B5 62 06 24 24 00 FF FF 06 03 00 00 00 00 10 27 00 00 05 00 FA 00 FA 00 64 00 2C 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 16 DC")

#create function equivalent to arduino millis();
def millis():
        return int(round(time_.time() * 1000))

#calcuate expected UBX ACK packet and parse UBX response from GPS
def getUBX_ACK(MSG):
        b = 0
        ackByteID = 0
        ackPacket = [0 for x in range(10)]
        startTime = millis()

        print "Reading ACK response: "
        
        #construct the expected ACK packet
        ackPacket[0] = int('0xB5', 16) #header
        ackPacket[1] = int('0x62', 16) #header
        ackPacket[2] = int('0x05', 16) #class
        ackPacket[3] = int('0x01', 16) #id
        ackPacket[4] = int('0x02', 16) #length
        ackPacket[5] = int('0x00', 16)
        ackPacket[6] = MSG[2] #ACK class
        ackPacket[7] = MSG[3] #ACK id
        ackPacket[8] = 0 #CK_A
        ackPacket[9] = 0 #CK_B

        #calculate the checksums
        for i in range(2,8):
                ackPacket[8] = ackPacket[8] + ackPacket[i]
                ackPacket[9] = ackPacket[9] + ackPacket[8]

        #print expected packet
        print "Expected ACK Response: "
        for byt in ackPacket:
                print byt
                
        print "Waiting for UBX ACK reply:"
        while 1:
                #test for success
                if ackByteID > 9 :
                        #all packets are in order
                        print "(SUCCESS!)"
                        return True

                #timeout if no valid response in 3 secs
                if millis() - startTime > 3000:
                        print "(FAILED!)"
                        return False
                #make sure data is availible to read
                if ser.inWaiting() > 0:
                        b = ser.read(1)
                        #check that bytes arrive in the sequence as per expected ACK packet
                        if ord(b) == ackPacket[ackByteID]:
                                ackByteID += 1
                                print ord(b)
                        else:
                                ackByteID = 0 #reset and look again, invalid order

def sendUBX(MSG, length):
        print "Sending UBX Command: "
        ubxcmds = ""
        for i in range(0, length):
                ser.write(chr(MSG[i])) #write each byte of ubx cmd to serial port
                ubxcmds = ubxcmds + str(MSG[i]) + " " # build up sent message debug output string
        ser.write("\r\n") #send newline to ublox
        print ubxcmds #print debug message
        print "UBX Command Sent..."




#actual program code below:
print "Setting uBlox nav mode: "

while not gps_set_sucess:
        sendUBX(setNav, len(setNav))
        gps_set_sucess = getUBX_ACK(setNav);

while 1:
        break
