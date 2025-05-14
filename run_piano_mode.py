import time
import cv2
import pygame.midi
import threading
from HandTrackingModule import handDetector

def run_piano_mode():
    # 🎹 Initialize Pygame MIDI
    pygame.midi.init()
    player = pygame.midi.Output(0)
    player.set_instrument(0)  # Acoustic Grand Piano

    # 🖐️ Initialize Hand Detector
    cap = cv2.VideoCapture(0)
    detector = handDetector(detectionCon=0.8)

    # 🎼 Chord Mapping
    chords = {
        "left": {
            "thumb": [62, 66, 69],
            "index": [64, 67, 71],
            "middle": [66, 69, 73],
            "ring": [67, 71, 74],
            "pinky": [69, 73, 76]
        },
        "right": {
            "thumb": [62, 66, 69],
            "index": [64, 67, 71],
            "middle": [66, 69, 73],
            "ring": [67, 71, 74],
            "pinky": [69, 73, 76]
        }
    }

    # 🎵 Sustain Management
    prev_states = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}

    def play_chord(notes):
        for note in notes:
            player.note_on(note, 127)

    def stop_chord_after_delay(notes):
        time.sleep(2.0)  # Sustain time
        for note in notes:
            player.note_off(note, 127)

    # 🎬 Main loop
    while True:
        success, img = cap.read()
        if not success:
            continue

        hands, img = detector.findHands(img, draw=True)  # Returns both image and hand list

        if hands:
            for hand in hands:
                hand_type = "left" if hand["type"] == "Left" else "right"
                fingers = detector.fingersUp(hand)
                finger_names = ["thumb", "index", "middle", "ring", "pinky"]

                for i, finger in enumerate(finger_names):
                    if finger in chords[hand_type]:
                        if fingers[i] == 1 and prev_states[hand_type][finger] == 0:
                            play_chord(chords[hand_type][finger])
                        elif fingers[i] == 0 and prev_states[hand_type][finger] == 1:
                            threading.Thread(target=stop_chord_after_delay,
                                             args=(chords[hand_type][finger],),
                                             daemon=True).start()
                        prev_states[hand_type][finger] = fingers[i]
        else:
            # No hands detected – stop all chords
            for hand in chords:
                for finger in chords[hand]:
                    threading.Thread(target=stop_chord_after_delay,
                                     args=(chords[hand][finger],), daemon=True).start()
            prev_states = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}

        cv2.imshow("🎹 Hand Piano Mode", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    pygame.midi.quit()
