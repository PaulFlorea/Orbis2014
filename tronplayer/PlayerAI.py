import sys
from tronclient.Client import *

#############################################################################
#Basic spacial methods and vars to simplify logic
CW = 0
CCW = 1

def isObstacle(board,pos):
	return board[pos[0]][pos[1]] != EMPTY and board[pos[0]][pos[1]] != POWERUP

def pFront(pos,direct):
	if direct == Direction.UP:
		return [pos[0],pos[1]-1]
	elif direct == Direction.DOWN:
		return [pos[0],pos[1]+1]
	elif direct == Direction.RIGHT:
		return [pos[0]+1,pos[1]]
	else:
		return [pos[0]-1,pos[1]]

def pRight(pos,direct):
	if direct == Direction.UP:
		return [pos[0]+1,pos[1]]
	elif direct == Direction.DOWN:
		return [pos[0]-1,pos[1]]
	elif direct == Direction.RIGHT:
		return [pos[0],pos[1]+1]
	else:
		return [pos[0],pos[1]-1]

def pLeft(pos,direct):
	if direct == Direction.UP:
		return [pos[0]-1,pos[1]]
	elif direct == Direction.DOWN:
		return [pos[0]+1,pos[1]]
	elif direct == Direction.RIGHT:
		return [pos[0],pos[1]-1]
	else:
		return [pos[0],pos[1]+1]

def moveForward(direct):
	if direct == Direction.UP:
		return PlayerActions.MOVE_UP
	elif direct == Direction.LEFT:
		return PlayerActions.MOVE_LEFT
	elif direct == Direction.RIGHT:
		return PlayerActions.MOVE_RIGHT
	else:
		return PlayerActions.MOVE_DOWN

def turnRight(direct):
	print "Turning Right"
	if direct == Direction.UP:
		return PlayerActions.MOVE_RIGHT
	elif direct == Direction.LEFT:
		return PlayerActions.MOVE_UP
	elif direct == Direction.RIGHT:
		return PlayerActions.MOVE_DOWN
	else:
		return PlayerActions.MOVE_LEFT

def turnLeft(direct):
	print "Turning Left"
	if direct == Direction.UP:
		return PlayerActions.MOVE_LEFT
	elif direct == Direction.LEFT:
		return PlayerActions.MOVE_DOWN
	elif direct == Direction.RIGHT:
		return PlayerActions.MOVE_UP
	else:
		return PlayerActions.MOVE_RIGHT

def willCollideWithEnemy(board,pos,direct):
	frontTwo = pFront(pFront(pos,direct),direct)
	return board[frontTwo[0]][frontTwo[1]] == LIGHTCYCLE

def atEdge(board,pos):
	return len(board[0])-1 == pos[0]+1 or len(board[0])-1 == pos[1]+1 or 0 == pos[0]-1 or 0 == pos[1]-1
#############################################################################

#Logic Methods


def obstacleIsSafe(board,pos):
	return not atEdge(board,pos) and (board[pos[0]][pos[1]] != TRAIL or board[pos[0]][pos[1]] != LIGHTCYCLE)

def isDeadEnd(board,pos,omitpos, step=12):
	if step:
		# print pos, omitpos, step
		omitpos.append(pos)
		if isObstacle(board,pos):
			return True
		if not isObstacle(board,[pos[0]+1,pos[1]]) and [pos[0]+1,pos[1]] not in omitpos:
			if isDeadEnd(board,[pos[0]+1,pos[1]],omitpos, step-1):
				return True
		elif not isObstacle(board,[pos[0]-1,pos[1]]) and [pos[0]-1,pos[1]] not in omitpos:
			if isDeadEnd(board,[pos[0]-1,pos[1]],omitpos, step-1):
				return True
		elif not isObstacle(board,[pos[0],pos[1]+1]) and [pos[0],pos[1]+1] not in omitpos:
			if isDeadEnd(board,[pos[0],pos[1]+1],omitpos, step-1):
				return True
		elif not isObstacle(board,[pos[0],pos[1]-1]) and [pos[0],pos[1]-1] not in omitpos:
			if isDeadEnd(board,[pos[0],pos[1]-1],omitpos, step-1):
				return True
		else:
			return True
	return False

