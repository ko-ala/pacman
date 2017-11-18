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

class GreedyAgent2(Agent):
    def final(self, state):
        #print "Looks like I just died!"
        #need to re-initialize pacmans internal variables before every game
        self.init = False

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        #print "Starting up!"
        name = "Pacman"
        #defines if the internal map has been initialized yet
        self.init = False
        #define the internal map
        self.map = None
        # define what direction in matrix corresponds to direction pacman must move in
        self.possibleMoves = [((-1,0), Directions.WEST), ((0,1),Directions.NORTH), ((1,0), Directions.EAST), ((0,-1),Directions.SOUTH)]
        #stores a list of moves for pacman to get to target destination
        #self.path = []
        #list of legal moves for this turn
        self.legal = []
        #the last direction pacman travelled in
        #self.lastDir = None
        self.pacman = []
        self.ghosts = []

    #this function initializes pacman's internal map by constructing it with available knowledge. Also resets its internal values
    def initialize(self, state):
        #print "initializing map"
        #sets the internal map of pacman to be empty
        self.map = None
        # get location of all visible food
        foods = api.food(state)
        #get location of all corners
        corners = api.corners(state)
        #get location of all visible capsules
        capsules = api.capsules(state)
        # Get the actions we can try, and remove "STOP" if that is one of them.
        #get location of all visible walls
        walls = api.walls(state)
        #get pacmans position
        pacman = api.whereAmI(state)
        pacmanX = pacman[0]
        pacmanY = pacman[1]

        #if the internal map has not been initialized
        if self.map == None:
            #finds the dimension of the map by location the extremes, in this case the corners
            width = 0
            height = 0
            for corner in corners:
                if corner[0] > width:
                    width = corner[0]
                if corner[1] > height:
                    height = corner[1]

            #once the size of the map has been identified, fill it up with "?", as pacman does not know what is in there
            self.map = [[0 for y in range(height+1)] for x in range(width+1)]
            #now add in all the information pacman knows initially. starting with all known locations of food
            for food in foods:
                #use "F" to mark food on the map
                self.map[food[0]][food[1]] = 10
            #now mark the location of capsules on the map, this time using "C"
            for capsule in capsules:
                self.map[capsule[0]][capsule[1]] = 5
            #now mark the location of the walls on the map, using "W"
            for wall in walls:
                self.map[wall[0]][wall[1]] = "W"

        #set init to true as the map has been initialized
        self.init = True

    #this function takes 2 positions and returns their sum
    def sumPair(self, pair1, pair2):
        ##print "sumPair"
        newX = pair1[0] + pair2[0]
        newY = pair1[1] + pair2[1]
        return (newX, newY)

    def setLegal(self, state):
        ##print "setLegal"
        self.legal = api.legalActions(state)
        self.pacman = api.whereAmI(state)
        self.ghosts = api.ghosts(state)

    def getMove(self, state):

        scores = [0,0,0,0]
        #searches all adjacent squares
        for i in range(len(self.possibleMoves)):
            direction = self.possibleMoves[i][1]
            #see if surrounding locations are legal moves. if so, add it to the search
            if direction in self.legal:
                deltaPosition = self.possibleMoves[i][0]
                nextPosition = self.sumPair(self.pacman, deltaPosition)
                if nextPosition in self.ghosts:
                    scores[i] = -10
                else:
                    positionScore = self.map[nextPosition[0]][nextPosition[1]]
                    scores[i] = positionScore
            else:
                scores[i] = -1

        cumulativeScore = [0,0,0,0]
        for i in range(len(scores)):
            if self.possibleMoves[i][1] in self.legal:
                cumulativeScore[i] = .1*scores[(i + 4) % 4] + .8*scores[i] + .1*scores[(i + 1) % 4]
            else:
                cumulativeScore[i] = -100


        max = -100
        index = 0
        for i in range(len(cumulativeScore)):
            if cumulativeScore[i] > max:
                index = i
                max = cumulativeScore[i]

        return api.makeMove(self.possibleMoves[index][1], self.legal)



    def getAction(self, state):
        if not self.init:
            self.initialize(state)
        #update the legal moves for this move
        self.setLegal(state)

        if self.map[self.pacman[0]][self.pacman[1]] < 0:
            self.map[self.pacman[0]][self.pacman[1]] = self.map[self.pacman[0]][self.pacman[1]] - 1
        else:
            self.map[self.pacman[0]][self.pacman[1]] = -1

        print "map"
        for row in self.map:
            print row

        return self.getMove(state)
