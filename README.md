
**FacialRecognitionAttendance**

**_Facial Recognition-Based Attendance System_**

This repository uses facial recognition technology to automate the process of employee attendance using video footage. The system can recognize faces, match them with employee records, and mark attendance accordingly.

**Setup Instructions**
Follow these steps to get started with the system:

_1. Prepare Employee Photos_
Collect all employee photos and store them in the 'Image_Database' folder.
Each photo should correspond to the respective employee.
After adding the photos, run the first_time_initialization.py file.
This script will:
Generate facial encodings for all employees.
Store these encodings in the 'Employee_Database/Face_Encodings.pkl' file for later use.

_2. Run Attendance Recording via Video_
If you have a pre-recorded video of employees entering the office/building, you can use the main_file.py to process it.
In main_file.py, update the video file source (currently set to 'Trial_4.mp4') to your desired video file.
The script will process the video and match faces in the frames to the existing employee records.
If a new face is detected that isn’t in the employee database, the script will prompt you to add the new employee to the system.

_3. Use Live Video Source for Attendance_
If you want to use a live video feed (e.g., webcam), use the tkinter.py file.
Open the script and change the video source number to your desired source (typically 0 for a webcam).
This script provides a graphical interface where you can monitor the live video feed and capture attendance in real time.

_Example Video_
For a demonstration of how the system works, please refer to the following example video:

Example Video on Google Drive: https://drive.google.com/file/d/1e9hn1NGHymqdNjLHnBfNac8d61AipdRL/view?usp=sharing

_Additional Notes_
The facial recognition system uses the face_recognition library, which leverages deep learning models to detect and encode faces in images/videos.
The system assumes that employees’ faces are clear and visible in the video frames for accurate recognition.
For the first-time initialization, you’ll need to have employee images ready in the 'Image_Database' folder to generate the facial encodings.
Feel free to ask if you need further assistance with setup or usage!

