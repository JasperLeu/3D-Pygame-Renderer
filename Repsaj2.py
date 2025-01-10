# Jasper's awesome 3d library
import pygame
import math
import numpy as np
import time

# -- CONSTANTS --
SCREEN_WIDTH = 800
ASPECT_RATIO = 1.5
FPS = 100

# --- SCREEN SETUP ---
screen = None
RENDER_DISTANCE = 30

def SetupScreen(screenWidth, aspectRatio, RenderDistance):
    global SCREEN_WIDTH
    global ASPECT_RATIO
    global screen
    global RENDER_DISTANCE
    SCREEN_WIDTH = screenWidth
    ASPECT_RATIO = aspectRatio
    RENDER_DISTANCE = RenderDistance
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
                End()
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
        scale = speed / FPS / math.dist(moveDir, [0, 0, 0]) if moveDir != [0, 0, 0] else 0
        moveOffset = rotatePos([moveDir[i] * scale for i in range(3)], [0, self.rotation[1], 0])
        self.position = [self.position[i] + moveOffset[i] for i in range(3)]

        # Camera Looking
        lookSpeed = lookSens / FPS
        # if self.upArrow and self.rotation[0] < 75:
        #     self.rotation[0] += lookSpeed
        # if self.downArrow and self.rotation[0] > -75:   *** fix when get smart ***
        #     self.rotation[0] -= lookSpeed
        if self.rightArrow:
            self.rotation[1] += lookSpeed
        if self.leftArrow:
            self.rotation[1] -= lookSpeed
        self.rotation[1] %= 360


# --- BASIC FUNCTIONS ---
def Clear():
    screen.fill((0, 0, 0))
def End():
    pygame.quit()

def angleDiff(angle1, angle2):
    diff = abs(angle1 - angle2)
    if diff > 180:
        diff = 360 - diff
    if round((angle1 - diff) % 360, 4) == round(angle2, 4):
        diff *= -1
    return diff

def rotatePos(position, rotation):
    xRot, yRot, zRot = [math.radians(i) for i in rotation]
    rot1 = np.dot(([1, 0, 0],
               [0, math.cos(xRot), -math.sin(xRot)],
               [0, math.sin(xRot), math.cos(xRot)]), position)
    rot2 = np.dot(([math.cos(yRot), 0, math.sin(yRot)],
                   [0, 1, 0],
                   [-math.sin(yRot), 0, math.cos(yRot)]), rot1)
    return(np.dot(([math.cos(zRot), -math.sin(zRot), 0],
                  [math.sin(zRot), math.cos(zRot), 0],
                   [0, 0, 1]), rot2))

#               ------ ALL OBJECTS ------
objects = []
class NewObject:
    def __init__(self, pos: list, vertices: list, triangles, color):
        self.pos = pos
        self.rotation = [0, 0, 0]
        self.vertices = vertices
        self.screenPts = [[0, 0] for _ in self.vertices]
        self.tris = triangles
        self.triangleDists = [-1 for _ in self.tris]
        self.color = color
        objects.append(self)

    def Calculate(self, player: Player):
        ratio = math.tan(math.radians(player.FOV/2))
        transformedVerts = [rotatePos(i, self.rotation) for i in self.vertices]
        for i, v in enumerate(transformedVerts):
            newPos = [v[p] + self.pos[p] - player.position[p] for p in range(3)]
            newPos = rotatePos(newPos, [-r for r in player.rotation])
            if newPos[2] > 0:
                self.screenPts[i][0] = (newPos[0]/newPos[2]/ratio+1) * SCREEN_WIDTH / 2
                self.screenPts[i][1] = (-newPos[1]/newPos[2]/ratio+1) * SCREEN_WIDTH / 2
        for t in range(len(self.tris)):
            center = [0, 0, 0]
            for point in range(3):
                center = [center[i] + transformedVerts[self.tris[t][point]][i] + self.pos[i] for i in range(3)]
            center = [i / 3 for i in center]
            self.triangleDists[t] = math.dist(center, player.position)


#               1   --- RENDERING FOR ALL OBJECTS ---
def Update(player: Player):
    tris = []
    player._getInputs()
    for i in objects:
        i.Calculate(player)
        for t in range(len(i.tris)):
            distPercent = 0 if 1 - i.triangleDists[t] / RENDER_DISTANCE < 0 else 1 - i.triangleDists[
                t] / RENDER_DISTANCE
            tris.append([i.screenPts[i.tris[t][0]], i.screenPts[i.tris[t][1]], i.screenPts[i.tris[t][2]],
                         i.triangleDists[t], [i.color[c] * distPercent for c in range(3)]])

    # order triangles by distance
    def sort(arr):
        if len(arr) <= 1:
            return arr
        else:
            pivot = arr[0]
            left = []
            right = []
            for i in arr[1:]:
                if i[3] > pivot[3]:
                    left.append(i)
                else:
                    right.append(i)
            left = sort(left)
            right = sort(right)
            return left + [pivot] + right

    tris = sort(tris)
    for t in tris:
        pygame.draw.polygon(screen, t[4], [t[0], t[1], t[2]])
    # -- UPDATE DISPLAY --
    pygame.display.update()
    time.sleep(1 / FPS)