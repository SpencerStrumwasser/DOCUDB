from query_generator import generate_inserts

import sys
import os
sys.path.insert(0, '../src/')

import myparser
import string

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


# For pluggin into expression only
def convert_val_to_query_val(v):


	if type(v) == type(1):
		return {'val' : v, 'query_val' : str(v)}

	elif type(v) == type(2.2):

		return {'val' : v, 'query_val' : str(v)}

	elif type(v) == type(True):

		return {'val' : v, 'query_val' : str(v)}

	elif type(v) == type('dddddd'):

		return {'val' : v, 'query_val' : ('"' + str(v) + '"')}

	else: # might be a dict or list
		return None

# Not for expression expressions
def create_rand_val():

	val_type = random.choice([0,1,2,3])


	if val_type == 0:
		ret =  random.choice(range(-1000000,1000000))
		return {'val' : ret, 'query_val' : str(ret)}

	elif val_type == 1:
		rc_big = ((random.random() - .5) * 1000000.)
		rc_small = random.random()
		ret =  random.choice([rc_big, rc_small])

		return {'val' : ret, 'query_val' : str(ret)}

	elif val_type == 2:
		ret =  random.choice([True, False])

		return {'val' : ret, 'query_val' : str(ret).lower()}

	elif val_type == 3:
		max_str = random.choice([1,10])
		ret =  ''.join(random.choice(string.digits+string.letters+'-_') for i in range(max_str))

		return {'val' : ret, 'query_val' : ('"' + str(ret) + '"')}


def update_test(collection_name, num_docs):
	'''
	Tests updates by generating a randomly filled DB table and running queries 
	against it. 
	'''

	mismatch_ct = 0

	inserts = (generate_inserts(collection_name, num_docs, min_cols=5, max_cols=10, max_int=100000, max_dec=.000001, max_str=3))
	insert_str = inserts[0]
	insert_dict = inserts [1]	

	sys.stdout = open(os.devnull, "w")

	del_qurey = 'drop ' + collection_name
	p.parse(del_qurey)

	creation_qurey = 'create ' + collection_name
	p.parse(creation_qurey)
	sys.stdout = sys.__stdout__

	ccc = 0

	# Write data to test-collection
	for line in insert_str.splitlines():
		sys.stdout = open(os.devnull, "w")
		p.parse(line)
		sys.stdout = sys.__stdout__

		if ccc % 30 == 0:

			print 'parse ' + str(ccc) + '/' + str(num_docs)

		ccc += 1

	# Test Update, run 20 tests
	i = 0
	while i < 20:

		# Col in wher exp
		rand_doc = random.choice(insert_dict)
		rand_col = random.choice(rand_doc.keys())
		rand_val = rand_doc[rand_col]
		rand_val_qq = convert_val_to_query_val(rand_val)
		if rand_val_qq == None: # we got a doc or list
			continue
		rand_val_q = rand_val_qq['query_val']

		# Col being updated
		rand_col_to_set = random.choice(rand_doc.keys())
		rand_val_to_set = create_rand_val()


		# update <collection_name> set [<rand_col_to_set>] = <>

		# Apply query to insert_dict
		new_insert_dict = []
		for docc in insert_dict:
			pred_eval = None
			if rand_col in docc:
				if docc[rand_col] == rand_val_qq['val']:
					pred_eval = True
				else:
					pred_eval = False
			else:
				pred_eval = False

			# print 'checking ' + str(docc[rand_col]) + ' and ' + str(rand_val_qq['val']) + ' equality'
			# print pred_eval

			if pred_eval:
				if rand_col_to_set in docc: # For updates, do not do anything if column to update DNE
					docc[rand_col_to_set] = rand_val_to_set['val']

			new_insert_dict.append(docc)

		# Apply query to actual database
		update_query = 'update ' + collection_name + ' set ' + '[' + rand_col_to_set + '] = [' +  rand_val_to_set['query_val'] + '] where ( ' + rand_col + ' == ' + rand_val_q + ') '

		print update_query


		p.parse(update_query)
		query_res = p.parse('select * from test_collection')

		# compare results
		query_res.sort()
		new_insert_dict.sort()

		if cmp(query_res, new_insert_dict) == 0:
			print 'Success ' + str(i)
		else:
			print 'Err'



			mismatch_ct += 1


		i += 1


	return mismatch_ct

def insert_test(collection_name, num_docs):
	'''
	Tests insert by generating a randomly filled DB table and running queries 
	against it. 
	'''
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
# # TODO: right now: collection name MUST be 'test_collection' bc it's hardcoded somewhere
# print '============================'
# print 'TESTING INSERT/SELECT'
# print '============================'
# tests_failed = insert_test('test_collection', num_docs)
# print str(tests_failed) + " Total Docs mismatched out of " + str(num_docs)


print '============================'
print 'TESTING UPDATE/SELECT'
print '============================'
update_test('test_collection' , 10)





