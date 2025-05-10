import obex

# In order for this to work on Android, the device running this code needs to be an audio sink. It also
# needs to advertise AVRCP 1.6 and Cover Art compatibility. BlueZ needs to be patched to advertise those 2 things.
# You must also enable AVRCP 1.6 in the Android device developer options.

# iOS doesn't seem to care about whether or not your device is even an audio sink so this should work as long
# as your phone and the PC running this code are paired to each other.

# Put the bluetooth address of your device here. obex.py will auto-detect if your device is Android or iOS
target_address = "B8:B2:F8:xx:xx:xx"

device = obex.obexDevice(target_address)
device.connect()

# Downloads the image associated with the handle and saves it to <handle>.jpg
# The handle refers to the cover art you're trying to get. On Android, you'd get this
# handle via AVRCP but that part isn't implemented. 

# iOS doesn't seem to care about what the handle is and will always return the cover
# art of the currently playing media. If obex.py detects that your device is an iOS device, 
# the handle is ignored.
device.getImage(handle=7)