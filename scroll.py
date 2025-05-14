import pyautogui
import cv2
from draw_utils import draw_text_box

def handle_scroll_mode(img, fingers, state):
    SCROLL_SPEED = 100

    if fingers == [0, 1, 0, 0, 0]:
        draw_text_box(
            img, 
            "SCROLL UP", 
            position='middle', 
            text_color=(0, 255, 0), 
            box_color=(0, 0, 100)
        )
        pyautogui.scroll(SCROLL_SPEED)

    elif fingers == [0, 1, 1, 0, 0]:
        draw_text_box(
            img, 
            "SCROLL DOWN", 
            position='middle', 
            text_color=(0, 0, 255), 
            box_color=(100, 0, 0)
        )
        pyautogui.scroll(-SCROLL_SPEED)

    elif fingers == [0, 0, 0, 0, 0]:
        state["active"] = 0
        state["mode"] = 'N'

    else:
        draw_text_box(img, "SCROLL MODE", position='top')
