# partialAgent.py
# parsons/15-oct-2017
#
# Version 1
#
# The starting point for CW1.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py
#python pacman.py -n 1000 -p PartialAgent -l mediumClassic --frameTime=0.001
from pacman import Directions
from game import Agent
import api
import random
import game
import util
from copy import copy, deepcopy
from random import *
from math import *

class SimpleMDPAgent(Agent):

    def final(self, state):
        self.init = False

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        #print "Starting up!"
        name = "Pacman"
        #defines if the internal map has been initialized yet
        self.init = False
        #define the internal map
        self.reward = None
        self.ghostReward = None
        self.utility = None
        # define what direction in matrix corresponds to direction pacman must move in
        self.possibleMoves = [((-1,0), Directions.WEST), ((0,1),Directions.NORTH), ((1,0), Directions.EAST), ((0,-1),Directions.SOUTH)]
        #list of legal moves for this turn
        self.legal = []
        self.pacman = ()
        self.ghosts = []
        self.discount = .6
        self.threshold = 0.000001

    #this function initializes pacman's internal map by constructing it with available knowledge. Also resets its internal values
    def initialize(self, state):
        #sets the reward of each grid
        self.reward = None
        #set the utility of each grid
        self.utility = None
        # get location of all visible food
        foods = api.food(state)
        #get location of all corners
        corners = api.corners(state)
        #get location of all visible capsules
        capsules = api.capsules(state)
        #get location of all visible walls
        walls = api.walls(state)
        #get pacmans position
        pacman = api.whereAmI(state)
        pacmanX = pacman[0]
        pacmanY = pacman[1]

        #if the internal map has not been initialized
        if self.reward == None and self.utility == None:
            #finds the dimension of the map by location the extremes, in this case the corners
            width = 0
            height = 0
            for corner in corners:
                if corner[0] > width:
                    width = corner[0]
                if corner[1] > height:
                    height = corner[1]

            #once the size of the map has been identified, fill it up with "?", as pacman does not know what is in there
            self.reward = [[-1 for y in range(height+1)] for x in range(width+1)]
            self.utility = [[random() for y in range(height+1)] for x in range(width+1)]
            #now add in all the information pacman knows initially. starting with all known locations of food
            for food in foods:
                #use "F" to mark food on the map
                self.reward[food[0]][food[1]] = 10
            #now mark the location of capsules on the map, this time using "C"
            for capsule in capsules:
                self.reward[capsule[0]][capsule[1]] = 5
            #now mark the location of the walls on the map, using "W"
            for wall in walls:
                self.reward[wall[0]][wall[1]] = "W"
                self.utility[wall[0]][wall[1]] = "W"

        #set init to true as the map has been initialized
        self.init = True

    def sumPair(self, pair1, pair2):
        newX = pair1[0] + pair2[0]
        newY = pair1[1] + pair2[1]
        return (newX, newY)

    def updateMap(self,state):
        #print "updateMap"
        reward = deepcopy(self.reward)
        '''
        # get location of all visible food
        foods = api.food(state)
        #get location of all visible capsules
        capsules = api.capsules(state)
        '''
        ghosts = api.ghostStatesWithTimes(state)
        '''
        #get location of all visible walls
        walls = api.walls(state)
        #now add in all the information pacman knows initially. starting with all known locations of food
        for food in foods:
            #use "F" to mark food on the map
            reward[food[0]][food[1]] = 10
        #now mark the location of capsules on the map, this time using "C"
        for capsule in capsules:
            reward[capsule[0]][capsule[1]] = 5
        '''
        for ghost in ghosts:
            ghostX = int(ghost[0][0])
            ghostY = int(ghost[0][1])
            if(ghost[1] > 0):
                reward[ghostX][ghostY] = reward[ghostX][ghostY]  + 11
                if(ghostX == ghost[0][0] and ghostY == ghost[0][1]):
                    reward[ghostX + 1][ghostY + 1] = reward[ghostX][ghostY]  + 10
            else:
                reward = self.markGhost(state, reward)
                #need to change reward of adjacent squares as well
                #reward[ghostX][ghostY] = reward[ghostX][ghostY] - 10
        '''
        #now mark the location of the walls on the map, using "W"
        for wall in walls:
            self.reward[wall[0]][wall[1]] = "W"
            self.utility[wall[0]][wall[1]] = "W"
        '''
        return reward

    def markGhost(state, reward):
        

    def bellman(self, state, reward):

        width = len(self.utility)
        height = len(self.utility[0])
        minDif = 10000
        count = 0
        while(minDif > self.threshold and count < 100000):
            newUtility = deepcopy(self.utility)
            #for every grid in the map
            maxDif = -10000
            for y in range(0, height):
                for x in range(0, width):
                    if newUtility[x][y] != "W":
                        #maxUtility = -1000000
                        scores = []
                        #scores = [-100000,-100000,-100000,-100000]
                        #need to fix
                        for i in range(len(self.possibleMoves)):
                            deltaForward = self.possibleMoves[i][0]
                            deltaLeft = self.possibleMoves[(i+3) % 4][0]
                            deltaRight = self.possibleMoves[(i+1) % 4][0]

                            nextForward = self.sumPair((x,y), deltaForward)
                            nextLeft = self.sumPair((x,y), deltaLeft)
                            nextRight = self.sumPair((x,y), deltaRight)

                            forwardUtility = self.utility[nextForward[0]][nextForward[1]]
                            leftUtility = self.utility[nextLeft[0]][nextLeft[1]]
                            rightUtility = self.utility[nextRight[0]][nextRight[1]]

                            if forwardUtility != "W":
                                left = 0.1
                                forward = 0.8
                                right = 0.1
                                if leftUtility == "W":
                                    leftUtility = self.utility[x][y]
                                if rightUtility == "W":
                                    rightUtility = self.utility[x][y]
                                adjUtility = left*leftUtility + forward*forwardUtility + right*rightUtility
                                #scores[i] = adjUtility
                                scores.append(adjUtility)

                        newUtility[x][y] = reward[x][y] + (self.discount * max(scores))
                        dif = abs(newUtility[x][y] - self.utility[x][y])
                        '''
                        print "maxDif"
                        print maxDif
                        print "dif"
                        print dif
                        '''
                        if dif > maxDif:
                            maxDif = dif
            if minDif >= maxDif:
                minDif = maxDif
            '''
            print "minDif"
            print minDif
            '''
            count = count + 1
            self.utility = newUtility
        print count

    def getMove(self,state):
        #print "getmove"
        maxScore = -10000000
        move = None
        for i in range(len(self.possibleMoves)):
            direction = self.possibleMoves[i][1]
            if direction in self.legal:
                deltaPosition = self.possibleMoves[i][0]
                nextPosition = self.sumPair(self.pacman, deltaPosition)
                positionScore = self.utility[nextPosition[0]][nextPosition[1]]
                if maxScore < positionScore:
                    maxScore = positionScore
                    move = direction
        if self.utility[self.pacman[0]][self.pacman[1]] > maxScore:
            print "dont move"
            return api.makeMove(Directions.STOP, self.legal)
        print self.pacman
        print move
        return api.makeMove(move, self.legal)

    def getAction(self, state):

        self.pacman = api.whereAmI(state)
        self.legal = api.legalActions(state)
        self.ghosts = api.ghosts(state)

        if not self.init:
            self.initialize(state)
        else:
        #    if self.reward[self.pacman[0]][self.pacman[1]] < 10:
        #        self.reward[self.pacman[0]][self.pacman[1]] = self.reward[self.pacman[0]][self.pacman[1]] - 1
        #    else:
                self.reward[self.pacman[0]][self.pacman[1]] = -1

        reward = self.updateMap(state)

        self.bellman(state, reward)
        '''
        print ''
        for row in reward:
            print row

        '''

        print ''
        for row in self.utility:
            print row


        return self.getMove(state)
        return api.makeMove(Directions.STOP, self.legal)
