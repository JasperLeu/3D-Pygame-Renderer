# -- My Cool Library --
import math
import Repsaj2
import Repsaj3

# -- SETUP --
Repsaj3.SetupScreen(800, 400)
playerObj = Repsaj3.Camera(Repsaj3.Transform([0, 0, -3], [0, 0, 0], [1, 1, 1]), 90)

# Initialize Objects
monkeyVerts, monkeyFaces = Repsaj3.uploadObj("Monkey.obj")
monkey = Repsaj3.GameObject(Repsaj3.Transform())
monkey.vertices = monkeyVerts
monkey.faces = monkeyFaces

# --- MAIN LOOP ---
while True:
    # - UPDATE GAME -
    Repsaj3.Update(playerObj)