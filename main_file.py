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


def remove_employee_record():
    """
    Removes an employee record from the system.
    Prompts the user to confirm deletion and updates the employee database
    and the corresponding face encoding file.
    """
    global my_data, face_encoding_list, face_names, encoding_file_name
    
    emp_id = int(input("Enter the employee ID: "))
    record = my_data[my_data["Emp_Id"] == emp_id]
    
    if record.shape[0] > 0:
        print("\nPlease confirm the employee details:")
        print(record)
        conf_inp = input("\nAre you sure you want to remove this record? (Y/N): ")
        
        if conf_inp.lower() == "y":
            # Drop the employee row and save to the database
            my_data.drop(record.index.values, inplace=True)
            my_data.to_csv(emp_rec, columns=["First Name", "Last Name", "Emp_Id", "Gender"], index=False)
            
            # Find the index of the employee's face encoding
            idx = [i for i, ele in enumerate(face_names) if str(emp_id) in ele]
            face_encoding_list.pop(idx[0])
            face_names.pop(idx[0])
            
            # Save the updated pickle file
            with open(encoding_file_name, 'wb') as f:
                pickle.dump([face_names, face_encoding_list], f)
            print("\nSuccessfully removed employee record.")
        else:
            print("\nNot removing the employee record.")
    else:
        print("\nEmployee record not found.")


def append_new_employee(encoded, emp, img_name):
    """
    Appends a new employee record to the database and saves the corresponding face encoding.
    """
    global my_data, emp_rec
    
    my_data.loc[len(my_data)] = [emp["First"].capitalize(),
                                 emp["Last"].capitalize(),
                                 emp["EID"],
                                 emp["Gender"].capitalize()]
    my_data.to_csv(emp_rec, columns=["First Name", "Last Name", "Emp_Id", "Gender"], index=False)
    
    dump_new_pickle(encoded, img_name)


def dump_new_pickle(new_encode, classname):
    """
    Adds a new face encoding to the list and saves it in a pickle file.
    """
    global face_encoding_list, face_names, encoding_file_name
    
    face_encoding_list.append(new_encode)
    face_names.append(classname)
    
    with open(encoding_file_name, 'wb') as f:
        pickle.dump([face_names, face_encoding_list], f)


def find_encoding(img):
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


def grab_new_employee():
    """
    Prompts the user to input employee details, captures an image, and saves the face encoding.
    """
    global path, my_data
    
    while True:
        print("Fill in the employee details.")
        emp_name = {
            "First": input("First Name: "),
            "Last": input("Last Name: ")
        }
        
        while True:
            try:
                emp_name["EID"] = int(input("Employee ID: "))
                break
            except ValueError:
                print("Please enter a valid Employee ID.")
        
        # Ensure unique Employee ID
        if emp_name["EID"] in set(my_data["Emp_Id"].values):
            print("Employee record already exists. Please choose a new Employee ID.")
            continue
        else:
            emp_name["Gender"] = input("Gender: ")
            break
    
    # Construct image filename and capture the face image
    img_name = f"{emp_name['First'].lower()}_{emp_name['Last'].lower()}_{emp_name['EID']}"
    
    webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    sleep(2)  # Wait for camera initialization
    
    while True:
        try:
            ret, frame = webcam.read()
            cv2.imshow("Capturing", frame)
            key = cv2.waitKey(1)
            
            if key == ord('s'):
                encoded = find_encoding(frame)
                if encoded:
                    cv2.imwrite(os.path.join(path, f"{img_name}.jpg"), frame)
                    append_new_employee(encoded, emp_name, img_name)
                    webcam.release()
                    print("Image saved and employee added.")
                    sleep(1.5)
                    break
            elif key == ord('e'):
                webcam.release()
                cv2.destroyAllWindows()
                break
        except KeyboardInterrupt:
            print("Turning off camera.")
            webcam.release()
            cv2.destroyAllWindows()
            break


def load_attendance():
    """
    Loads the current month's attendance database or creates a new one if it doesn't exist.
    """
    # Generate the correct file name based on the current month
    month_name = datetime.now().strftime("%b-%Y")
    attendance_file_name = f"Attendance_Database/{month_name}-Attendance.csv"
    img_db_name = f"Attendance_Database/Captured_Images/{month_name}-Images"
    
    # Check if the file exists
    if not os.path.exists(attendance_file_name):
        # Create new attendance file
        df = pd.DataFrame(columns=["Emp_Id", "First Name", "Last Name", "Date", "Time"])
        os.makedirs(img_db_name, exist_ok=True)
        return df, attendance_file_name
    
    # If the file exists, load it
    df = pd.read_csv(attendance_file_name, parse_dates=[3, 4], header=0)
    return df, attendance_file_name


