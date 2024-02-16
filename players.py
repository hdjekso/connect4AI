import random
import time
import pygame
import math
import sys
import numpy as np
from numpy import inf
from connect4 import connect4
from copy import deepcopy

class connect4Player(object):
	def __init__(self, position, seed=0, CVDMode=False):
		self.position = position
		self.opponent = None
		self.seed = seed
		random.seed(seed)
		if CVDMode:
			global P1COLOR
			global P2COLOR
			P1COLOR = (227, 60, 239)
			P2COLOR = (0, 255, 0)

	def play(self, env: connect4, move: list) -> None:
		move = [-1]

class human(connect4Player):

	def play(self, env: connect4, move: list) -> None:
		move[:] = [int(input('Select next move: '))]
		while True:
			if int(move[0]) >= 0 and int(move[0]) <= 6 and env.topPosition[int(move[0])] >= 0:
				break
			move[:] = [int(input('Index invalid. Select next move: '))]

class human2(connect4Player):

	def play(self, env: connect4, move: list) -> None:
		done = False
		while(not done):
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

				if event.type == pygame.MOUSEMOTION:
					pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
					posx = event.pos[0]
					if self.position == 1:
						pygame.draw.circle(screen, P1COLOR, (posx, int(SQUARESIZE/2)), RADIUS)
					else: 
						pygame.draw.circle(screen, P2COLOR, (posx, int(SQUARESIZE/2)), RADIUS)
				pygame.display.update()

				if event.type == pygame.MOUSEBUTTONDOWN:
					posx = event.pos[0]
					col = int(math.floor(posx/SQUARESIZE))
					move[:] = [col]
					done = True

class randomAI(connect4Player):

	def play(self, env: connect4, move: list) -> None:
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		move[:] = [random.choice(indices)]

class stupidAI(connect4Player):

	def play(self, env: connect4, move: list) -> None:
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		if 3 in indices:
			move[:] = [3]
		elif 2 in indices:
			move[:] = [2]
		elif 1 in indices:
			move[:] = [1]
		elif 5 in indices:
			move[:] = [5]
		elif 6 in indices:
			move[:] = [6]
		else:
			move[:] = [0]

def weight(window, player, opp):
	score = 0

	#count number of player tiles and evaluate
	pCount = window.count(player)
	emptyCount = window.count(0) #count number of empty tiles (used to check if connect 4 possible)
	if pCount == 1 and emptyCount == 3: #1 player tile in window, and 3 empty: connect 4 possible
		score += 1
	elif pCount == 2 and emptyCount == 2:
		score += 3
	elif pCount == 3 and emptyCount == 1:
		score += 8
	elif pCount == 4: #connect 4 formed
		score += inf

	#count number of opponent tiles and evaluate
	oppCount = window.count(opp)
	if oppCount == 1 and emptyCount == 3: #1 player tile in window, and 3 empty: connect 4 possible
		score -= 1
	elif oppCount == 2 and emptyCount == 2:
		score -= 3
	elif oppCount == 3 and emptyCount == 1:
		score -= 8
	elif oppCount == 4: #connect 4 formed
		score -= inf
		
	return score

#evaluation function
def eval(board, player, opp): #player: 1 or 2 #opp: 2 or 1 #board = env.board
	score = 0

	#calculate score of horizontal moves
	for i in range(6): #iterate over all 6 rows
		curRow = board[i, :] #extract row
		for k in range(4): #numcols - 3 = 4
			window = curRow[k:k+4] #extract window of length 4 from current row
			score += weight(window, player, opp) #evaluate weight of window based on player tiles and opponent tiles in window

	#vertical
	for j in range(7): #iterate over all 7 cols
		curCol = board[:, j] #extract col
		for k in range(3): #numrows - 3 = 3
			window = curCol[k:k+4] #extract window of length 4 from current col
			score += weight(window, player, opp) #evaluate weight of window based on player tiles and opponent tiles in window

	#left diagonal
	for i in range(3): #iterate over rows: 6 - 3 = 3
		for j in range(4): #iterate over cols: 7 - 3 = 4

			#create singular window
			window = [0]*4
			for k in range(4): #traverse downwards to the right
				window[k] = board[i+k][j+k] 
			
			score += weight(window, player, opp)
	
	#right diagonal
	for i in range(5, 2, -1): #iterate over rows (start from row 6, stop at row 4 inclusive)
		for j in range(4): #iterate over cols: 7 - 3 = 4

			#create singular window
			window = [0]*4
			for k in range(4): #traverse upwards to the right
				window[k] = board[i-k][j+k]
			
			score += weight(window, player, opp)

	return score

class minimaxAI(connect4Player):
	def successor_state(self):
		return 

	def max_value(self, env, col):
		bestMove = -1 #stores col index of best move
		#env = deepcopy(env)
		#env = simulate_move(env, col) #get board with current move applied
		prevPlayer = self.opponent.position #get the player who made the move that caused the board to become its current state
		if self.gameOver(col, prevPlayer):
			return -1, bestMove #min won
		v = -inf

		#get possible next moves
		possible = env.topPosition >= 0
		indices = []

		#if len(indices) == 0: #no more possible moves
			#return 0, bestMove  #draw

		for i, p in enumerate(possible):
			if p: indices.append(i)

		for i in indices:
			s = self.successor_state(env, i) #generate successor state given current board and desired move
			curMax = self.min_value(s, i, bestMove) #the value max will get for visiting that child
			if curMax > v:
				v = curMax
				bestMove = i
		
		return v, bestMove
	
	def min_value(self, env, col, bestMove):
		#env = deepcopy(env)
		#env = simulate_move(env, col) #get board with current move applied
		prevPlayer = self.opponent.position #get the player who made the move that caused the board to become its current state
		if self.gameOver(col, prevPlayer):
			return 1 #max player won
		v = 0

		#get possible next moves
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)

		#if len(indices) == 0:
			#return 0 #draw

		for i in indices:
			s = self.successor_state(env, i) #generate successor state given current board and next move
			v = max(v, self.max_value(s))
		
		return v


	def play(self, env: connect4, move: list) -> None:
		env = deepcopy(env)
		v = -inf
		v, bestMove = max(v, self.max_value(env, 0))
		move[:] = bestMove

class alphaBetaAI(connect4Player):

	def play(self, env: connect4, move: list) -> None:
		pass


SQUARESIZE = 100
BLUE = (0,0,255)
BLACK = (0,0,0)
P1COLOR = (255,0,0)
P2COLOR = (255,255,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

pygame.init()

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)




