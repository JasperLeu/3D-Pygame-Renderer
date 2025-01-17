#                       ------- Jasper's awesome 3d library --------
import pygame
import math
import numpy as np

# -- CONSTANTS --
SCREEN_WIDTH = 800
ASPECT_RATIO = 1.5
DELTA_TIME = 0.1
runTime = 0

# --- SCREEN SETUP ---
screen = None
LIGHT_VECTOR = [0, -1, 0]
def SetupScreen(screenWidth, aspectRatio):
    global SCREEN_WIDTH
    global ASPECT_RATIO
    global screen
    SCREEN_WIDTH = screenWidth
    ASPECT_RATIO = aspectRatio
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_WIDTH / ASPECT_RATIO))


# --- PLAYER SETUP ---
class Player:
    def __init__(self, position, rotation, fieldOfView):
        self.FOV = fieldOfView
        self.position = position
        self.rotation = rotation

        # Input States
        self.leftArrow = False
        self.rightArrow = False
        self.upArrow = False
        self.downArrow = False
        self.wKey = False
        self.sKey = False
        self.aKey = False
        self.dKey = False

    def _getInputs(self):
        inputs = pygame.event.get()
        for keyPress in inputs:
            # Camera Controls
            if keyPress.type == pygame.KEYDOWN:
                if keyPress.key == pygame.K_LEFT:
                    self.leftArrow = True
                elif keyPress.key == pygame.K_RIGHT:
                    self.rightArrow = True
                elif keyPress.key == pygame.K_UP:
                    self.upArrow = True
                elif keyPress.key == pygame.K_DOWN:
                    self.downArrow = True
                if keyPress.key == pygame.K_w:
                    self.wKey = True
                elif keyPress.key == pygame.K_a:
                    self.aKey = True
                elif keyPress.key == pygame.K_s:
                    self.sKey = True
                elif keyPress.key == pygame.K_d:
                    self.dKey = True
            elif keyPress.type == pygame.KEYUP:
                if keyPress.key == pygame.K_LEFT:
                    self.leftArrow = False
                elif keyPress.key == pygame.K_RIGHT:
                    self.rightArrow = False
                elif keyPress.key == pygame.K_UP:
                    self.upArrow = False
                elif keyPress.key == pygame.K_DOWN:
                    self.downArrow = False
                if keyPress.key == pygame.K_w:
                    self.wKey = False
                elif keyPress.key == pygame.K_a:
                    self.aKey = False
                elif keyPress.key == pygame.K_s:
                    self.sKey = False
                elif keyPress.key == pygame.K_d:
                    self.dKey = False
            # QUIT GAME
            elif keyPress.type == pygame.QUIT:
                pygame.quit()
    def movementActions(self, speed, lookSens):
        # Movement
        moveDir = [0, 0, 0]
        if self.wKey:
            moveDir[2] += 1
        if self.sKey:
            moveDir[2] -= 1
        if self.dKey:
            moveDir[0] += 1
        if self.aKey:
            moveDir[0] -= 1
        scale = speed * DELTA_TIME / math.dist(moveDir, [0, 0, 0]) if moveDir != [0, 0, 0] else 0
        moveOffset = rotatePos([moveDir[i] * scale for i in range(3)], [0, self.rotation[1], 0])
        self.position = [self.position[i] + moveOffset[i] for i in range(3)]

        # Camera Looking
        lookSpeed = lookSens * DELTA_TIME
        if self.upArrow:
            self.rotation[0] -= lookSpeed
        if self.downArrow:
            self.rotation[0] += lookSpeed
        if self.rightArrow:
            self.rotation[1] += lookSpeed
        if self.leftArrow:
            self.rotation[1] -= lookSpeed
        self.rotation = [r % 360 for r in self.rotation]


# --- BASIC FUNCTIONS ---

def angleDiff(angle1, angle2):
    diff = abs(angle1 - angle2)
    if diff > 180:
        diff = 360 - diff
    if round((angle1 - diff) % 360, 4) == round(angle2, 4):
        diff *= -1
    return diff

def rotatePos(position, rotation, order=None):
    order = [0, 1, 2] if order is None else order
    xRot, yRot, zRot = [math.radians(i) for i in rotation]
    for r in order:
        if r == 0:
            position = np.dot(([1, 0, 0],
                       [0, math.cos(xRot), -math.sin(xRot)],
                       [0, math.sin(xRot), math.cos(xRot)]), position)
        elif r == 1:
            position = np.dot(([math.cos(yRot), 0, math.sin(yRot)],
                       [0, 1, 0],
                       [-math.sin(yRot), 0, math.cos(yRot)]), position)
        elif r == 2:
            position = np.dot(([math.cos(zRot), -math.sin(zRot), 0],
                      [math.sin(zRot), math.cos(zRot), 0],
                      [0, 0, 1]), position)
    return position


