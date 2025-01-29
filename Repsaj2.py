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

#                        ----- CORE FUNCTIONS -----
def SetupScreen(screenWidth, aspectRatio):
    global SCREEN_WIDTH
    global ASPECT_RATIO
    global screen
    SCREEN_WIDTH = screenWidth
    ASPECT_RATIO = aspectRatio
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_WIDTH / ASPECT_RATIO))
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

#                   ---- OBJECT TRANSFORMS ------
class Transform:
    def __init__(self, position, rotation, scale):
        self.position = position
        self.localPosition = position
        self.rotation = rotation
        self.localRotation = rotation
        self.scale = scale
        self.localScale = scale
    def setParent(self, parent):
        newLocalPos = rotatePos(self.localPosition, parent.rotation)
        self.position = [parent.position[i] + newLocalPos[i] for i in range(3)]
        self.rotation = [parent.rotation[i] + self.localRotation[i] for i in range(3)]
        self.scale = [parent.scale[i] * self.localScale[i] for i in range(3)]

#                                       ------- CAMERA SETUP -------
# Input States
leftArrow = False
rightArrow = False
upArrow = False
downArrow = False
wKey = False
sKey = False
aKey = False
dKey = False
spaceKey = False
shiftKey = False
class Camera:
    def __init__(self, transform: Transform, fieldOfView):
        self.FOV = fieldOfView
        self.transform = transform
    def movementActions(self, speed, lookSens):
        # Movement
        moveDir = [0, 0, 0]
        if wKey:
            moveDir[2] += 1
        if sKey:
            moveDir[2] -= 1
        if dKey:
            moveDir[0] += 1
        if aKey:
            moveDir[0] -= 1
        scale = speed * DELTA_TIME / math.dist(moveDir, [0, 0, 0]) if moveDir != [0, 0, 0] else 0
        moveOffset = rotatePos([moveDir[i] * scale for i in range(3)], [0, self.transform.rotation[1], 0])
        self.transform.position = [self.transform.position[i] + moveOffset[i] for i in range(3)]
        if spaceKey:
            self.transform.position[1] += speed * DELTA_TIME
        if shiftKey:
            self.transform.position[1] -= speed * DELTA_TIME

        # Camera Looking
        lookSpeed = lookSens * DELTA_TIME
        if upArrow:
            self.transform.rotation[0] -= lookSpeed
        if downArrow:
            self.transform.rotation[0] += lookSpeed
        if rightArrow:
            self.transform.rotation[1] += lookSpeed
        if leftArrow:
            self.transform.rotation[1] -= lookSpeed
        self.transform.rotation = [r % 360 for r in self.transform.rotation]
# --- USER INPUTS ---
def _getInputs():
    global leftArrow
    global rightArrow
    global upArrow
    global downArrow
    global wKey
    global aKey
    global sKey
    global dKey
    global spaceKey
    global shiftKey
    inputs = pygame.event.get()
    for keyPress in inputs:
        # Camera Controls
        if keyPress.type == pygame.KEYDOWN:
            if keyPress.key == pygame.K_LEFT:
                leftArrow = True
            elif keyPress.key == pygame.K_RIGHT:
                rightArrow = True
            elif keyPress.key == pygame.K_UP:
                upArrow = True
            elif keyPress.key == pygame.K_DOWN:
                downArrow = True
            elif keyPress.key == pygame.K_w:
                wKey = True
            elif keyPress.key == pygame.K_a:
                aKey = True
            elif keyPress.key == pygame.K_s:
                sKey = True
            elif keyPress.key == pygame.K_d:
                dKey = True
            elif keyPress.key == pygame.K_SPACE:
                spaceKey = True
            elif keyPress.key == pygame.K_LSHIFT:
                shiftKey = True

        elif keyPress.type == pygame.KEYUP:
            if keyPress.key == pygame.K_LEFT:
                leftArrow = False
            elif keyPress.key == pygame.K_RIGHT:
                rightArrow = False
            elif keyPress.key == pygame.K_UP:
                upArrow = False
            elif keyPress.key == pygame.K_DOWN:
                downArrow = False
            elif keyPress.key == pygame.K_w:
                wKey = False
            elif keyPress.key == pygame.K_a:
                aKey = False
            elif keyPress.key == pygame.K_s:
                sKey = False
            elif keyPress.key == pygame.K_d:
                dKey = False
            elif keyPress.key == pygame.K_SPACE:
                spaceKey = False
            elif keyPress.key == pygame.K_LSHIFT:
                shiftKey = False
        # QUIT GAME
        elif keyPress.type == pygame.QUIT:
            pygame.quit()

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
    def Mesh(cam: Camera, transform: Transform, vertices, faces, color):
        ratio = math.tan(math.radians(cam.FOV/2))
        transformedVerts = [rotatePos(r, transform.rotation) for r in vertices]
        transformedVerts = [[t[i] * transform.scale[i] for i in range(3)] for t in transformedVerts]
        screenPts = [[0, 0] for _ in vertices]
        for i, v in enumerate(transformedVerts):
            newPos = [v[p] + transform.position[p] - cam.transform.position[p] for p in range(3)]
            newPos = rotatePos(newPos, [-r for r in cam.transform.rotation], [2, 1, 0])
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
                    center[p] += transform.position[p]+transformedVerts[point][p]
            if outOfFrame: continue
            avg = [p / len(f) for p in center]
            faceDist = math.dist(avg, cam.transform.position)
            vec1 = [transformedVerts[f[1]][i] - transformedVerts[f[0]][i] for i in range(3)]
            vec2 = [transformedVerts[f[2]][i] - transformedVerts[f[0]][i] for i in range(3)]
            normal = np.cross(vec1, vec2)
            vectorProduct = math.dist(vec1, [0, 0, 0]) * math.dist(vec2, [0, 0, 0])
            factor = -np.dot(LIGHT_VECTOR, normal)/vectorProduct/2+.5 if vectorProduct != 0 else 1
            globalFaces.append([screenPts[p] for p in f]+[faceDist, [c*factor for c in color]])

    @ staticmethod
    def Cube(cam: Camera, transform: Transform, color):
        verts = [[1, 1, 1], [1, -1, 1], [-1, -1, 1], [-1, 1, 1],
                 [1, 1, -1], [1, -1, -1], [-1, -1, -1], [-1, 1, -1]]
        tris = [[3, 2, 1, 0], [4, 5, 6, 7], [0, 1, 5, 4],
                [2, 3, 7, 6], [3, 0, 4, 7], [1, 2, 6, 5]]
        Render.Mesh(cam, transform, verts, tris, color)

    @ staticmethod
    def Plane(cam: Camera, transform: Transform, color):
        verts = [[5, 0, 5], [5, 0, -5], [-5, 0, -5], [-5, 0, 5]]
        Render.Mesh(cam, transform, verts, [[0, 1, 2, 3]], color)


#               1   --- GAME UPDATE / RENDERING STACK ---
def Update():
    global runTime
    global DELTA_TIME
    global globalFaces
    _getInputs()
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