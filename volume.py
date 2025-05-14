import cv2
import math
import numpy as np
from draw_utils import draw_text_box

def handle_volume_mode(img, lmList, fingers, state):
    x1, y1 = lmList[4][1], lmList[4][2]   # Thumb tip
    x2, y2 = lmList[8][1], lmList[8][2]   # Index finger tip

    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

    # Calculate distance between thumb and index finger
    length = math.hypot(x2 - x1, y2 - y1)

    # Convert length to volume
    vol = np.interp(length, [30, 200], [state["minVol"], state["maxVol"]])
    volBar = np.interp(length, [30, 200], [400, 150])
    volPer = np.interp(length, [30, 200], [0, 100])

    state["volume"].SetMasterVolumeLevel(vol, None)
    state["volBar"] = volBar
    state["volPer"] = volPer

    # Draw volume bar
    cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 430),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

    # Show volume up/down message
    if volPer > 60:
        draw_text_box(img, "VOLUME UP", position='top', text_color=(0, 255, 0), box_color=(0, 50, 0))
    elif volPer < 40:
        draw_text_box(img, "VOLUME DOWN", position='top', text_color=(0, 0, 255), box_color=(50, 0, 0))
    else:
        draw_text_box(img, "VOLUME MODE", position='top')

    # Exit if all fingers down
    if fingers == [0, 0, 0, 0, 0]:
        state["active"] = 0
        state["mode"] = 'N'
