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
        #sets the path of pacman to be empty
        #self.path = []
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

    def runAway(self, state):
        #print "runaway!"

        #legal = api.legalActions(state)
        x = self.pacman[0]
        y = self.pacman[1]
        #initialize the queue for a Breath First Seach
        bfsQueue = []
        #searches all adjacent squares
        for move in self.possibleMoves:
            direction = move[1]
            #see if surrounding locations are legal moves. if so, add it to the search
            if direction in self.legal:
                deltaPosition = move[0]
                nextPosition = self.sumPair(self.pacman, deltaPosition)
                #list of position, move pairs
                path = [(nextPosition, direction)]
                #add in a position list pair to the queue
                bfsQueue.append((nextPosition, path))

        copyMap = deepcopy(self.map)
        #set the maximum distance to look for ghost to be 3
        maxDistGhost = 3

        #conduct the BFS search
        while len(bfsQueue) != 0 and len(bfsQueue[0][1]) < maxDistGhost:
            #print "finding ghost"
            #pop the element from the queue
            nextCheck = bfsQueue.pop(0)
            #get the position stored at element
            nextCheckPosition = nextCheck[0]
            #if the position searched is the position of the ghost
            if nextCheckPosition in self.ghosts:
                position = bfsQueue[-1][0]
                self.map[position[0]][position[1]] = -10
            #if the position is not contained in ghosts, continue the search
            else:
                for move in self.possibleMoves:
                    #get the next position in the search
                    nextPosition = self.sumPair(move[0], nextCheckPosition)
                    #if this postion is neither a wall nor a location already searched by the algorithm, add it to the search
                    if self.map[nextPosition[0]][nextPosition[1]] != "W" and copyMap[nextPosition[0]][nextPosition[1]] != "X":
                        #mark this location as searched by the BFS algorithm
                        if not nextPosition in self.ghosts:
                            copyMap[nextPosition[0]][nextPosition[1]] = "X"
                        #copy the existing path from the search into a new variable
                        path = deepcopy(nextCheck[1])
                        #add in the new loation and the direction to move to said location to the path
                        path.append((nextPosition, move[1]))
                        #add the path to the bfsQueue
                        bfsQueue.append((nextPosition, path))
        return self.getMove(self)

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

        if self.map[self.pacman[0]][self.pacman[1]] < 10:
            self.map[self.pacman[0]][self.pacman[1]] = self.map[self.pacman[0]][self.pacman[1]] - 1
        else:
            self.map[self.pacman[0]][self.pacman[1]] = -1

        #if pacman can detect a ghost nearby pacman needs to run away
        if self.ghosts:
            return self.runAway(state)

        return self.getMove(state)



