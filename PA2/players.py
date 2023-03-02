import numpy as np
import random
import sys
import time
import pygame
import signal
import math
from copy import deepcopy

class connect4Player(object):
	def __init__(self, position, seed=0):
		self.position = position
		self.opponent = None
		self.seed = seed
		random.seed(seed)

	def play(self, env, move):
		move = [-1]

class human(connect4Player):

	def play(self, env, move):
		move[:] = [int(input('Select next move: '))]
		while True:
			if int(move[0]) >= 0 and int(move[0]) <= 6 and env.topPosition[int(move[0])] >= 0:
				break
			move[:] = [int(input('Index invalid. Select next move: '))]

class human2(connect4Player):

	def play(self, env, move):
		done = False
		while(not done):
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

				if event.type == pygame.MOUSEMOTION:
					pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
					posx = event.pos[0]
					if self.position == 1:
						pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
					else: 
						pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
				pygame.display.update()

				if event.type == pygame.MOUSEBUTTONDOWN:
					posx = event.pos[0]
					col = int(math.floor(posx/SQUARESIZE))
					move[:] = [col]
					done = True

class randomAI(connect4Player):

	def play(self, env, move):
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		move[:] = [random.choice(indices)]

class stupidAI(connect4Player):

	def play(self, env, move):
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