def save_attendance(values):
    """
    Saves the attendance record for an employee to the current month's attendance file.
    """
    global att_file, att_file_name
    
    # Append the new attendance record
    att_file.loc[len(att_file)] = values
    att_file.to_csv(att_file_name, columns=["Emp_Id", "First Name", "Last Name", "Date", "Time"], index=False)


def save_captured_image(img, img_db_name, name, dt_string, time_string):
    """
    Saves the captured image in the appropriate directory.
    """
    img_filename = f"{name}_{dt_string.replace('/', '-')}_{time_string.replace(':', '-')}.jpg"
    cv2.imwrite(os.path.join(img_db_name, img_filename), img)


def mark_attendance(name, img):
    """
    Marks attendance for a recognized employee.
    """
    global att_file, att_file_name
    
    emp_details = [ele.capitalize() for ele in name.split("_")]
    current_time = datetime.now()
    time_string = current_time.strftime('%H:%M:%S')
    dt_string = current_time.strftime("%b/%d/%Y")
    
    # Check if today's attendance has already been recorded
    todays_attendance = att_file[att_file["Date"] == dt_string]
    
    # Save the captured image
    img_db_name = f"Attendance_Database/Captured_Images/{current_time.strftime('%b-%Y')}-Images"
    
    if sum(todays_attendance["Emp_Id"] == int(emp_details[2])) == 0:
        values_to_add = [int(emp_details[2]), emp_details[0], emp_details[1], dt_string, time_string]
        save_attendance(values_to_add)
        print(f"Attendance recorded for {name}.")
        save_captured_image(img, img_db_name, name, dt_string, time_string)
    else:
        print(f"{name} has already marked attendance today.")


# Main Execution
encoding_file_name = 'Employee_Database/Face_Encodings.pkl'

# Load face encodings and names
with open(encoding_file_name, 'rb') as f:
    face_names, face_encoding_list = pickle.load(f)

# Load Employee Database
emp_rec = 'Employee_Database/EmployeeRecords.csv'
my_data = pd.read_csv(emp_rec, names=["First Name", "Last Name", "Emp_Id", "Gender"], header=0)

# Path for the main images database
path = 'Image_Database'

# Acceptable image formats
formats = {"jpeg", "jpg", "png", "tif", "tiff", "gif"}

# Optionally remove or add employee records
cinp = input("Do you want to remove any employee record? (Yes/No): ")
if cinp.lower() == "yes":
    remove_employee_record()

cinp = input("Do you want to add a new employee to the record? (Yes/No): ")
if cinp.lower() == "yes":
    grab_new_employee()

# Load attendance data
att_file, att_file_name = load_attendance()

# Initialize webcam
cap = cv2.VideoCapture("Trial_4.mp4")  # Using a video file for testing (replace with camera source)
counter = 0
un_counter = 0
found_emp = []
unknown_enc_list = []

while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture image from video.")
        break

    img_resized = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)

    faces_in_frame = face_recognition.face_locations(img_rgb)
    encodes_in_frame = face_recognition.face_encodings(img_rgb, faces_in_frame)

    for encode_face, face_loc in zip(encodes_in_frame, faces_in_frame):
        matches = face_recognition.compare_faces(face_encoding_list, encode_face, tolerance=0.5)
        face_distances = face_recognition.face_distance(face_encoding_list, encode_face)
        match_index = np.argmin(face_distances)

        # If a match is found with a known face
        if matches[match_index]:
            name = face_names[match_index].upper()
            y1, x2, y2, x1 = face_loc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            counter += 1
            found_emp.append(name)

            # Mark attendance after 3 detections of the same person
            if counter == 3 and len(set(found_emp)) == 1:
                mark_attendance(name, img)
                counter = 0
                found_emp = []

            elif counter > 3:
                counter = 0
                found_emp = []

        else:
            # If the face doesn't match any known faces
            name = "Unknown_User"
            y1, x2, y2, x1 = face_loc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            if len(unknown_enc_list) > 0:
                # Check if the unknown face matches any previously stored unknown faces
                matches_unknown = face_recognition.compare_faces(unknown_enc_list, encode_face, tolerance=0.6)
                face_distances_unknown = face_recognition.face_distance(unknown_enc_list, encode_face)
                match_index_unknown = np.argmin(face_distances_unknown)
                
                if matches_unknown[match_index_unknown]:
                    decision = 1
                else:
                    decision = 0
            else:
                decision = 0

            if decision == 1:
                pass  # Repeating unknown person, do nothing
            else:
                un_counter += 1
                if un_counter == 3:
                    name = f"Unknown_User_{un_counter}"
                    unknown_enc_list.append(encode_face)
                    mark_attendance(name, img)
                    un_counter = 0

    # Display the resulting image
    img_resized_display = cv2.resize(img, (540, 960))
    cv2.imshow('Recording Attendance', img_resized_display)

    key = cv2.waitKey(1)
    if key == ord('e'):
        cap.release()
        cv2.destroyAllWindows()
        break

