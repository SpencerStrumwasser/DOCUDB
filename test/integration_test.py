from query_generator import generate_inserts

import sys
import os
sys.path.insert(0, '../src/')

import myparser


p = myparser.Parser()



def dic_list_cmp(lst1, lst2):
	'''
	Takes in 2 lists representing the return of a select query. Returns true if match.
	lst1 is the expected list
	lst2 is the actual list

	*** ORDER MATTERS: because of the way floats are stored in disk
	'''

	if len(lst2) != len(lst1):
		return False

	for i in range(len(lst1)):
		dict1 = lst1[i] # expected
		dict2 = lst2[i] # actual

		if len(dic1) != len(dict2):
			return False

		for col in dict1:
			if col not in dict2:
				return False
			elif 1:
				pass


	

def insert_test(collection_name, num_docs):
	inserts = (generate_inserts(collection_name, num_docs, min_cols=5, max_cols=10, max_int=100000, max_dec=.000001, max_str=3333))
	insert_str = inserts[0]
	insert_dict = inserts [1]

	# TODO DELETE
	# print insert_str
	# print insert_dict


	sys.stdout = open(os.devnull, "w")


	del_qurey = 'drop ' + collection_name
	p.parse(del_qurey)

	creation_qurey = 'create ' + collection_name
	p.parse(creation_qurey)

	sys.stdout = sys.__stdout__

	ccc = 0

	for line in insert_str.splitlines():
		# print line
		# print ''
		# print 'query to run:'
		# print line
		# print '----'
		sys.stdout = open(os.devnull, "w")
		p.parse(line)
		sys.stdout = sys.__stdout__

		if ccc % 30 == 0:

			print 'parse ' + str(ccc) + '/' + str(num_docs)

		ccc += 1

		
	sys.stdout = open(os.devnull, "w")
	res_sel = p.parse('select * from test_collection')
	sys.stdout = sys.__stdout__

	
	count = 0
	for i in range(0, len(insert_dict)):
		if cmp(insert_dict[i], res_sel[i]) == 0:

			# print '---------------------------\nExpected\n---------------------------'
			# print insert_dict
			# print '---------------------------\n********\n---------------------------'

			# print '---------------------------\nActual\n---------------------------'
			# print res_sel
			# print '---------------------------\n********\n---------------------------'

			print "Success " + str(i)
		else:
			print '---------------------------\nExpected\n---------------------------'
			print insert_dict
			print '---------------------------\n********\n---------------------------'

			print '---------------------------\nActual\n---------------------------'
			print res_sel
			print '---------------------------\n********\n---------------------------'
			print 'mismatch'
			count += 1
	return count

num_docs = 1000
tests_failed = insert_test('test_collection', num_docs)

print str(tests_failed) + " Total Docs mismatched out of " + str(num_docs)








