from query_generator import generate_inserts

import sys
import os
sys.path.insert(0, '../src/')

import myparser


p = myparser.Parser()


def insert_test2(collection_name, num_docs):
	# inserts = (generate_inserts(collection_name, num_docs, min_cols=1, max_cols=1, max_int=(2*31), max_dec=(2**31), max_str=10))
	# insert_str = inserts[0]
	# insert_dict = inserts [1]


	# sys.stdout = open(os.devnull, "w")
	# del_qurey = 'drop ' + collection_name
	# p.parse(del_qurey)

	# creation_qurey = 'create ' + collection_name
	# p.parse(creation_qurey)


	# for line in insert_str.splitlines():
	# 	# print line
	# 	# print ''
	# 	print 'query to run:'
	# 	print line
	# 	print '----'
	# 	p.parse(line)

		
	
	# res_sel = p.parse('select * from test_collection')


	# sys.stdout = sys.__stdout__
	# count = 0
	# for i in range(0, len(insert_dict)):
	# 	if cmp(insert_dict[i], res_sel[i]) == 0:
	# 		print "Success"
	# 	else:
	# 		print '---------------------------\nExpected\n---------------------------'
	# 		print insert_dict
	# 		print '---------------------------\n********\n---------------------------'

	# 		print '---------------------------\nActual\n---------------------------'
	# 		print res_sel
	# 		print '---------------------------\n********\n---------------------------'
	# 		print 'mismatch'
	# 		count += 1
	return count


def insert_test(collection_name, num_docs):
	inserts = (generate_inserts(collection_name, num_docs, min_cols=100, max_cols=100, max_int=10, max_dec=(2**31), max_str=100000))
	insert_str = inserts[0]
	insert_dict = inserts [1]


	sys.stdout = open(os.devnull, "w")
	del_qurey = 'drop ' + collection_name
	p.parse(del_qurey)

	creation_qurey = 'create ' + collection_name
	p.parse(creation_qurey)


	for line in insert_str.splitlines():
		# print line
		# print ''
		print 'query to run:'
		print line
		print '----'
		p.parse(line)

		
	
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
			print "Success"
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


num_docs = 10
tests_failed = insert_test('test_collection', num_docs)

print str(tests_failed) + " Total Docs mismatched out of " + str(num_docs)








