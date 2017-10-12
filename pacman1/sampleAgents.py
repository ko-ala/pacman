# sampleAgents.py
# parsons/28-sep-2017
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
        legal = state.getLegalPacmanActions()
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

    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = state.getLegalPacmanActions()
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # Get the current score
        current_score = state.getScore()
        # Get the last action
        last = state.getPacmanState().configuration.direction
        # If we can repeat the last action, do it. Otherwise make a
        # random choice.
        if last in legal:
            return api.makeMove(last, legal)
        else:
            pick = random.choice(legal)
            return api.makeMove(pick, legal)

# SensingAgent
#
# Doesn't move, but reports sensory data available to Pacman
class SensingAgent(Agent):

    def getAction(self, state):

        # Demonstrates the information that Pacman can access about the state
        # of the game.

        # What are the current moves available
        legal = state.getLegalPacmanActions()
        print "Legal moves: ", legal

        # Where is Pacman?
        pacman = api.whereAmI(state)
        print "\nPacman position: ", pacman, pacman[0]

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

class GoWestAgent(Agent):

    def getAction(self, state):

        #current possible moves
        legal = state.getLegalPacmanActions()

        #Prevent it from stopping
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        #if it can go west, go west
        if Directions.WEST in legal:
            return api.makeMove(Directions.WEST, legal)
        #else pick a random direction
        else:
            pick = random.choice(legal)
            return api.makeMove(pick, legal)

class CornerSeekingAgent(Agent):

    def getAction(self, state):

        pacman = api.whereAmI(state)
        x = pacman[0]
        y = pacman[1]

        food = api.food(state)

        capsule = api.capsules(state)
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = state.getLegalPacmanActions()

        walls = api.walls(state)

        q = Queue.Queue()

        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        if Directions.WEST in legal:
            #print "West"
            q.put(((x-1,y), Directions.WEST))
        if Directions.EAST in legal:
            #print "East"
            q.put(((x+1,y), Directions.EAST))
        if Directions.NORTH in legal:
            #print "North"
            q.put(((x,y+1), Directions.NORTH))
        if Directions.SOUTH in legal:
            #print "South"
            q.put(((x,y-1), Directions.SOUTH))

        #print food
        #print q.toString()

        while not q.empty():
            possible = q.get()
            position = possible[0]
            x = position[0]
            y = position[1]
            print position
            if position in (food or capsules):
                print "moving"
                return api.makeMove(possible[1], legal)
            else:
                #print "searching"
                if (x-1,y) not in walls:
                    q.put(((x-1,y), possible[1]))
                if (x+1,y) not in walls:
                    q.put(((x+1,y), possible[1]))
                if (x,y+1) not in walls:
                    q.put(((x,y+1), possible[1]))
                if (x,y-1) not in walls:
                    q.put(((x,y-1), possible[1]))

class HungryAgent(Agent):

    def getAction(self, state):

        #current possible moves
        legal = state.getLegalPacmanActions()

        #get current position
        pacman = api.whereAmI(state)
        pacmanX = pacman[0]
        pacmanY = pacman[1]

        #get food locations
        food = api.food(state)

        foodLoc = []

        # get Distance
        for loc in food:
            foodLoc.append((abs(loc[0]-pacmanX + loc[1]-pacmanY),(loc[0]-pacmanX, loc[1]-pacmanY)))

        print foodLoc


        #Prevent it from stopping
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        pick = random.choice(legal)
        return api.makeMove(pick, legal)
