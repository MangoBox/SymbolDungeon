import random

class Block:
	def __init__(self, name, icon, color, bob=False):
		self.name = name
		self.icon = icon
		self.color = color
		self.bob = bob
		if bob:
			#Makes sure bobbing blocks are never in sync with one another.
			self.offset = random.random() * 12