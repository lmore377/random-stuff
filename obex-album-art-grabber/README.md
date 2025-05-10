# obex-album-art-grabber

Pulls album art via OBEX from an Android or iOS device supporting AVRCP 1.6

## Bad code notice
This code is very bad and should not be used in a real world application without some major refactoring. It does work though.

## Usage
`obex.py` is where the bulk of the code is. See `test.py` for an example of usage and important information.

In order for this to work when connecting to an Android device, the device running this code needs to be an audio sink. \
It also needs to advertise AVRCP 1.6 and Cover Art compatibility. BlueZ needs to be patched to advertise those 2 things and for that you can find a *very bad* patch in `bluez-avrcp-patch.patch`. \
This will likely fail to apply but it should give you an idea of what needs to be changed.

More reading:\
https://www.bluetooth.com/specifications/specs/a-v-remote-control-profile-1-6-2/ \
https://www.bluetooth.com/specifications/specs/basic-imaging-profile-1-0/ \
https://btprodspecificationrefs.blob.core.windows.net/ext-ref/IrDA/OBEX15.pdf
