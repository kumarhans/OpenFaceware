import cv2
import sys
import autopy
import time

cascPath1 = sys.argv[1]
faceCascade = cv2.CascadeClassifier(cascPath1)
cascPath2 = sys.argv[2]
noseCascade = cv2.CascadeClassifier(cascPath2)
cascPath3 = sys.argv[3]
eyeCascade = cv2.CascadeClassifier(cascPath3)

video_capture = cv2.VideoCapture(0)

def almostEqual(face1, face2):
    w1, h1, w2, h2 = face1[2], face1[3], face2[2], face2[3]
    if (w2 <= w1 + 50 or w2 >= w1 - 50) and (h2 <= h1 + 50 or h2 >= h1 - 50):
        return True
    return False

def rateOfYChange(nose1, nose2):
    y1, y2 = nose1[1], nose2[1]
    return (y2-y1)/5

def noSigXChange(nose1, nose2):
    x1, x2 = nose1[0], nose2[0]
    return 100 > abs(x2-x1)

def rateOfChange(face1, face2):
    w1, h1, w2, h2 = face1[2], face1[3], face2[2], face2[3]
    return (w2*h2 - w1*h1)/5

def insideBox(nose, face):
    noseX, noseY, noseW, noseH = nose
    x, y, w, h = face
    faceX, faceY = w/3 + x -15, h/3 + y-15
    faceW, faceH = w*1/3+30, h*1/3+30
    return ((noseX > faceX and noseY > faceY) and 
        (noseX + noseW < faceX + faceW and noseY + noseH < faceY + faceH))

# Face variables
prevLargestFace = None
curLargestFace = None
faceFiveSecondsAgo = None
dabbedAlready = False

# Nose variables
curNose = None
prevNose = None
noseFiveSecondsAgo = None

timer1 = timer2 = 0
zoom = scroll = dab = False

while True:

    ############### ZOOM ############### 

    # Capture frame-by-frame
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if cv2.waitKey(1) & 0xFF == ord('z'): 
        zoom = not zoom
    elif cv2.waitKey(1) & 0xFF == ord('s'):
        scroll = not scroll
    elif cv2.waitKey(1) & 0xFF == ord('d'):
        dab = not dab

    if zoom == True:

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )

        curLargest = 0

        for (x, y, w, h) in faces:
            if w < 150 and h < 150: continue # Ignore anything too small
            elif w*h > curLargest*1.2:
                prevLargestFace = curLargestFace
                curLargestFace = (x, y, w, h)
                curLargest = w*h

        if (curLargestFace != None and prevLargestFace != None and 
            almostEqual(curLargestFace, prevLargestFace)):
            (x, y, w, h) = curLargestFace
            print(x, y, x+w, y+h)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            if timer1 % 7 == 0:
                if faceFiveSecondsAgo != None:
                # Calculate rate of change
                    rate = rateOfChange(faceFiveSecondsAgo, curLargestFace)
                    if rate > 2500:
                        print("BIGGER")
                        autopy.key.tap("=", autopy.key.MOD_SHIFT | autopy.key.MOD_CONTROL)
                        autopy.key.tap("=", autopy.key.MOD_SHIFT | autopy.key.MOD_CONTROL)
                    elif rate < -2500:
                        print("SMALLER")
                        autopy.key.tap("-", autopy.key.MOD_SHIFT | autopy.key.MOD_CONTROL)
                        autopy.key.tap("-", autopy.key.MOD_SHIFT | autopy.key.MOD_CONTROL)
                faceFiveSecondsAgo = curLargestFace
        timer1 += 1

    elif scroll == True: 

        crop_img = None

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )
        
        curLargest = 0

        for (x, y, w, h) in faces:
            if w < 150 and h < 150: continue # Ignore anything too small
            elif w*h > curLargest*1.2 or w*h < curLargestFace*0.8:
                prevLargestFace = curLargestFace
                curLargestFace = (x, y, w, h)
                curLargest = w*h

        if (curLargestFace != None and prevLargestFace != None and 
            almostEqual(curLargestFace, prevLargestFace)):
            (x, y, w, h) = curLargestFace
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        noses = noseCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )

        curLargestSize = 0

        for nose in noses:
            if insideBox(nose, curLargestFace):
                (x1, y1, w1, h1) = nose
                if w1*h1 > curLargestSize:
                    prevNose = curNose
                    curNose = (x1, y1, w1, h1)
                    curLargestSize = w*h

        if (curNose != None and prevNose != None and 
            almostEqual(curNose, prevNose)):
            (x2, y2, w2, h2) = curNose
            cv2.rectangle(frame, (x2, y2), (x2+w2, y2+h2), (0, 255, 0), 2)
            if timer2 % 3 == 0:
                if noseFiveSecondsAgo != None and noSigXChange(noseFiveSecondsAgo, curNose):
                # Calculate rate of change
                    rate = rateOfYChange(noseFiveSecondsAgo, curNose)
                    if rate > 2:
                        print("DOWN")
                        autopy.key.tap(autopy.key.K_PAGEDOWN)
                        time.sleep(1)
                    elif rate < -2:
                        print("UP")
                        autopy.key.tap(autopy.key.K_PAGEUP)
                        time.sleep(1)
                noseFiveSecondsAgo = curNose
        timer2 += 1

    elif dab == True and dabbedAlready == False:

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )
        
        eyes = eyeCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags = cv2.cv.CV_HAAR_SCALE_IMAGE
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        for (x, y, w, h) in eyes:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        if len(faces) == 0 and len(eyes) == 0:
            autopy.mouse.smooth_move(500, 30)

            time.sleep(1)

            autopy.mouse.click()

            for i in range(200):
                autopy.key.tap(autopy.key.K_BACKSPACE)

            autopy.key.type_string("https")
            autopy.key.tap(";", autopy.key.MOD_SHIFT)
            autopy.key.type_string("//www.youtube.com/watch")


            autopy.key.tap("\n")

            dabbedAlready = True

    # Display the resulting frame
    cv2.imshow('OpenFaceware', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
