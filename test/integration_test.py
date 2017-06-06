from query_generator import generate_inserts

import sys
sys.path.insert(0, '../src/')

import myparser


p = myparser.Parser()





def insert_test(collection_name, num_docs):
	inserts = (generate_inserts(collection_name, num_docs, min_cols=1, max_cols=1, max_int=(10), max_dec=(2**31), max_str=10))
	insert_str = inserts[0]
	insert_dict = inserts [1]



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
	print '---------------------------\nExpected\n---------------------------'
	print insert_dict
	print '---------------------------\n********\n---------------------------'

	print '---------------------------\nActual\n---------------------------'
	print res_sel
	print '---------------------------\n********\n---------------------------'

	if cmp(insert_dict, res_sel) == 0:
		pass
	else:
		print 'mismatch'

insert_test('test_collection', 1)