class PlayerAI():
	def __init__(self):
		self.switching = False
		self.chokePoints = list()
		self.orientation = None
		return

	def new_game(self, game_map, player_lightcycle, opponent_lightcycle):
		return

	def get_move(self, game_map, player_lightcycle, opponent_lightcycle, moveNumber):

		myPos = player_lightcycle['position']
		myX = myPos[0]
		myY = myPos[1]
		myDir = player_lightcycle['direction']

		#Wall check
		if self.orientation is None:
			if isObstacle(game_map,pRight(myPos,myDir)) and not isObstacle(game_map,pLeft(myPos,myDir)):
				self.orientation=CCW
			elif isObstacle(game_map,pLeft(myPos,myDir)) and not isObstacle(game_map,pRight(myPos,myDir)):
				self.orientation=CW

		#Init avoidance algo		
		if self.orientation is None:
			if not isObstacle(game_map,pFront(myPos,myDir)) and not willCollideWithEnemy(game_map,myPos,myDir):
				return moveForward(myDir)
			elif not isObstacle(game_map,pRight(myPos,myDir)):
				self.orientation=CW
				return turnRight(myDir)
			else:
				self.orientation=CCW
				return turnLeft(myDir)

		#Rotation Fill algo
		if self.orientation is not None: 
			#Clockwise
			if self.orientation == CW:
				if self.switching:
					self.switching = False
					if not isObstacle(game_map,pLeft(myPos,myDir)) and (not isObstacle(game_map,pFront(myPos,myDir)) or not isObstacle(game_map,pLeft(myPos,myDir))):
					 return turnLeft(myDir)

				#Hug wall
				if not isObstacle(game_map,pLeft(myPos,myDir)):
					return turnLeft(myDir)

				#Check for self.orientation switch
				if not atEdge(game_map,myPos):
					potentialObstacle = pFront(pFront(pRight(myPos,myDir),myDir),myDir)
					if ((not isObstacle(game_map,pFront(pLeft(myPos,myDir),myDir)) and isObstacle(game_map,pFront(pFront(pLeft(myPos,myDir),myDir),myDir)))
					 or (isObstacle(game_map,potentialObstacle) and not obstacleIsSafe(game_map,potentialObstacle) 
						and not isObstacle(game_map,pFront(pFront(myPos,myDir),myDir)))):
						self.chokePoints.append(pFront(pLeft(myPos,myDir),myDir))
						self.switching = True
						self.orientation = CCW
						print "Switching to CCW"
						if not isObstacle(game_map,pRight(myPos,myDir)):
							return turnRight(myDir)

				#Move clockwise, avoiding obstacles and one-way paths
				if (not isObstacle(game_map,pFront(myPos,myDir)) and not willCollideWithEnemy(game_map,myPos,myDir) and 
					(not isObstacle(game_map,pRight(pFront(myPos,myDir),myDir)) or not isDeadEnd(game_map,pFront(myPos,myDir),[myPos,])
					or not obstacleIsSafe(game_map,pRight(pFront(myPos,myDir),myDir)))):
					return moveForward(myDir)
				elif not isObstacle(game_map,pRight(myPos,myDir)) and not isDeadEnd(game_map, pRight(myPos,myDir), [myPos,]):
						return turnRight(myDir)
				elif not isObstacle(game_map,pFront(myPos,myDir)):
					print "welp"
					return moveForward(myDir)
				else:
					print "OH NO"
					return turnLeft(myDir)

			#Counter clockwise
			if self.orientation == CCW:
				if self.switching:
					self.switching = False
					if not isObstacle(game_map,pRight(myPos,myDir)) and (not isObstacle(game_map,pFront(myPos,myDir)) or not isObstacle(game_map,pRight(myPos,myDir))):
					 return turnRight(myDir)

				#Hug wall
				if not isObstacle(game_map,pRight(myPos,myDir)):
					return turnRight(myDir)

				#Check for self.orientation switch
				if not atEdge(game_map,myPos):
					potentialObstacle = pFront(pFront(pLeft(myPos,myDir),myDir),myDir)
					if ((not isObstacle(game_map,pFront(pRight(myPos,myDir),myDir)) and isObstacle(game_map,pFront(pFront(pRight(myPos,myDir),myDir),myDir)))
						or (isObstacle(game_map,potentialObstacle) and not obstacleIsSafe(game_map,potentialObstacle)
						 and not isObstacle(game_map,pFront(pFront(myPos,myDir),myDir)))):
						self.chokePoints.append(pFront(pRight(myPos,myDir),myDir))
						self.switching = True
						self.orientation = CW
						print "Switching to CW"
						if not isObstacle(game_map,pLeft(myPos,myDir)):
							return turnLeft(myDir)

				#Move counter clockwise, avoiding obstacles and one-way paths
				if (not isObstacle(game_map,pFront(myPos,myDir)) and not willCollideWithEnemy(game_map,myPos,myDir) and 
					(not isObstacle(game_map,pLeft(pFront(myPos,myDir),myDir)) or not isDeadEnd(game_map,pFront(myPos,myDir),[myPos,])
						or not obstacleIsSafe(game_map,pLeft(pFront(myPos,myDir),myDir)))):
					return moveForward(myDir)
				elif not isObstacle(game_map,pLeft(myPos,myDir)) and not isDeadEnd(game_map, pLeft(myPos,myDir), [myPos,]):
						return turnLeft(myDir)
				elif not isObstacle(game_map,pFront(myPos,myDir)):
					print "welp"
					return moveForward(myDir)
				else:
					print "OH NO"
					return turnRight(myDir)





