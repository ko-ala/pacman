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
        self.phost = None

    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like I just died!"

    def sumPair(self, pair1, pair2):
        newX = pair1[0] + pair2[0]
        newY = pair1[1] + pair2[1]
        return (newX, newY)

    #this function initializes pacman's internal map by constructing it with available knowledge
    def initialize(self, state):

        # get location of all visible food
        foods = api.food(state)
        #get location of all corners
        corners = api.corners(state)
        #get location of all visible capsules
        capsules = api.capsules(state)
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        #get location of all visible walls
        walls = api.walls(state)
        #get pacmans position
        pacman = api.whereAmI(state)
        x = pacman[0]
        y = pacman[1]

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
                self.map[capsule[0]][capsule[1]] = "F"
            #now mark the location of the walls on the map, using "W"
            for wall in walls:
                #print wall
                self.map[wall[0]][wall[1]] = "W"
            #last pacman knows where it is, so mark that as "P"
            self.map[x][y] = "P"

            #for row in self.map:
            #    print row
        #set init to true as the map has been initialized
        self.init = True

    def getDFSQueue(self, state):

        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        #get pacmans position
        pacman = api.whereAmI(state)
        x = pacman[0]
        y = pacman[1]

        #initialize the queue for a Depth First Seach
        dfsQueue = []

        #searches all squares of distance 1
        for move in self.possibleMoves:
            direction = move[1]
            if direction in legal:
                deltaPosition = move[0]
                nextPosition = self.sumPair(pacman, deltaPosition)
                #list of position, move pairs
                path = [(nextPosition, direction)]
                #add in a position list pairs
                dfsQueue.append((nextPosition, path))

        return dfsQueue

    def findPath(self, state):

        #initialize the queue for a Depth First Seach
        dfsQueue = self.getDFSQueue(state)

        copyMap = deepcopy(self.map)

        #conducts bfs search
        while len(dfsQueue) != 0:
            nextCheck = dfsQueue.pop(0)
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
                print "searching dfs"
                for move in self.possibleMoves:
                    nextPosition = self.sumPair(move[0], nextCheckPosition)
                    if self.map[nextPosition[0]][nextPosition[1]] != "W" and copyMap[nextPosition[0]][nextPosition[1]] != "X":
                        copyMap[nextPosition[0]][nextPosition[1]] = "X"
                        path = deepcopy(nextCheck[1])
                        path.append((nextPosition, move[1]))
                        dfsQueue.append((nextPosition, path))

        print "no move"
        return api.makeMove(Directions.STOP, legal)

    def runAway(self, state):
        print "runaway!"
        legal = api.legalActions(state)
        legal.remove(Directions.STOP)
        ghosts = api.ghosts(state)

        dfsQueue = self.getDFSQueue(state)
        copyMap = deepcopy(self.map)
        count = 0

        while len(dfsQueue) != 0 and count < 4:
            count = count + 1
            nextCheck = dfsQueue.pop(0)
            nextCheckPosition = nextCheck[0]
            possibleX = nextCheckPosition[0]
            possibleY = nextCheckPosition[1]

            if nextCheckPosition in ghosts:
                print "next move"
                
                self.ghost = nextCheckPosition
                nextMove = nextCheck[1].pop(0)
                self.path = nextCheck[1]

                self.map[nextMove[0][0]][nextMove[0][1]] = "P"
                if self.opposite[nextMove[1]] in legal:
                    return api.makeMove(self.opposite[nextMove[1]], legal)
                else:
                    legal.remove(nextMove[1])
                    pick = random.choice(legal)
                    return api.makeMove(pick, legal)
            else:
                for move in self.possibleMoves:
                    nextPosition = self.sumPair(move[0], nextCheckPosition)
                    if self.map[nextPosition[0]][nextPosition[1]] != "W" and copyMap[nextPosition[0]][nextPosition[1]] != "X":
                        copyMap[nextPosition[0]][nextPosition[1]] = "X"
                        path = deepcopy(nextCheck[1])
                        path.append((nextPosition, move[1]))
                        dfsQueue.append((nextPosition, path))

                #possibleMoves = [((x-1,y),Directions.WEST), ((x+1,y), Directions.EAST), ((x,y+1), Directions.NORTH),((x,y-1), Directions.SOUTH)]
                #print "searching dfs"
                #for move in possibleMoves:
                #    ghostX = move[0][0]
                #    ghostY = move[0][1]
                #    if self.map[ghostX][ghostY] != "W" and copyMap[ghostX][ghostY] != "X":
                #        copyMap[ghostX][ghostY] = "X"
                #        route = deepcopy(nextPossible[1])
                #        path = deepcopy(nextPossible[2])
                #        route.append(move[0])
                #        path.append(move[1])
                #        dfsQueue.append((move[0], route, path))
        return api.makeMove(random.choice(legal), legal)

    # For now I just move randomly
    def getAction(self, state):
        legal = api.legalActions(state)
        # if the internal map of the environment has yet to be initialized, initialize it
        if not self.init:
            self.initialize(state)

        #if pacman can detect a ghost nearby pacman needs to run away
        if api.ghosts(state):
            self.path = []
            return self.runAway(state)

        #if a route has been found, pacman will follow it instead of searching again
        if len(self.path) != 0:
            nextMove = self.path.pop(0)
            self.map[nextMove[0][0]][nextMove[0][1]] = "P"
            return api.makeMove(nextMove[1], legal)
        else:
            return self.findPath(state)
