from enum import Enum
from enum import auto

#CB changing the type of this
#A class representing a syntax symbol in a propositional statement
class PropSyntax(Enum):
	IMPLIES = auto()
	NOT = auto()
	AND = auto()
	OR = auto()

#A class representing a propositional statement
class Proposition():
	#CB adding recursive aspects here. Propostions embed within each other
	def __init__(self, stringArr):
		for s in range(len(stringArr)):
			try: 
				PropSyntax[stringArr[s]]
			except:
				continue
			else:
				stringArr[s] = PropSyntax[stringArr[s]]
				nextBit = stringArr[s+1:]
				if len(nextBit) > 1:
					stringArr[s+1] = Proposition(nextBit)
					stringArr = stringArr[:s+2]
					break
		self.propArr = stringArr
	def getPropArr(self):
		return self.propArr
	def checkRuleValidity(self, ruleNumber):
		if ruleNumber == 1:
			if self.propArr[1] == PropSyntax.AND or self.propArr[1] == PropSyntax.OR:
				return True
			else:
				return False
		elif ruleNumber == 2:
			if self.propArr[1] == PropSyntax.IMPLIES:
				return True
			else:
				return False
		elif ruleNumber ==3:
			if self.propArr[1] == PropSyntax.OR or self.PropArr[1] == PropSyntax.AND:
				return True
			else:
				return False
		elif ruleNumber == 4:
			if not type(self.propArr[2]) is Proposition:
				return False
			if self.propArr[1] == PropSyntax.OR and self.propArr[2].getPropArr()[1] == PropSyntax.OR:
				return True
			if self.propArr[1] == PropSyntax.AND and self.propArr[2].getPropArr()[1] == PropSyntax.AND:
				return True
			return False
		elif ruleNumber == 5:
			if self.propArr[1] == PropSyntax.OR:
				return True
			else:
				return False
		elif ruleNumber == 6:
			if self.propArr[1] == PropSyntax.IMPLIES:
				return True
			else: 
				return False
		elif ruleNumber == 7:
			if not type(self.propArr[2]) is Proposition:
				return False
			if self.propArr[1] == PropSyntax.OR and self.propArr[2].getPropArr()[1] == PropSyntax.AND:
				return True
			if self.propArr[1] == PropSyntax.AND and self.propArr[2].getPropArr()[1] == PropSyntax.OR:
				return True
			return False
		#CB on GPS' 'main expression' rules
	def applyRule(self, ruleNumber):
		#CB construction
		if ruleNumber == 1:
			temp = self.propArr[0]
			self.propArr[0] = self.propArr[2]
			self.propArr[2] = temp
		if ruleNumber == 2:

