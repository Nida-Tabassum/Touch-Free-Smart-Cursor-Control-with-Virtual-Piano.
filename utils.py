import cv2
import time
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Finger tip landmark IDs
tipIds = [4, 8, 12, 16, 20]

# ===================== Drawing Utility ===================== #
def draw_text_box(img, text, position='middle', 
                  text_color=(0, 255, 255), 
                  box_color=(50, 50, 50), 
                  text_scale=1.2, 
                  thickness=2,
                  padding=20):
    """Draw text with a background box for better visibility"""
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, text_scale, thickness)[0]

    if position == 'middle':
        text_x = (img.shape[1] - text_size[0]) // 2
        text_y = (img.shape[0] + text_size[1]) // 2
    elif position == 'top':
        text_x = (img.shape[1] - text_size[0]) // 2
        text_y = 50
    elif position == 'bottom':
        text_x = (img.shape[1] - text_size[0]) // 2
        text_y = img.shape[0] - 50
    else:
        text_x, text_y = 50, 50  # Default fallback

    # Draw background box
    cv2.rectangle(img,
                  (text_x - padding, text_y - text_size[1] - padding),
                  (text_x + text_size[0] + padding, text_y + padding),
                  box_color, -1)

    # Draw text
    cv2.putText(img, text, (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX, text_scale,
                text_color, thickness, cv2.LINE_AA)

# ===================== Gesture Utilities ===================== #
def get_finger_state(lmList):
    """Determine which fingers are up based on landmark positions"""
    fingers = []

    # Thumb (horizontal check)
    if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers (vertical check)
    for id in range(1, 5):
        if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

def set_mode(fingers, active, current_mode):
    """Determine control mode based on which fingers are up"""
    if fingers == [0, 0, 0, 0, 0] and active == 0:
        return 'N'
    elif fingers in [[0, 1, 0, 0, 0], [0, 1, 1, 0, 0]] and active == 0:
        return 'Scroll'
    elif fingers == [1, 1, 0, 0, 0] and active == 0:
        return 'Volume'
    elif fingers == [1, 1, 1, 1, 1] and active == 0:
        return 'Cursor'
    elif fingers == [1, 0, 0, 0, 1] and active == 0:
        return 'Zoom'
    return current_mode

# ===================== Audio Control ===================== #
def setup_audio_control():
    """Set up access to system volume control"""
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volRange = volume.GetVolumeRange()
    return volume, volRange

# ===================== FPS Display ===================== #
def display_fps(img, state):
    """Calculate and display FPS at the top-right with color based on performance"""
    curr_time = time.time()
    time_diff = curr_time - state.get("prev_time", 0.0001)
    fps = 0 if time_diff == 0 else 1 / time_diff
    state["prev_time"] = curr_time

    text = f'FPS: {int(fps)}'
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_PLAIN, 3, 3)[0]

    # Determine FPS color
    if fps > 30:
        color = (0, 255, 0)      # Green
    elif fps > 15:
        color = (0, 255, 255)    # Yellow
    else:
        color = (0, 0, 255)      # Red

    # Position at top-right
    x = img.shape[1] - text_size[0] - 30
    y1, y2 = 30, 90

    # Background box
    cv2.rectangle(img, (x - 10, y1), (x + text_size[0] + 10, y2), (50, 50, 50), -1)

    # FPS text
    cv2.putText(img, text, (x, 70), cv2.FONT_HERSHEY_PLAIN, 3, color, 3)

