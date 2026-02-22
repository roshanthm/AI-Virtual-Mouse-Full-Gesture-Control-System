import cv2
import time
import math
import numpy as np
import sys
import threading

try:
    import mediapipe as mp
except:
    print("Install mediapipe: pip install mediapipe")
    raise

try:
    import pyautogui
except:
    print("Install pyautogui: pip install pyautogui")
    raise

try:
    import pyttsx3
    TTS_AVAILABLE = True
except:
    TTS_AVAILABLE = False

SCREEN_W, SCREEN_H = pyautogui.size()
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

SMOOTHING = 7
CLICK_DISTANCE = 0.04
DOUBLE_CLICK_TIME = 0.35
SCROLL_MULT = 3.0
DRAG_THRESHOLD = 0.02

prev_x, prev_y = 0, 0
smooth_x, smooth_y = 0, 0
prev_time = 0
last_click_time = 0
dragging = False
mouse_enabled = True
overlay = True

if TTS_AVAILABLE:
    tts_engine = pyttsx3.init()
else:
    tts_engine = None

def speak(text):
    if tts_engine:
        def _speak():
            try:
                tts_engine.say(text)
                tts_engine.runAndWait()
            except:
                pass
        threading.Thread(target=_speak, daemon=True).start()

def normalized_distance(lm1, lm2, w, h):
    x1, y1 = lm1[0] / w, lm1[1] / h
    x2, y2 = lm2[0] / w, lm2[1] / h
    return math.hypot(x2 - x1, y2 - y1)

def main(camera_index=0):
    global prev_x, prev_y, smooth_x, smooth_y, prev_time, last_click_time, dragging, mouse_enabled, overlay

    cap = cv2.VideoCapture(camera_index)
    cap.set(3, 640)
    cap.set(4, 480)
    cam_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cam_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    hands = mp_hands.Hands(max_num_hands=1,
                           min_detection_confidence=0.6,
                           min_tracking_confidence=0.5)

    prev_frame_time = 0
    fps = 0
    last_pinch_time = 0
    pinch_down = False
    last_scroll_y = None

    if TTS_AVAILABLE:
        speak("Gesture control activated")

    while True:
        success, img = cap.read()
        if not success:
            break

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = hands.process(img_rgb)

        gesture_text = "No hand"
        action_text = "Idle"

        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]
            lm = []
            for lm_obj in hand_landmarks.landmark:
                lm_x = int(lm_obj.x * cam_w)
                lm_y = int(lm_obj.y * cam_h)
                lm.append((lm_x, lm_y))

            thumb_tip = lm[4]
            index_tip = lm[8]
            middle_tip = lm[12]
            ring_tip = lm[16]
            pinky_tip = lm[20]

            if overlay:
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            pinch_dist = normalized_distance(thumb_tip, index_tip, cam_w, cam_h)
            two_finger_dist = normalized_distance(index_tip, middle_tip, cam_w, cam_h)
            cx, cy = index_tip

            norm_x = cx / cam_w
            norm_y = cy / cam_h

            target_x = SCREEN_W * norm_x
            target_y = SCREEN_H * norm_y

            smooth_x = prev_x + (target_x - prev_x) / SMOOTHING
            smooth_y = prev_y + (target_y - prev_y) / SMOOTHING

            prev_x, prev_y = smooth_x, smooth_y

            if mouse_enabled:
                try:
                    pyautogui.moveTo(smooth_x, smooth_y, duration=0)
                except:
                    pass

            now = time.time()
            is_pinch = pinch_dist < CLICK_DISTANCE
            is_two_finger = two_finger_dist < CLICK_DISTANCE * 1.1

            if is_pinch and not pinch_down:
                pinch_down = True
                if now - last_pinch_time < DOUBLE_CLICK_TIME:
                    try:
                        pyautogui.doubleClick()
                        action_text = "Double Click"
                        speak("Double click") if TTS_AVAILABLE else None
                    except:
                        pass
                    last_pinch_time = 0
                else:
                    last_pinch_time = now
                    try:
                        pyautogui.mouseDown()
                        dragging = True
                        action_text = "Drag Start"
                        speak("Drag") if TTS_AVAILABLE else None
                    except:
                        pass

            if not is_pinch and pinch_down:
                pinch_down = False
                now2 = time.time()
                if dragging:
                    try:
                        pyautogui.mouseUp()
                        dragging = False
                        action_text = "Drag End"
                    except:
                        pass
                else:
                    if now2 - last_pinch_time < 0.35:
                        try:
                            pyautogui.click()
                            action_text = "Click"
                            speak("Click") if TTS_AVAILABLE else None
                        except:
                            pass
                last_pinch_time = now2

            if is_two_finger:
                if now - last_click_time > 0.7:
                    try:
                        pyautogui.click(button='right')
                        action_text = "Right Click"
                        last_click_time = now
                        speak("Right click") if TTS_AVAILABLE else None
                    except:
                        pass

            index_mid_dist = normalized_distance(index_tip, middle_tip, cam_w, cam_h)
            fingers_open = index_mid_dist > 0.12

            if fingers_open:
                if last_scroll_y is None:
                    last_scroll_y = smooth_y
                else:
                    dy = last_scroll_y - smooth_y
                    if abs(dy) > 10:
                        try:
                            scroll_amount = int(np.sign(dy) * min(10, abs(dy) / 10 * SCROLL_MULT))
                            pyautogui.scroll(scroll_amount)
                            action_text = f"Scroll {scroll_amount}"
                            last_scroll_y = smooth_y
                        except:
                            pass
            else:
                last_scroll_y = None

            gesture_text = f"Pinch:{is_pinch} TwoPinch:{is_two_finger}"

        curr_time = time.time()
        fps = 1 / (curr_time - prev_frame_time) if (curr_time - prev_frame_time) > 0 else 0
        prev_frame_time = curr_time

        if overlay:
            cv2.rectangle(img, (0, 0), (300, 70), (0, 0, 0), -1)
            cv2.putText(img, f"Mode: {'ON' if mouse_enabled else 'OFF'} (m)", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(img, f"Action: {action_text}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            cv2.putText(img, f"FPS: {int(fps)}", (200, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(img, f"{gesture_text}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

        cv2.imshow("AI Virtual Mouse - Press 'q' or ESC to quit", img)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == 27:
            break
        elif key == ord('m'):
            mouse_enabled = not mouse_enabled
            speak("Mouse off" if not mouse_enabled else "Mouse on") if TTS_AVAILABLE else None
        elif key == ord('v'):
            overlay = not overlay

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
