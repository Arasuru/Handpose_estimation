import pyautogui
import time
import pygetwindow as gw
import socket
import datetime

pyautogui.FAILSAFE = False
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

def bring_obs_to_front():
    windows = gw.getWindowsWithTitle("OBS")
    if windows:
        obs_window = windows[0]
        try:
            retries = 5
            while retries > 0:
                print(f"Window state - Minimized: {obs_window.isMinimized}, Active: {obs_window.isActive}")
                if obs_window.isMinimized:
                    obs_window.restore()
                obs_window.activate()
                time.sleep(0.5)
                if obs_window.isActive:
                    print("OBS window activated successfully")
                    return True
                else:
                    retries -= 1
                    print(f"Retrying... ({5 - retries} attempts left)")
            print("Window activation failed after multiple attempts")
            return False
        except Exception as e:
            print(f"Error activating OBS window: {e}")
            return False
    else:
        print("OBS window not found. Is OBS running?")
        return False


def start_recording():
    """Simulates pressing the 'Start Recording' hotkey in OBS."""
    if bring_obs_to_front():
        print(f"video recording started at {datetime.datetime.now().time()}")
        pyautogui.hotkey("ctrl", "r")
        print("Started recording")

def stop_recording():
    """Simulates pressing the 'Stop Recording' hotkey in OBS."""
    if bring_obs_to_front():
        print(f"video recording stopped at {datetime.datetime.now().time()}")
        pyautogui.hotkey("ctrl", "q")
        print("Stopped recording")

s = connect_to_server()
while(True):
    try:
        data = s.recv(1024)
        if data == b'START':
            start_recording()
        elif data == b'STOP':
            stop_recording()
            break
    except BlockingIOError:
        pass
    except Exception as e:
        print(f"caught error in server message {e}")
        break