class minimaxAI(connect4Player):
 
	def play(self, env, move):
		depth = 3
		# Find legal moves
		env = deepcopy(env)
		env.visualize = False
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		# Init fitness trackers, zeros at start, will be replaced with the nash equilibrium for each
		vs = np.zeros(7)
		# Play until told to stop
		store = -math.inf
		for i in indices:
			#print(str(i))
			env_copy = deepcopy(env)
			self.simulateMove(env_copy, i, self.position)
			value = self.minimax(env_copy, depth-1, False, i)
			vs[i] = max(store, value)
			move[:] = [np.argmax(vs)]
		move[:] = [np.argmax(vs)]
		print("I finished")


	def verticalCombo(self,env,player, opponent):
		#playerTwos, playerThrees, playerFours, blockTwos, blockThrees, blockFours
		score = np.zeros(6)
		for row in range(len(env.board)-3):
			for col in range(len(env.board[row])):
				if (env.board[row][col] == player and env.board[row+1][col] == player):
					if (env.board[row+2][col] == player):
						if (env.board[row+3][col] == player):
							score[2] += 1
						else:
							score[1] += 1

				#Blocking VERTICAL lose stack: X O O O
				if	(env.board[row][col] == player and env.board[row+1][col] == opponent):
					if (env.board[row+2][col] == opponent):
						if (env.board[row+3][col] == opponent):
							score[5] += 1
						else:
							score[4] += 1

		return score

	def horizontalCombo(self, env, player, opponent):
		#playerTwos, playerThrees, playerFours, blockTwos, blockThrees, blockFours
		score = np.zeros(6)
		for row in range(len(env.board)):
			for col in range(4):
				if (env.board[row][col] == player and env.board[row][col+1] == player):
					if (env.board[row][col+2] == player):
						if (env.board[row][col+3] == player):
							score[2] += 1
						else:
							score[1] += 1

				#Blocking HORIZONTAL lose stacks: O X O O; X O O O
				if	(env.board[row][col] == player and env.board[row][col+1] == opponent) or (env.board[row][col] == opponent and env.board[row][col+1] == player):
					if (env.board[row][col+2] == opponent):
						if (env.board[row][col+3] == opponent):
							score[5] += 1
						else:
							score[4] += 1

			for col in range(3, 7):
				if	(env.board[row][col] == player and env.board[row][col-1] == opponent) or (env.board[row][col] == opponent and env.board[row][col-1] == player):
					if (env.board[row][col-2] == opponent):
						if (env.board[row][col-3] == opponent):
							score[5] += 1
						else:
							score[4] += 1

			for col in range(1,6):
				if	(env.board[row][col+1] == opponent and env.board[row][col] == player and env.board[row][col-1] == opponent):
					score[5] += 1

		return score

	def diagonalCombo(self,env, player, opponent):
		#playerTwos, playerThrees, playerFours, blockTwos, blockThrees, blockFours
		score = np.zeros(6)
		for col in range(len(env.board[0])-3):
			for row in range(len(env.board)-3):
				if (env.board[row][col] == player and env.board[row+1][col+1] == player):

					if (env.board[row+2][col+2] == player):

						if (env.board[row+3][col+3] == player):
							score[2] += 1
						else:
							score[1] += 1
					else:
						score[0] += 1
				#Blocking
				if	(env.board[row][col] == player and env.board[row+1][col+1] == opponent) or (env.board[row][col] == opponent and env.board[row+1][col+1] == player):
					if (env.board[row+2][col+2] == opponent):
						if (env.board[row+3][col+3] == opponent):
							score[5] += 1
						else:
							score[4] += 1
				if	(env.board[row][col] == opponent and env.board[row+1][col+1] == opponent):
					if (env.board[row+2][col+2] == player):
						if (env.board[row+3][col+3] == opponent):
							score[5] += 1
						else:
							score[4] += 1
				if	(env.board[row][col] == opponent and env.board[row+1][col+1] == opponent):
					if (env.board[row+2][col+2] == opponent):
						if (env.board[row+3][col+3] == player):
							score[5] += 1
						else:
							score[4] += 1
		
			for row in range(3,6):
				if (env.board[row][col] == player and env.board[row-1][col+1] == player):

					if (env.board[row-2][col+2] == player):
						if (env.board[row-3][col+3] == player):
							score[2] += 1
						else:
							score[1] += 1
					else:
						score[0] += 1
				#Blocking
				if	(env.board[row][col] == player and env.board[row-1][col+1] == opponent) or (env.board[row][col] == opponent and env.board[row-1][col+1] == player):
					if (env.board[row-2][col+2] == opponent):
						if (env.board[row-3][col+3] == opponent):
							score[5] += 1
						else:
							score[4] += 1
				if	(env.board[row][col] == opponent and env.board[row-1][col+1] == opponent):
					if (env.board[row-2][col+2] == player):
						if (env.board[row-3][col+3] == opponent):
							score[5] += 1
						else:
							score[4] += 1
				if	(env.board[row][col] == opponent and env.board[row-1][col+1] == opponent):
					if (env.board[row-2][col+2] == opponent):
						if (env.board[row-3][col+3] == player):
							score[5] += 1
						else:
							score[4] += 1
		
		return score

	def combo(self, env, player, opponent):
		#numberTwos, numberThrees, numberFours, blockTwos, blockThrees, blockFours
		score = np.zeros(6)
		score = np.add(score, self.verticalCombo(env, player, opponent) )
		score = np.add(score, self.horizontalCombo(env, player, opponent) )
		score = np.add(score, self.diagonalCombo(env, player, opponent))
		return score

	def evaluation(self, env, player, opponent):
		#playerTwos, playerThrees, playerFours, blockTwos, blockThrees, blockFours
		playerCombo = np.zeros(6)	
		opponentCombo = np.zeros(6)	
		playerCombo = self.combo(env, player, opponent)
		opponentCombo = self.combo(env, opponent, player)
		#1. 1000000000		win
		#2. 100000		block opponent win
  		#3. 10000		build 3
    	#4. 1000		block 3
    	#5. 250			block 2
		#6. 50			build 2
		return ((playerCombo[2] * 1000000000 + playerCombo[5] * 100000 + playerCombo[1] * 10000 + playerCombo[4] * 1000 + playerCombo[3] * 250 + playerCombo[0]*50) - (opponentCombo[2] * 1000000000 + opponentCombo[5] * 100000  + opponentCombo[1] * 10000 + opponentCombo[4] * 1000 + opponentCombo[3] * 250 + opponentCombo[0]*50))

	def minimax(self, env, depth, maxPlayer, move):

		if maxPlayer:	
			position = self.position
			bestValue = -math.inf
		else:
			bestValue = math.inf
			position = self.opponent.position
		env = deepcopy(env)
		env.visualize = False
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		#If depth = 0 or game over on next move
		#POTENTIAL PROBLEM 228 - 229

		if depth == 0 or env.gameOver(move, self.position) or env.gameOver(move, self.opponent.position):
			return self.evaluation(env, self.position, self.opponent.position)

		for i in indices:
			child = deepcopy(env)
			self.simulateMove(child, i, position)
			value = self.minimax(child, depth - 1, not maxPlayer, i)
			if maxPlayer:	#MAX
				bestValue = max(bestValue, value)
			else:			#MIN
				bestValue = min(bestValue, value)
		return bestValue
    
	def simulateMove(self, env, move, player):
		env.board[env.topPosition[move]][move] = player
		env.topPosition[move] -= 1
		env.history[0].append(move)

	def signal_handler(self):
		print("SIGTERM ENCOUNTERED")
		sys.exit(0)
  
