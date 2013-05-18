#img timestamp should include data
#flightmode
#checksum needs to be added
import serial
import os
import time
import shutil
import crcmod
ser = serial.Serial("/dev/ttyACM0", 9600)
rtty = serial.Serial("/dev/ttyAMA0", 600 , serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_TWO)

#define variables
ssdvi = 1
ssdv_enable = True
msgi = 1
gpstxs = 3
txdelay = 5
crc16f = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0xFFFF, xorOut=0x0000) # function for crc16CCITT0xFFFF

while 1:
	linein = ser.readline()
	print linein
	if linein.startswith('$GPGGA'):
		gpsdata = linein.split(",")
		tim = gpsdata[1][:6]
		lats = gpsdata[2]
		lngs = gpsdata[4]
		print "time:" + tim
		#print "lats:" + lats
		#print "lngs:" + lngs
		
		#process the NMEA coords to decimal
                latdecs = ""
                latdecs2 = ""
		for i in range(0, lats.index('.') - 2):
                        latdecs = latdecs + lats[i]
                for i in range(lats.index('.') - 2, len(lats) - 1):
                        latdecs2 = latdecs2 + lats[i]
                lat = float(latdecs) + float(str((float(latdecs2)/60))[:8])
                lngdecs = ""
                lngdecs2 = ""
		for i in range(0, lngs.index('.') - 2):
                        lngdecs = lngdecs + lngs[i]
                for i in range(lngs.index('.') - 2, len(lngs) - 1):
                        lngdecs2 = lngdecs2 + lngs[i]
                lng = float(lngdecs) + float(str((float(lngdecs2)/60))[:8])
                if gpsdata[3] == "W":
                        lat = 0 - lat
                if gpsdata[5] == "S":
                        lng = 0 - lng                                
                #NMEA coords have been converted to dec coords lat/lng

                for x in range(0, gpstxs):
                        datastring = "NSEPI," + str(msgi) + "," + str(tim) + "," + str(lat) + "," + str(lng)
                        datastring = datastring + "*" + str(hex(crc16f(datastring))).upper()[2:]
                        datastring = datastring + "\n"
                        datastring = "$$$$" + datastring
                        rtty.write(datastring)
                        rtty.flush()
                        msgi += 1


                print "lat:" + str(lat)
                print "lng:" + str(lng)

                ser.close()


                if ssdv_enable:
                        #take photo img.jpg after dumping 9 frames
                        os.system("sudo fswebcam --no-banner -S 9 -R img.jpg")

                        #copy photo to img/time.jpg
                        shutil.copyfile("img.jpg","img/" + tim + ".jpg")

                        #encode jpeg to SSDV.txt
                        os.system("ssdv/ssdv -e -c NSEPI -i " + str(ssdvi) + " img.jpg ssdv.txt")

                        ssdvi += 1

                        #read in encoded data
                        c = ""
                        with open("ssdv.txt") as f:
                                c = f.read()

                        rtty.write(c)  #send SSDV image
                        rtty.flush()   #wait for image to send
                        
                        print("all packets sent")
                #endif
                ser = serial.Serial("/dev/ttyACM0", 9600)
