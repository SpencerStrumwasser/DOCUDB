from query_generator import generate_inserts

import sys
sys.path.insert(0, '../src/')

import myparser


p = myparser.Parser()





def insert_test(collection_name, num_docs):
	inserts = (generate_inserts(collection_name, num_docs, min_cols=1, max_cols=10, max_int=(2**31), max_dec=(2**31), max_str=10))[0]


	creation_qurey = 'create ' + collection_name
	p.parse(creation_qurey)


	for line in inserts.splitlines():
		# print line
		# print ''
		p.parse(line)



insert_test('test_collection', 10)


