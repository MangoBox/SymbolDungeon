import sys, pygame
import random
import copy
#importing some helper classes
from item import Item
import block
import time
import math

#RENDER WINDOW
pygame.init()
pygame.display.set_caption('SymbolDungeon by Liam Davies')
title_area_height = 30
description_area_height = 200
inventory_area_width = 500
health_area_height = 25
cellSize = 25
screen_dim = [800,500]
screen = pygame.display.set_mode(screen_dim)

#Standard font initialisation
pygame.font.init()
myfont = pygame.font.Font("Arial-Unicode-MS_4302.ttf", 25)


#GRID
grid_dim = [15,15]
grid = [[0 for y in range(grid_dim[1])] for x in range(grid_dim[0])]
anim_time = 0

#COLORS
bg_color = 0, 0, 0

#ENEMIES
enemies = []
enemies_killed = 0

#PLAYER PARAMETERS
pl_pos = [0,0]
start_time = time.time()
curHealth = 10
maxHealth = 10
level = 1
#0 = title screen, 1 = playing, 2 = game over
game_state = 0

#INVENTORY
items = []
cur_item = 0
inventory = []
max_inventory_size = 10
curDescriptionList = []

#Returns the float time in seconds since the game started.
def getTime():
	return time.time() - start_time

#Generates the class definitions for all items.
def generateItems():
	global items
	items.clear()

	#        |    Name   |Icon|       Color      |DrpChance|
	i1 = Item("Parablade", "¶", (120,120,180,255), 0.05)
	i1.type = "sword"
	i1.description = ["It reeks of terrible MS Word formatting.", "As expected, it does nothing that useful.", "Press space to kill enemies nearby."]
	items.append(i1)

	i1 = Item("Integro", "∫", (180,20,120,255), 0.05)
	i1.description = ["Wow! The area affected by its curve!", "Press space to kill enemies in a huge radius."]
	i1.type = "sword"
	items.append(i1)

	i1 = Item("Gammos", "Ɣ", (0,198,0,255), 0.05)
	i1.description = ["So strong, it can only be stopped by a thick layer of lead.",  "Also increases chest spawn rate!", "Press space to kill enemies nearby."]
	i1.type = "sword"
	items.append(i1)

	i1 = Item("Squaro", "√", (174,20,144,255), 0.05)
	i1.description = ["Plus-minus symbol sold seperately.", "Kills a random enemy on the screen when you get hurt." "Press space to kill enemies nearby."]
	i1.type = "sword"
	items.append(i1)

	i1 = Item("Totaler", "∑", (255,127,255,255), 0.05)
	i1.description = ["The amount of enemies you kill from this really adds up to your health!", "Press space to kill enemies nearby."]
	i1.type = "sword"
	items.append(i1)

	i1 = Item("Pie", "π", (255,127,255,255), 0.05)
	i1.description = ["Om nom nom. Increased heart spawn rate.", "Press space to kill enemies nearby."]
	i1.type = "sword"
	items.append(i1)

	i1 = Item("Bandage", "✚", (255,0,0,255), 0.3)
	i1.description = ["Press space to heal 3HP."]
	i1.type = "bandage"
	items.append(i1)

	i1 = Item("Ultra Bandage", "✙", (120,120,120,255), 0.12)
	i1.description = ["Press space to heal to max HP!"]
	i1.type = "ultra_bandage"
	items.append(i1)

	i1 = Item("Grenade", "Ф", (120,120,120,255), 0.3)
	i1.description = ["Press space to kill all enemies nearby you!"]
	i1.type = "grenade"
	items.append(i1)

	i1 = Item("Ultra Grenade", "Φ", (120,120,120,255), 0.12)
	i1.description = ["Press space to kill all enemies in a huge range!"]
	i1.type = "ultra_grenade"
	items.append(i1)

	cur_item = 0

#Generates enemies and places them on the grid.
def generateEnemies():
	spawn_chance = 0.08
	enemies.clear()
	for y in range(grid_dim[1]):
		for x in range(grid_dim[0]):
			if grid[x][y] == None and random.random() < spawn_chance and not y == 0:
				enemies.append([x,y])

#Prints a description caption at the bottom of the screen.
def printDescriptionTitle(title):
	curDescriptionList.clear()
	curDescriptionList.append(title)

#Prints a description caption at the bottom of the screen.
def addDescriptionTitle(title):
	curDescriptionList.append(title)

