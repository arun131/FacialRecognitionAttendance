import cv2
import numpy as np
import face_recognition
import glob
import pandas as pd
import pickle
from time import sleep
import os
from datetime import datetime
from IPython.display import clear_output

# # Run for the first time

# # for savnig the face encodings for the first time
# def saveEncodingList(classNames, images, encoding_file_name):
#     encodeList = []
#     for img in images:
#         encode = findEncoding(img)
#         encodeList.append(encode)
#     with open(encoding_file_name, 'wb') as f:
#         pickle.dump([classNames, encodeList], f)
    
#     #return encodeList
    
# # get all the images in the database for the first time
# myList = glob.glob(path + "\*")
# # select only the acceptable image formats 
# toRem = []
# for i, pic_path in enumerate(myList):
#     if pic_path.lower().split(".")[1] not in formats:
#         toRem.append(pic_path)
# for ele in toRem:
#     myList.remove(ele)

# # Read the list of images
# images = []
# classNames = []
# for cl in myList:
#     curImg = cv2.imread(f'{cl}')
#     images.append(curImg)
#     classNames.append(cl.split("\\")[1].split(".")[0])
    
# #saveEncodingList(classNames, images, encoding_file_name)


def remove_employee_record():
    global my_data, face_encoding_list, face_names, encoding_file_name
    idd = int(input("Enter the employee ID: "))
    record = my_data[my_data["Emp_Id"] == idd]
    if record.shape[0] > 0:
        print("\nPlease confirm the employee details")
        print(my_data[my_data["Emp_Id"] == idd])
        conf_inp = input("\nAre you sure to remove?\n(Y/N): ")
        if conf_inp.lower() == "y":
            # drop the employee row and save to the database
            my_data.drop(record.index.values, inplace = True)
            my_data.to_csv(emp_rec,columns = ["First Name", "Last Name", "Emp_Id", "Gender"],index = False)
            
            # find the index of the employee
            idx = [i for i, ele in enumerate(face_names) if str(idd) in ele]
            face_encoding_list.pop(idx[0])
            face_names.pop(idx[0])
            # droped and save the pickle file
            with open(encoding_file_name, 'wb') as f:
                pickle.dump([face_names, face_encoding_list], f)
            print("\nSuccessfully Removed Employee Record")
        else:
            print("\nNot Removing the Employee Record")
    else:
        print("\nEmployee Record Not Found")

def append_new_employee(encoded, emp, img_name):
    global my_data, emp_rec
    my_data.loc[len(my_data)] = ([emp["First"].capitalize(),
                                      emp["Last"].capitalize(),
                                      emp["EID"],
                                      emp["Gender"].capitalize()])
    my_data.to_csv(emp_rec,columns = ["First Name", "Last Name", "Emp_Id", "Gender"],index = False)
    
    dump_new_pickle(encoded, img_name)

def dump_new_pickle(new_encode, classname):
    global face_encoding_list, face_names, encoding_file_name
    face_encoding_list.append(new_encode)
    face_names.append(classname)
    with open(encoding_file_name, 'wb') as f:
        pickle.dump([face_names, face_encoding_list], f)
    
def findEncoding(img):
    encodeList = []
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encode = face_recognition.face_encodings(img)
    if len(encode) == 0:
        print("Face not clear.\nPlease capture a clear image.")
        return
    else:
        encodeList.append(encode[0])
    return encodeList[0]

def grabnewemployee():
    global path, my_data
    # Get the Employee name details from user
    while True:
        print("Fill the employee details")
        emp_name = {}
        emp_name["First"] = input("First Name: ")
        emp_name["Last"] = input("Last Name: ")
        # check for correct emp_id value
        while True:
            try:
                emp_name["EID"] = int(input("Emp_Id: "))
                break
            except ValueError:
                print("Enter a correct number:")
                continue
        # Raise Error till we get a unique emp id
        if emp_name["EID"] in set(my_data["Emp_Id"].values):           
            print("Employee Record Already Exists \nChoose a new Employee Id")
            continue
        else:
            emp_name["Gender"] = input("Gender: ")
            break
    #file name and face name
    img_name = emp_name["First"].lower() + "_" + emp_name["Last"].lower() + "_" + str(emp_name["EID"])
    
    # activate the camera
    key = cv2.waitKey(1) # wait indefinetely for the key
    webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW) # load camera
    sleep(2)
    while True:

        try:
            check, frame = webcam.read()
            cv2.imshow("Capturing", frame)
            key = cv2.waitKey(1)
            if key == ord('s'):
                encoded = findEncoding(frame)
                if len(encoded) > 0:
                    cv2.imwrite(path + f'\\{img_name}.jpg', frame)
                    webcam.release()
                    print("Saving image...")
                    append_new_employee(encoded, emp_name, img_name)
                    sleep(1.5)
                    break
                else:
                    continue

            elif key == ord('e'):
                webcam.release()
                cv2.destroyAllWindows()
                break

        except KeyboardInterrupt:
            print("Turning off camera.")
            webcam.release()
            print("Camera off.")
            print("Program ended.")
            cv2.destroyAllWindows()
            break


