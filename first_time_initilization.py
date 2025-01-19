import cv2
import glob
import pickle
import os
import numpy as np
from time import sleep
import face_recognition

# Path to store images and encodings
path = 'Image_Database'  # Folder where the images are stored
formats = {"jpeg", "jpg", "png", "tif", "tiff", "gif"}  # Acceptable image formats
encoding_file_name = 'Employee_Database/Face_Encodings.pkl'  # The pickle file to store encodings

def findEncoding(img):
    """
    Extracts the face encoding from the given image.
    Returns the encoding if successful, else returns None.
    """
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encode_list = face_recognition.face_encodings(img_rgb)
    
    if len(encode_list) == 0:
        print("Face not clear. Please capture a clear image.")
        return None
    
    return encode_list[0]


def saveEncodingList(classNames, images, encoding_file_name):
    """
    Saves the face encodings for the first time into a pickle file.
    """
    encodeList = []
    for img in images:
        encode = findEncoding(img)
        if encode is not None:
            encodeList.append(encode)
        else:
            print("Skipping image due to unclear face.")
    
    # Save the encodings to a pickle file
    with open(encoding_file_name, 'wb') as f:
        pickle.dump([classNames, encodeList], f)
    print("Face encodings saved successfully!")

    
def initialize_encodings():
    """
    Perform the first-time setup for saving face encodings.
    This will collect images from the database, process them, and store their encodings.
    """
    # Get all the images in the database folder
    myList = glob.glob(os.path.join(path, "*"))
    
    # Select only the acceptable image formats
    toRemove = []
    for pic_path in myList:
        if pic_path.lower().split(".")[-1] not in formats:
            toRemove.append(pic_path)
    
    # Remove unsupported images
    for ele in toRemove:
        myList.remove(ele)

    # Read the list of images and their corresponding class names
    images = []
    classNames = []
    
    for cl in myList:
        curImg = cv2.imread(cl)
        images.append(curImg)
        classNames.append(os.path.basename(cl).split(".")[0])  # Use the image name (without extension) as class name
    
    # Save the encodings list to the file
    saveEncodingList(classNames, images, encoding_file_name)


# First-time setup to initialize face encodings
if not os.path.exists(encoding_file_name):
    print("First time initialization...")
    initialize_encodings()
else:
    print("Encodings already exist. Skipping first-time initialization.")