#Prints a custom bar value to the screen.
def printBar(amount,max_amount,suffix):
	bar_str = "+"
	for a in range(0,max_amount):
		bar_str += "-"
	bar_str += "+"
	print(bar_str)
	main_str = "|"
	for a in range(0,max_amount):
		main_str += "=" if a < amount else " "
	main_str += "|"
	main_str += " " + str(amount) + "/" + str(max_amount) + suffix
	print(main_str)
	print(bar_str)

#Safely accesses the grid, preventing any invalid accesses
def safeAccessGrid(gr,x,y):
	if x < 0 or y < 0 or x >= grid_dim[0] or y >= grid_dim[1]:
		return 0
	return gr[x][y]

#Safely assignments the grid, preventing any invalid assignments
def safeAssignGrid(gr,x,y,val):
	if x < 0 or y < 0 or x >= grid_dim[0] or y >= grid_dim[1]:
		return False
	gr[x][y] = val
	return True

#Tests if a coordinate is valid on the grid.
def isCoordValid(gr,x,y):
	return x >= 0 and y >= 0 and x < grid_dim[0] and y < grid_dim[1]

#Tests if a coordinate is a wall.
def isCoordWall(coord):
	if coord[0] >= len(grid[0]) or coord[1] >= len(grid[1]):
		return True
	if coord[0] < 0 or coord[1] < 0:
		return True
	return safeGridAccessName(coord[0],coord[1]) == "wall"

#Tests for a grid block and acesses it.
def safeGridAccessName(x,y):
	if grid[x][y] != None:
		return grid[x][y].name
	else:
		return ""

#Initialises the game grid.
def initGrid():
	clearGrid()
	wall = block.Block("wall","[  ]", (80,80,80,255))

	for y in range(0,grid_dim[1]):
		for x in range(0,grid_dim[0]):
			if x == 0 or x == grid_dim[0] - 1 or y == 0 or y == grid_dim[1]- 1:
				if not (x == int(grid_dim[0]/2) and (y == 0 or y == grid_dim[1] - 1)):
					grid[x][y] = wall
			else:
				if random.random() < 0.12 and not x == int(grid_dim[0]/2):
					grid[x][y] = wall
				#SPECIAL ITEM: PI (Increases heart spawn rate)
				if random.random() < 0.03 or (random.random() < 0.06 and getCurrentItemName() == "Pie"):
					grid[x][y] = block.Block("heart","❤", (255,0,0,255), True)
				#SPECIAL ITEM: Gammos (Increases chest spawn rate)
				if random.random() < 0.015 or (random.random() < 0.01 and getCurrentItemName() == "Gammos"):
					grid[x][y] = block.Block("chest","[?]", (0,255,0,255))
	pl_pos[0] = int(grid_dim[0]/2)
	pl_pos[1] = 0

#Clears all items on the grid.
def clearGrid():
	for y in range(grid_dim[1]):
		for x in range(grid_dim[0]):
			grid[x][y] = None

#Gets the current item name. Useful for implementing special item functionality.
def getCurrentItemName():
	if len(inventory) == 0:
		return ""
	return inventory[cur_item].name

#Hurts the player and returns True if the player survived the attack.
def hurtPlayer(amount):
	global curHealth
	curHealth -= amount
	if curHealth <= 0:
		#dead
		return False
	#is alive
	return True

#Is the players inventory full?
def isInventoryFull():
	return len(inventory) >= max_inventory_size

#Heals the player an amount. Retusn true if the player reaches max health.
def healPlayer(amount):
	global curHealth
	curHealth += amount
	if curHealth > maxHealth:
		curHealth = maxHealth
		#player is at max health
		return True
	return False

#Resets all parameters of the game.
def resetGame():
	global curHealth, maxHealth, level, enemies_killed
	curHealth = maxHealth
	enemies_killed = 0
	inventory.clear()
	enemies.clear()
	initGrid()
	generateEnemies()
	generateItems()

	#PLAYER PARAMETERS
	pl_pos = [0,0]
	start_time = time.time()
	curHealth = 10
	maxHealth = 10
	level = 1
	#0 = title screen, 1 = playing, 2 = game over
	game_state = 0

	#Adds the standard Parablade sword to the players inventory.
	inventory.append(items[0])

#Returns a range of damage enemies can deal with two functions of the level.
def getEnemyDamage():
	lower_dmg = 2 * level + 2
	upper_dmg = 3 * level + 4
	return random.randint(lower_dmg, upper_dmg)

#Adds an item found to the inventory and a list of found items.
def addInventoryItem(things_found, item):
	things_found.append("You found a {0}! Added it to your inventory.".format(item.name))
	inventory.append(item)

