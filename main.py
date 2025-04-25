# -- My Cool Library --
import Repsaj3
import math

# -- SETUP --
Display = Repsaj3.Window([600, 300], 5)
playerCam = Repsaj3.Camera(Repsaj3.Transform([0, 3, -20], [30, 0, 0]), 90)

# Initialize Objects
Plane = Repsaj3.GameObject(Repsaj3.Transform([0, 0, 0]))
side = 10
planeVerts = []
planeFaces = []
for y in range(side):
    for x in range(side):
        planeVerts.append([-side/2+x, 0, -side/2+y])
        if x < side - 1 and y < side -1:
            planeFaces.append([y*side+x, (y+1)*side+x, y*side+x+1])
            planeFaces.append([y*side+x+1, (y+1)*side+x, (y+1)*side+x+1])
Plane.vertices = planeVerts
Plane.faces = planeFaces
Plane.color = (150, 220, 255)

# Initialize Monke
monkyVerts, monkyFaces = Repsaj3.uploadObj("Monkey.obj")
monke = Repsaj3.GameObject(Repsaj3.Transform([0, 2, 0]))
monke.vertices = monkyVerts
monke.faces = monkyFaces

# --- GAME LOOP ----
while True:
    # spinny monke
    monke.transform.rotation[1] += Repsaj3.Time.deltaTime * 60
    monke.transform.position[1] = math.cos(Repsaj3.Time.runTime) + 1.5
    
    # Wavey plane
    for y in range(side):
        for x in range(side):
            height = math.sin(Repsaj3.Time.runTime + math.dist([x, y], [side/2]*2))
            # height += math.sin(Repsaj3.Time.runTime + x)
            Plane.vertices[y*side+x][1] = height

    # - UPDATE GAME -
    Repsaj3.UpdateGame(playerCam, Display)
    Display.refresh()
