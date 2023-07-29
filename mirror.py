import sys, os

# toggles the mirror lock for various canon camera models without needing to touch them
# if your camera isn't listed and you don't have a status > mirrorlock in your INDI tab, 
# follow these instructions to find the "magic" values:
#   https://github.com/gphoto/libgphoto2/blob/master/camlibs/ptp2/canon-eos-customfunc.txt#L72

if len(sys.argv) == 1:
    print(f"usage: {sys.argv[0]} on|off|status")
    sys.exit(0)

waitSeconds = 3

customfunc = {
    "Canon DSLR EOS 60D" : [
        "50,1,3,44,5,505,1,1,50f,1,0,510,1,0,50e,1,0,60f,1,0,", 
        "50,1,3,44,5,505,1,1,50f,1,0,510,1,0,50e,1,0,60f,1,1,"
    ],
     "Canon DSLR EOS 450D" : [
        "d4,4,1,20,2,101,1,0,10f,1,0,2,38,4,201,1,0,202,1,0,203,1,0,204,1,0,3,2c,3,50e,1,0,511,1,0,60f,1,0,4,38,4,701,1,0,704,1,0,811,1,0,80f,1,0,", 
        "d4,4,1,20,2,101,1,0,10f,1,0,2,38,4,201,1,0,202,1,0,203,1,0,204,1,0,3,2c,3,50e,1,0,511,1,0,60f,1,1,4,38,4,701,1,0,704,1,0,811,1,0,80f,1,0,"
    ],
}
def exec(cmd, doPrint=True):
    if doPrint:
        print(cmd)
    try:
        p = os.popen(cmd)
        res = p.readline()[:-1]
        p.close()
        return res
    except:
        print("error")
        sys.exit(0)

arg = sys.argv[1]
deviceName = exec("indi_getprop |grep Canon | head -1 | cut -d . -f 1", False)
if sys.argv[1] == 'status':
    cmd = ""
    try:
        customfunc[deviceName]
        print(exec(f"indi_getprop '{deviceName}.customfuncex.customfuncex'", False))
    except KeyError:
         print(exec(f"indi_getprop '{deviceName}.mirrorlock.mirrorlock0'", False))
         print(exec(f"indi_getprop '{deviceName}.mirrorlock.mirrorlock1'", False))
    print(exec(f"indi_getprop '{deviceName}.MIRROR_LOCK.MIRROR_LOCK_SECONDS'", False))
else:
    index = 1 if arg == 'on' else 0
    seconds = 0
    if index == 1:
        seconds = waitSeconds

    cmd = ""
    try:
        val = customfunc[deviceName][index]
        cmd = f"indi_setprop '{deviceName}.customfuncex.customfuncex={customfunc[deviceName][index]}'"
    except KeyError:
        cmd = f"indi_setprop '{deviceName}.mirrorlock.mirrorlock{index}=On'"
    exec(f"{cmd}")
    cmd = f"indi_setprop '{deviceName}.MIRROR_LOCK.MIRROR_LOCK_SECONDS={seconds}'"
    exec(f"{cmd}")