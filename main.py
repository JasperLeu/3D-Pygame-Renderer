# -- My Cool Library --
import Repsaj2

# -- SETUP --
Repsaj2.SetupScreen(800, 1.5, 30)
playerObj = Repsaj2.Player([0, 5, 0], [0, 0, 0], 90)

# Initialize Objects
wall1 = Repsaj2.NewObject([10, 0, 15], [[-10, 0, 0], [-10, 10, 0], [0, 10, 0], [0, 0, 0]],
                      [[0, 1, 3], [1, 2, 3]], (0, 255, 0))
wall2 = Repsaj2.NewObject([10, 0, 15], [[0, 0, 0], [0, 0, -10], [0, 10, -10], [0, 10, 0]],
                       [[0, 1, 2], [2, 3, 0]], (0, 0, 255))
wall3 = Repsaj2.NewObject([10, 0, 15], [[0, 0, 0], [-10, 0, -10], [-10, 0, 0], [0, 0, -10]],
                         [[0, 1, 2], [0, 1, 3]], (255, 0, 0))
cube = Repsaj2.NewObject([5, 5, 10], [[2, 2, 2], [-2, 2, 2], [-2, -2, 2], [2, -2, 2],
                                       [2, 2, -2], [-2, 2, -2], [-2, -2, -2], [2, -2, -2]],
                        [[0, 1, 2], [2, 3, 0], [4, 5, 6], [6, 7, 4],
                         [0, 4, 7], [7, 3, 0], [1, 5, 6], [6, 2, 1],
                         [0, 1, 5], [5, 4, 0], [3, 2, 6], [6, 7, 3]], (255, 255, 0))


# --- MAIN LOOP ---
running = True
rot = 0
while running:
    Repsaj2.Clear()
    # Player
    playerObj.movementActions(10, 60)
    # Objects
    cube.rotation = [rot, rot, 0]
    rot+=1

    # - UPDATE GAME -
    Repsaj2.Update(playerObj)

Repsaj2.End()
