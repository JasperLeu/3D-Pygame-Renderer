# -------------------------------------------THE BEST 3D PYTHON LIBRARY-------------------------------------------------
import pygame
import math
import numpy as np


# -------------------------------------------SCREEN OBJECT--------------------------------------------------------------
class Window:
    def __init__(self):
        self.display = pygame.display.set_mode()
        self.resolution = []
        self.pixelStack = []

# -------------------------------------------TIME CLASS--------------------------------------------------------------
class Timer:
    def __init__(self):
        self.deltaTime = 0.1
        self.runTime = 0

    def frameStep(self):
        tempTime = pygame.time.get_ticks()/1000
        self.deltaTime = tempTime - self.runTime
        self.runTime = tempTime

# GLOBAL VARIABLES
LIGHT_VECTOR = [0, -1, 0]
Time = Timer()
screen = Window()
gameObjects = []


# -------------------------------------------SETUP FUNCTIONS------------------------------------------------------------
def SetupScreen(screenWidth, screenHeight):
    global screen
    screen.resolution = [screenWidth, screenHeight]
    screen.pixelStack = np.zeros((screenWidth, screenHeight))
    pygame.init()
    screen.display = pygame.display.set_mode((screenWidth, screenHeight))


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


# ---------------------------------------------OBJECT TRANSFORMS--------------------------------------------------------
class Transform:
    def __init__(self, position=None, rotation=None, scale=None):
        self.position = [0, 0, 0] if position is None else position
        self.localPosition = position
        self.rotation = [0, 0, 0] if rotation is None else rotation
        self.localRotation = rotation
        self.scale = [1, 1, 1] if scale is None else scale
        self.localScale = scale
        self.parent = None

    def Update(self):
        if self.parent != None:
            newLocalPos = rotatePos(self.localPosition, self.parent.rotation)
            self.position = [self.parent.position[i] + newLocalPos[i] for i in range(3)]
            self.rotation = [self.parent.rotation[i] + self.localRotation[i] for i in range(3)]
            self.scale = [self.parent.scale[i] * self.localScale[i] for i in range(3)]

# ---------------------------------------------CAMERA-SETUP-------------------------------------------------------------
# Input States
leftArrow = False
rightArrow = False
upArrow = False
downArrow = False
wKey = False
sKey = False
dKey = False
aKey = False
spaceKey = False
shiftKey = False


class Camera:
    def __init__(self, transform: Transform, fieldOfView):
        self.FOV = fieldOfView
        self.transform = transform
        self.clipPlane = 0.1
        self.speed = 5
        self.lookSense = 90

    def movementActions(self):
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
        scale = self.speed * Time.deltaTime / math.dist(moveDir, [0, 0, 0]) if moveDir != [0, 0, 0] else 0
        moveOffset = rotatePos([moveDir[i] * scale for i in range(3)], [0, self.transform.rotation[1], 0])
        self.transform.position = [self.transform.position[i] + moveOffset[i] for i in range(3)]
        if spaceKey:
            self.transform.position[1] += self.speed * Time.deltaTime
        if shiftKey:
            self.transform.position[1] -= self.speed * Time.deltaTime

        # Camera Looking
        lookSpeed = self.lookSense * Time.deltaTime
        if upArrow:
            self.transform.rotation[0] -= lookSpeed
        if downArrow:
            self.transform.rotation[0] += lookSpeed
        if rightArrow:
            self.transform.rotation[1] += lookSpeed
        if leftArrow:
            self.transform.rotation[1] -= lookSpeed
        self.transform.rotation = [r % 360 for r in self.transform.rotation]

# ---------------------------------------------USER INPUTS--------------------------------------------------------------
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


# -----------------------------------------------OBJECT CLASS-----------------------------------------------------------
class GameObject:
    def __init__(self, transform: Transform):
        global gameObjects
        self.transform = transform
        self.vertices = []
        self.faces = []
        self.color = (255, 255, 255)
        gameObjects.append(self)

    def Render(self, cam: Camera):
        objectFaces = []
        ratio = math.tan(math.radians(cam.FOV/2))
        transformedVerts = [rotatePos(r, self.transform.rotation) for r in self.vertices]
        transformedVerts = [[t[i] * self.transform.scale[i] for i in range(3)] for t in transformedVerts]
        screenPts = [[0, 0] for _ in self.vertices]
        for i, v in enumerate(transformedVerts):
            newPos = [v[p] + self.transform.position[p] - cam.transform.position[p] for p in range(3)]
            newPos = rotatePos(newPos, [-r for r in cam.transform.rotation], [2, 1, 0])
            if newPos[2] > 0:
                screenPts[i][0] = (newPos[0]/newPos[2]/ratio+1) * screen.resolution[0] / 2
                screenPts[i][1] = (-newPos[1]/newPos[2]/ratio+1) * screen.resolution[0] / 2
            else:
                screenPts[i] = [False]
        for f in self.faces:
            outOfFrame = False
            center = [0, 0, 0]
            for point in f:
                if screenPts[point] == [False]: outOfFrame = True
                for p in range(3):
                    center[p] += self.transform.position[p]+transformedVerts[point][p]
            if outOfFrame:
                continue
            avg = [p / len(f) for p in center]
            faceDist = math.dist(avg, cam.transform.position)
            vec1 = [transformedVerts[f[1]][i] - transformedVerts[f[0]][i] for i in range(3)]
            vec2 = [transformedVerts[f[2]][i] - transformedVerts[f[0]][i] for i in range(3)]
            normal = np.cross(vec1, vec2)
            vectorProduct = math.dist(vec1, [0, 0, 0]) * math.dist(vec2, [0, 0, 0])
            factor = -np.dot(LIGHT_VECTOR, normal)/vectorProduct/2+.5 if vectorProduct != 0 else 1
            objectFaces.append([screenPts[p] for p in f]+[faceDist, [c*factor for c in self.color]])
        return objectFaces


# -------------------------------------GAME UPDATE / RENDERING----------------------------------------------------------
def Update(camera: Camera):
    global Time
    global gameObjects

    # Update Inputs
    _getInputs()
    camera.movementActions()

    # Get all faces in gameobjects
    globalFaces = []
    for obj in gameObjects:
        globalFaces += obj.Render(camera)

    # -- ORDER RENDERED TRIANGLES --
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

    # -- UPDATE GAME --
    screen.display.fill((0, 0, 0))
    for f in globalFaces:
        pygame.draw.polygon(screen.display, f[-1], f[:-2])
    pygame.display.update()
    Time.frameStep()