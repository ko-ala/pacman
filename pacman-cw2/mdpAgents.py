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

class MDPAgent(Agent):

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
        #pacmans current position`
        self.pacman = ()
        #list of scared ghosts
        self.scaredGhosts = []
        #list of ghost positions
        self.ghosts = []
        #list of positions adjacent to ghosts
        self.adjGhosts = []
        #defines the discount factor
        self.discount = 0.3
        #defines the threshold for the bellman euation
        self.threshold = 0.01
        #reward for food
        self.foodReward = 2
        #reward for an empty grid
        self.baseReward = -1
        #reward for capsules
        self.capsuleReward = 1
        #reward for a regular ghost
        self.ghostReward = -20
        #reward for a scared ghost
        self.scaredGhostReward = 5

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
        #pacman's x position
        pacmanX = pacman[0]
        #pacman's y position
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

            #once the size of the map has been identified, initialize the rewards of each position with the approriate value
            self.reward = [[self.baseReward for y in range(height+1)] for x in range(width+1)]
            #do the same with the utility, however with random values between 0 and 1
            self.utility = [[random() for y in range(height+1)] for x in range(width+1)]
            #now add in all the information pacman knows initially. starting with all known locations of food
            for food in foods:
                #set the reward of food to the value defined above
                self.reward[food[0]][food[1]] = self.foodReward
                #self.utility[food[0]][food[1]] = self.foodReward
            #set the reward of capsules with the reward defined above
            for capsule in capsules:
                self.reward[capsule[0]][capsule[1]] = self.capsuleReward
                #self.utility[capsule[0]][capsule[1]] = self.capsuleReward

            #now mark the location of the walls on the map, using "W"
            for wall in walls:
                self.reward[wall[0]][wall[1]] = "W"
                self.utility[wall[0]][wall[1]] = "W"

        #set init to true as the map has been initialized
        self.init = True

    #this function sums the value of 2 pairs and returns the new pair
    def sumPair(self, pair1, pair2):
        newX = pair1[0] + pair2[0]
        newY = pair1[1] + pair2[1]
        return (newX, newY)

    def findGhosts(self, state):
        ghostStates = api.ghostStatesWithTimes(state)
        self.scaredGhosts = []
        self.ghosts = []
        self.adjGhosts = []

        for ghostStates in ghostStates:
            if ghostStates[1] > 0:
                self.scaredGhosts.append(ghostStates[0])
            else:
                self.ghosts.append(ghostStates[0])
            for ghost in self.ghosts:
                for move in self.possibleMoves:
                    self.adjGhosts.append(self.sumPair(ghost, move[0]))

    def calcAdjUtility(self, x, y):
        #list to store calculated utilities in
        scores = []
        #for each adjacent square
        for i in range(len(self.possibleMoves)):
            #get the change in position to target adjacent square
            deltaForward = self.possibleMoves[i][0]
            #get change in position to left adjacent square. Needed due to noise
            deltaLeft = self.possibleMoves[(i+3) % 4][0]
            #get change in position to right adjacent square
            deltaRight = self.possibleMoves[(i+1) % 4][0]

            #get the positions of the three adjacent squares
            nextForward = self.sumPair((x,y), deltaForward)
            nextLeft = self.sumPair((x,y), deltaLeft)
            nextRight = self.sumPair((x,y), deltaRight)

            #retrieve utilities of each adjacent square by querying approriate position in utilities map
            forwardUtility = self.utility[nextForward[0]][nextForward[1]]
            leftUtility = self.utility[nextLeft[0]][nextLeft[1]]
            rightUtility = self.utility[nextRight[0]][nextRight[1]]

            #the weights of each utility
            left = 0.1
            forward = 0.8
            right = 0.1

            #if any of the adjacent positions are walls, consider the utility of the current pos instead
            if forwardUtility == "W":
                forwardUtility = self.utility[x][y]
            if leftUtility == "W":
                leftUtility = self.utility[x][y]
            if rightUtility == "W":
                rightUtility = self.utility[x][y]

            #calculate the utility of the target position
            adjUtility = left*leftUtility + forward*forwardUtility + right*rightUtility

            #append the utility to scores
            scores.append(adjUtility)
        return scores

    #this function interates through the Bellman Equation
    def bellman(self, state):
        #width and height of the environment
        width = len(self.utility)
        height = len(self.utility[0])
        #the maximum difference between interations, initialized with a large value
        maxDif = self.utility
        #number of interations done
        count = 0
        #While the iterations have not reached below the threshold or looped more than 100 times
        while(maxDif > self.threshold and count < 100):
            #create a new copy of utility to overwrite
            newUtility = deepcopy(self.utility)
            #the difference for an iteration
            #minDif = -10000
            #loop through every position in the map
            for y in range(0, height):
                for x in range(0, width):
                    #if the position doesnt contain a wall, calculate the utility
                    if newUtility[x][y] != "W":
                        scores = self.calcAdjUtility(x,y)
                        #print scores
                        #set the reward to the approriate value from self.reward
                        reward = self.reward[x][y]
                        #if the position is adjacent to a ghost or is a ghost, adjust reward approriately
                        if (x,y) in self.ghosts:
                            reward = self.ghostReward
                        elif (x,y) in self.adjGhosts:
                            reward = self.ghostReward/2
                        elif (x,y) in self.scaredGhosts:
                            reward = self.scaredGhostReward

                        #calculate the utility with the apporpriate values
                        newUtility[x][y] = reward + (self.discount * max(scores))

                        #get the difference between the utility of the last iteration and current iteration
                        dif = abs(newUtility[x][y] - self.utility[x][y])

                        #if the difference is greater than the greatest difference of this iteration, replace it
                        if dif > maxDif:
                            maxDif = dif
            '''
            #if the difference of this iteration
            if minDif >= maxDif:
                minDif = maxDif
            '''
            count = count + 1

            self.utility = newUtility

    #decide the move pacman should make
    def getMove(self,state):
        #print "getmove"
        #calculate the scores from all possible moves
        scores = self.calcAdjUtility(self.pacman[0], self.pacman[1])
        #get the maximum value from calculated utilities
        maxUtility = max(scores)
        #get the imdex of the move
        index = scores.index(maxUtility)
        #get the direction that orresponds to the highest utility
        direction = self.possibleMoves[index][1]
        #if staying still can provide higher utility, then stay still
        if self.utility[self.pacman[0]][self.pacman[1]] >= maxUtility:
            return api.makeMove(Directions.STOP, self.legal)
        #otherwise move in the previously found direction
        return api.makeMove(direction, self.legal)

    def getAction(self, state):
        #set the current location of pacman, legal moves in the internal memory
        self.pacman = api.whereAmI(state)
        self.legal = api.legalActions(state)

        #if the internal memory hasn't been initialized initialize it
        if not self.init:
            self.initialize(state)
        else:
            #update the reward of the current location to be the base reward
            self.reward[self.pacman[0]][self.pacman[1]] = self.baseReward

        #run the Bellman Equation to reflect new state of envrionment
        self.bellman(state)

        '''
        print ''
        for row in self.reward:
            print row


        print ''
        for row in self.utility:
            print row

            '''
        #get the apporpriate move pacman should make
        return self.getMove(state)
        #return api.makeMove(Directions.STOP, self.legal)
