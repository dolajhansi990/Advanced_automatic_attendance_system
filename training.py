# import the necessary packages
from imutils import paths
import face_recognition
import pickle
import qrcode
import cv2
import os

def generateQR(student_id):
    directory = f"Trained_Models\\{student_id}"
    if not os.path.exists(directory):
        os.makedirs(directory)
        qr = qrcode.QRCode(version = 3, error_correction = qrcode.constants.ERROR_CORRECT_M, box_size = 8, border = 6)
        qr.add_data(student_id)
        qr.make(fit = True)
        img = qr.make_image()
        img.save(f"{directory}\\{student_id}_(QRCODE).jpg")
        return img


# initialize the list of known encodings and known names
knownEncodings = []
knownNames = []

def trainData(i, imagePath, imagePaths):
    print(f"[INFO] processing image {i+1}/{len(imagePaths)}")
    try:
        f = open("Training_Status.txt","w")
        f.write(f"{i+1}|{len(imagePaths)}")
        f.close()
    except Exception as e:
        pass
    name = imagePath.split(os.path.sep)[-2]
	# load the input image and convert it from BGR (OpenCV ordering)
	# to dlib ordering (RGB)
    image = cv2.imread(imagePath)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

	# detect the (x, y)-coordinates of the bounding boxes
	# corresponding to each face in the input image
    boxes = face_recognition.face_locations(rgb, model="hog")
	# compute the facial embedding for the face

    encodings = face_recognition.face_encodings(rgb, boxes)

	# loop over the encodings
    for encoding in encodings:
		# add each encoding + name to our set of known names and
		# encodings
        knownEncodings.append(encoding)
        knownNames.append(name)

    completed_percentage = int(((i+1)/len(imagePaths))*100)
    return completed_percentage

    # dump the facial encodings + names to disk
def dumpEncodings(student_id):
    print("[INFO] serializing encodings...")
    data = {"encodings": knownEncodings, "names": knownNames}
    f = open(f"Trained_Models\\{student_id}\\{student_id}_(Model).pickle", "wb")
    f.write(pickle.dumps(data))
    f.close()
