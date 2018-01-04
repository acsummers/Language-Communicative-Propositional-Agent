from enum import Enum
from enum import auto

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
					if node.label() == 'NN' or node.label() == 'NNS' or node.label() == 'NNP' or node.label() == 'NNPS' or node.label() == 'PRP' or node.label == 'PRP$':
						subjects.append((node[0], node.label()))
				
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
				adjpSeen = False

				for i in range(len(VP)):
					if VP[i].label() == 'SBAR':
						SBAR = VP[i]
					elif (VP[i].label()  == 'NN' or VP[i].label() == 'JJ' or VP[i].label() == 'JJR' or VP[i].label() == 'JJS' or VP[i].label() == 'VBG' or VP[i].label() == 'VBN' or VP[i].label() == 'NNS' or VP[i].label() == 'NNP' or VP[i].label() == 'NNPS' or VP[i].label() == 'PRP' or VP[i].label() == 'PRP$'):
						objects.append((VP[i][0], VP[i].label()))
					elif (VP[i].label() == 'NP'):
						node = VP[i]
						while not type(node[0][0]) is str:
							node = node[0]
						for o in range(len(node)):
							temp = node[o]
							if temp.label() == 'NN' or temp.label() == 'NNS' or temp.label() == 'NNP' or temp.label() == 'NNPS' or temp.label() == 'PRP' or temp.label == 'PRP$':
								objects.append((temp[0], temp.label()))
					elif (VP[i].label() == 'VP'):
						node = VP[i]
						while not type(node[0][0]) is str:
							node = node[0]
						for o in range(len(node)):
							temp = node[o]
							if temp.label() == 'VBN' or temp.label() == 'VBG':
								objects.append((temp[0], temp.label()))
					elif (VP[i].label() == 'ADJP'):
						adjpSeen = True
						node = VP[i]
						while not type(node[0][0]) is str:
							node = node[0]
						for o in range(len(node)):
							temp = node[o]
							if temp.label() == 'JJ' or temp.label() == 'JJR' or temp.label() == 'JJS':
								objects.append((temp[0], temp.label()))
					elif (VP[i].label() == 'PP' and adjpSeen == True):
						node = VP[i]
						for n in range(len(node)):
							if node[n].label() == 'NP':
								node = node[n]
						while not type(node[0][0]) is str:
							node = node[0]
						for o in range(len(node)):
							temp = node[o]
							if temp.label() == 'NN' or temp.label() == 'NNS' or temp.label() == 'NNP' or temp.label() == 'NNPS' or temp.label() == 'PRP' or temp.label == 'PRP$':
								objects.append((temp[0], temp.label()))

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
from nltk.wsd import lesk
from nltk.corpus import wordnet

class Agent():
	def __init__(self):
		self.speechProcessor = SpeechProcessor()
		self.stemmer = PorterStemmer()
		self.propositions = []
		self.synsetsList = []

	def checkSynset(self, synset, usedByAdd=False):
		if not synset:
			return -1

		candidate = -1
		topScore = -1

		for s in range(len(self.synsetsList)):
			theSet = self.synsetsList[s]
			for i in range(len(theSet)):
				item = theSet[i]
				simScore = synset.wup_similarity(item)

				#This handles the fact that there 
				#needs to be extra information returned
				#in the case that we want to know whether or not to add a synset
				#to the list
				if item == synset or simScore == 1.00:
					if not usedByAdd:
						return s
					else:
						return (s,)
				if simScore and simScore > 0.75 and simScore > topScore:
					candidate = s
					topScore = simScore

		return candidate

	def addSynset(self, synset):
		candidate = self.checkSynset(synset, usedByAdd=True)
		if type(candidate) is tuple:
			return candidate[0]
		if candidate != -1:
			self.synsetsList[candidate].append(synset)
			return candidate
		else:
			self.synsetsList.append([synset])
			return len(self.synsetsList)-1


	#Create proposition helper method
	def constructClause(self, inputArray, splitSentence):
		toReturn = []
		for tup in inputArray:
				synSubj = None
				if treeToWordNet(tup[1]):
					synSubj = lesk(splitSentence, tup[0], treeToWordNet(tup[1]))
				if not synSubj:
					toReturn.append(tup[0])
				else:
					print("Word: " + tup[0])
					print(synSubj)
					setIndex = self.addSynset(synSubj)
					toReturn.append("SYN_" + str(setIndex))
		return toReturn


	def createPropositions(self, sentence):
		logic = self.speechProcessor.extractLogic(sentence)
		splitSentence = sentence.split()

		#CB supporting hypotheticals
		#CB incorporating difference between subject and object into symbols themselves
		if 'conclusion' in logic:
			premise = self.constructClause(logic['premise']['subjects'], splitSentence)

			
			premise.extend(self.constructClause(logic['premise']['objects'], splitSentence))
				
			conclusion = self.constructClause(logic['conclusion']['subjects'], splitSentence)
			conclusion.extend(self.constructClause(logic['conclusion']['objects'], splitSentence))

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
			allFacts = self.constructClause(logic['subjects'], splitSentence)
			allFacts.extend(self.constructClause(logic['objects'], splitSentence))
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
		splitSentence = question.split()

		if 'subjects' in logic:
			q = ""
			for s in logic['subjects']:
				subj = s[0]
				leskAnalysis = None
				if treeToWordNet(s[1]):
					leskAnalysis = lesk(splitSentence, s[0], treeToWordNet(s[1]))
				setIndex = self.checkSynset(leskAnalysis)
				if setIndex != -1:
					subj = "SYN_" + str(setIndex)

				if q == "":
					q = subj
				else:
					q = q + " " + subj
			for o in logic['objects']:
				obj = o[0]
				leskAnalysis = None
				if treeToWordNet(o[1]):
					leskAnalysis = lesk(splitSentence, o[0], treeToWordNet(o[1]))
				setIndex = self.checkSynset(leskAnalysis)
				if setIndex != -1:
					obj = "SYN_" + str(setIndex)

				if q == "":
					q = obj
				else:
					q = q + " " + obj
			print(q)
			if len(q) > 0:
				return self.query(q)
		return False
			
def treeToWordNet(tag):
	if tag == "NNS" or tag =="NN":
		return "n"
	if tag == "VB" or tag =="VBD" or tag =="VBG" or tag =="VBN" or tag =="VBP" or tag =="VBZ":
		return "v"
	if tag == "JJ" or tag =="JJR" or tag =="JJS":
		return "a"
	if tag =="RB" or tag == "RBR" or tag == "RBS":
		return "r"

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


