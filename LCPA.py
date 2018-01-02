#
#	TODO
#

#Different verbs represented logically
#Synonyms represented as the same logical concept
#Word sense disambiguation to differentiate between different meanings or contexts of the same word
#Logical not and whether it works with horn clauses
#

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

import nltk.parse.stanford
class SpeechProcessor():
	def __init__(self):
		self.stanfordParser = nltk.parse.stanford.StanfordParser(path_to_jar='/usr/local/Cellar/stanford-parser/3.8.0/libexec/stanford-parser.jar', path_to_models_jar='/usr/local/Cellar/stanford-parser/3.8.0/libexec/stanford-parser-3.8.0-models.jar', model_path='/usr/local/Cellar/stanford-parser/3.8.0/libexec/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz')
	def rawParse(self, sentence):
		return list(self.stanfordParser.raw_parse(sentence))
	def extractLogic(self, sentence, inputTree=None):
		hypothetical = False

		if not inputTree:
			rawParsed = self.rawParse(sentence)
			inputTree = rawParsed[0][0]

		SBAR = None
		#Only handling declarative sentences for now
		if inputTree.label() == 'S':
			for i in range(len(inputTree)):
				if inputTree[i].label() == 'NP':
					NP = inputTree[i]
				elif inputTree[i].label() == 'VP':
					VP = inputTree[i]
				elif inputTree[i].label() == 'SBAR':
					SBAR = inputTree[i]
			try:
				VP and NP
			except:
				return
			else:
				while not type(NP[0][0]) is str:
					NP = NP[0]
				subjects =[]
				for s in range(len(NP)):
					node = NP[s]
					if type(node[0]) is str:
						subjects.append(node[0])

				#print(VP)
				#CB sentences like 
				#The sun is bigger than the earth
				#Subjects: The sun Objects: N/A
				#CB Boston is the capitol of massachusetts
				#Subjects: Boston Objects: the capitol
				#CB The crown is a tv series about queen elizabeth
				#Subjects: The crown Objects: a tv series

				#There are 24 hours in a day
				#Subjects: There Objects: 24 hours
				#The subject is right given the parse tree, handle cases like this in more detail

				newVP = None

				for i in range(len(VP)):
					if (newVP == None and (VP[i].label() == 'NP' or VP[i].label() == 'ADJP' or VP[i].label() == 'VP')):
						newVP = VP[i]
					elif VP[i].label() == 'MD':
						hypothetical = True
					elif VP[i].label() == 'SBAR':
						SBAR = VP[i]


				if newVP:
					VP = newVP

				objects = []
				for i in range(len(VP)):
					if VP[i].label() == 'SBAR':
						SBAR = VP[i]
					elif (VP[i].label()  == 'NN' or VP[i].label() == 'JJ' or VP[i].label() == 'VBG' or VP[i].label() == 'VBN' or VP[i].label() == 'NNS'):
						objects.append(VP[i][0])
					elif (VP[i].label() == 'NP'):
					#or VP[i].label() == 'ADJP' or VP[i].label() == 'PP'):
					#CB more complicated internal phrases
						node = VP[i]
						while not type(node[0][0]) is str:
							node = node[0]
						for o in range(len(node)):
							temp = node[o]
							if type(temp[0]) is str:
								objects.append(temp[0])
					#CB if this is really necessary, might not have as many of these internal verb phrases
					elif (VP[i].label() == 'VP'):
						node = VP[i]
						while not type(node[0][0]) is str:
							node = node[0]
						for o in range(len(node)):
							temp = node[o]
							if temp.label() == 'VBN' or temp.label() == 'VBG' and type(temp[0]) is str:
								objects.append(temp[0])

				if SBAR:
					for node in SBAR:
						if node.label() == 'S':
							SBAR = self.extractLogic('', node)
				if SBAR:
					return {'conclusion':{'subjects': subjects, 'objects': objects}, 'premise': SBAR}
				else:
					if hypothetical:
						return {'conclusion':{'subjects': subjects, 'objects': objects}, 'premise': '?'}
					else:
						return {'subjects': subjects, 'objects': objects}
		return None

