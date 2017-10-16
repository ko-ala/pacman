# sampleAgents.py
# parsons/07-oct-2017
#
# Version 1.1
#
# Some simple agents to work with the PacMan AI projects from:
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

# The agents here are extensions written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util
from copy import copy, deepcopy

# RandomAgent
#
# A very simple agent. Just makes a random pick every time that it is
# asked for an action.
class RandomAgent(Agent):

    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # Random choice between the legal options.
        return api.makeMove(random.choice(legal), legal)

# RandomishAgent
#
# A tiny bit more sophisticated. Having picked a direction, keep going
# until that direction is no longer possible. Then make a random
# choice.
class RandomishAgent(Agent):

    # Constructor
    #
    # Create a variable to hold the last action
    def __init__(self):
         self.last = Directions.STOP

    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # If we can repeat the last action, do it. Otherwise make a
        # random choice.
        if self.last in legal:
            return api.makeMove(self.last, legal)
        else:
            pick = random.choice(legal)
            # Since we changed action, record what we did
            self.last = pick
            return api.makeMove(pick, legal)

# SensingAgent
#
# Doesn't move, but reports sensory data available to Pacman
class SensingAgent(Agent):

    def getAction(self, state):

        # Demonstrates the information that Pacman can access about the state
        # of the game.

        # What are the current moves available
        legal = api.legalActions(state)
        print "Legal moves: ", legal

        # Where is Pacman?
        pacman = api.whereAmI(state)
        print "Pacman position: ", pacman

        # Where are the ghosts?
        print "Ghost positions:"
        theGhosts = api.ghosts(state)
        for i in range(len(theGhosts)):
            print theGhosts[i]

        # How far away are the ghosts?
        print "Distance to ghosts:"
        for i in range(len(theGhosts)):
            print util.manhattanDistance(pacman,theGhosts[i])

        # Where are the capsules?
        print "Capsule locations:"
        print api.capsules(state)

        # Where is the food?
        print "Food locations: "
        print api.food(state)

        # Where are the walls?
        print "Wall locations: "
        print api.walls(state)

        # getAction has to return a move. Here we pass "STOP" to the
        # API to ask Pacman to stay where they are.
        return api.makeMove(Directions.STOP, legal)

class CornerSeekingAgent(Agent):

    def __init__(self):
        self.init = False
        self.map = None
        self.route = []
        self.path = []

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

        if self.map == None:
            width = 0
            height = 0
            for corner in corners:
                if corner[0] > width:
                    width = corner[0]
                if corner[1] > height:
                    height = corner[1]
            self.map = [["?" for y in range(height)] for x in range(width)]
            for wall in walls:
                self.map[wall[0]][wall[1]] = "W"
            for food in foods:
                self.map[food[0]][food[1]] = "F"
            for capsule in capsules:
                self.map[capsule[0]][capsule[1]] = "F"
            self.map[x][y] = "0"

        self.init = True


    def getAction(self, state):

        if not self.init:
            self.initialize(state)

        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)

        if len(self.route) != 0 and len(self.path) != 0:
            print "next move"
            nextPosition = self.route.pop(0)
            nextMove = self.path.pop(0)
            print nextPosition
            print nextMove
            self.map[nextPosition[0]][nextPosition[1]] = "0"
            return api.makeMove(nextMove, legal)

        #get pacmans position
        pacman = api.whereAmI(state)
        x = pacman[0]
        y = pacman[1]

        #initialize the queue for a Depth First Seach
        dfsQueue = []
        #remove the stop from pacman
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        print "current position"
        print "(" + str(x) + "," + str(y) + ")"
        print legal

        if Directions.WEST in legal:
            nextPosition = (x-1, y)
            route = [nextPosition]
            #route.append(nextPosition)
            path = [Directions.WEST]
            #path.append(Directions.WEST)
            dfsQueue.append((nextPosition, route, path))
        if Directions.EAST in legal:
            nextPosition = (x+1, y)
            route = [nextPosition]
            #route.append(nextPosition)
            path = [Directions.EAST]
            #path.append(Directions.EAST)
            dfsQueue.append((nextPosition, route, path))
        if Directions.NORTH in legal:
            nextPosition = (x, y+1)
            route = [nextPosition]
            #route.append(nextPosition)
            path = [Directions.NORTH]
            #path.append(Directions.NORTH)
            dfsQueue.append((nextPosition, route, path))
        if Directions.SOUTH in legal:
            nextPosition = (x, y-1)
            route = [nextPosition]
            #route.append(nextPosition)
            path = [Directions.SOUTH]
            #path.append(Directions.SOUTH)
            dfsQueue.append((nextPosition, route, path))

        print dfsQueue

        copyMap = deepcopy(self.map)

        while not len(dfsQueue) == 0:
            nextPossible = dfsQueue.pop(0)
            nextPossiblePosition = nextPossible[0]
            x = nextPossiblePosition[0]
            y = nextPossiblePosition[1]
            print "find move"
            print "(" + str(x) + "," + str(y) + ")"
            print nextPossible[1]

            for row in self.map:
                print row

            if self.map[x][y] == "F" or self.map[x][y] == "?":
                print "next move"
                nextPosition = nextPossible[1].pop(0)
                nextMove = nextPossible[2].pop(0)
                self.route = nextPossible[1]
                self.path = nextPossible[2]
                self.map[nextPosition[0]][nextPosition[1]] = "0"
                print nextPosition
                print nextMove
                return api.makeMove(nextMove, legal)

            else:
                possibleMoves = [((x-1,y),Directions.WEST), ((x+1,y), Directions.EAST), ((x,y+1), Directions.NORTH),((x,y-1), Directions.SOUTH)]
                print "searching dfs"
                for move in possibleMoves:
                    possibleX = move[0][0]
                    possibleY = move[0][1]
                    if self.map[possibleX][possibleY] != "W" and copyMap[possibleX][possibleY] != "X":
                        print move[1]
                        copyMap[x-1][y] = "X"
                        route = nextPossible[1]
                        path = nextPossible[2]
                        route.append(move[0])
                        path.append(move[1])
                        dfsQueue.append((move[0], route, path))
                #if self.map[x+1][y] != "W" and copyMap[x+1][y] != "X":
                #    print "east"
                #    position = (x+1,y)
                #    copyMap[x+1][y] = "X"
                #    route = nextPossible[1]
                #    path = nextPossible[2]
                #    route.append(position)
                #    path.append(Directions.EAST)
                #    dfsQueue.append((position, route, path))
                #if self.map[x][y+1] != "W" and copyMap[x][y+1] != "X":
                #    print "north"
                #    position = (x,y+1)
                #    copyMap[x][y+1] = "X"
                #    route = nextPossible[1]
                #    path = nextPossible[2]
                #    route.append(position)
                #    path.append(Directions.NORTH)
                #    dfsQueue.append((position, route, path))
                #if self.map[x][y-1] != "W" and copyMap[x][y-1] != "X":
                #    print "south"
                #    position = (x,y-1)
                #    copyMap[x][y-1] = "X"
                #    route = nextPossible[1]
                #    path = nextPossible[2]
                #    route.append(position)
                #    path.append(Directions.SOUTH)
                #    dfsQueue.append((position, route, path))
        print "no move"
