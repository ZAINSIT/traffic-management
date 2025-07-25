import random
import time
import threading
import pygame
import os
import sys
timeElapsed = 0
simulationTime = 300
timeElapsedCoods = (1100,50)
vehicleCountTexts = ["0", "0", "0", "0"]
vehicleCountCoods = [(480,210),(880,210),(880,550),(480,550)]
# Default values of signal timers in seconds
defaultGreen = {0:20, 1:20, 2:20, 3:20}
defaultRed = 150
defaultYellow = 5
signals = []
noOfSignals = 4
currentGreen = 0   # Indicates which signal is green currently
nextGreen = (currentGreen+1)%noOfSignals
currentYellow = 0   # Indicates whether yellow signal is on or off
speeds = {'car':2.25, 'bus':1.8, 'truck':1.8, 'bike':2.5}  # average speeds of vehicles
# Coordinates of vehicles' start
x = {'right':[0,0,0], 'down':[755,727,697], 'left':[1400,1400,1400], 'up':[602,627,657]}
y = {'right':[348,370,398], 'down':[0,0,0], 'left':[498,466,436], 'up':[800,800,800]}
vehicles = {'right': {0:[], 1:[], 2:[], 'crossed':0}, 'down': {0:[], 1:[], 2:[], 'crossed':0}, 'left': {0:[], 1:[], 2:[], 'crossed':0}, 'up': {0:[], 1:[], 2:[], 'crossed':0}}
vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'bike'}
directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}
# Coordinates of signal image, timer, and vehicle count
signalCoods = [(530,230),(810,230),(810,570),(530,570)]
signalTimerCoods = [(530,210),(810,210),(810,550),(530,550)]
# Coordinates of stop lines
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}
# Gap between vehicles
stoppingGap = 25    # stopping gap
movingGap = 25
allowedVehicleTypes = {'car': True, 'bus': True, 'truck': True, 'bike': True}
allowedVehicleTypesList = []
vehiclesTurned = {'right': {1: [], 2: []}, 'down': {1: [], 2: []}, 'left': {1: [], 2: []}, 'up': {1: [], 2: []}}
vehiclesNotTurned = {'right': {1: [], 2: []}, 'down': {1: [], 2: []}, 'left': {1: [], 2: []}, 'up': {1: [], 2: []}}
rotationAngle = 3
mid = {'right': {'x': 705, 'y': 445}, 'down': {'x': 695, 'y': 450}, 'left': {'x': 695, 'y': 425},'up': {'x': 695, 'y': 400}}
randomGreenSignalTimer = True
randomGreenSignalTimerRange = [10, 20]
# moving gap
pygame.init()
simulation = pygame.sprite.Group()
class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = ""
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        self.crossedIndex = 0
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.image = pygame.image.load(path)

        if (len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0):
                if (direction == 'right'):
                    self.stop = vehicles[direction][lane][self.index - 1].stop- vehicles[direction][lane][self.index - 1].image.get_rect().width- stoppingGap
                elif (direction == 'left'):
                    self.stop = vehicles[direction][lane][self.index - 1].stop+ vehicles[direction][lane][self.index - 1].image.get_rect().width+ stoppingGap
                elif (direction == 'down'):
                    self.stop = vehicles[direction][lane][self.index - 1].stop- vehicles[direction][lane][self.index - 1].image.get_rect().height- stoppingGap
                elif (direction == 'up'):
                    self.stop = vehicles[direction][lane][self.index - 1].stop+ vehicles[direction][lane][self.index - 1].image.get_rect().height+ stoppingGap
        else:
                self.stop = defaultStop[direction]

            # Set new starting and stopping coordinate
        if (direction == 'right'):
                temp = self.image.get_rect().width + stoppingGap
                x[direction][lane] -= temp
        elif (direction == 'left'):
                temp = self.image.get_rect().width + stoppingGap
                x[direction][lane] += temp
        elif (direction == 'down'):
                temp = self.image.get_rect().height + stoppingGap
                y[direction][lane] -= temp
        elif (direction == 'up'):
                temp = self.image.get_rect().height + stoppingGap
                y[direction][lane] += temp
        simulation.add(self)
    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        if (self.direction == 'right'):
            if (self.crossed == 0 and self.x + self.image.get_rect().width > stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if (self.willTurn == 0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if (self.willTurn == 1):
                if (self.lane == 1):
                    if (self.crossed == 0 or self.x + self.image.get_rect().width < stopLines[self.direction] + 40):
                        if ((self.x + self.image.get_rect().width <= self.stop or (
                                currentGreen == 0 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.x + self.image.get_rect().width < (
                                vehicles[self.direction][self.lane][self.index - 1].x - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.x += self.speed
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x += 2.4
                            self.y -= 2.8
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.y > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().height + movingGap))):
                                self.y -= self.speed
                elif (self.lane == 2):
                    if (self.crossed == 0 or self.x + self.image.get_rect().width < mid[self.direction]['x']):
                        if ((self.x + self.image.get_rect().width <= self.stop or (
                                currentGreen == 0 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.x + self.image.get_rect().width < (
                                vehicles[self.direction][self.lane][self.index - 1].x - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.x += self.speed
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x += 2
                            self.y += 1.8
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or ((self.y + self.image.get_rect().height) < (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y - movingGap))):
                                self.y += self.speed
            else:
                if (self.crossed == 0):
                    if ((self.x + self.image.get_rect().width <= self.stop or (
                            currentGreen == 0 and currentYellow == 0)) and (
                            self.index == 0 or self.x + self.image.get_rect().width < (
                            vehicles[self.direction][self.lane][self.index - 1].x - movingGap))):
                        self.x += self.speed
                else:
                    if ((self.crossedIndex == 0) or (self.x + self.image.get_rect().width < (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].x - movingGap))):
                        self.x += self.speed
        elif (self.direction == 'down'):
            if (self.crossed == 0 and self.y + self.image.get_rect().height > stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if (self.willTurn == 0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if (self.willTurn == 1):
                if (self.lane == 1):
                    if (self.crossed == 0 or self.y + self.image.get_rect().height < stopLines[self.direction] + 50):
                        if ((self.y + self.image.get_rect().height <= self.stop or (
                                currentGreen == 1 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.y + self.image.get_rect().height < (
                                vehicles[self.direction][self.lane][self.index - 1].y - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.y += self.speed
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x += 1.2
                            self.y += 1.8
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or ((self.x + self.image.get_rect().width) < (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].x - movingGap))):
                                self.x += self.speed
                elif (self.lane == 2):
                    if (self.crossed == 0 or self.y + self.image.get_rect().height < mid[self.direction]['y']):
                        if ((self.y + self.image.get_rect().height <= self.stop or (
                                currentGreen == 1 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.y + self.image.get_rect().height < (
                                vehicles[self.direction][self.lane][self.index - 1].y - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.y += self.speed
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x -= 2.5
                            self.y += 2
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.x > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].x +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().width + movingGap))):
                                self.x -= self.speed
            else:
                if (self.crossed == 0):
                    if ((self.y + self.image.get_rect().height <= self.stop or (
                            currentGreen == 1 and currentYellow == 0)) and (
                            self.index == 0 or self.y + self.image.get_rect().height < (
                            vehicles[self.direction][self.lane][self.index - 1].y - movingGap))):
                        self.y += self.speed
                else:
                    if ((self.crossedIndex == 0) or (self.y + self.image.get_rect().height < (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].y - movingGap))):
                        self.y += self.speed
        elif (self.direction == 'left'):
            if (self.crossed == 0 and self.x < stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if (self.willTurn == 0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if (self.willTurn == 1):
                if (self.lane == 1):
                    if (self.crossed == 0 or self.x > stopLines[self.direction] - 70):
                        if ((self.x >= self.stop or (
                                currentGreen == 2 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index - 1].x +
                                                             vehicles[self.direction][self.lane][
                                                                 self.index - 1].image.get_rect().width + movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.x -= self.speed
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x -= 1
                            self.y += 1.2
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or ((self.y + self.image.get_rect().height) < (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y - movingGap))):
                                self.y += self.speed
                elif (self.lane == 2):
                    if (self.crossed == 0 or self.x > mid[self.direction]['x']):
                        if ((self.x >= self.stop or (
                                currentGreen == 2 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index - 1].x +
                                                             vehicles[self.direction][self.lane][
                                                                 self.index - 1].image.get_rect().width + movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.x -= self.speed
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x -= 1.8
                            self.y -= 2.5
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.y > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().height + movingGap))):
                                self.y -= self.speed
            else:
                if (self.crossed == 0):
                    if ((self.x >= self.stop or (currentGreen == 2 and currentYellow == 0)) and (
                            self.index == 0 or self.x > (
                            vehicles[self.direction][self.lane][self.index - 1].x + vehicles[self.direction][self.lane][
                        self.index - 1].image.get_rect().width + movingGap))):
                        self.x -= self.speed
                else:
                    if ((self.crossedIndex == 0) or (self.x > (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].x +
                            vehiclesNotTurned[self.direction][self.lane][
                                self.crossedIndex - 1].image.get_rect().width + movingGap))):
                        self.x -= self.speed
        elif (self.direction == 'up'):
            if (self.crossed == 0 and self.y < stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if (self.willTurn == 0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if (self.willTurn == 1):
                if (self.lane == 1):
                    if (self.crossed == 0 or self.y > stopLines[self.direction] - 60):
                        if ((self.y >= self.stop or (
                                currentGreen == 3 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index - 1].y +
                                                             vehicles[self.direction][self.lane][
                                                                 self.index - 1].image.get_rect().height + movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.y -= self.speed
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x -= 2
                            self.y -= 1.2
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.x > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].x +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().width + movingGap))):
                                self.x -= self.speed
                elif (self.lane == 2):
                    if (self.crossed == 0 or self.y > mid[self.direction]['y']):
                        if ((self.y >= self.stop or (
                                currentGreen == 3 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index - 1].y +
                                                             vehicles[self.direction][self.lane][
                                                                 self.index - 1].image.get_rect().height + movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.y -= self.speed
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x += 1
                            self.y -= 1
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.x < (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].x -
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().width - movingGap))):
                                self.x += self.speed
            else:
                if (self.crossed == 0):
                    if ((self.y >= self.stop or (currentGreen == 3 and currentYellow == 0)) and (
                            self.index == 0 or self.y > (
                            vehicles[self.direction][self.lane][self.index - 1].y + vehicles[self.direction][self.lane][
                        self.index - 1].image.get_rect().height + movingGap))):
                        self.y -= self.speed
                else:
                    if ((self.crossedIndex == 0) or (self.y > (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].y +
                            vehiclesNotTurned[self.direction][self.lane][
                                self.crossedIndex - 1].image.get_rect().height + movingGap))):
                        self.y -= self.speed
def initialize():
        minTime = randomGreenSignalTimerRange[0]
        maxTime = randomGreenSignalTimerRange[1]
        if (randomGreenSignalTimer):
            ts1 = TrafficSignal(0, defaultYellow, random.randint(minTime, maxTime))
            signals.append(ts1)
            ts2 = TrafficSignal(ts1.yellow + ts1.green, defaultYellow, random.randint(minTime, maxTime))
            signals.append(ts2)
            ts3 = TrafficSignal(defaultRed, defaultYellow, random.randint(minTime, maxTime))
            signals.append(ts3)
            ts4 = TrafficSignal(defaultRed, defaultYellow, random.randint(minTime, maxTime))
            signals.append(ts4)
        else:
            ts1 = TrafficSignal(0, defaultYellow, defaultGreen[0])
            signals.append(ts1)
            ts2 = TrafficSignal(ts1.yellow + ts1.green, defaultYellow, defaultGreen[1])
            signals.append(ts2)
            ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[2])
            signals.append(ts3)
            ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[3])
            signals.append(ts4)
        repeat()
def printStatus():
    for i in range(0, 4):
        if(signals[i] != None):
            if(i==currentGreen):
                if(currentYellow==0):
                    print(" GREEN TS",i+1,"-> r:",signals[i].red," y:",signals[i].yellow," g:",signals[i].green)
                else:
                    print("YELLOW TS",i+1,"-> r:",signals[i].red," y:",signals[i].yellow," g:",signals[i].green)
            else:
                print("   RED TS",i+1,"-> r:",signals[i].red," y:",signals[i].yellow," g:",signals[i].green)
    print()
def repeat():
    global currentGreen, nextGreen, currentYellow

    agent = QLearningAgent(actions=[0, 1, 2, 3])  # 4 signals
    while True:
        state = get_state()
        currentGreen = agent.choose_action(state)

        # Simulate green time
        for _ in range(signals[currentGreen].green):
            printStatus()
            updateValues()
            time.sleep(1)

        # Simulate yellow time
        currentYellow = 1
        for _ in range(signals[currentGreen].yellow):
            printStatus()
            updateValues()
            time.sleep(1)
        currentYellow = 0

        # Compute reward (e.g., how many vehicles crossed)
        reward = vehicles[directionNumbers[currentGreen]]['crossed']
        next_state = get_state()
        agent.learn(state, currentGreen, reward, next_state)

        # Reset signals
        for i in range(noOfSignals):
            if i == currentGreen:
                signals[i].green = random.randint(10, 20)
                signals[i].yellow = defaultYellow
                signals[i].red = defaultRed
            else:
                signals[i].red += signals[currentGreen].green + signals[currentGreen].yellow

def showStats():
    totalVehicles = 0
    print('Direction-wise Vehicle Counts')
    for i in range(0,4):
        if(signals[i]!=None):
            print('Direction',i+1,':',vehicles[directionNumbers[i]]['crossed'])
            totalVehicles += vehicles[directionNumbers[i]]['crossed']
    print('Total vehicles passed:',totalVehicles)
    print('Total time:',timeElapsed)
def get_state():
    """Return a simplified state for RL agent - vehicles waiting at each direction."""
    state = []
    for i in range(noOfSignals):
        count = len(vehicles[directionNumbers[i]])
        state.append(min(count, 9))  # Cap at 9 to limit state space
    return tuple(state)
def simTime():
    global timeElapsed, simulationTime
    while(True):
        timeElapsed += 1
        time.sleep(1)
        if(timeElapsed==simulationTime):
            showStats()
            os._exit(1)
def updateValues():
    for i in range(0, noOfSignals):
        if(i==currentGreen):
            if(currentYellow==0):
                signals[i].green-=1
            else:
                signals[i].yellow-=1
        else:
            signals[i].red-=1
def generateVehicles():
    while(True):
        vehicle_type = random.choice(allowedVehicleTypesList)
        lane_number = random.randint(1,2)
        will_turn = 0
        if(lane_number == 1):
            temp = random.randint(0,99)
            if(temp<40):
                will_turn = 1
        elif(lane_number == 2):
            temp = random.randint(0,99)
            if(temp<40):
                will_turn = 1
        temp = random.randint(0,99)
        direction_number = 0
        dist = [25,50,75,100]
        if(temp<dist[0]):
            direction_number = 0
        elif(temp<dist[1]):
            direction_number = 1
        elif(temp<dist[2]):
            direction_number = 2
        elif(temp<dist[3]):
            direction_number = 3
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number], will_turn)
        time.sleep(1)
class QLearningAgent:
    def __init__(self, actions):
        self.q_table = {}
        self.actions = actions
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.05

    def get_q(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        q_values = [self.get_q(state, a) for a in self.actions]
        max_q = max(q_values)
        return self.actions[q_values.index(max_q)]

    def learn(self, state, action, reward, next_state):
        current_q = self.get_q(state, action)
        max_future_q = max([self.get_q(next_state, a) for a in self.actions])
        new_q = current_q + self.alpha * (reward + self.gamma * max_future_q - current_q)
        self.q_table[(state, action)] = new_q
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

class Main:
    global allowedVehicleTypesList
    i = 0
    for vehicleType in allowedVehicleTypes:
        if (allowedVehicleTypes[vehicleType]):
            allowedVehicleTypesList.append(i)
        i += 1
    thread1 = threading.Thread(name="initialization", target=initialize, args=())
    thread1.daemon = True
    thread1.start()

    black = (0, 0, 0)
    white = (255, 255, 255)
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)
    background = pygame.image.load('images/intersection.png')
    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)

    thread2 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())
    thread2.daemon = True
    thread2.start()

    # thread for simulation duration check
    thread3 = threading.Thread(name="simTime", target=simTime, args=())
    thread3.daemon = True
    thread3.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # show statistics when simulation is quit
                showStats()
                sys.exit()
        screen.blit(background, (0, 0))
        for i in range(0, noOfSignals):
            if (i == currentGreen):
                if (currentYellow == 1):
                    signals[i].signalText = signals[i].yellow
                    screen.blit(yellowSignal, signalCoods[i])
                else:
                    signals[i].signalText = signals[i].green
                    screen.blit(greenSignal, signalCoods[i])
            else:
                if (signals[i].red <= 10):
                    signals[i].signalText = signals[i].red
                else:
                    signals[i].signalText = "---"
                screen.blit(redSignal, signalCoods[i])
        signalTexts = ["", "", "", ""]

        for i in range(0, noOfSignals):
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i], signalTimerCoods[i])

        # display vehicle count
        for i in range(0, noOfSignals):
            displayText = vehicles[directionNumbers[i]]['crossed']
            vehicleCountTexts[i] = font.render(str(displayText), True, black, white)
            screen.blit(vehicleCountTexts[i], vehicleCountCoods[i])

        # display time elapsed
        timeElapsedText = font.render(("Time Elapsed: " + str(timeElapsed)), True, black, white)
        screen.blit(timeElapsedText, timeElapsedCoods)

        for vehicle in simulation:
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()
        pygame.display.update()
Main()