def loop_dungeon_gameMechanics():
	#HANDLES
	#-----------------------------------------
	pos = ()
	global game_state, pl_pos, enemies, cur_item, curHealth, maxHealth, level, enemies_killed
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				#USE ITEM
				typ = inventory[cur_item].type
				#Using a sword
				if typ == "sword":
					rad = 2 if getCurrentItemName() == "Integro" else 1
					old_len = len(enemies)
					available_ens = [e for e in enemies if e[0] >= pl_pos[0] - rad and e[0] <= pl_pos[0] + rad and e[1] >= pl_pos[1] - rad and e[1] <= pl_pos[1] + rad]
					enemies = [x for x in enemies if x not in available_ens]
					enemies_killed += old_len - len(enemies)
					if getCurrentItemName() == "Totaler" and random.random() < 0.3:
						healPlayer(1)
					continue

				#Using a bandage
				if typ == "bandage" or typ == "ultra_bandage":
					curHealth += 3 if typ == "bandage" else (maxHealth - curHealth)
					if curHealth > maxHealth:
						curHealth = maxHealth
					inventory.remove(inventory[cur_item])

				#Using a grenade
				if typ == "grenade" or typ == "ultra_grenade":
					to_remove = []
					rad = 2 if typ == "grenade" else 3
					for e in enemies:
						if e[0] >= pl_pos[0] - rad and e[0] <= pl_pos[0] + rad and e[1] >= pl_pos[1] - rad and e[1] <= pl_pos[1] + rad:
							to_remove.append(e)
					for e in to_remove:
						enemies.remove(e)
						enemies_killed += 1
					inventory.remove(inventory[cur_item])

			#Quit the game
			if event.key == pygame.K_ESCAPE:
				sys.exit()

			#Delete item from inventory
			if event.key == pygame.K_BACKSPACE:
				#delete current item
				if len(inventory) > 1:
					inventory.remove(inventory[cur_item])

			#Inventory slots
			if event.key == pygame.K_COMMA or event.key == pygame.K_LEFTBRACKET:
				cur_item -= 1
			if event.key == pygame.K_PERIOD or event.key == pygame.K_RIGHTBRACKET:
				cur_item += 1
			#Ensure inventory indexing can't escape the inventory's size.
			cur_item %= len(inventory)

			#PLAYER MOVEMENT
			tmp = copy.copy(pl_pos)
			moved = False
			if event.key == pygame.K_LEFT:
				tmp[0] -= 1
				moved = True
			if event.key == pygame.K_RIGHT:
				tmp[0] += 1
				moved = True
			if event.key == pygame.K_UP:
				tmp[1] -= 1
				moved = True
			if event.key == pygame.K_DOWN:
				tmp[1] += 1
				moved = True

			#Tests if player can move into spot (if its not a wall)
			if not isCoordWall(tmp) and moved:
				pl_pos = tmp
				#reset player description
				printDescriptionTitle("")
				anim_time = getTime()

				#ENEMIES MOVEMENT
				#Moved player, updates enemies
				for e in enemies:
					#Five attempts to move enemy
					for i in range(0,4):
						e_pos = copy.copy(e)
						sel = int(random.random() * 8)
						if sel == 0:
							e_pos[0] += 1
						elif sel == 1:
							e_pos[0] -= 1
						elif sel == 2:
							e_pos[1] += 1
						elif sel == 3:
							e_pos[1] -= 1

						if e_pos[0] < 0 or e_pos[0] > grid_dim[0] - 1 or e_pos[1] < 0 or e_pos[1] > grid_dim[1] - 1:
							continue
						#Checks there isn't already an enemy there
						for en in enemies:
							if e_pos == en:
								continue
						#Updates the enemies new position
						if grid[e_pos[0]][e_pos[1]] == None:
							enemies.remove(e)
							enemies.append(e_pos)
							break

				for e in enemies:
					#Tests if any enemy is on the players position.
					if e[0] == pl_pos[0] and e[1] == pl_pos[1]:
						#Player taken damage
						dmg = getEnemyDamage()
						#Special item: Squaro. Kills enemies when player hurt
						if getCurrentItemName() == "Squaro":
							enemies.remove(random.choice(enemies))
						addDescriptionTitle("An enemy hit you! (-{0} HP)".format(dmg))
						if e in enemies:
							enemies.remove(e)

						if not hurtPlayer(dmg):
							#PLAYER DIES
							game_state = 2
						break

		#FINDING CHEST
		if safeGridAccessName(pl_pos[0],pl_pos[1]) == "chest":
			printDescriptionTitle("You found a chest!")
			#resetting position
			grid[pl_pos[0]][pl_pos[1]] = None
			thingsFound = []
			for i in range(10):
				if isInventoryFull():
					break
				ran_item = random.choice(items)
				if ran_item.drop_chance > random.random():
					addInventoryItem(thingsFound, ran_item)	
				if random.random() < 0.1:
					thingsFound.append("You found a health potion! (Max HP +1)")
					maxHealth += 1
			if len(thingsFound) == 0:
				thingsFound.append("There was nothing in it.")
			curDescriptionList.extend(thingsFound)

		#FINDING HEART
		if safeGridAccessName(pl_pos[0],pl_pos[1]) == "heart":
			#finding chest
			if curHealth >= maxHealth:
				printDescriptionTitle("You're already at maximum health.")
			else:		
				printDescriptionTitle("You found extra health! (+1 HP)")
				#resetting position
				grid[pl_pos[0]][pl_pos[1]] = None
				curHealth += 1

		#FINISHING LEVEL
		if pl_pos[0] == int(grid_dim[0]/2) and pl_pos[1] == grid_dim[1] - 1:
			#finish player level
			initGrid()
			generateEnemies()
			generateItems()
			level += 1