import json
from nltk import PorterStemmer
class Agent():
	def __init__(self):
		self.speechProcessor = SpeechProcessor()
		self.stemmer = PorterStemmer()
		self.propositions = []
	def createPropositions(self, sentence):
		logic = self.speechProcessor.extractLogic(sentence)

		#CB supporting hypotheticals
		#CB incorporating difference between subject and object into symbols themselves
		if 'conclusion' in logic:
			premise = [subject for subject in logic['premise']['subjects']]
				#subject + "_S"
			premise.extend([obj for obj in logic['premise']['objects']])
				#obj + "_O"
			conclusion = [subject for subject in logic['conclusion']['subjects']]
			conclusion.extend([obj for obj in logic['conclusion']['objects']])

			for p in range(len(premise)-1, 0, -1):
				premise.insert(p, 'AND')

			toReturn = []
			#CB the logic on this
			finalConclusion = ""
			for c in conclusion:
				if finalConclusion == "":
					finalConclusion = c
				else:
					finalConclusion = finalConclusion + " " + c

			temp = premise.copy()
			temp.extend(['IMPLIES', finalConclusion])
			toReturn.append(temp)

			return [Proposition(r) for r in toReturn]
		else:
			allFacts = logic['subjects']
			allFacts.extend(logic['objects'])
			return [Proposition([s]) for s in allFacts]

		#return Proposition([finalSubject, 'IMPLIES', finalObject])
	def storeProposition(self, sentence):
		self.propositions.extend(self.createPropositions(sentence))
	def getPropositions(self):
		return self.propositions
	def displayPropArr(self, index=-1):
		if index == -1:
			for prop in self.propositions:
				print(prop.getPropArr())
		else:
			print(self.propositions[index].getPropArr())
	def query(self, q):
		return PL_FC_Entails([prop.propArr for prop in self.propositions], q)
	def askQuestion(self, question):
		logic = self.speechProcessor.extractLogic(question)
		if 'subjects' in logic:
			q = ""
			for s in logic['subjects']:
				if q == "":
					q = s
				else:
					q = q + " " + s
			for o in logic['objects']:
				if q == "":
					q = o
				else:
					q = q + " " + o
			if len(q) > 0:
				return self.query(q)
		return False
			



#Implemented Propositional Logic Forward Chain Entails algorithm here,
#as described in Artificial Intelligence A Modern Approach by Russell and Norvig
def PL_FC_Entails(KB, q=None):
	agenda = []
	inferred = {}
	count = {}


	for clauseIndex in range(len(KB)):
		clause = KB[clauseIndex]

		#If there is no implies symbol in the horn clause, the clause is simply a known fact
		try: 
			clause.index(PropSyntax.IMPLIES)
		except:
			agenda.extend(clause)

		#Count the symbols in the proposition, as well as check for unique symbols in the entire clause, in one loop
		c = 0
		impliesSeen = False
		for symbol in clause:
			#Once the implies symbol is seen, the remaining symbol is part of the conclusion
			if symbol == PropSyntax.IMPLIES:
				impliesSeen = True
			#While handling symbols, we want to ignore all propositional syntax
			elif type(symbol) != PropSyntax:
				if not symbol in inferred:
					inferred[symbol] = False
				if impliesSeen == False:	
					c = c + 1

		count[clauseIndex] = c

	while agenda:
		p = agenda.pop()
		if p == q:
			return True
		if inferred[p] == False:
			inferred[p] = True
			#CB make this more efficient with some presorting
			for clauseIndex in range(len(KB)):

				clause = KB[clauseIndex]

				try:
					pIndex = clause.index(p)
				except:
					None
				else:
					try:
						iIndex = clause.index(PropSyntax.IMPLIES)
					except:
						None
					else:
						if pIndex < iIndex:
							count[clauseIndex] = count[clauseIndex] - 1
							if count[clauseIndex] == 0:
								agenda.append(clause[iIndex+1])
	return False


