import cv2
import os
import threading
import base64
import queue

# -------------------------------------------------------Globals
frameQ = []
convQ = []
# Locks and semaphores from extracting to converting
b1Lock = threading.Lock()
e1Sem = threading.Semaphore(10)
f1Sem = threading.Semaphore(10)
# Locks and semaphores from converting to displaying
b2Lock = threading.Lock()
e2Sem = threading.Semaphore(10)
f2Sem = threading.Semaphore(10)

class extractFrames(threading.Thread):
    def __init__(self):
        super(extractFrames, self).__init__()

    def run(self):
        clipFileName = 'clip.mp4'
        vidcap = cv2.VideoCapture(clipFileName) # Open video
        # read first frame
        success,image = vidcap.read()
        count = 0;

        print("Reading frame {} {} ".format(count, success))
        count+=1

        while success:
            e1Sem.acquire()
            b1Lock.acquire()

            #encode the frame as base 64 to make debugging easier
            frameQ.append(image)

            #read next image
            success,image = vidcap.read()
            print('Reading frame {}'.format(count))
            count += 1
            b1Lock.release()
            f1Sem.release()
        for i in range(10):
            print("______________________________________________ Releasing f1 ", i)
            f1Sem.release()


class convertFrames(threading.Thread):
    def __init__(self):
        super(convertFrames, self).__init__()

    def run(self):
        countC = 0
        while True:
            f1Sem.acquire()
            e2Sem.acquire()


            b1Lock.acquire()
            b2Lock.acquire()

            # get the next frame
            if(frameQ):
                frameAux = frameQ.pop()
            else:
                break
            #convert to grayscale
            grayscaleFrame = cv2.cvtColor(frameAux, cv2.COLOR_BGR2GRAY)
            # send to next queue
            convQ.append(grayscaleFrame)
            print('------------Converting frame {}'.format(countC))
            countC+=1

            b2Lock.release()
            b1Lock.release()

            f2Sem.release()
            e1Sem.release()
        b2Lock.release()
        b1Lock.release()
        e1Sem.release()
        for i in range(10):
            print("------------f2 released ", i)
            f2Sem.release()

class displayFrames(threading.Thread):
    def __init__(self):
        super(displayFrames, self).__init__()

    def run(self):
        while True:
            f2Sem.acquire()
            b2Lock.acquire()
            if (convQ):
                img=convQ.pop()
                cv2.imshow("Video", img)
                if cv2.waitKey(24) and 0xFF == ord("q"):
                    break
            else:
                print("DONE!!!!!!")
                break
            b2Lock.release()
            e2Sem.release()



for i in range(10):
    f1Sem.acquire()
    f2Sem.acquire()

dFrames = displayFrames()
cFrames = convertFrames()
eFrames = extractFrames()

print("Starting thread ------------------- extract")
eFrames.start()

print("Starting thread ------------------- convert")
cFrames.start()

print("Starting thread ------------------- display")
dFrames.start()
