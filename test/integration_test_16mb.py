from query_generator_16mb import generate_inserts

import sys
import os
sys.path.insert(0, '../src/')

import myparser
import random

p = myparser.Parser()



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

	val_type = random.choice([3])


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



def upsert_test(collection_name, num_docs):
	'''
	Tests updates by generating a randomly filled DB table and running queries 
	against it. 
	'''

	mismatch_ct = 0

	inserts = (generate_inserts(collection_name, num_docs, min_cols=1, max_cols=2, max_int=100000, max_dec=.000001, max_str=3))
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


	# Test Update, run 20 test queries
	i = 0
	while i < 20:

		# Col in wher exp
		rand_doc = random.choice(insert_dict)
		rand_col = random.choice(rand_doc.keys())
		for _ in range(100):
			rand_col = random.choice(rand_doc.keys())
			if rand_col != '_key': # not sure why it runs forever sometimes
				break

				
		rand_val = rand_doc[rand_col]
		rand_val_qq = convert_val_to_query_val(rand_val)
		if rand_val_qq == None: # we got a doc or list
			continue
		rand_val_q = rand_val_qq['query_val']

		# Col being updated
		rand_col_to_set = random.choice(rand_doc.keys())
		for _ in range(100):
			rand_col_to_set = random.choice(rand_doc.keys())
			if rand_col_to_set != '_key': # not sure why it runs forever sometimes
				break

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


			if pred_eval:
				# For upsert, set the column, even if it does not exist before
				docc[rand_col_to_set] = rand_val_to_set['val']


			new_insert_dict.append(docc)

		# Apply query to actual database
		update_query = 'upsert  ' + str(collection_name) + ' set ' + '[' + str(rand_col_to_set) + '] = [' +  str(rand_val_to_set['query_val']) + '] where ( ' + rand_col + ' == ' + rand_val_qq['query_val'] + ') '

		mismatch_query = 0


		sys.stdout = open(os.devnull, "w")
		p.parse(update_query)
		query_res = p.parse('select * from test_collection')
		sys.stdout = sys.__stdout__

		# compare results
		query_res.sort()
		new_insert_dict.sort()
		if len(query_res) != len(new_insert_dict):
			mismatch_query = 1
		else:
			for doc_i in range(len(query_res)):
				# print 'actual'
				# print query_res
				# print 'expect'
				# print new_insert_dict

				# print '\n'


				if cmp(query_res[doc_i], new_insert_dict[doc_i]) == 0:
					print 'Success: upsert query ' + str(i) + ', document ' + str(doc_i)
				else:
					mismatch_query = 1
					print update_query
					print 'Mismatch: '
					print 'Expected: '
					print '\t' + str(new_insert_dict[doc_i])
					print 'Actual:'
					print '\t' + str(query_res[doc_i])

			

		mismatch_ct += mismatch_query
		i += 1


	return mismatch_ct






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




def delete_test(collection_name, num_docs):
	inserts = (generate_inserts(collection_name, num_docs, min_cols=5, max_cols=10, max_int=100000, max_dec=.000001, max_str=100000))
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
	count += len(insert_dict) - len(res_sel)
	return count




total_errs = 0

num_docs = 3
tests_failed = insert_test('test_collection', num_docs)

print " Total Insertions errors: " + str(tests_failed)
total_errs += tests_failed

tests_failed = delete_test('test_collection', num_docs)

print " Total Deletions errors: " + str(tests_failed)
total_errs += tests_failed

tests_failed = update_test('test_collection' , 10)

print "Total Update errors: " + str(tests_failed)
total_errs += tests_failed


tests_failed = upsert_test('test_collection' , 10)

print "Total Upsert errors: " + str(tests_failed)
total_errs += tests_failed


if total_errs == 0:
	print 'NO ERRORS FOUND'
else:
	print str(total_errs) + ' total errors found.'


