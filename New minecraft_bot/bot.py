import cv2
import numpy as np
from grabscreen import grab_screen
import keys as k
import time
import random
import keyboard

keys = k.Keys()

#tuning knobs
EDGE_THRESHOLD = 500000      #edge pixels count
STUCK_MSE_THRESHOLD = 15      # not moving
STUCK_FRAMES_FOR_JUMP = 6     # consecutive stuck frames before trying a jump
STUCK_FRAMES_FOR_TURN = 12     # consecutive stuck frames before giving up and turning
LOOP_DELAY = 0.1

state = "WALK"
stuck_counter = 0
walking = False  # tracks whether W is currently held, so we don't spam key presses


def get_roi(screen):
    h, w = screen.shape[:2]
    #return screen[int(h * 0.40):int(h * 0.90), int(w * 0.30):int(w * 0.70)]
    return screen[int(h * 0.30):int(h * 0.80), int(w * 0.30):int(w * 0.70)]

def obstacle_amount(roi_gray):
    edges = cv2.Canny(roi_gray, 80, 150)
    return np.sum(edges)


def start_walk():
    global walking #global = not in any function of class
    if not walking:
        keys.directKey("W")
        walking = True


def stop_walk():
    global walking
    if walking:
        keys.directKey("W", keys.key_release)
        walking = False


def jump():
    keys.directKey("SPACE")
    time.sleep(0.05)
    keys.directKey("SPACE", keys.key_release)


def turn():
    angle = random.choice([-500, -200, 200, 500])
    keys.directMouse(angle, 0)
    time.sleep(0.2)


#main 
time.sleep(3)
start_walk()

prev_roi_gray = None

while True:
    screen = grab_screen()
    roi = get_roi(screen)

    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    roi_gray_small = cv2.resize(roi_gray, (64, 64))

    edge_score = obstacle_amount(roi_gray)

    if prev_roi_gray is None:
        prev_roi_gray = roi_gray_small
        time.sleep(LOOP_DELAY)
        continue

    diff = roi_gray_small.astype(np.float32) - prev_roi_gray.astype(np.float32)
    mse_v = float(np.mean(diff ** 2))

    print(f"state={state} edge={edge_score} mse={mse_v:.1f} stuck_count={stuck_counter}")

    is_stuck = mse_v < STUCK_MSE_THRESHOLD
    obstacle_ahead = edge_score > EDGE_THRESHOLD

    if state == "WALK":
        start_walk()

    if is_stuck or obstacle_ahead:
        stuck_counter += 1
    else:
        stuck_counter = 0

    if stuck_counter >= STUCK_FRAMES_FOR_JUMP:
            state = "JUMPING"

    elif state == "JUMPING":
        jump()
        time.sleep(0.3)
        stuck_counter += 1

    if stuck_counter >= STUCK_FRAMES_FOR_TURN:
        state = "TURNING"
        
    elif not is_stuck and not obstacle_ahead:
        state = "WALK"
        stuck_counter = 0

    elif state == "TURNING":
        stop_walk()
        turn()
        state = "WALK"
        stuck_counter = 0
        start_walk()

    # small random look-around even when things are fine, so exploration
    # doesn't walk in a dead-straight line forever
    if state == "WALK" and random.random() < 0.05:
        turn()

    prev_roi_gray = roi_gray_small
    cv2.imwrite("test2.jpg", screen)

    if keyboard.is_pressed("q"):
        break

    time.sleep(LOOP_DELAY)

stop_walk()
keys.directKey("SPACE", keys.key_release)
cv2.destroyAllWindows()
print("Bot stopped")