class alphaBetaAI(connect4Player):
 
	def play(self, env, move):
		start = time.time()
		random.seed(self.seed)
		max_depth = random.randint(3, 20)
		# Find legal moves
		env = deepcopy(env)
		env.visualize = False
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		# Init fitness trackers, zeros at start, will be replaced with the nash equilibrium for each
		vs = np.zeros(7)
		# Play until told to stop
		for depth in range(1, max_depth):
			if time.time() - start > 0.5:
				break
			store = -math.inf
			alpha = -math.inf
			beta = math.inf
			for i in indices:
				child = deepcopy(env)
				self.simulateMove(child, i, self.position)
				value = self.alphaBeta(child, depth-1, False, i, alpha, beta)
				vs[i] = max(store, value)
				alpha = max(alpha, value)
				if alpha >= beta:
					break
			move[:] = [np.argmax(vs)]
		move[:] = [np.argmax(vs)]

	def verticalCombo(self,env,player, opponent):
		#playerTwos, playerThrees, playerFours, blockTwos, blockThrees, blockFours
		score = np.zeros(6)
		for row in range(len(env.board)-3):
			for col in range(len(env.board[row])):
				if (env.board[row][col] == player and env.board[row+1][col] == player):
					if (env.board[row+2][col] == player):
						if (env.board[row+3][col] == player):
							score[2] += 1
						else:
							score[1] += 1

				#Blocking VERTICAL lose stack: X O O O
				if	(env.board[row][col] == player and env.board[row+1][col] == opponent):
					if (env.board[row+2][col] == opponent):
						if (env.board[row+3][col] == opponent):
							score[5] += 1
						else:
							score[4] += 1

		return score

	def horizontalCombo(self, env, player, opponent):
		#playerTwos, playerThrees, playerFours, blockTwos, blockThrees, blockFours
		score = np.zeros(6)
		for row in range(len(env.board)):
			for col in range(4):
				if (env.board[row][col] == player and env.board[row][col+1] == player):
					if (env.board[row][col+2] == player):
						if (env.board[row][col+3] == player):
							score[2] += 1
						else:
							score[1] += 1

				#Blocking HORIZONTAL lose stacks: O X O O; X O O O
				if	(env.board[row][col] == player and env.board[row][col+1] == opponent) or (env.board[row][col] == opponent and env.board[row][col+1] == player):
					if (env.board[row][col+2] == opponent):
						if (env.board[row][col+3] == opponent):
							score[5] += 1
						else:
							score[4] += 1

			for col in range(3, 7):
				if	(env.board[row][col] == player and env.board[row][col-1] == opponent) or (env.board[row][col] == opponent and env.board[row][col-1] == player):
					if (env.board[row][col-2] == opponent):
						if (env.board[row][col-3] == opponent):
							score[5] += 1
						else:
							score[4] += 1

			for col in range(1,6):
				if	(env.board[row][col+1] == opponent and env.board[row][col] == player and env.board[row][col-1] == opponent):
					score[5] += 1

		return score

	def diagonalCombo(self,env, player, opponent):
		#playerTwos, playerThrees, playerFours, blockTwos, blockThrees, blockFours
		score = np.zeros(6)
		for col in range(len(env.board[0])-3):
			for row in range(len(env.board)-3):
				if (env.board[row][col] == player and env.board[row+1][col+1] == player):

					if (env.board[row+2][col+2] == player):

						if (env.board[row+3][col+3] == player):
							score[2] += 1
						else:
							score[1] += 1
					else:
						score[0] += 1
				#Blocking
				if	(env.board[row][col] == player and env.board[row+1][col+1] == opponent) or (env.board[row][col] == opponent and env.board[row+1][col+1] == player):
					if (env.board[row+2][col+2] == opponent):
						if (env.board[row+3][col+3] == opponent):
							score[5] += 1
						else:
							score[4] += 1
				if	(env.board[row][col] == opponent and env.board[row+1][col+1] == opponent):
					if (env.board[row+2][col+2] == player):
						if (env.board[row+3][col+3] == opponent):
							score[5] += 1
						else:
							score[4] += 1
				if	(env.board[row][col] == opponent and env.board[row+1][col+1] == opponent):
					if (env.board[row+2][col+2] == opponent):
						if (env.board[row+3][col+3] == player):
							score[5] += 1
						else:
							score[4] += 1
		
			for row in range(3,6):
				if (env.board[row][col] == player and env.board[row-1][col+1] == player):

					if (env.board[row-2][col+2] == player):
						if (env.board[row-3][col+3] == player):
							score[2] += 1
						else:
							score[1] += 1
					else:
						score[0] += 1
				#Blocking
				if	(env.board[row][col] == player and env.board[row-1][col+1] == opponent) or (env.board[row][col] == opponent and env.board[row-1][col+1] == player):
					if (env.board[row-2][col+2] == opponent):
						if (env.board[row-3][col+3] == opponent):
							score[5] += 1
						else:
							score[4] += 1
				if	(env.board[row][col] == opponent and env.board[row-1][col+1] == opponent):
					if (env.board[row-2][col+2] == player):
						if (env.board[row-3][col+3] == opponent):
							score[5] += 1
						else:
							score[4] += 1
				if	(env.board[row][col] == opponent and env.board[row-1][col+1] == opponent):
					if (env.board[row-2][col+2] == opponent):
						if (env.board[row-3][col+3] == player):
							score[5] += 1
						else:
							score[4] += 1
		
		return score

	def combo(self, env, player, opponent):
		#numberTwos, numberThrees, numberFours, blockTwos, blockThrees, blockFours
		score = np.zeros(6)
		score = np.add(score, self.verticalCombo(env, player, opponent) )
		score = np.add(score, self.horizontalCombo(env, player, opponent) )
		score = np.add(score, self.diagonalCombo(env, player, opponent))
		return score

	def evaluation(self, env, player, opponent):
		#playerTwos, playerThrees, playerFours, blockTwos, blockThrees, blockFours
		playerCombo = np.zeros(6)	
		opponentCombo = np.zeros(6)	
		playerCombo = self.combo(env, player, opponent)
		opponentCombo = self.combo(env, opponent, player)
		#1. 1000000000	win
		#2. 100000		block opponent win
  		#3. 10000		build 3
    	#4. 1000		block 3
    	#5. 250			block 2
		#6. 50			build 2
		return ((playerCombo[2] * 1000000000 + playerCombo[5] * 100000 + playerCombo[1] * 10000 + playerCombo[4] * 1000 + playerCombo[3] * 250 + playerCombo[0]*50) - (opponentCombo[2] * 1000000000 + opponentCombo[5] * 100000  + opponentCombo[1] * 10000 + opponentCombo[4] * 1000 + opponentCombo[3] * 250 + opponentCombo[0]*50))

	def alphaBeta(self, env, depth, maxPlayer, move, alpha, beta):
		if maxPlayer:
			position = self.position
			bestValue = -math.inf
		else:
			bestValue = math.inf
			position = self.opponent.position
		env = deepcopy(env)
		env.visualize = False
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)

		if depth == 0 or env.gameOver(move, self.position) or env.gameOver(move, self.opponent.position):
			return self.evaluation(env, self.position, self.opponent.position)

		for i in indices:
			child = deepcopy(env)
			self.simulateMove(child, i, position)
			value = self.alphaBeta(child, depth - 1, not maxPlayer, i, alpha, beta)
			if maxPlayer:
				bestValue = max(bestValue, value)
				alpha = max(alpha, bestValue)
				if alpha >= beta:
					break
			else:
				bestValue = min(bestValue, value)
				beta = min(beta, bestValue)
				if alpha >= beta:
					break
		return bestValue
    
	def simulateMove(self, env, move, player):
		env.board[env.topPosition[move]][move] = player
		env.topPosition[move] -= 1
		env.history[0].append(move)

	def signal_handler(self):
		print("SIGTERM ENCOUNTERED")
		sys.exit(0)


SQUARESIZE = 100
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

pygame.init()

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)




