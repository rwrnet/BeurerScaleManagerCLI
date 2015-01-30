import usb.core
import usb.backend.libusb1
import sys
import struct

dumpFile = "dump.bin"
dumpSize = 8192

def updateDump():
    # choose backend, e.g. if own libusb should be used - then switch commenting and adjust the following lines
    #backend = usb.backend.libusb1.get_backend(find_library=lambda x: "/opt/local/lib/libusb-1.0.0.dylib")
    backend = usb.backend.libusb1.get_backend()
    
    # Find device by vendor and product id
    dev = usb.core.find(idVendor=0x04d9, idProduct=0x8010, backend=backend)
    
    if dev is None:
        raise ValueError('Device not found')
    
    # In case kernel driver is busying the device (it is a HID) - detach it
    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)
    
    data = bytearray()
    
    # Trigger transfer for bmRequestType 0x21, bRequest 0x9, wValue 0x0300, wIndex 0 and read in chunks of 8 byte
    dev.ctrl_transfer(0x21, 0x09, 0x0300, 0, '\x10\x00\x00\x00\x00\x00\x00\x00')
    while len(data) < dumpSize:
        try:
            data += bytearray(dev.read(0x81,8))
        except usb.core.USBError as e:
            print e
            break
    
    # If dump is completed - save it to file
    if len(data) == dumpSize:
        newFile = open (dumpFile, "wb")
        newFile.write(data);
        newFile.close();

def decodeDump():
    dFile = open (dumpFile, "rb")
    dump = dFile.read(dumpSize);
    dFile.close();
    # split dump into user blocks (768 bytes each)
    userstrings = [dump[i:i+768] for i in range(0, len(dump), 768)]
    users = []
    for userstring in userstrings:
        if len(userstring) < 768:
            continue
        # split user block into measure blocks (128 bytes each)
        measures = [userstring[i:i+128] for i in range(0, len(userstring), 128)]
        user = {}
        user['weights'] = struct.unpack('>60H',measures[0][:120]) # up to 60 weight measures
        user['bodyfats'] = struct.unpack('>60H',measures[1][:120]) # up to 60 bodyfat measures
        user['waters'] = struct.unpack('>60H',measures[2][:120]) # up to 60 water measures
        user['muscles'] = struct.unpack('>60H',measures[3][:120]) # up to 60 muscle measures
        user['dates'] = ['-'.join([
            str(int('{0:016b}'.format(date)[0:7],2)+1920),
            '{0:02d}'.format(int('{0:016b}'.format(date)[7:11],2)),
            '{0:02d}'.format(int('{0:016b}'.format(date)[11:16],2))
            ]) for date in struct.unpack('>60H',measures[4][:120])] # up to 60 dates
        user['times'] = [':'.join('{0:02d}'.format(i) for i in struct.unpack('>2B', struct.pack('>H', time))) for time in struct.unpack('>60H',measures[5][:120])] # up to 60 times
        users.append(user)
    
    print "{0}\t{1} {2}\t{3}\t{4}\t{5}\t{6}".format("User","Date","Time","Weight","Bodyfat%","Water%","Muscles%")
    for u in range(len(users)):
        for i in range(len(users[u]['weights'])):
            if users[u]['weights'][i] == 0xFFFF: continue
            print "{0}\t{1} {2}\t{3}\t{4}\t{5}\t{6}".format(u+1, users[u]['dates'][i], users[u]['times'][i], float(users[u]['weights'][i])/10, float(users[u]['bodyfats'][i])/10, float(users[u]['waters'][i])/10, float(users[u]['muscles'][i])/10)
    
def main(argv):
    if len(argv) == 2 and argv[1] == "update":
        updateDump();
    decodeDump();
    
if __name__ == "__main__":
    main(sys.argv)