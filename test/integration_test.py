from query_generator import generate_inserts

import sys
import os
sys.path.insert(0, '../src/')

import myparser
import random

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




def delete_test(collection_name, num_docs):
	inserts = (generate_inserts(collection_name, num_docs, min_cols=5, max_cols=10, max_int=100000, max_dec=.000001, max_str=10))
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

		sys.stdout = open(os.devnull, "w")
		p.parse(line)
		sys.stdout = sys.__stdout__

		if ccc % 30 == 0:

			print 'parse ' + str(ccc) + '/' + str(num_docs)

		ccc += 1

		del_vals_list = []	
	sys.stdout = open(os.devnull, "w")
	for dic in range(0,len(insert_dict)):
		
		del_type = random.randint(0,2)
		if del_type == 0:
			continue
		elif del_type == 1:
			
			str_del = ' '
			lis_key_del = []
			for key in insert_dict[dic]:
				rand_del = random.randint(0,10)
				if rand_del > 7:
					if key == '_key':
						continue
					elif len(str_del) > 2:
						str_del += ', ' + str(key)
					else:
						str_del += str(key)
					lis_key_del.append(key)
			for key in lis_key_del:
				del insert_dict[dic][key]
			if len(str_del) > 2:
				p.parse('delete' + str_del + ' from test_collection where (_key == "' + str(insert_dict[dic]['_key'])+ '")')
		elif del_type == 2:
			p.parse('delete * from test_collection where (_key == "' + str(insert_dict[dic]['_key']) + '")')
			del_vals_list.append(dic)
	sys.stdout = sys.__stdout__	
	count_del_list = 0
	for i in del_vals_list:
		del insert_dict[i - count_del_list]
		count_del_list += 1
	sys.stdout = open(os.devnull, "w")
	res_sel = p.parse('select * from test_collection')
	sys.stdout = sys.__stdout__
	count = 0
	if len(insert_dict) != 0:	
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
				print insert_dict[i]
				print '---------------------------\n********\n---------------------------'

				print '---------------------------\nActual\n---------------------------'
				print res_sel[i]
				print '---------------------------\n********\n---------------------------'
				print 'mismatch'
				count += 1
	return count











num_docs = 100
tests_failed = insert_test('test_collection', num_docs)

print str(tests_failed) + " Total Insertions mismatched out of " + str(num_docs)

tests_failed = delete_test('test_collection', num_docs)

print str(tests_failed) + " Total Deletions mismatched out of " + str(num_docs)







