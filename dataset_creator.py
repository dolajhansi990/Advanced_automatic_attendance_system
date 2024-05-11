import os
import cv2
import numpy
import shutil
import pyttsx3
import threading
import face_recognition
from imutils import paths
from playsound import playsound
import ctypes
def createDataSet(student_id, no_of_images):
	engine = pyttsx3.init()
	en_voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"  # female
	ru_voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_RU-RU_IRINA_11.0"  # male
	engine.setProperty('voice', en_voice_id)
	rate = engine.getProperty('rate')
	engine.setProperty('rate', rate - 20)

	def talk_function(audio):
		print(f"Computer: {audio}")
		engine.say(audio)
		engine.runAndWait()



	user32 = ctypes.windll.user32
	screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
	Screen_Width = 820
	Screen_Height = 620
	Screen_Center_Width = int((screensize[0] - Screen_Width) / 2)
	Screen_Center_Height = int((screensize[1] - Screen_Height) / 2) - 30






	cap = cv2.VideoCapture(0)

	folder_name = student_id
	total = no_of_images
	current = 1

	font                   = cv2.FONT_HERSHEY_SIMPLEX
	bottomLeftCornerOfText = (10,40)
	fontScale              = 1
	fontColor              = (0,0,255)
	lineType               = 2


	CapturePosition  = (10,80)
	CaptureFontColor = (255,0,0)
	ExitPosition     = (10,120)


	if not os.path.exists("Datasets\\{}".format(folder_name)):
	    os.makedirs("Datasets\\{}".format(folder_name))


	def soundPlay():
		playsound('Sound.mp3')

	is_running = True

	while is_running:

		ret,frame = cap.read()
		frame = cv2.resize(frame, (Screen_Width, Screen_Height))
		#frame = cv2.resize(frame, (screensize[0], screensize[1]))
		#cv2.namedWindow("Display", cv2.WND_PROP_FULLSCREEN)
		#cv2.setWindowProperty("Display",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

		newImage = frame.copy()
		cv2.putText(newImage,'({} / {})'.format(current - 1,total), bottomLeftCornerOfText, font, fontScale, fontColor,lineType)
		cv2.putText(newImage,"Press 'Spacebar' to capture images".format(current,total), CapturePosition, font, 1, CaptureFontColor,2)
		cv2.putText(newImage,"Press 'Escape' to Exit".format(current,total), ExitPosition, font, 1, CaptureFontColor,2)
		cv2.imshow("Display",newImage)
		cv2.moveWindow('Display', Screen_Center_Width, Screen_Center_Height) ##center window

		k = cv2.waitKey(1)

		if k == 32:
			if int(current) <= int(total):

			   thread1 = threading.Thread(target = soundPlay)
			   thread1.start()

			   rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			   boxes = face_recognition.face_locations(rgb, model="hog")

			   if(len(boxes) != 0):
				   cv2.imwrite(f"Datasets\\{folder_name}\\{current}.jpg",frame)
				   print(f"Image No: {current}")
				   current = current + 1

				   talk_function("Ok, Next")
			   else:
			   	   talk_function("Try Again")

			else:

				try:
					talk_function("Thank you so much, The image capturing has been done.")
					file = open("Data_Creator_Status.txt","w")
					file.write("Finished")
					file.close()
					is_running = False
					cv2.destroyAllWindows()
					return 1


				except Exception as e:
					is_running = False


		elif k == 27:

			talk_function("The image capturing process has been stopped by the user.")
			shutil.rmtree("Datasets\\{}".format(folder_name))

			try:
				file = open("Data_Creator_Status.txt","w")
				file.write("Stopped")
				file.close()
				is_running = False
			except Exception as e:
				is_running = False
	cv2.destroyAllWindows()
	return 0