class PartialAgent(Agent):

    # This is what gets run in between multiple games
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
        self.possibleMoves = [((-1,0), Directions.WEST), ((1,0), Directions.EAST),
            ((0,1),Directions.NORTH), ((0,-1),Directions.SOUTH)]
        #stores a list of moves for pacman to get to target destination
        self.path = []
        #list of legal moves for this turn
        self.legal = []
        #the last direction pacman travelled in
        self.lastDir = None

    #this function takes 2 positions and returns their sum
    def sumPair(self, pair1, pair2):
        ##print "sumPair"
        newX = pair1[0] + pair2[0]
        newY = pair1[1] + pair2[1]
        return (newX, newY)

    #this function sets the legal moves for each action
    def setLegal(self, state):
        ##print "setLegal"
        self.legal = api.legalActions(state)
        if Directions.STOP in self.legal:
            self.legal.remove(Directions.STOP)

    #this function initializes pacman's internal map by constructing it with available knowledge. Also resets its internal values
    def initialize(self, state):
        #print "initializing map"
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
                self.map[wall[0]][wall[1]] = "W"
            #last pacman knows where it is, so mark that as "P"
            self.map[pacmanX][pacmanY] = "P"

        #set init to true as the map has been initialized
        self.init = True


    #this function returns a BFS search of the 4 adjacent positions relative to pacman.
    #Queue is a list of position path pairs, where the path is the path pacman takes to get to the position
    def getBFSQueue(self, state):
        #print "getBFSQueue"
        #get pacmans position
        pacman = api.whereAmI(state)
        x = pacman[0]
        y = pacman[1]
        #initialize the queue for a Breath First Seach
        bfsQueue = []

        #searches all adjacent squares
        for move in self.possibleMoves:
            direction = move[1]
            #see if surrounding locations are legal moves. if so, add it to the search
            if direction in self.legal:
                deltaPosition = move[0]
                nextPosition = self.sumPair(pacman, deltaPosition)
                #list of position, move pairs
                path = [(nextPosition, direction)]
                #add in a position list pair to the queue
                bfsQueue.append((nextPosition, path))

        return bfsQueue

    #this method queires a bfsQueue from getBFSQueue() and finds the shortest path to either food or unknown areas of the environment
    def findPath(self, state):
        #print "findPath"
        #initialize the queue for a Depth First Seach
        bfsQueue = self.getBFSQueue(state)
        #copy of the current state of internal map to mark searched nodes
        copyMap = deepcopy(self.map)

        #conducts bfs search
        while len(bfsQueue) != 0:
            #pop the element from the queue
            nextCheck = bfsQueue.pop(0)
            #get the position stored at element
            nextCheckPosition = nextCheck[0]
            #extract x position from position
            possibleX = nextCheckPosition[0]
            #extract y position from position
            possibleY = nextCheckPosition[1]
            #if the position contains food, a capsule, or is unknown, pacman will visit it
            if self.map[possibleX][possibleY] == "F" or self.map[possibleX][possibleY] == "?" or self.map[possibleX][possibleY] == "C":
                #print "next move"
                #pop the first step of the path stored in the currently searching element
                nextMove = nextCheck[1].pop(0)
                #set the internal path of pacman to the one found by the BFS
                self.path = nextCheck[1]
                #mark the position on the map as "P" to mark visited positions
                self.map[nextMove[0][0]][nextMove[0][1]] = "P"
                #set lastDir as the next move
                self.lastDir = nextMove[1]
                #return the popped direction stored at the frist step above as the next move
                return api.makeMove(self.lastDir, api.legalActions(state))
            else:
                #if position does not contain food, capsule, or unknown information, continue the BFS search
                #print "searching bfs"
                #check all possibleMoves from the current popped from the queue in the current iteration of the BFS algorithm
                for move in self.possibleMoves:
                    #get the next position in the search
                    nextPosition = self.sumPair(move[0], nextCheckPosition)
                    #if this postion is neither a wall nor a location already searched by the algorithm, add it to the search
                    if self.map[nextPosition[0]][nextPosition[1]] != "W" and copyMap[nextPosition[0]][nextPosition[1]] != "X":
                        #mark this location as searched by the BFS algorithm
                        copyMap[nextPosition[0]][nextPosition[1]] = "X"
                        #copy the existing path from the search into a new variable
                        path = deepcopy(nextCheck[1])
                        #add in the new loation and the direction to move to said location to the path
                        path.append((nextPosition, move[1]))
                        #add the path to the bfsQueue
                        bfsQueue.append((nextPosition, path))

        #if no moves are available, pacman will not move
        self.lastDir = Directions.STOP
        return api.makeMove(Directions.STOP,  api.legalActions(state))

    #this method discovers the shortest paths to a visible ghost and removes those directions from possible directions pacman can travel in
    def runAway(self, state):
        #print "runaway!"
        #retireve the location of visible ghosts
        ghosts = api.ghosts(state)
        #gets a bfsQueue from getBFSQueue
        bfsQueue = self.getBFSQueue(state)
        #copy the map to mark nodes already searched in BFS
        copyMap = deepcopy(self.map)
        #set the maximum distance to look for ghost to be 3
        maxDistGhost = 3

        #conduct the BFS search
        while len(bfsQueue) != 0 and len(bfsQueue[0][1]) < maxDistGhost:
            #print "finding ghost"
            #pop the element from the queue
            nextCheck = bfsQueue.pop(0)
            #get the position stored at element
            nextCheckPosition = nextCheck[0]
            #if the position searched is the position of the ghost
            if nextCheckPosition in ghosts:
                #pop the first step of the path stored in the currently searching element
                nextMove = nextCheck[1].pop(0)
                #set the variable of the directional to the ghost as dirGhost
                dirGhost = nextMove[1]
                #if dirGhost is in list of legal moves, remove it
                if dirGhost in self.legal:
                    self.legal.remove(dirGhost)
            #if the position is not contained in ghosts, continue the search
            else:
                for move in self.possibleMoves:
                    #get the next position in the search
                    nextPosition = self.sumPair(move[0], nextCheckPosition)
                    #if this postion is neither a wall nor a location already searched by the algorithm, add it to the search
                    if self.map[nextPosition[0]][nextPosition[1]] != "W" and copyMap[nextPosition[0]][nextPosition[1]] != "X":
                        #mark this location as searched by the BFS algorithm
                        if not nextPosition in ghosts:
                            copyMap[nextPosition[0]][nextPosition[1]] = "X"
                        #copy the existing path from the search into a new variable
                        path = deepcopy(nextCheck[1])
                        #add in the new loation and the direction to move to said location to the path
                        path.append((nextPosition, move[1]))
                        #add the path to the bfsQueue
                        bfsQueue.append((nextPosition, path))

        return self.findPath(state)

    # For now I just move randomly
    def getAction(self, state):
        #if the internal map of the environment has yet to be initialized, initialize it
        if not self.init:
            self.initialize(state)
        #update the legal moves for this move
        self.setLegal(state)

        #if pacman can detect a ghost nearby pacman needs to run away
        if api.ghosts(state):
            return self.runAway(state)

        #if a route has been found, pacman will follow it instead of searching again
        if len(self.path) != 0:
            #pop off the first move in the path
            nextMove = self.path.pop(0)
            #check that the move is legal
            if nextMove[1] in self.legal:
                #mark that position as visited with "P"
                self.map[nextMove[0][0]][nextMove[0][1]] = "P"
                self.lastDir = nextMove[1]
                #return the move
                return api.makeMove(self.lastDir, self.legal)
            #if the move is not legal, find a new path
            else:
                return self.findPath(state)
        #otherwise find a path
        else:
            return self.findPath(state)
