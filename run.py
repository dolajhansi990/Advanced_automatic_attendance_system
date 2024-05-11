import cv2
import pyttsx3
import numpy as np
from pyzbar.pyzbar import decode
from scipy.spatial import distance as dist
from imutils import face_utils
import imutils
import time
import dlib
import mysql.connector
import face_recognition
import pickle
import random
import ctypes
from datetime import datetime
from dialouges import *

mydb = mysql.connector.connect(

    host="localhost",
    user="root",
    passwd="",
    database="management_auto_attendance_system"
)

SelectDataCursor = mydb.cursor()

engine = pyttsx3.init()
en_voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"  # female
ru_voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_RU-RU_IRINA_11.0"  # male
engine.setProperty('voice', en_voice_id)
rate = engine.getProperty('rate')
engine.setProperty('rate', rate - 20)


def talk_function(audio):
    print("Computer: {}".format(audio))
    engine.say(audio)
    engine.runAndWait()


user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

Screen_Width = 820
Screen_Height = 620

Screen_Center_Width = int((screensize[0] - Screen_Width) / 2)
Screen_Center_Height = int((screensize[1] - Screen_Height) / 2) - 30

now = datetime.now()
Global_Current_Date = now.strftime("%d-%b-%Y")

Counter = 0

Student_ID = ""
Student_Name = ""
Attendance_Type = ""

EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 2
# initialize the frame counters and the total number of blinks
Eye_COUNTER = 0
TOTAL_Blinks = 0

# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("Shape_Model\\shape_predictor_68_face_landmarks.dat")

# grab the indexes of the facial landmarks for the left and
# right eye, respectively
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

face_exception = "";

f = open("System_Settings\\Face_rec.txt")
face_exception = f.read()
f.close()


def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])
    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)
    # return the eye aspect ratio
    return ear


cap = cv2.VideoCapture(0)
isexit = False