'''

8888888 8888888888 8 888888888o.			,o888888o.		 b.						 8 
			8 8888			 8 8888		`88.	. 8888		 `88.	 888o.					8 
			8 8888			 8 8888		 `88 ,8 8888			 `8b	Y88888o.			 8 
			8 8888			 8 8888		 ,88 88 8888				`8b .`Y888888o.		8 
			8 8888			 8 8888.	 ,88' 88 8888				 88 8o. `Y888888o. 8 
			8 8888			 8 888888888P'	88 8888				 88 8`Y8o. `Y88888o8 
			8 8888			 8 8888`8b			88 8888				,8P 8	 `Y8o. `Y8888 
			8 8888			 8 8888 `8b.		`8 8888			 ,8P	8			`Y8o. `Y8 
			8 8888			 8 8888	 `8b.	 ` 8888		 ,88'	 8				 `Y8o.` 
			8 8888			 8 8888		 `88.		`8888888P'		 8						`Yo
			
																Quick Guide
								--------------------------------------------
											Feel free to delete this comment.

				1. THIS IS THE ONLY .PY OR .BAT FILE YOU SHOULD EDIT THAT CAME FROM THE ZIPPED STARTER KIT

				2. Any external files should be accessible from this directory

				3. new_game is called once at the start of the game if you wish to initialize any values

				4. get_move is called for each turn the game goes on

				5. game_map is a 2-d array that contains values for every board position.
								example call: game_map[2][3] == POWERUP would evaluate to True if there was a powerup at (2, 3)

				6. player_lightcycle is your lightcycle and is what the turn you respond with will be applied to.
								It is a dictionary with corresponding keys: "position", "direction", "hasPowerup", "isInvincible", "powerupType"
								position is a 2-element int array representing the x, y value
								direction is the direction you are travelling in. can be compared with Direction.DIR where DIR is one of UP, RIGHT, DOWN, or LEFT
								hasPowerup is a boolean representing whether or not you have a powerup
								isInvincible is a boolean representing whether or not you are invincible
								powerupType is what, if any, powerup you have

				7. opponent_lightcycle is your opponent's lightcycle. Same keys and values as player_lightcycle

				8. You ultimately are required to return one of the following:
																								PlayerAction.SAME_DIRECTION
																								PlayerAction.MOVE_UP
																								PlayerAction.MOVE_DOWN
																								PlayerAction.MOVE_LEFT
																								PlayerAction.MOVE_RIGHT
																								PlayerAction.ACTIVATE_POWERUP
																								PlayerAction.ACTIVATE_POWERUP_MOVE_UP
																								PlayerAction.ACTIVATE_POWERUP_MOVE_DOWN
																								PlayerAction.ACTIVATE_POWERUP_MOVE_LEFT
																								PlayerAction.ACTIVATE_POWERUP_MOVE_RIGHT
								
				9. If you have any questions, contact challenge@orbis.com

				10. Good luck! Submissions are due Sunday, September 21 at noon. You can submit multiple times and your most recent submission will be the one graded.
	
'''
