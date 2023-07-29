import sys, os

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
def exec(cmd):
    print(cmd)
    try:
        p = os.popen(cmd)
        res = p.readline()[:-1]
        p.close()
        return res
    except:
        print("error")
        sys.exit(0)


deviceName = exec("indi_getprop |grep Canon | head -1 | cut -d . -f 1")
index = 1 if sys.argv[1] == 'on' else 0
seconds = 0
if index == 1:
    seconds = 3

cmd = ""
try:
    val = customfunc[deviceName][index]
    cmd = f"indi_setprop '{deviceName}.customfuncex.customfuncex={customfunc[deviceName][index]}'"
except KeyError:
    cmd = f"indi_setprop '{deviceName}.mirrorlock.mirrorlock{index}=On'"
exec(f"{cmd}")
cmd = f"indi_setprop '{deviceName}.MIRROR_LOCK.MIRROR_LOCK_SECONDS={seconds}'"
exec(f"{cmd}")