def AttendanceSystem():
    global Counter, cap, TOTAL_Blinks, Eye_COUNTER, Student_Name, Student_ID, Attendance_Type, Global_Current_Date, face_exception

    ###############
    #    Reset    #
    ###############

    TOTAL_Blinks = 0
    Eye_COUNTER = 0
    Student_ID = ""
    Student_Name = ""
    Section = ""

    ###############
    #    Reset    #
    ###############

    while True:

        success, img = cap.read()
        img = imS = cv2.resize(img, (Screen_Width, Screen_Height))
        # img = imS = cv2.resize(img, (screensize[0], screensize[1]))
        # cv2.namedWindow("Display_1", cv2.WND_PROP_FULLSCREEN)
        # cv2.setWindowProperty("Display_1",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

        QRcodeData = decode(img)

        if len(QRcodeData) != 0:
            CodeType = QRcodeData[0][1]

            if CodeType == "QRCODE":

                hiddenData = QRcodeData[0][0].decode('utf-8')

                if Counter == 5:

                    Counter = 0

                    SelectDataCursor.execute(
                        "SELECT full_name, section FROM students WHERE student_id = '{}' AND is_model_available = 'True'".format(
                            hiddenData))
                    collecttedData = SelectDataCursor.fetchall()

                    if not collecttedData:
                        talk_function(random.choice(unauthorized_IDcard_Voice_Data))

                    else:

                        SelectDataCursor.execute(
                            "SELECT * FROM attendance WHERE _date = '{}' and Student_id = '{}'".format(
                                Global_Current_Date, hiddenData))
                        AlreadyExit = SelectDataCursor.fetchall()

                        if not AlreadyExit:

                            Student_ID = hiddenData
                            Student_Name = collecttedData[0][0]
                            Section = collecttedData[0][1]


                            cv2.destroyAllWindows()
                            break

                        else:

                            talk_function(random.choice(Attendance_Already_Exit))

                pts = np.array([QRcodeData[0][3]], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(img, [pts], True, (0, 255, 0), 5)

                Counter += 1

        cv2.imshow('Display_1', img)
        cv2.moveWindow('Display_1', Screen_Center_Width, Screen_Center_Height)  ##center window
        key = cv2.waitKey(1)

        if key == 27:
            talk_function(random.choice(shutting_Down_Voices))
            cv2.destroyAllWindows()
            return 1

    talk_function(random.choice(blink_Eye_Voice_Data))

    while True:

        success, frame = cap.read()
        frame = imS = cv2.resize(frame, (Screen_Width, Screen_Height))
        # frame = imS = cv2.resize(frame, (screensize[0], screensize[1]))
        # cv2.namedWindow("Display_2", cv2.WND_PROP_FULLSCREEN)
        # cv2.setWindowProperty("Display_2",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

        CacheFrame = frame.copy()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # detect faces in the grayscale frame
        rects = detector(gray, 0)
        # loop over the face detections
        for rect in rects:
            # determine the facial landmarks for the face region, then
            # convert the facial landmark (x, y)-coordinates to a NumPy
            # array
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            # extract the left and right eye coordinates, then use the
            # coordinates to compute the eye aspect ratio for both eyes
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            # average the eye aspect ratio together for both eyes
            ear = (leftEAR + rightEAR) / 2.0

            # compute the convex hull for the left and right eye, then
            # visualize each of the eyes
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            # check to see if the eye aspect ratio is below the blink
            # threshold, and if so, increment the blink frame counter
            if ear < EYE_AR_THRESH:
                Eye_COUNTER += 1
            # otherwise, the eye aspect ratio is not below the blink
            # threshold
            else:
                # if the eyes were closed for a sufficient number of
                # then increment the total number of blinks
                if Eye_COUNTER >= EYE_AR_CONSEC_FRAMES:
                    TOTAL_Blinks += 1

                # reset the eye frame counter
                Eye_COUNTER = 0

        if TOTAL_Blinks == 2:
            TOTAL_Blinks = 0
            cv2.imwrite("Cache/CacheImg.jpg", CacheFrame)

            data = pickle.loads(
                open("Trained_Models\\{}\\{}_(Model).pickle".format(Student_ID, Student_ID), "rb").read())
            image = cv2.imread("Cache\\CacheImg.jpg")
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb, model='hog')

            if (len(boxes) == 1):  # if it finds only one face

                BreakStatus = False

                encodings = face_recognition.face_encodings(rgb, boxes)

                for encoding in encodings:
                    matches = face_recognition.compare_faces(data["encodings"], encoding, 0.5)

                    if True in matches:

                        now = datetime.now()
                        currentTime = now.strftime("%I:%M:%S %p")

                        BreakStatus = True

                        # Insert Query
                        insert_cursor = mydb.cursor()
                        sqlCode = "INSERT INTO attendance(student_id,student_name,section, in_time, _date, face_recognition_entering) VALUES ('{}', '{}', '{}','{}', '{}', '{}')".format(
                            Student_ID, Student_Name, Section, currentTime, Global_Current_Date, "True","")
                        insert_cursor.execute(sqlCode)
                        mydb.commit()

                        talk_function(random.choice(Entering_Attendance_Passed))



                    else:
                        talk_function(random.choice(unauthorized_face_Voice_Data))
                        BreakStatus = False

                if BreakStatus == True:
                    break

            else:
                talk_function(random.choice(try_again_Voice_Data))

        # show the frame
        cv2.imshow("Display_2", frame)
        cv2.moveWindow('Display_2', Screen_Center_Width, Screen_Center_Height)  # center window
        key = cv2.waitKey(1)

        if key == 32:
            talk_function(random.choice(Restarting_Voice))

            break

        elif key == 13:

            if face_exception.strip() == "True":

                now = datetime.now()
                currentTime = now.strftime("%I:%M:%S %p")
                timestampStr = now.strftime("%d-%b-%Y_(%H-%M-%S-%f)")

                img_name = "{}_Entering.jpg".format(timestampStr)
                # Insert Query
                cv2.imwrite("Attendance_Pending_Images/{}".format(img_name), frame)
                insert_cursor = mydb.cursor()
                sqlCode = "INSERT INTO attendance(student_id,student_name,section, in_time, _date, face_recognition_entering) VALUES ('{}', '{}', '{}','{}', '{}', '{}')".format(
                    Student_ID, Student_Name, Section, currentTime, Global_Current_Date, "True")
                insert_cursor.execute(sqlCode)
                mydb.commit()

                talk_function(random.choice(Entering_Attendance_Passed_Pending))

                break

            elif key == 27:
                talk_function(random.choice(shutting_Down_Voices))
                cv2.destroyAllWindows()
                return 1

    cv2.destroyAllWindows()
    AttendanceSystem()



