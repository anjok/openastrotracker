import sys, os

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
