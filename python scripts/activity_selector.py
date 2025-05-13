from datetime import datetime
import random
import socket
import os
import uuid
import csv


gestures = ["thumbs up", "peace", "ok sign", "open palm", "pointing finger"] * 3
activities = ["pouring water", "writing", "moving an object", "stacking blocks", "using controller"] 

activity_order = []
timestamps = []
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


def choose_activity():
    choice = "None"
    starttime = datetime.now().timestamp()
    while activities or gestures:  # Loop only while there are activities or gestures
        input_value = input()  # Check for any input
        non_empty_lists = [lst for lst in [activities, gestures] if lst]
        if non_empty_lists:
            cat = random.choice(non_empty_lists)
            choice = random.choice(cat)
            cat.remove(choice)
            curr_time = datetime.now().timestamp()
            timestamp = curr_time - starttime
            print(f"selected activity: {choice} at timestamp:{timestamp:.2f}")
            activity_order.append(choice)
            timestamps.append(timestamp)

    print("all activities are done")
    
        
def save_activities():
    datafile = f"{uuid.uuid4()}.csv"
    with open(os.path.join("../activity_timestamps", datafile), mode='w', newline='') as f:
        csv_writer = csv.writer(f)
        header = ["Activity", "Timestamp"]
        csv_writer.writerow(header)  # Write CSV header
        for i in range(len(timestamps)):
            row = [activity_order[i], timestamps[i]]
            csv_writer.writerow(row)
    print(f'file saved under name {datafile}')


s = connect_to_server()
while(True):
    try:
        data = s.recv(1024)
        if data == b'START':
            choose_activity()
        elif data == b'STOP':
            save_activities()
            break
    except BlockingIOError:
        pass
    except Exception as e:
        print(f"caught error in server message {e}")
        break