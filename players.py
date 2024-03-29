import random
import time
import pygame
import math
import sys
import numpy as np
from numpy import inf
from connect4 import connect4
from copy import deepcopy
import timeit

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
		#print(f"game over check: {env.gameOver(move[0], self.opponent)}")
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
	pCount = np.count_nonzero(window == player)
	emptyCount =np.count_nonzero(window == 0) #count number of empty tiles (used to check if connect 4 possible)
	if pCount == 2 and emptyCount == 2:
		score += 4
	elif pCount == 3 and emptyCount == 1:
		score += 8
	elif pCount == 4: #connect 4 formed
		score += inf
		#return inf
	
	#count number of opponent tiles and evaluate
	oppCount = np.count_nonzero(window == opp)
	if oppCount == 2 and emptyCount == 2:
		score -= 4
		#if timeit() is not allowed: score -= 6
	elif oppCount == 3 and emptyCount == 1:
		#if timeit() is not allowed: score -= 12
		score -= 8
	elif oppCount == 4: #connect 4 formed
		score -= inf
	
	return score

#evaluation function
def eval(board, player, opp): #player: 1 or 2 #opp: 2 or 1 #board = env.board
	score = 0

	#center tiles
	center_array = board[:, 3]
	center_count = np.count_nonzero(center_array == player)
	score += center_count * 3

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
			window = np.zeros(4)
			for k in range(4): #traverse downwards to the right
				window[k] = board[i+k][j+k] 
			
			score += weight(window, player, opp)
		
	#right diagonal
	for i in range(5, 2, -1): #iterate over rows (start from row 6, stop at row 4 inclusive)
		for j in range(4): #iterate over cols: 7 - 3 = 4

			#create singular window
			window = np.zeros(4)
			for k in range(4): #traverse upwards to the right
				window[k] = board[i-k][j+k]
			score += weight(window, player, opp)

	return score

class minimaxAI(connect4Player):
	
	def simulateMove(self, env: connect4, move: int, player: int):
		env.board[env.topPosition[move]][move] = player #topPopsition[move] indicates row
		env.topPosition[move] -= 1 #decrement row

		return env

	def max_value(self, env, col, depth, dummyBestMove):
		bestMove = -1 #stores col index of best move

		#gameover check
		prevPlayer = self.opponent.position #get the player who made the move that caused the board to become its current state

		if col != -1: #this is the not the first/ second move
			if env.gameOver(col, prevPlayer) or depth == 0:
				return eval(env.board, self.position, self.opponent.position), dummyBestMove
		
		v = -inf

		#get possible next moves
		possible = env.topPosition >= 0
		indices = []

		#if len(indices) == 0: #no more possible moves
			#return 0, bestMove  #draw
		for i, p in enumerate(possible):
			if p: indices.append(i)

		#iterate over successor states
		for i in indices:
			s = deepcopy(env)
			self.simulateMove(s, i, self.position) #generate successor state given current board and desired move
			curMax = self.min_value(s, i, depth - 1, dummyBestMove)[0] #the value max will get for visiting that child
			if curMax > v:
				v = curMax
				bestMove = i
		
		#print(f"v: {v}, best move: {bestMove}")
		return v, bestMove
	
	def min_value(self, env, col, depth, dummyBestMove):
		#game over check
		prevPlayer = self.opponent.position #get the player who made the move that caused the board to become its current state
		if env.gameOver(col, prevPlayer) or depth == 0:
			return eval(env.board, self.position, self.opponent.position), dummyBestMove	
		v = inf

		#get possible next moves
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		#if len(indices) == 0:
			#return 0 #draw

		#iterate over successor states
		for i in indices:
			s = deepcopy(env)
			self.simulateMove(s, i, self.opponent.position) #generate successor state given current board and next move
			curMin = self.max_value(s, i, depth - 1, dummyBestMove)[0]
			if curMin < v:
				v = curMin
		
		return v, dummyBestMove

	def play(self, env: connect4, move: list) -> None:
		env_copy = deepcopy(env)
		
		if np.min(env_copy.topPosition) == 5: #we are making the first move, hardcode center col
			move[0] = 3
		else:
			bestMove = self.max_value(env_copy, -1, 4, -1)[1]
			#print(f"best move obtained: {bestMove}")
			move[0] = bestMove

class alphaBetaAI(connect4Player):

	def successor(self, indices, lastMove):
		def difference_from_index(element):
			return abs(element - lastMove)
		sortedIndices = sorted(indices, key=difference_from_index)

		return sortedIndices

	def simulateMove(self, env: connect4, move: int, player: int):
		env.board[env.topPosition[move]][move] = player #topPopsition[move] indicates row
		env.topPosition[move] -= 1 #decrement row

		return env

	def max_value(self, env, col, depth, dummyBestMove, alpha, beta):
		bestMove = -1 #stores col index of best move

		#gameover check
		prevPlayer = self.opponent.position #get the player who made the move that caused the board to become its current state
		if col != -1: #this is the not the first/ second move, check for gameover
			if env.gameOver(col, prevPlayer) or depth == 0:
				return eval(env.board, self.position, self.opponent.position), dummyBestMove
		
		v = -inf

		#get possible next moves
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)

		#call successor function
		orderedIndices = self.successor(indices, col) 

		#iterate over successor states
		for i in orderedIndices:
			s = deepcopy(env)
			self.simulateMove(s, i, self.position) #generate successor state given current board and desired move
			curMax = self.min_value(s, i, depth - 1, dummyBestMove, alpha, beta)[0] #the value max will get for visiting that child
			if curMax > v:
				v = curMax
				bestMove = i
			if v >= beta:
				return v, bestMove
			alpha = max(alpha, v)
		
		return v, bestMove
	
	def min_value(self, env, col, depth, dummyBestMove, alpha, beta):
		#game over check
		prevPlayer = self.opponent.position #get the player who made the move that caused the board to become its current state
		if env.gameOver(col, prevPlayer) or depth == 0:
			return eval(env.board, self.position, self.opponent.position), dummyBestMove
		v = inf

		#get possible next moves
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		#if len(indices) == 0:
			#return 0 #draw

		#call successor function
		orderedIndices = self.successor(indices, col)

		#iterate over successor states
		for i in orderedIndices:
			s = deepcopy(env)
			self.simulateMove(s, i, self.opponent.position) #generate successor state given current board and next move
			curMin = self.max_value(s, i, depth - 1, dummyBestMove, alpha, beta)[0]
			if curMin < v:
				v = curMin
			if v <= alpha:
				return v, dummyBestMove
			beta = min(beta, v)
		
		return v, dummyBestMove

	def play(self, env: connect4, move: list) -> None:
		env_copy = deepcopy(env)
		
		if np.min(env_copy.topPosition) == 5: #we are making the first move, hardcode center col
			move[0] = 3
		else:
			#if timeit() is not allowed: bestMove = self.max_value(env_copy, -1, 3, -1, -inf, inf)[1]
			bestMove = self.max_value(env_copy, -1, 4, -1, -inf, inf)[1]
			move[0] = bestMove

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