def uploadObj(file_path):
    vertices = []
    faces = []

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('v '):
                vertex = line.split()[1:]
                vertices.append([float(v) for v in vertex])
            elif line.startswith('f '):
                face = line.split()[1:]
                face = [int(f.split('/')[0])-1 for f in face]
                faces.append(face)
    return vertices, faces

#               ------ OBJECTS AND RENDERING------
globalFaces = []
class Render:
    @ staticmethod
    def Mesh(player: Player, position, rotation, scale, vertices, faces, color):
        ratio = math.tan(math.radians(player.FOV/2))
        transformedVerts = [rotatePos(r, rotation) for r in vertices]
        transformedVerts = [[t[i] * scale[i] for i in range(3)] for t in transformedVerts]
        screenPts = [[0, 0] for _ in vertices]
        for i, v in enumerate(transformedVerts):
            newPos = [v[p] + position[p] - player.position[p] for p in range(3)]
            newPos = rotatePos(newPos, [-r for r in player.rotation], [2, 1, 0])
            if newPos[2] > 0:
                screenPts[i][0] = (newPos[0]/newPos[2]/ratio+1) * SCREEN_WIDTH / 2
                screenPts[i][1] = (-newPos[1]/newPos[2]/ratio+1) * SCREEN_WIDTH / 2
            else:
                screenPts[i] = [False]
        for f in faces:
            outOfFrame = False
            center = [0, 0, 0]
            for point in f:
                if screenPts[point] == [False]: outOfFrame = True
                for p in range(3):
                    center[p] += position[p]+transformedVerts[point][p]
            if outOfFrame: continue
            avg = [p / len(f) for p in center]
            faceDist = math.dist(avg, player.position)
            vec1 = [transformedVerts[f[1]][i] - transformedVerts[f[0]][i] for i in range(3)]
            vec2 = [transformedVerts[f[2]][i] - transformedVerts[f[0]][i] for i in range(3)]
            normal = np.cross(vec1, vec2)
            vectorProduct = math.dist(vec1, [0, 0, 0]) * math.dist(vec2, [0, 0, 0])
            factor = -np.dot(LIGHT_VECTOR, normal)/vectorProduct/2+.5 if vectorProduct != 0 else 1
            globalFaces.append([screenPts[p] for p in f]+[faceDist, [c*factor for c in color]])

    @ staticmethod
    def Cube(player: Player, position, rotation, scale, color):
        verts = [[1, 1, 1], [1, -1, 1], [-1, -1, 1], [-1, 1, 1],
                 [1, 1, -1], [1, -1, -1], [-1, -1, -1], [-1, 1, -1]]
        tris = [[3, 2, 1, 0], [4, 5, 6, 7], [0, 1, 5, 4],
                [2, 3, 7, 6], [3, 0, 4, 7], [1, 2, 6, 5]]
        Render.Mesh(player, position, rotation, scale, verts, tris, color)

    @ staticmethod
    def Plane(player: Player, position, rotation, scale, color):
        verts = [[5, 0, 5], [5, 0, -5], [-5, 0, -5], [-5, 0, 5]]
        Render.Mesh(player, position, rotation, scale, verts, [[0, 1, 2, 3]], color)


#               1   --- GAME UPDATE / RENDERING STACK ---
def Update(player: Player):
    global runTime
    global DELTA_TIME
    global globalFaces
    player._getInputs()
    screen.fill((0, 0, 0))

    # -- ORDER RENDERED OBJs --
    def sort(arr):
        if len(arr) <= 1:
            return arr
        else:
            pivot = arr[0]
            left = []
            right = []
            for i in arr[1:]:
                if i[-2] > pivot[-2]:
                    left.append(i)
                else:
                    right.append(i)
            left = sort(left)
            right = sort(right)
            return left + [pivot] + right
    globalFaces = sort(globalFaces)

    # -- UPDATE CHANGES --
    for f in globalFaces:
        pygame.draw.polygon(screen, f[-1], f[:-2])
    globalFaces = []
    pygame.display.update()
    t = pygame.time.get_ticks()/1000
    DELTA_TIME = t-runTime
    runTime = t