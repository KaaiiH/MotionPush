import practice
import subprocess
import os

# gitpush = subprocess.Popen(["./gitpush.sh"], "/Users/kaihoenshell/git/MotionPush", stdin=subprocess.PIPE)

if(practice.x > 1):

    subprocess.call("./gitpush.sh", shell=True)



    # gitpush.stdin.write("yes\n")
    # gitpush.stdin.close()
    # returncode = gitpush.wait()
