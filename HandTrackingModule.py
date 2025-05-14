import cv2
import mediapipe as mp

class handDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = float(detectionCon)
        self.trackCon = float(trackCon)

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            model_complexity=1,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.results = None
        self.multiHandList = []

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        self.multiHandList = []

        if self.results.multi_hand_landmarks:
            for handIndex, handLms in enumerate(self.results.multi_hand_landmarks):
                hand_info = {}

                # Get label: "Left" or "Right"
                if self.results.multi_handedness:
                    label = self.results.multi_handedness[handIndex].classification[0].label
                    hand_info["type"] = label

                # Get landmark positions
                lmList = []
                h, w, _ = img.shape
                for id, lm in enumerate(handLms.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append((id, cx, cy))
                hand_info["lmList"] = lmList

                self.multiHandList.append(hand_info)

                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)

        return self.multiHandList, img

    def findPosition(self, img, handNo=0, draw=True):
        lmList = []

        if self.results and self.results.multi_hand_landmarks:
            try:
                myHand = self.results.multi_hand_landmarks[handNo]
            except IndexError:
                return lmList  # Avoid crash if hand index is invalid

            h, w, c = img.shape
            for id, lm in enumerate(myHand.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        return lmList

    def fingersUp(self, hand):
        """Return a list of 5 finger states (1 if finger is up, 0 if down)."""
        lmList = hand.get("lmList", [])
        if len(lmList) == 0:
            return []

        fingers = []

        # Thumb (compare x for left/right hand)
        if hand["type"] == "Right":
            fingers.append(1 if lmList[4][1] > lmList[3][1] else 0)
        else:
            fingers.append(1 if lmList[4][1] < lmList[3][1] else 0)

        # Fingers (index to pinky): check y position of tip vs pip
        tips = [8, 12, 16, 20]
        for tip in tips:
            fingers.append(1 if lmList[tip][2] < lmList[tip - 2][2] else 0)

        return fingers
