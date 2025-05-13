import mediapipe as mp
import cv2
import numpy as np
import uuid
import os
import csv
import socket
import datetime
import time

#setting up server connection function
def connect_to_server(host='localhost', port=33333):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        s.setblocking(False)  # Make socket non-blocking
        print("Connected to server")
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        return None
    return s

#setting up mediapipe objects
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

#variables for recording video
recording = False
out = None
all_landmarks = []

#setting-up webcam and mediapipe overlay and connection to the server
cap = cv2.VideoCapture(2)

num_frames = 30
start_time = time.time()
for i in range(num_frames):
    ret, frame = cap.read()
    if not ret:
        print("Error reading frame during FPS calculation")
        exit()
end_time = time.time()
elapsed_time = end_time - start_time
fps = int(num_frames / elapsed_time)
print(f"Calculated FPS: {fps}")

s = connect_to_server()

with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5,max_num_hands=1) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  #cv2 reads BGR format, mediapipe uses RGB format, so convert
        image.flags.writeable =False

        frame_width, frame_height = frame.shape[1], frame.shape[0]
        landmarks_3d = [] #to store the xyz coordinates of each joint
        #mediapipe processing the image
        results = hands.process(image)

        # Create a blank frame with the same dimensions as the video frame
        blank_frame = np.zeros_like(frame)
        
        image.flags.writeable=True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks: #gives the coordinates of hand if a hand is detected
            for num, hand in enumerate(results.multi_hand_landmarks):
                mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS,  #use image instead of blank_frame to save actual video
                                         mp_drawing.DrawingSpec(color=(255, 0, 21), thickness=2, circle_radius=2), #for joints and dots
                                         mp_drawing.DrawingSpec(color=(16, 255, 0), thickness=2, circle_radius=2)) #for connections and lines
      
                
                #this is to store the x,y,z co-ordinates
                for lm in hand.landmark:
                    x = int(lm.x * frame_width)
                    y = int(lm.y * frame_height)
                    z = lm.z  # Depth can be scaled if needed
                    landmarks_3d.append((x, y, z))

                if recording and landmarks_3d:
                    all_landmarks.append(landmarks_3d)  # Append current frame landmarks
                    
        cv2.imshow('Hand Tracking', image) #use image instead of blank_frame to save actual video
        cv2.pollKey()

        try:  # Toggle recording on 'r' key press
            data = s.recv(1024)
            if data == b'START' and not recording:
                # Start recording
                print(f"start signal received at {datetime.datetime.now().time()}")
                recording = True
                filename = f"{uuid.uuid4()}.mp4"
                frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                #fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(os.path.join("../mediapipe videos",filename), fourcc, fps, (frame_width, frame_height))
                print(f"Recording started: {filename}")
            elif data == b'STOP' and recording:
                # Stop recording
                recording = False
                datafile = filename.replace(".mp4", ".csv")
                with open(os.path.join("../coordinates data", datafile), mode='w', newline='') as f:
                    csv_writer = csv.writer(f)
                    header = [f'joint_{i}_{axis}' for i in range(21) for axis in ['x', 'y', 'z']]
                    csv_writer.writerow(header)  # Write CSV header
                    for frame_landmarks in all_landmarks:
                        row = [value for joint in frame_landmarks for value in joint]
                        csv_writer.writerow(row)
                all_landmarks = []       #empty the current data for recording 
                out.release()
                out = None
                print("Recording stopped")
                break
        except BlockingIOError:
            pass

        if recording and out is not None:
            out.write(image) #use image instead of blank_frame to save actual video

cap.release()
if out is not None:
    out.release()
cv2.destroyAllWindows()