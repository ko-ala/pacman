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
        self.opposite = {Directions.WEST: Directions.EAST, Directions.EAST: Directions.WEST,
            Directions.NORTH: Directions.SOUTH, Directions.SOUTH: Directions.NORTH}

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
            print "width and height"
            print width
            print height
            self.map = [["?" for y in range(height+1)] for x in range(width+1)]
            for food in foods:
                self.map[food[0]][food[1]] = "F"
            for capsule in capsules:
                self.map[capsule[0]][capsule[1]] = "F"
            for wall in walls:
                print wall
                self.map[wall[0]][wall[1]] = "W"
            self.map[x][y] = "0"

            for row in self.map:
                print row
        self.init = True

    def runAway(self, state):

        legal = api.legalActions(state)
        ghosts = api.ghosts(state)
        pacman = api.whereAmI(state)
        x = pacman[0]
        y= pacman[1]
        dfsQueue = []
        copyMap = deepcopy(self.map)

        if Directions.WEST in legal:
            nextPosition = (x-1, y)
            route = [nextPosition]
            path = [Directions.WEST]
            dfsQueue.append((nextPosition, route, path))
        if Directions.EAST in legal:
            nextPosition = (x+1, y)
            route = [nextPosition]
            path = [Directions.EAST]
            dfsQueue.append((nextPosition, route, path))
        if Directions.NORTH in legal:
            nextPosition = (x, y+1)
            route = [nextPosition]
            path = [Directions.NORTH]
            dfsQueue.append((nextPosition, route, path))
        if Directions.SOUTH in legal:
            nextPosition = (x, y-1)
            route = [nextPosition]
            path = [Directions.SOUTH]
            dfsQueue.append((nextPosition, route, path))

        while not len(dfsQueue) == 0:
            nextPossible = dfsQueue.pop(0)
            nextPossiblePosition = nextPossible[0]
            x = nextPossiblePosition[0]
            y = nextPossiblePosition[1]
            print "find move"

            for row in self.map:
                print row

            if nextPossiblePosition in ghosts:
                print "next move"
                nextPosition = nextPossible[1].pop(0)
                nextMove = nextPossible[2].pop(0)
                self.route = nextPossible[1]
                self.path = nextPossible[2]
                self.map[nextPosition[0]][nextPosition[1]] = "0"
                if self.opposite[nextMove] in legal:
                    return api.makeMove(self.opposite[nextMove], legal)
                else:
                    legal.remove(nextMove)
                    pick = random.choice(legal)
                    return api.makeMove(pick, legal)


            else:
                possibleMoves = [((x-1,y),Directions.WEST), ((x+1,y), Directions.EAST), ((x,y+1), Directions.NORTH),((x,y-1), Directions.SOUTH)]
                print "searching dfs"
                for move in possibleMoves:
                    ghostX = move[0][0]
                    ghostY = move[0][1]
                    if self.map[ghostX][ghostY] != "W" and copyMap[ghostX][ghostY] != "X":
                        copyMap[ghostX][ghostY] = "X"
                        route = deepcopy(nextPossible[1])
                        path = deepcopy(nextPossible[2])
                        route.append(move[0])
                        path.append(move[1])
                        dfsQueue.append((move[0], route, path))


    def getAction(self, state):

        if not self.init:
            self.initialize(state)

        if api.ghosts(state):
            return self.runAway(state)

        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)

        if len(self.route) != 0 and len(self.path) != 0:

            #for num in range(len(self.route)):
            #    print self.route[num]
            #    print self.path[num]

            print len(self.route)
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


        #searches all squares of distance 1
        if Directions.WEST in legal:
            nextPosition = (x-1, y)
            route = [nextPosition]
            path = [Directions.WEST]
            dfsQueue.append((nextPosition, route, path))
        if Directions.EAST in legal:
            nextPosition = (x+1, y)
            route = [nextPosition]
            path = [Directions.EAST]
            dfsQueue.append((nextPosition, route, path))
        if Directions.NORTH in legal:
            nextPosition = (x, y+1)
            route = [nextPosition]
            path = [Directions.NORTH]
            dfsQueue.append((nextPosition, route, path))
        if Directions.SOUTH in legal:
            nextPosition = (x, y-1)
            route = [nextPosition]
            path = [Directions.SOUTH]
            dfsQueue.append((nextPosition, route, path))

        copyMap = deepcopy(self.map)

        #conducts bfs search
        while not len(dfsQueue) == 0:
            nextPossible = dfsQueue.pop(0)
            nextPossiblePosition = nextPossible[0]
            x = nextPossiblePosition[0]
            y = nextPossiblePosition[1]
            print "find move"

            for row in self.map:
                print row

            if self.map[x][y] == "F" or self.map[x][y] == "?":
                print "next move"
                nextPosition = nextPossible[1].pop(0)
                nextMove = nextPossible[2].pop(0)
                self.route = nextPossible[1]
                self.path = nextPossible[2]
                self.map[nextPosition[0]][nextPosition[1]] = "0"
                return api.makeMove(nextMove, legal)

            else:
                possibleMoves = [((x-1,y),Directions.WEST), ((x+1,y), Directions.EAST), ((x,y+1), Directions.NORTH),((x,y-1), Directions.SOUTH)]
                print "searching dfs"
                for move in possibleMoves:
                    possibleX = move[0][0]
                    possibleY = move[0][1]
                    if self.map[possibleX][possibleY] != "W" and copyMap[possibleX][possibleY] != "X":
                        copyMap[possibleX][possibleY] = "X"
                        route = deepcopy(nextPossible[1])
                        path = deepcopy(nextPossible[2])
                        route.append(move[0])
                        path.append(move[1])
                        dfsQueue.append((move[0], route, path))
        print "no move"
