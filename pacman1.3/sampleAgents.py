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
import Queue

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
        self.traversed = []
        self.init = False
        self.map = None

    def initialize(self, state):

        corners = api.corners(state)
        walls = api.walls(state)

        if self.map == None:
            width = 0
            height = 0
            for corner in corners:
                if corner[0] > width:
                    width = corner[0]
                if corner[1] > height:
                    height = corner[1]
            self.map = [[0 for y in range(height)] for x in range(width)]
            for wall in walls:
                self.map[wall[0]][wall[1]] = "W"

        self.init = True


    def getAction(self, state):

        if not self.init:
            self.initialize(state)

        pacman = api.whereAmI(state)
        x = pacman[0]
        y = pacman[1]

        food = api.food(state)

        capsules = api.capsules(state)
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)

        walls = api.walls(state)

        #print walls

        q = Queue.Queue()

        #print self.map
        #print "start search"

        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        if Directions.WEST in legal:
            q.put(((x-1,y), Directions.WEST))
        if Directions.EAST in legal:
            q.put(((x+1,y), Directions.EAST))
        if Directions.NORTH in legal:
            q.put(((x,y+1), Directions.NORTH))
        if Directions.SOUTH in legal:
            q.put(((x,y-1), Directions.SOUTH))

        if not (len(food) == 0 and len(capsules) == 0):
            while not q.empty():
                possible = q.get()
                position = possible[0]
                x = position[0]
                y = position[1]
                print position
                if position in (food or capsules):
                    print "moving"
                    #self.traversed.append(position)
                    return api.makeMove(possible[1], legal)
                else:
                    #print "searching"
                    if (x-1,y) not in (walls or self.traversed):
                        q.put(((x-1,y), possible[1]))
                    if (x+1,y) not in (walls or self.traversed):
                        q.put(((x+1,y), possible[1]))
                    if (x,y+1) not in (walls or self.traversed):
                        q.put(((x,y+1), possible[1]))
                    if (x,y-1) not in (walls or self.traversed):
                        q.put(((x,y-1), possible[1]))
        else:
            print "cant see food"
            for row in self.map:
                print row
            return api.makeMove(Directions.STOP, legal)
