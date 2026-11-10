'''
import time
import random
from javascript import require, On

mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinding')

bot = mineflayer.createBot({
    'host': 'localhost',       
    'port': 25565,             
    'username': 'PythonBot',   
    'version': '1.20.1'        
})

bot.loadPlugin(pathfinder.pathfinder)

def start_exploring():
    current_pos = bot.entity.position
    random_x = current_pos.x + random.randint(-40, 40)
    random_z = current_pos.z + random.randint(-40, 40)
    
    print(f"Exploring towards: X: {int(random_x)}, Z: {int(random_z)}")
    
    Movements = pathfinder.Movements
    GoalXZ = pathfinder.goals.GoalXZ
    
    default_movements = Movements(bot)
    bot.pathfinder.setMovements(default_movements)
    bot.pathfinder.setGoal(GoalXZ(random_x, random_z))

@On(bot, 'spawn')
def on_spawn(*args):
    print("PythonBot has spawned into the world!")
    time.sleep(2)
    start_exploring()

@On(bot, 'goal_reached')
def on_goal_reached(*args):
    print("Reached destination! Finding a new area...")
    time.sleep(2)  
    start_exploring()

@On(bot, 'error')
def on_error(this, err):
    print("An error occurred:", err)


from grabscreen import grab_screen
import cv2

def pathing(minimap):
    pass

for i in range(100):
    screen = grab_screen(region=(951, 522))
    screen = cv2.cvtColor(screen, cv2.COLOR_)
    cv2.imshow("cv2screen", screen)
    cv2.waitKey(10)
cv2.destroyAllWindows()
'''

import cv2
import numpy as np
from grabscreen import grab_screen
import keys as k
import time

# Keep the key initialization
keys = k.Keys()

def pathing(roi_image):
    # 1. CHANGE: Convert to HSV to find your Minecraft path/map color
    hsv = cv2.cvtColor(roi_image, cv2.COLOR_BGR2HSV)
    
    # 2. CHANGE: Adjust these HSV values for your Minecraft target color 
    # (These example values target a bright red block/line)
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, lower_red, upper_red)
    
    # Keep the math that finds where the pixels are
    matches = np.where(mask == 255)
    
    # If no path is found, stop moving to avoid falling into lava/off cliffs
    if len(matches[0]) == 0:
        return 0 
        
    # Keep the calculation for finding the center of the path
    mean_x = np.mean(matches[1]) # Index 1 is the X coordinates
    target = roi_image.shape[1] / 2 # The middle of our cropped view
    error = target - mean_x
    
    return error

# --- Main Loop ---
time.sleep(3) # Time to click back into your Minecraft window!
keys.directKey("W") # Start walking forward

while True:
    # 3. CHANGE: Set this region to match your Minecraft window coordinates
    screen = grab_screen(region=(0, 40, 800, 640)) 
    
    # 4. CHANGE: Slice the screen to look at your crosshair/path area
    # Example: cropping a 200x200 box around the center of an 800x600 window
    roi = screen[200:400, 300:500] 
    
    error = pathing(roi)
    
    # Keep the steering logic
    if error != 0:
        # Move mouse horizontally based on the error
        # Adjust the multiplier (e.g., * 0.5 or * 2) to control steering sensitivity
        keys.directMouse(int(-1 * error * 0.5), 0) 
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

keys.releaseKey("W")
cv2.destroyAllWindows()