def load_attendance():
    """
    This function returs the current months attendance database file and the file name in the system
    If file doesnt exist, it will create a new empty file
    """
    
    # generate the correct file name
    name = datetime.now().date().strftime("%b-%Y") + "-Attendance.csv"
    img_db_name = datetime.now().date().strftime("%b-%Y") + "-Images"
    # get the available file names
    available = glob.glob("Attendance_Database\*")
    available = [ele.split("\\")[1] for ele in available]
    # check if the current month's file exists
    if name not in available:
        # if dosent exist, generate an empty file
        df = pd.DataFrame(columns=["Emp_Id","First Name","Last Name","Date", "Time"])
        # Create an empty diectory
        os.mkdir("Attendance_Database\\Captured_Images\\" + img_db_name)
        return df, "Attendance_Database\\" + name
    if name in available:
        # if exists, load the file 
        name = "Attendance_Database\\" + name
        df = pd.read_csv(name, header = 0, names = ["Emp_Id","First Name","Last Name","Date", "Time"],
                    parse_dates=[3,4],)
        return df, name
    
def save_attendance(values):
    """
    This function appends the employee record to the current month's data base file in Attendace Database folder
    """
    # load the global attendance df and file name
    global att_file, att_file_name
    # add the values to the end of the dataframe
    att_file.loc[len(att_file)] = values
    # save the csv file
    att_file.to_csv(att_file_name, columns=["Emp_Id","First Name","Last Name","Date", "Time"],
                     index = False)
    
def save_captured_image(img, img_db_name, name, dtString, timeString):
    cv2.imwrite(f"{img_db_name}/{name}_{dtString.replace('/', '-')}_{timeString.replace(':', '-')}.jpg", img) 


def markAttendance(name, img):
    """
    This function checks if the attendance is already recorded for the day and enters if not recorded
    """
    # load the attendance file and its file name
    global att_file, att_file_name
    # get the employee details
    emp_details = [ele.capitalize() for ele in name.split("_")]
    # calculate the current time and date 
    now = datetime.now()
    timeString = now.strftime('%H:%M:%S')
    dtString = now.strftime("%b/%d/%Y")
    # filter out only today's attendance entrance
    todays_attendance = att_file[att_file["Date"] == dtString]
    # img capture name
    img_db_name = now.date().strftime("%b-%Y") + "-Images"
    img_db_name = "Attendance_Database/Captured_Images/" + img_db_name
    # check if already entered
    if sum(todays_attendance["Emp_Id"] == int(emp_details[2])) == 0:
        values_to_add = [int(emp_details[2]),
                        emp_details[0],
                        emp_details[1],
                        dtString,
                        timeString]
        save_attendance(values_to_add)
        print(f"Attendance given to {name}")
        # Save the captured images
        save_captured_image(img, img_db_name, name, dtString, timeString)
        
    else:
        print(f"{name} has already entered today")
        


# Load face encodings and names
encoding_file_name = 'Employee_Database\\Face_Encodings.pkl'
with open(encoding_file_name, 'rb') as f:
    tmp = pickle.load(f)
face_names = tmp[0][:]
face_encoding_list = tmp[1][:]
del tmp

# Load Employee Database
emp_rec = 'Employee_Database\\EmployeeRecords.csv'
my_data = pd.read_csv(emp_rec,names= ["First Name", "Last Name", "Emp_Id", "Gender"],header = 0)
print(my_data)

# Path of the main images database
path = 'Image_Database'

#acceptable image formats
formats = set(["jpeg", "jpg", "png", "tif", "tiff", "gif"])

cinp = input("Do you want to remove any employee record?\n Yes/No")

if cinp.lower() == "yes":
    remove_employee_record()

cinp = input("Do you want to add a new employee to the record?\n Yes/No")

if cinp.lower() == "yes":
    grabnewemployee()
    
att_file, att_file_name = load_attendance()

key = cv2.waitKey(1) # wait indefinetely for any key
# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # load camera
cap = cv2.VideoCapture("Trial_4.mp4") # load camera
counter = 0
counter2 = 0
un_counter = 0
found_emp = []
found_emp_enc = []
unknown_enc_list = []
while True:
    success, img = cap.read()
    # cv2.imshow("Recording Attendance", img)
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    
    #imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
    
    # get face encodings in the images
    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(face_encoding_list, encodeFace,tolerance=0.5)
        faceDis = face_recognition.face_distance(face_encoding_list, encodeFace)
        matchIndex = np.argmin(faceDis)
        # check if face matches with known faces
        if matches[matchIndex]:
            # if matches do below 
            name = face_names[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            counter += 1
            found_emp.append(name)
            # count 3 times and mark attendance 
            if counter == 3 and len(set(found_emp)) == 1:
                markAttendance(name, img)
                # markAttendance(name, imgS)
                counter = 0
                found_emp = []
                
            elif counter > 3:
                counter = 0
                found_emp = []
                
        # if dosent match in known faces         
        else:
            name = f"Unknown_User"
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            if len(unknown_enc_list) > 0:
                # check if the face exists in unknown enc list
                matches = face_recognition.compare_faces(unknown_enc_list, encodeFace, tolerance=0.6)
                faceDis = face_recognition.face_distance(unknown_enc_list, encodeFace)
                matchIndex = np.argmin(faceDis)
                if matchIndex:
                    decision = 1
                else:
                    decision = 0
            else:
                decision = 0
            
            # check if face matches in unknown faces list
            if decision == 1:
                # if matches, repeating unknown person
                pass
            # if face dosent match in unknown faces list
            else:
                # count 3 times
                un_counter += 1
                if un_counter == 3:
                    name = f"Unknown_User_{un_counter}"
                    unknown_enc_list.append(encodeFace)
                    markAttendance(name, img)
                    un_counter = 0

    #os.system('clear')
    clear_output(wait=True)
    imgR = cv2.resize(img, (540, 960))
    cv2.imshow('Recording Attendance', imgR)
    key = cv2.waitKey(1)
    if key == ord('e'):
        cap.release()
        cv2.destroyAllWindows()
        break    
