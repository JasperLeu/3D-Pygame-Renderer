# -- My Cool Library --
import math
import Repsaj2

# -- SETUP --
Repsaj2.SetupScreen(800, 1.5)
playerObj = Repsaj2.Camera([0, 5, 0], [0, 0, 0], 90)

# Initialize Objects
monkeyVerts, monkeyFaces = Repsaj2.uploadObj("notagun.obj")
# --- MAIN LOOP ---
while True:
    # - UPDATE PLAYER -
    playerObj.movementActions(10, 90)

    # Objects
    rot = Repsaj2.runTime * 60
    Repsaj2.Render.Mesh(playerObj, [5, 5, 5], [0, 0, 0], [2.5, 2.5, 2.5],
                        monkeyVerts, monkeyFaces, (255, 0, 0))
    Repsaj2.Render.Cube(playerObj, [-5, 3, 5], [40, rot, 0], [1, 1, 1], [255, 255, 0])
    Repsaj2.Render.Plane(playerObj, [0, 0, 5], [0, 0, 0], [2, 0, 1], [0, 255, 0])

    # - UPDATE GAME -
    Repsaj2.Update()