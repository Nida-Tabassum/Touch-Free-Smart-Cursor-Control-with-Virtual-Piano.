import cv2 
import time
import numpy as np
import pyautogui
import autopy
import pygame.midi
import threading

from HandTrackingModule import handDetector
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from piano_overlay import draw_piano

from scroll import handle_scroll_mode
from volume import handle_volume_mode
from zoom import handle_zoom_mode
from cursor import handle_cursor_mode
from utils import draw_text_box, get_finger_state, set_mode, setup_audio_control, display_fps

# Camera setup
wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

# Detector and audio setup
detector = handDetector(maxHands=2, detectionCon=0.85, trackCon=0.8)
volume, volRange = setup_audio_control()
minVol, maxVol = volRange[0], volRange[1]
pyautogui.FAILSAFE = False

# Piano MIDI setup
pygame.midi.init()
player = pygame.midi.Output(0)
player.set_instrument(0)  # Acoustic Grand Piano

# Piano chords for each finger
chords = {
    "left": {
        "thumb": [62, 66, 69],
        "index": [64, 67, 71],
        "middle": [66, 69, 73],
        "ring": [67, 71, 74],
        "pinky": [69, 73, 76]
    },
    "right": {
        "thumb": [72, 76, 79],
        "index": [74, 77, 81],
        "middle": [76, 79, 83],
        "ring": [77, 81, 84],
        "pinky": [79, 83, 86]
    }
}
prev_states = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}

def play_chord(notes):
    for note in notes:
        player.note_on(note, 127)

def stop_chord_after_delay(notes):
    time.sleep(2.0)
    for note in notes:
        player.note_off(note, 127)

# System state
state = {
    "active": 0,
    "mode": 'N',
    "volBar": 400,
    "volPer": 0,
    "click_cooldown": 0,
    "volume": volume,
    "minVol": minVol,
    "maxVol": maxVol,
    "prev_time": time.time()
}
piano_mode = False

# =================== MAIN LOOP ===================
while True:
    success, img = cap.read()
    if not success:
        print("Error: Failed to capture image")
        continue

    hands, img = detector.findHands(img)  # now returns both hands and img
    lmList = detector.findPosition(img, draw=False)

    # Toggle modes with keypress
    key = cv2.waitKey(1) & 0xFF
    if key == ord('p'):
        piano_mode = not piano_mode
        print(f"Piano Mode: {'ON' if piano_mode else 'OFF'}")
        time.sleep(0.3)
    if key == ord('q'):
        break

    # Active notes list for piano overlay
    active_notes = []

    # 🎹 PIANO MODE
    if piano_mode and hands:
        for hand in hands:
            hand_type = "left" if hand["type"] == "Left" else "right"
            fingers = detector.fingersUp(hand)
            finger_names = ["thumb", "index", "middle", "ring", "pinky"]

            for i, finger in enumerate(finger_names):
                if finger in chords[hand_type]:
                    notes = chords[hand_type][finger]
                    if fingers[i] == 1 and prev_states[hand_type][finger] == 0:
                        play_chord(notes)
                        active_notes.extend(notes)
                    elif fingers[i] == 0 and prev_states[hand_type][finger] == 1:
                        threading.Thread(target=stop_chord_after_delay,
                                         args=(notes,), daemon=True).start()
                    if fingers[i] == 1:
                        active_notes.extend(notes)
                    prev_states[hand_type][finger] = fingers[i]
    elif not hands:
        for hand in chords:
            for finger in chords[hand]:
                threading.Thread(target=stop_chord_after_delay,
                                 args=(chords[hand][finger],), daemon=True).start()
        prev_states = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}

    # 🖱️ VIRTUAL MOUSE MODE
    if not piano_mode and len(lmList) != 0:
        fingers = get_finger_state(lmList)
        state["mode"] = set_mode(fingers, state["active"], state["mode"])

        if state["mode"] == 'Scroll':
            handle_scroll_mode(img, fingers, state)
        elif state["mode"] == 'Volume':
            handle_volume_mode(img, lmList, fingers, state)
        elif state["mode"] == 'Cursor':
            handle_cursor_mode(img, lmList, fingers, state)
        elif state["mode"] == 'Zoom':
            handle_zoom_mode(img, lmList, fingers, state)
    elif not piano_mode:
        draw_text_box(img, "NO HAND DETECTED", position='middle',
                      text_color=(0, 0, 255), box_color=(50, 50, 50))

    # 🎨 Draw piano overlay if in piano mode
    if piano_mode:
        img = draw_piano(img, active_notes)

    # Show FPS and window
    display_fps(img, state)
    cv2.imshow('Hand Gesture Control', img)

# Cleanup
cap.release()
cv2.destroyAllWindows()
pygame.midi.quit()
