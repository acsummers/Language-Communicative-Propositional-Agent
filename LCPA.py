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
	#Constructor assumes a properly formatted string array as input
	def __init__(self, stringArr):
		newArr = []
		s = 0
		while s < len(stringArr):
			if stringArr[s] == "(":
				newProp = Proposition(stringArr[s+1:])
				newArr.append(newProp)
				s += newProp.getTotalLength()+2
			elif stringArr[s] == ")":
				break
			try: 
			 	PropSyntax[stringArr[s]]
			except:
				if s < len(stringArr):
					newArr.append(stringArr[s])
					s += 1
				continue
			else:
				#Add in the not case
				newArr.append(PropSyntax[stringArr[s]])
				#if stringArr[s] == "NOT":
				#	if (s+1) == (len(stringArr)-1):
				#		continue
				#	else:

				
			s += 1
		self.propArr = newArr
	def getPropArr(self):
		return self.propArr
	def getTotalLength(self):
		length = 0
		for item in self.propArr:
			if type(item) is Proposition:
				#Includes parens
				length += item.getTotalLength() + 2
			else:
				length += 1
		return length
	#TODO: implement the rules portion
	"""def checkRuleValidity(self, ruleNumber):
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
		#CB this one
		#if ruleNumber == 2:
		#if ruleNumber == 3:"""

import nltk.parse.stanford
class SpeechProcessor():
	def __init__(self):
		self.stanfordParser = nltk.parse.stanford.StanfordParser(path_to_jar='/usr/local/Cellar/stanford-parser/3.8.0/libexec/stanford-parser.jar', path_to_models_jar='/usr/local/Cellar/stanford-parser/3.8.0/libexec/stanford-parser-3.8.0-models.jar', model_path='/usr/local/Cellar/stanford-parser/3.8.0/libexec/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz')
	def rawParse(self, sentence):
		return list(self.stanfordParser.raw_parse(sentence))
	def extractLogic(self, sentence):
		rawParsed = self.rawParse(sentence)
		#Only handling declarative sentences for now
		if rawParsed[0][0].label() == 'S':
			for i in range(len(rawParsed[0][0])):
				if rawParsed[0][0][i].label() == 'NP':
					NP = rawParsed[0][0][i]
				elif rawParsed[0][0][i].label() == 'VP':
					VP = rawParsed[0][0][i]
			try:
				VP and NP
			except:
				return
			else:
				while not type(NP[0]) is str:
					NP = NP[0]
				subjects =[]
				for s in range(len(NP)):
					if type(NP[s]) is str:
						subjects.append(NP[s])

				print(VP)
				#CB sentences like 
				#The sun is bigger than the earth
				#Subjects: The Objects: N/A
				#CB Boston is the capitol of massachusetts
				#Subjects: Boston Objects: N/A
				#CB The crown is a tv series about queen elizabeth
				#Subjects: The Objects: N/A
				#There are 24 hours in a day
				#Subjects: There Objects: N/A
				for i in range(len(VP)):
					if (VP[i].label() == 'NP' or VP[i].label() == 'ADJP'):
						VP = VP[i]
						break

				objects = []
				for i in range(len(VP)):
					if (VP[i].label()  == 'NN' or VP[i].label() == 'JJ' or VP[i].label() == 'VBG'):
						objects.append(VP[i][0])
		return "subjects: " + " ".join(subjects) + ". objects: " + " ".join(objects) + "."


				

