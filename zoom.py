import cv2
import pyautogui
import time
from draw_utils import draw_text_box

def handle_zoom_mode(img, lmList, fingers, state):
    """
    Handle zoom in/out functionality based on hand gestures.
    Zoom In: Thumb + Index + Pinky up
    Zoom Out: Thumb + Middle + Ring up
    """

    # Initialize zoom state variables
    if "zoomLevel" not in state:
        state["zoomLevel"] = 5  # Range 0–10
    if "zoom_cooldown" not in state:
        state["zoom_cooldown"] = time.time()
    if "zoom_fill" not in state:
        state["zoom_fill"] = int((state["zoomLevel"] / 10) * 250)

    current_time = time.time()
    cooldown_duration = 0.5  # Time between zoom events

    # Gesture logic
    fingers_up = fingers  # [Thumb, Index, Middle, Ring, Pinky]

    # Zoom In: [1, 1, 0, 0, 1] (Thumb, Index, Pinky up)
    if fingers_up == [1, 1, 0, 0, 1] and (current_time - state["zoom_cooldown"] > cooldown_duration):
        pyautogui.keyDown('ctrl')
        pyautogui.press('+')
        pyautogui.keyUp('ctrl')
        state["zoomLevel"] = min(state["zoomLevel"] + 1, 10)
        draw_text_box(img, "ZOOM IN", position='middle', text_color=(0, 255, 0), box_color=(0, 50, 0))
        state["zoom_cooldown"] = current_time

    # Zoom Out: [1, 0, 1, 1, 0] (Thumb, Middle, Ring up)
    elif fingers_up == [1, 0, 1, 1, 0] and (current_time - state["zoom_cooldown"] > cooldown_duration):
        pyautogui.keyDown('ctrl')
        pyautogui.press('-')
        pyautogui.keyUp('ctrl')
        state["zoomLevel"] = max(state["zoomLevel"] - 1, 0)
        draw_text_box(img, "ZOOM OUT", position='middle', text_color=(0, 0, 255), box_color=(50, 0, 0))
        state["zoom_cooldown"] = current_time

    # Show mode label
    draw_text_box(img, "ZOOM MODE", position='top')

    # Zoom bar parameters
    bar_x, bar_y = 570, 150
    bar_height = 250
    bar_width = 20

    # Calculate animated fill height
    target_fill = int((state["zoomLevel"] / 10) * bar_height)
    state["zoom_fill"] += (target_fill - state["zoom_fill"]) * 0.3
    current_fill = int(state["zoom_fill"])

    # Draw zoom bar
    cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), 3)
    cv2.rectangle(img, (bar_x, bar_y + bar_height - current_fill),
                  (bar_x + bar_width, bar_y + bar_height), (255, 255, 0), cv2.FILLED)

    # Show percentage
    zoom_percent = f'{state["zoomLevel"] * 10}%'
    cv2.putText(img, zoom_percent, (bar_x - 10, bar_y + bar_height + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4)  # Shadow
    cv2.putText(img, zoom_percent, (bar_x - 10, bar_y + bar_height + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
