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