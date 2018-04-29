#from pymongo import MongoClient
import zipfile
from io import BytesIO
import sys
import os
import linecache
import random

import graphviz
from sklearn import tree
from sklearn.preprocessing import LabelBinarizer
from sklearn.tree import DecisionTreeClassifier


class node:

	discrete = False
	isplit = 0
	dataType = ""
	left = None
	right = None

	def __init__(self, discrete, isplit, dataType):
		self.discrete = discrete
		self.isplit = isplit
		self.dataType = dataType

def labels(A):
	L = []
	if(0 in A):
		L.append("first_time_homebuyer_flag")
	if(1 in A):
		L.append("morg_insur_percent")
	if(2 in A):
		L.append("num_units")
	if(3 in A):
		L.append("occupancy_stat")
	if(4 in A):
		L.append("combined_loan_to_val")
	if(5 in A):
		L.append("orig_debt_to_income")
	if(6 in A):
		L.append("orig_upb")
	if(7 in A):
		L.append("orig_loan_to_val")
	if(8 in A):
		L.append("orig_interest_rate")
	if(9 in A):
		L.append("prepay_penalty_flag")
	if(10 in A):
		L.append("loan_purpose")
	if(11 in A):
		L.append("orig_loan_term")
	if(12 in A):
		L.append("num_borrowers")
	return L

def makeNice(data, A):
	new = []

	#"first_time_homebuyer_flag",
	if(0 in A):
		if(data[2] == "Y"):
			new.append(1)
		else:
			new.append(-1)
	if(1 in A):
		new.append(float(data[5]))#"morg_insur_percent",
	if(2 in A):
		new.append(float(data[6]))#"num_units",
		#"occupancy_stat",
	if(3 in A):
		if(data[7] == "P"):
			new.append(1)
		else:
			new.append(-1)

	if(4 in A):
		new.append(float(data[8]))#"combined_loan_to_val",
	if(5 in A):
		new.append(float(data[9]))#"orig_debt_to_income",
	if(6 in A):
		new.append(float(data[10]))#"orig_upb",
	if(7 in A):
		new.append(float(data[11]))#"orig_loan_to_val",
	if(8 in A):
		new.append(float(data[12]))#"orig_interest_rate",
		
	#"prepay_penalty_flag",
	if(9 in A):
		if(data[14] == "Y"):
			new.append(1)
		else:
			new.append(-1)

	#"loan_purpose",
	if(10 in A):
		if(data[20] == "P"):
			new.append(1)
		else:
			new.append(-1)
	if(11 in A):
		new.append(float(data[21]))#"orig_loan_term",
	if(12 in A):
		new.append(float(data[22]))#"num_borrowers",

	return new

def getData(maxData, origfile, svcfile):
	x = [] #[labels()]
	y = [] #['default']

	panic = False

	with open(origfile) as orig:
		i = 1
		maxDataI = 0
		for line in orig:
			origDat = line.split('|')
			#find monthly data
			found = False
			panic = False
			j = 0
			while(j < 100):
				j+=1
				monthDat = (linecache.getline(svcfile, i)).split('|')
				
				if(monthDat[0] == origDat[19]):
					j -= 1
					found = True
				elif(found):
					monthDat = linecache.getline(svcfile, i-1).split('|')
					if(monthDat[3] == "R"):
						origDat.append(0)
					else:
						origDat.append(int(monthDat[3]) >= 4) 
					break

				if(j == 99):
					print("Panic: " + str(maxDataI))
					i -= 100
					#print(monthDat[0])
					#print(origDat[19])
					panic = True
					break
				i+=1

			if(panic):
				continue

			if(origDat[26]):
				y.append(1)
			else:
				y.append(-1)
			origDat.pop()
			x.append(origDat)
			

			maxDataI +=1
			if(maxData == maxDataI):
				break
		orig.close()
		linecache.clearcache()
	return x,y

def dTree(nodes, maxNodes, x0,y):
	x = []
	for i in x0:
		x.append(makeNice(i, nodes))

	clf = DecisionTreeClassifier(max_depth=3)
	clf = clf.fit(x, y)

	#dot_data = tree.export_graphviz(clf, out_file=None,feature_names=labels(),class_names=["Defaulted", "Didn't Default"],filled=True, rounded=True,special_characters=True)
	#graph = graphviz.Source(dot_data)
	#graph.view()
	return clf

def test(tree, nodes, x0, y):
	x = []
	fp = 0
	fn = 1
	tp = 0
	tn = 0
	for i in range(0, len(x0)):
		v = tree.predict([makeNice(x0[i], nodes)])

		if(v==1 and y[i] == 1):
			tp += 1
		elif(v== 1 and y[i] == -1):
			fp += 1
		elif(v== -1 and y[i] == -1):
			tn += 1		
		elif(v== -1 and y[i] == 1):
			fn += 1

	return tp/fn

def testForest(trees, nodes, x0, y):
	x = []
	fp = 0
	fn = 0
	tp = 0
	tn = 0
	default = []
	nodefault = []
	for i in range(0, len(x0)):
		v = 0
		for j in range (0, len(trees)):
			if( trees[j].predict([makeNice(x0[i], nodes[j])]) == 1):
				v+=1
		if(v > 0):
			v = 1
		else:
			v = -1

		if(v==1 and y[i] == 1):
			tp += 1
		elif(v== 1 and y[i] == -1):
			fp += 1
		elif(v== -1 and y[i] == -1):
			tn += 1		
		elif(v== -1 and y[i] == 1):
			fn += 1

	print("tp: " + str(tp))
	print("fp: " + str(fp))
	print("tn: " + str(tn))
	print("fn: " + str(fn))

def randomForest(numTrees, maxNodes):
	data = getData(20000, "historical_data1_Q12009.txt", "historical_data1_time_Q12009.txt")
	trainingx = data[0]
	trainingy = data[1]
	print("got data")

	data = getData(20000, "historical_data1_Q22009.txt", "historical_data1_time_Q22009.txt")
	testingx=  data[0]
	testingy=  data[1]
	print("got data")

	data = getData(20000, "historical_data1_Q32008.txt", "historical_data1_time_Q32008.txt")
	trainingx +=  data[0]
	trainingy += data[1]
	print("got data")

	data = getData(20000, "historical_data1_Q42008.txt", "historical_data1_time_Q42008.txt")
	testingx +=  data[0]
	testingy +=  data[1]
	print("got data")

	trees = [[],[]]
	for i in range(numTrees):
		if ((i + 1) % numTrees/2 == 0):
			print("halfway")
		A = [0,1,2,3,4,5,6,7,8,9,10,11,12]
		random.shuffle(A)
		for i in range(0, 8):
			A.pop()
		A.sort()
		trees[0].append(dTree(A, 0, trainingx,trainingy))
		trees[1].append(A)

	print("pruning")
	#prune forest
	goodtrees = [[],[]]
	prune = []
	for i in range(0, numTrees):
		prune.append(test(trees[0][i], trees[1][i], testingx, testingy))
		if(prune[i] > 0):
			goodtrees[0].append(trees[0][i])
			goodtrees[1].append(trees[1][i])

	print(prune)
	
	print("testing forest")
	testForest(goodtrees[0], goodtrees[1], trainingx, trainingy)

	return trees


# WARNING: WILL DELETE OLD LOANS DB IF TRUE
DEBUG = True  # If in debug mode, will only insert 1 record from each quarter from each year

randomForest(30,0)
#print(n.dataType)