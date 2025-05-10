import os
import bluetooth
from enum import Enum

class devType(Enum):
    UNKNOWN = 0
    iOS = 1
    ANDROID = 2

class obexDevice:
    def __init__(self, bt_addr):
        print("Device:", bt_addr)
        self.dev_type = devType.UNKNOWN
        self.bt_addr = bt_addr
        self.sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)

    def connect(self):
        try:
            try:
                print("Trying Android connection")
                psm = 0x1001  # Typical Android PSM - You should get this from the AVRCP metadata
                self.obex_conn_id, self.dev_type = connectObex(self, psm)

            except: # If connection fails on 0x1001, device is probably an iPhone
                print("Not Android. Trying iOS connection")
                psm = 0x1007  # Typical iOS PSM - You should get this from the AVRCP metadata
                self.obex_conn_id, self.dev_type = connectObex(self, psm)

        except Exception as ex: 
            print("Failed to connect. Error:", ex)

    def getImage(self, handle=0):
        if self.dev_type is devType.ANDROID:
            getAndroidImage(self.sock, self.obex_conn_id, handle)
        elif self.dev_type is devType.iOS:
            getiOSImage(self.sock, self.obex_conn_id)



obexConnReq = bytes.fromhex("80001a1500069b4600137163dd544a7e11e2b47c0050c2490048") # OBEX Connection request message
def connectObex(device: obexDevice, psm):
    device.sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
    device.sock.set_l2cap_mtu(1024)
    device.sock.set_l2cap_options([1024, 1024, 65535, 3, 1, 16, 63])
    print(f"Connecting to {device.bt_addr} on PSM {psm}")
    device.sock.connect((device.bt_addr, psm))
    print(f"Connected to {device.bt_addr} on PSM {psm}. Requesting OBEX Connection...")
    device.sock.send(obexConnReq)
    obexResp = device.sock.recv(1024)
    print(obexResp.hex())
    if obexResp[0] != 160: # 0xA0/160 is a success response
        print("OBEX Handshake failed.")
        quit()
    else:
        conn_id = obexResp[8:12]
        if conn_id == bytes.fromhex("00000001"):
            print("Connection ID is 1. Assuming Android.") # Android seems to always set the connection ID to 1
            dev_type = devType.ANDROID
        else:
            print("Connection ID is not 1. Assuming iOS.") # In my testing I never saw 1 as the connection ID
            dev_type = devType.iOS

    return conn_id, dev_type



def parseObex(dataIn: bytes):
    type = dataIn[0]
    length = int.from_bytes(dataIn[1:3])
    data = dataIn
    return type, length, data

# On Android, you can refer to an image by a handle to get the whole image. This allows you to pull old and current images.
# After sending a request, you can just keep reading the socket until you reach the last image chunk to get a whole image.

def getAndroidImage(sock, conn_id, handle: int):
    print("Getting image handle:", handle)

    ################## Assemble OBEX GET request ##################
    
    # buffer = bytes.fromhex("83002dcb00000001420010782d62742f696d672d74686d0030001300") # OBEX GET x-bt/img-thm - returns 200x200 jpg on android
    # buffer = bytes.fromhex("83002DCB00000001420010782D62742F696D672D696D670030001300") # OBEX GET x-bt/img-img - returns same as above on android
    buffer = bytes.fromhex("83002dcb" + conn_id.hex() + "420010782d62742f696d672d74686d0030001300") # OBEX GET x-bt/img-thm
    # 83:      GET request
    # 00 2d:   Packet length (45 in this case)
    # cb:      Connection ID header
    # conn_id: Connection ID that's returned by the OBEX server when connecting
    # 42:      Type Header
    # 00 10:   Length of type header (16)
    # 78 2d 62 74 2f 69 6d 67 2d 74 68 6d 00: "x-bt/img-thm"
    # 30: User-defined header - In this case it's the image handle
    # 00 13: Header length (19)

    # Images are referred to by handle. You get this via the media metadata given by AVRCP
    num_str = str(handle).zfill(7) # Put handle in the format of xxxxxxx. Example: 12 = 0000012
    buffer += bytes.fromhex(''.join([f'{ord(digit):02x}00' for digit in num_str])) # Put 0x00 in between each character

    buffer += bytes.fromhex("009701") # Last chunk of file request

    ###############################################################
    
    sock.send(buffer) # Send image request

    ################## Download image from device ##################
    # On Android, you can keep reciving data until the entire image has been downloaded (which is signaled by a OBEX SUCCESS packet)
    finished = False
    imageOpened = False
    while not finished:
        data_received = sock.recv(1025)  # Receive up to 1025 bytes

        if data_received.hex() == ("c4000acb" + conn_id.hex() +"9701"): # Response from android when file not found
            print(num_str + ": File not found")
            finished = True
            break
        else:
            if not imageOpened:
                fileName = str(num_str) + ".jpg"
                out_image = open(fileName, "wb")
                imageOpened = True

        if data_received[0] == 144: # 0x90/144 is OBEX CONTINUE, aka. keep reading file
            if data_received[8:10] == bytes.fromhex("9701"): # 0x97 0x01 enables OBEX SRM mode. Also marks first chunk of image
                print("Start downloading...")
                out_image.write(data_received[13:]) # Cut off the header and get the image data
            else:
                print(".", end="")
                out_image.write(data_received[11:]) # Cut off the header and get the image data

        elif data_received[0] == 160: # 0xa0/160 is OBEX SUCCESS, aka. stop reading file
            out_image.write(data_received[11:]) # Cut off the header and get the image data
            finished = True
            out_image.close()
            outSize = os.path.getsize(fileName)
            print("\n", num_str, ": Saved", outSize, "bytes as", fileName)
    ###############################################################



# iOS is weird. You just request any handle over and over again
# to get all of the chunks of the current image. You can not request previous images.
def getiOSImage(sock, conn_id):
    handle = 0 # Hardcode the handle because iOS just ignores it anyways

    ################## Assemble OBEX GET request ##################
    # Refer to Android section for a detailed breakdown. The only difference here is that the handle is hardcoded to 0
    print("Getting current image")
    buffer = bytes.fromhex("83002dcb" + conn_id.hex() + "420010782d62742f696d672d74686d0030001300")
    finished = False

    # Images are referred to by handle
    num_str = str(handle).zfill(7) # Put handle in the format of xxxxxxx. Example: 12 = 0000012
    buffer  += bytes.fromhex(''.join([f'{ord(digit):02x}00' for digit in num_str])) # Put 0x00 in between each character

    buffer += bytes.fromhex("009701") # Last chunk of file request
    ###############################################################

    finished = False
    outFile = open("iOS.jpg", "wb")

    ################## Download image from device ##################
    # Unlike Android, iOS only sends a small chunk of the image for every GET request.
    # You have to send several GET requests over and over again until you get SUCCESS
    # This is probably the wrong way of doing this but this works so ¯\_(ツ)_/¯
    
    while not finished:
        sock.send(buffer)
        data_received = sock.recv(1025)  # Receive up to 1025 bytes
        if data_received[0] == 144: # 0x90/144 is OBEX CONTINUE, aka. keep reading file
            outFile.write(data_received[6:])

        elif data_received[0] == 160: # 0xa0/160 is OBEX SUCCESS, aka. stop reading file
            outFile.write(data_received[6:])
            finished = True
            outFile.close()
            outSize = os.path.getsize("iOS.jpg")
            print(num_str, ": Saved", outSize, "bytes as", "iOS.jpg")

    ###############################################################
