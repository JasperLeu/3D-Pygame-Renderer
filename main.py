# -- My Cool Library --
import Repsaj2
import Repsaj3

# -- SETUP --
Display = Repsaj3.Window([400, 200], 4)
playerCam = Repsaj3.Camera(Repsaj3.Transform([0, 0, -3], [0, 0, 0], [1, 1, 1]), 90)

# Initialize Monke
vertices, faces = Repsaj3.uploadObj("Monkey.obj")
shape = Repsaj3.GameObject(Repsaj3.Transform())
shape.vertices = vertices
shape.faces = faces

# --- MAIN LOOP ----
while True:
    # - UPDATE GAME -
    Display.refresh()
    Repsaj3.UpdateGame(playerCam, Display)