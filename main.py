from pygame import mixer
import cv2
import mediapipe as mp
import os

os.system("echo Created by Mithun!")

class CameraError(Exception):
    pass

mixer.init()

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

MUSIC_FOLDER = "songs"
playlist = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith((".mp3", ".wav", ".ogg"))]
playlist.sort()
current_index = 0
playing = False

def play_song(index):
    global playing
    song_path = os.path.join(MUSIC_FOLDER, playlist[index])
    mixer.music.load(song_path)
    mixer.music.play()
    playing = True
    return playlist[index]

def stop_song():
    global playing
    mixer.music.stop()
    playing = False

def next_song():
    global current_index
    current_index = (current_index + 1) % len(playlist)
    return play_song(current_index)

def detect_gesture(results, frame):
    """Detects the person's hand and draws land marks on the hand

    Args:
        results (): the hand
        frame (_type_): frame

    Returns:
        str, None: what the hand is
    """
    
    if results.multi_hand_landmarks:
        for lm in results.multi_hand_landmarks:
            # draw landmarks
            mp_drawing.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)

            # fingertip landmarks
            tip_ids = [8, 12, 16, 20]  # index, middle, ring, pinky
            fingers = [lm[tip].y < lm[tip - 2].y for tip in tip_ids]  # True if extended

            # detect gestures
            if all(not f for f in fingers):
                return "fist"
            elif all(f for f in fingers):
                return "open"
            else:
                dx = abs(lm[4].x - lm[8].x)
                dy = abs(lm[4].y - lm[8].y)
                if dx < 0.05 and dy < 0.05:
                    return "pinch"

    return None


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise CameraError("Failed to open camera")

while True:
    ret, frame = cap.read()
    if not ret:
        raise CameraError("Failed to access the camera!")
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.BGR2RGB)
    results = hands.process(rgb_frame)

    gesture = detect_gesture()

    if gesture == "fist" and playing:
        stop_song()
    elif gesture == "open" and not playing:
        play_song(current_index)
    elif gesture == "pinch":
        next_song()
    
    print(gesture)
    
    text = playlist[current_index] if playing else "Stopped"
    cv2.putText(frame, text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 140, 255), 2)

    cv2.imshow("Music Control using Gestures", frame)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destoryAllWindows()
mixer.quit()
exit(0)
    