def loop_dungeon_renderGraphics():
	#RENDERING
	#-----------------------------------------
	for x in range(0, grid_dim[0]):
		for y in range(0, grid_dim[1]):
			#Gathering rendering parameters
			txt = ""
			isPlayer = pl_pos[0] == x and pl_pos[1] == y
			isEnemy = len([e for e in enemies if e[0] == x and e[1] == y]) >= 1
			txt = ""
			color = (255,255,255,255)
			bob = False
			#Entity symbols
			if isEnemy:
				txt = "〠"
			if isPlayer:
				txt = "♜"

				#rendering item
				if cur_item < len(inventory) or cur_item >= 0:
					item = inventory[cur_item]
					icon_txt = myfont.render(item.icon, True, item.color)
					screen.blit(icon_txt, (x*cellSize + 15, y*cellSize + 10))

			#If rendering block on screen
			if grid[x][y] != None and not isEnemy and not isPlayer:
				txt = grid[x][y].icon
				color = grid[x][y].color
				bob = grid[x][y].bob

			offset = [0,0]
			#If this item needs to bob
			if bob:
				offset[1] = math.sin(getTime()*5+grid[x][y].offset)*3

			#Render symbols onto centered screen position
			textsurface = myfont.render(txt, True, color)
			text_rect = textsurface.get_rect(center=(x*cellSize+(cellSize/2)+offset[0],title_area_height+y*cellSize+(cellSize/2)+offset[1]))
			screen.blit(textsurface, text_rect)

def loop_dungeon_renderUI():
	#UI RENDERING
	#-----------------------------------------
	#Renders health bar with colours
	health_perc = curHealth / maxHealth
	health_color = (255 - (255 * health_perc), 255 * health_perc, 0, 255) if health_perc >= 0 else (255,0,0,255)
	textsurface = myfont.render("[{2}] {0}/{1}HP ".format(curHealth,maxHealth,("❙" * curHealth) + " " * (maxHealth-curHealth)), True, health_color)
	screen.blit(textsurface, (cellSize * grid_dim[0] + 5, 25))

	#Renders level text
	leveltext = myfont.render("Level {0}".format(level), True, (255,255,255,255))
	screen.blit(leveltext, (0,0))

	#Renders below-game descriptions of items and enemy statuses.
	description_font = pygame.font.Font("Arial-Unicode-MS_4302.ttf",14)
	if len(curDescriptionList) != 0:
		for i in range(len(curDescriptionList)):
			textsurface = description_font.render(curDescriptionList[i], True, (255,255,255,255))
			screen.blit(textsurface, (0,5+ i * 15 + cellSize * grid_dim[1] + title_area_height + 5))

	#Renders inventory area
	inventory_text = myfont.render("Inventory [{0}/{1} Items]".format(len(inventory), max_inventory_size), True, (255,255,255,255))
	screen.blit(inventory_text, (grid_dim[1] * cellSize + 5, title_area_height + health_area_height))

	inventory_line = myfont.render("---------------------", True, (255,255,255,255))
	screen.blit(inventory_line, (grid_dim[1] * cellSize + 5, title_area_height + health_area_height + 20))

	#Renders items and changes colour if item is selected.
	for i in range(0,len(inventory)):
		i_str = "[ " + inventory[i].icon + " ] " + inventory[i].name
		inventory_item = myfont.render(i_str, True, (255,255,255,255) if i == cur_item else (75,75,75,255))
		screen.blit(inventory_item, (grid_dim[1] * cellSize + 5, title_area_height + health_area_height + 	40 + i * 30))

	inventory_line = myfont.render("---------------------", True, (255,255,255,255))
	screen.blit(inventory_line, (grid_dim[1] * cellSize + 5, title_area_height + health_area_height + 	40 + len(inventory) * 30))
		
	#Renders current item description. Lets user know what item does.
	cur_i = inventory[cur_item]
	description_font = pygame.font.Font("Arial-Unicode-MS_4302.ttf",14)
	for i in range(len(cur_i.description)):
		d_str = cur_i.description[i]
		inventory_item = description_font.render(d_str, True, (255,255,255,255))
		screen.blit(inventory_item, (grid_dim[1] * cellSize + 5, title_area_height + health_area_height + 60 + len(inventory) * 30 + i * 20))

	#Subtitle text to help user know controls.
	sub_text = description_font.render("| WASD to move | Space: Use Item | Backspace: Delete Item | <>: Switch Item | Esc: Quit Game |", True, (170,170,170,255))
	screen.blit(sub_text, (120,5))

