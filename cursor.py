import numpy as np
import autopy
import cv2
import time
from draw_utils import draw_text_box

def handle_cursor_mode(img, lmList, fingers, state):
    # Init
    if "click_cooldown" not in state:
        state["click_cooldown"] = time.time()
    if "wScr" not in state or "hScr" not in state:
        state["wScr"], state["hScr"] = autopy.screen.size()

    wScr, hScr = state["wScr"], state["hScr"]

    # Cursor movement
    x1, y1 = lmList[8][1], lmList[8][2]  # Index fingertip
    x3 = np.interp(x1, (100, 540), (0, wScr))
    y3 = np.interp(y1, (100, 380), (0, hScr))
    x3 = max(0, min(x3, wScr - 1))
    y3 = max(0, min(y3, hScr - 1))

    autopy.mouse.move(x3, y3)
    draw_text_box(img, "CURSOR MODE", position='top')

    # Cooldown check
    cooldown_time = 0.5  # seconds
    current_time = time.time()

        # Handle clicking
    if state["click_cooldown"] > 0:
        state["click_cooldown"] -= 1

    # Left Click: Index + Pinky Up
    if fingers == [0, 1, 0, 0, 1] and state["click_cooldown"] == 0:
        autopy.mouse.click()
        draw_text_box(img, "LEFT CLICK", position='middle', text_color=(0, 255, 0), box_color=(0, 100, 0))
        state["click_cooldown"] = 10

    # Right Click: Index + Middle + Pinky Up
    elif fingers == [0, 1, 1, 0, 1] and state["click_cooldown"] == 0:
        autopy.mouse.click(autopy.mouse.Button.RIGHT)
        draw_text_box(img, "RIGHT CLICK", position='middle', text_color=(0, 0, 255), box_color=(100, 0, 0))
        state["click_cooldown"] = 10


    # Exit gesture: Only thumb up
    if fingers == [1, 0, 0, 0, 0]:
        state["mode"] = 'N'
