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

from pacman import Directions
from game import Agent
import api
import random
import game
import util
from copy import copy, deepcopy

class PartialAgent(Agent):

    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like I just died!"
        #need to re-initialize pacmans internal variables before every game
        self.init = False

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up!"
        name = "Pacman"
        #defines if the internal map has been initialized yet
        self.init = False
        #define the internal map
        self.map = None
        # defines which directions are opposite from one another
        self.opposite = {Directions.WEST: Directions.EAST, Directions.EAST: Directions.WEST,
            Directions.NORTH: Directions.SOUTH, Directions.SOUTH: Directions.NORTH}
        # define what direction in matrix corresponds to direction pacman must move in
        self.possibleMoves = [((-1,0), Directions.WEST), ((1,0), Directions.EAST),
            ((0,1),Directions.NORTH), ((0,-1),Directions.SOUTH)]
        #stores a list of moves for pacman to get to target destination
        self.path = []
        #stores last known position of a ghost
        #self.ghost = False
        self.legal = []
        self.newUpdate = False

    #this function takes 2 positions and returns their sum
    def sumPair(self, pair1, pair2):
        #print "sumPair"
        newX = pair1[0] + pair2[0]
        newY = pair1[1] + pair2[1]
        return (newX, newY)

    #this function sets the legal moves for each action
    def setLegal(self, state):
        #print "setLegal"
        self.legal = api.legalActions(state)
        if Directions.STOP in self.legal:
            self.legal.remove(Directions.STOP)

    #this function initializes pacman's internal map by constructing it with available knowledge. Also resets its internal values
    def initialize(self, state):
        print "initializing map"
        #sets the path of pacman to be empty
        self.path = []
        #sets the internal map of pacman to be empty
        self.map = None
        # get location of all visible food
        foods = api.food(state)
        #get location of all corners
        corners = api.corners(state)
        #get location of all visible capsules
        capsules = api.capsules(state)
        # Get the actions we can try, and remove "STOP" if that is one of them.
        #legal = api.legalActions(state)
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
            #print "width and height"
            #print width
            #print height
            #once the size of the map has been identified, fill it up with "?", as pacman does not know what is in there
            self.map = [["?" for y in range(height+1)] for x in range(width+1)]
            #now add in all the information pacman knows initially. starting with all known locations of food
            for food in foods:
                #use "F" to mark food on the map
                self.map[food[0]][food[1]] = "F"
            #now mark the location of capsules on the map, this time using "C"
            for capsule in capsules:
                self.map[capsule[0]][capsule[1]] = "C"
            #now mark the location of the walls on the map, using "W"
            for wall in walls:
                #print wall
                self.map[wall[0]][wall[1]] = "W"
            #last pacman knows where it is, so mark that as "P"
            self.map[pacmanX][pacmanY] = "P"

            #for row in self.map:
            #    print row
        #set init to true as the map has been initialized
        for row in self.map:
            print row

        self.init = True

    def updateMap(self, state):
        print "updateMap"
        # get location of all visible food
        foods = api.food(state)
        #get location of all visible capsules
        capsules = api.capsules(state)

        print foods
        for food in foods:
            #use "F" to mark food on the map
            self.map[food[0]][food[1]] = "F"
        #now mark the location of capsules on the map, this time using "C"
        print capsules
        for capsule in capsules:
            self.map[capsule[0]][capsule[1]] = "C"

        for row in self.map:
            print row


    def checkAdjacent(self, state):
        print "checkAdjacent"
        # Get the actions we can try, and remove "STOP" if that is one of them.
        #legal = api.legalActions(state)
        #if Directions.STOP in legal:
        #    legal.remove(Directions.STOP)
        #get pacmans position
        pacman = api.whereAmI(state)

        unknown = False
        #searches all squares of distance 1
        for move in self.possibleMoves:
            direction = move[1]
            if direction in self.legal:
                deltaPosition = move[0]
                nextPosition = self.sumPair(pacman, deltaPosition)

                if self.map[nextPosition[0]][nextPosition[1]] == "?":
                    self.map[nextPosition[0]][nextPosition[1]] = "P"
                    unknown = True

        return unknown


    def getDFSQueue(self, state):
        print "getDFSQueue"

        # Get the actions we can try, and remove "STOP" if that is one of them.
        #legal = api.legalActions(state)
        #if Directions.STOP in legal:
        #    legal.remove(Directions.STOP)
        #get pacmans position
        pacman = api.whereAmI(state)
        x = pacman[0]
        y = pacman[1]

        #initialize the queue for a Depth First Seach
        bfsQueue = []

        #searches all squares of distance 1
        for move in self.possibleMoves:
            direction = move[1]
            if direction in self.legal:
                deltaPosition = move[0]
                nextPosition = self.sumPair(pacman, deltaPosition)
                #list of position, move pairs
                path = [(nextPosition, direction)]
                #add in a position list pairs
                bfsQueue.append((nextPosition, path))

        return bfsQueue

    def findPath(self, state):
        print "findPath"
        #initialize the queue for a Depth First Seach
        bfsQueue = self.getDFSQueue(state)
        #copy of the current state of internal map
        copyMap = deepcopy(self.map)

        #conducts bfs search
        while len(bfsQueue) != 0:
            nextCheck = bfsQueue.pop(0)
            nextCheckPosition = nextCheck[0]
            possibleX = nextCheckPosition[0]
            possibleY = nextCheckPosition[1]
            if self.map[possibleX][possibleY] == "F" or self.map[possibleX][possibleY] == "?" or self.map[possibleX][possibleY] == "C":
                print "next move"
                nextMove = nextCheck[1].pop(0)
                self.path = nextCheck[1]
                self.map[nextMove[0][0]][nextMove[0][1]] = "P"
                return api.makeMove(nextMove[1], api.legalActions(state))

            else:
                print "searching bfs"
                for move in self.possibleMoves:
                    nextPosition = self.sumPair(move[0], nextCheckPosition)
                    if self.map[nextPosition[0]][nextPosition[1]] != "W" and copyMap[nextPosition[0]][nextPosition[1]] != "X":
                        copyMap[nextPosition[0]][nextPosition[1]] = "X"
                        path = deepcopy(nextCheck[1])
                        path.append((nextPosition, move[1]))
                        bfsQueue.append((nextPosition, path))

        print "no move"
        for row in self.map:
            print row
        return api.makeMove(Directions.STOP,  api.legalActions(state))

    def runAway(self, state):
        print "runaway!"
        print api.whereAmI(state)
        #legal = api.legalActions(state)
        #legal.remove(Directions.STOP)
        ghosts = api.ghosts(state)
        print ghosts

        bfsQueue = self.getDFSQueue(state)
        copyMap = deepcopy(self.map)
        count = 0

        while len(bfsQueue) != 0 and len(bfsQueue[0][1]) < 3:
            count = count + 1
            nextCheck = bfsQueue.pop(0)
            nextCheckPosition = nextCheck[0]
            possibleX = nextCheckPosition[0]
            possibleY = nextCheckPosition[1]

            if nextCheckPosition in ghosts:
                print "next move"

                self.ghost = nextCheckPosition
                nextMove = nextCheck[1].pop(0)
                self.path = nextCheck[1]
                dirGhost = nextMove[1]
                if dirGhost in self.legal:
                    self.legal.remove(dirGhost)
                dirOpposite = self.opposite[dirGhost]

                if dirOpposite in self.legal:
                    print dirOpposite
                    #deltaPosition = None
                    for directions in self.possibleMoves:
                        if dirOpposite == directions[1]:
                            deltaPosition = directions[0]
                            nextPosition = self.sumPair(deltaPosition, (nextMove[0][0], nextMove[0][1]))
                    self.map[nextPosition[0]][nextPosition[1]] = "P"
                    self.path = []

                    #return self.findPath(state)

                    #return api.makeMove(self.opposite[nextMove[1]], self.legal)

                #else:
                #    if len(self.legal) == 0:
                #        print "trapped"
                #        self.path = []
                #        return api.makeMove(Directions.STOP, self.legal)

                    #pick = random.choice(self.legal)
                    #print pick
                    #self.path = []
                    #return api.makeMove(pick, self.legal)

                    #return self.findPath(state)

            else:
                for move in self.possibleMoves:
                    nextPosition = self.sumPair(move[0], nextCheckPosition)
                    if self.map[nextPosition[0]][nextPosition[1]] != "W" and copyMap[nextPosition[0]][nextPosition[1]] != "X":
                        copyMap[nextPosition[0]][nextPosition[1]] = "X"
                        path = deepcopy(nextCheck[1])
                        path.append((nextPosition, move[1]))
                        bfsQueue.append((nextPosition, path))

        print "Not running away"
        return self.findPath(state)

    # For now I just move randomly
    def getAction(self, state):

        #legal = api.legalActions(state)
        # if the internal map of the environment has yet to be initialized, initialize it
        if not self.init:
            self.initialize(state)

        self.setLegal(state)

        #if pacman can detect a ghost nearby pacman needs to run away
        if api.ghosts(state):
            #self.path = []
            return self.runAway(state)

        '''
        if self.newUpdate:
            self.updateMap(state)
            self.newUpdate = False

        unknownAdjacent = self.checkAdjacent(state)

        if unknownAdjacent:
            self.newUpdate = True
            print "new map"
            return api.makeMove(Directions.STOP, self.legal)
        '''
        #if a route has been found, pacman will follow it instead of searching again
        if len(self.path) != 0:
            nextMove = self.path.pop(0)
            self.map[nextMove[0][0]][nextMove[0][1]] = "P"
            if nextMove[1] in self.legal:
                return api.makeMove(nextMove[1], self.legal)
            else:
                return self.findPath(state)
        else:
            return self.findPath(state)