def loop_mainMenu():
	global game_state
	#Input handling
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				#play
				resetGame()
				game_state = 1
				
			if event.key == pygame.K_ESCAPE:
				sys.exit()

	#Falling letters
	t = getTime()
	falling_font = pygame.font.Font("Arial-Unicode-MS_4302.ttf",25)
	i = 0
	for letter_ind in list(range(32,126)) * 5:
		letter = str(chr(letter_ind))
		inventory_item = falling_font.render(letter, True, (70,70,70,255))
		screen.blit(inventory_item, (math.sin(letter_ind * i * 1203 + 155) * screen_dim[0], -100 + (t*25 + math.cos(letter_ind) * (i+5) * 100)% (screen_dim[1] + 200)))
		i += 1

	#Title screen
	title_font = pygame.font.Font("Arial-Unicode-MS_4302.ttf",35)
	title_text = title_font.render("SymbolDungeon", False, (255,255,255,255))
	text_rect = title_text.get_rect(center=(screen_dim[0]/2,screen_dim[1]/2-35))
	screen.blit(title_text, text_rect)

	#Menu Names
	title_font = pygame.font.Font("Arial-Unicode-MS_4302.ttf",25)
	title_text = title_font.render("Press Space to play or press Escape to quit.", False, (255,255,255,255))
	text_rect = title_text.get_rect(center=(screen_dim[0]/2,screen_dim[1]/2+30))
	screen.blit(title_text, text_rect)

	#Subtitle
	title_font = pygame.font.Font("Arial-Unicode-MS_4302.ttf",15)
	title_text = title_font.render("A game made entirely with text symbols!", False, (255,255,255,150))
	text_rect = title_text.get_rect(center=(screen_dim[0]/2,screen_dim[1]/2))
	screen.blit(title_text, text_rect)

def loop_gameOverMenu():
	global game_state, level, enemies_killed
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				game_state = 0

	#GAME OVER
	title_font = pygame.font.Font("Arial-Unicode-MS_4302.ttf",50)
	offset_y = -math.cos(getTime()*1.5+1203) * 5
	title_text = title_font.render("GAME OVER", False, (255,0,0,255))
	text_rect = title_text.get_rect(center=(screen_dim[0]/2,screen_dim[1]/2+offset_y))
	screen.blit(title_text, text_rect)

	title_font = pygame.font.Font("Arial-Unicode-MS_4302.ttf",15)
	title_text = title_font.render("You reached level {0} and killed {1} enemies!".format(level, enemies_killed), False, (255,255,255,150))
	text_rect = title_text.get_rect(center=(screen_dim[0]/2,screen_dim[1]/2+40))
	screen.blit(title_text, text_rect)

	title_font = pygame.font.Font("Arial-Unicode-MS_4302.ttf",15)
	title_text = title_font.render("Press space to go to main menu.".format(level), False, (255,255,255,150))
	text_rect = title_text.get_rect(center=(screen_dim[0]/2,screen_dim[1]/2+55))
	screen.blit(title_text, text_rect)

#The primary loop for dungeon code.
def loop_dungeon():
	loop_dungeon_gameMechanics()	
	loop_dungeon_renderGraphics()
	loop_dungeon_renderUI()
	

#Main Function of game.
def startGame():
	global game_state, pl_pos, enemies, cur_item, curHealth, maxHealth, level
	resetGame()
	while 1:
		if game_state == 0:
			loop_mainMenu()
		if game_state == 1:
			loop_dungeon()
		if game_state == 2:
			loop_gameOverMenu()

		#Writes changes to graphics buffer
		pygame.display.flip()
		#Clears screen
		screen.fill(bg_color)
		
#Makes sure this code is being run from this file alone.
if __name__ == "__main__":
	startGame()