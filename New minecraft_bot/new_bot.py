import cv2
import numpy as np
from grabscreen import grab_screen
import keys as k
import time
import random
import keyboard

keys = k.Keys()

# tuning knobs
# these are placeholder numbers - print edge_score / mse_v for a minute
# while walking in the open vs into a wall, then set these based on
# what you actually see
EDGE_THRESHOLD = 1000000
STUCK_MSE_THRESHOLD = 13
STUCK_FRAMES_FOR_JUMP = 3     # consecutive stuck frames before trying a jump
MAX_JUMP_ATTEMPTS = 2         # how many jumps to try before giving up and turning
LOOP_DELAY = 0.1


state = "WALK"          # WALK -> JUMPING -> TURNING -> back to WALK
stuck_counter = 0
jump_attempts = 0
walking = False
just_jumped = False


def get_roi(screen):
    h, w = screen.shape[:2]
    return screen[int(h * 0.55):int(h * 0.90), int(w * 0.35):int(w * 0.65)]


def obstacle_amount(roi_gray):
    edges = cv2.Canny(roi_gray, 80, 150)
    return np.sum(edges)


def start_walk():
    global walking
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

#find out the roi
    h, w = screen.shape[:2]
    print("screen shape:", screen.shape)
    debug_frame = screen.copy()
    cv2.rectangle(debug_frame, (int(w*0.30), int(h*0.40)), (int(w*0.70), int(h*0.90)), (0,255,0), 3)
    cv2.imwrite("roi_check.jpg", debug_frame)
#------
    edge_score = obstacle_amount(roi_gray)

    if prev_roi_gray is None:
        prev_roi_gray = roi_gray_small
        time.sleep(LOOP_DELAY)
        continue

    diff = roi_gray_small.astype(np.float32) - prev_roi_gray.astype(np.float32)
    mse_v = float(np.mean(diff ** 2))

    print(f"state={state} edge={edge_score} mse={mse_v:.1f} stuck={stuck_counter} jumps={jump_attempts}")

    is_stuck = mse_v < STUCK_MSE_THRESHOLD
    obstacle_ahead = edge_score > EDGE_THRESHOLD
    
    if state == "WALK":
        start_walk()
        if is_stuck and obstacle_ahead:
            stuck_counter += 1
        else:
            stuck_counter = 0

        if stuck_counter >= STUCK_FRAMES_FOR_JUMP:
            state = "JUMPING"
            jump_attempts = 0

    elif state == "JUMPING":
        jump()
        time.sleep(0.4)        
        jump_attempts += 1
#fresh photo
        new_screen = grab_screen()
        new_roi = get_roi(new_screen)
        new_roi_gray = cv2.cvtColor(new_roi, cv2.COLOR_BGR2GRAY)
        new_roi_gray_small = cv2.resize(new_roi_gray, (64, 64))

        new_edge_score = obstacle_amount(new_roi_gray)
        new_diff = new_roi_gray_small.astype(np.float32) - prev_roi_gray.astype(np.float32)
        new_mse_v = float(np.mean(new_diff ** 2))

        still_stuck = new_mse_v < STUCK_MSE_THRESHOLD
        still_obstacle = new_edge_score > EDGE_THRESHOLD

        print(f"[post-jump check] mse={new_mse_v:.1f} edge={new_edge_score} stuck={still_stuck} obstacle={still_obstacle}")

        if not still_stuck and not still_obstacle:
            # view looks clear now - jump worked
            state = "WALK"
            stuck_counter = 0
        elif jump_attempts >= MAX_JUMP_ATTEMPTS:
            state = "TURNING"

        prev_roi_gray = new_roi_gray_small
        screen = new_screen
        just_jumped = True

    elif state == "TURNING":
        stop_walk()
        turn()
        state = "WALK"
        stuck_counter = 0
        jump_attempts = 0
        start_walk()

    if state == "WALK" and random.random() < 0.05:
        turn()

    if not just_jumped:
        prev_roi_gray = roi_gray_small
    just_jumped = False
    cv2.imwrite("test2.jpg", screen)

    if keyboard.is_pressed("q"):
        break

    time.sleep(LOOP_DELAY)

stop_walk()
keys.directKey("SPACE", keys.key_release)
cv2.destroyAllWindows()
print("Bot stopped")