
import random
import string

'''
Various functions for generating DocuDB queries


Current datatypes:
- int
- dec
- string
- bool

Not yet supported datatypes:
- nested document
- list

'''

NUM_DATATYPES = 5 # currently 7 different datatypes 


def generate_inserts(collection_name, num_docs, min_cols=1, max_cols=10, max_int=(2**15-1), max_dec=(1), max_str=999999, only_str=False):
	'''
	Generates a string of insert statements, filled with random data

	input: collection_name -> collection to insert into
	input: num_docs -> number of insert statements to make
	input: min_cols -> min number of cols for inserted rows
	input: max_cols -> max num of cols for inserted rows
	input: max_int -> max integer value any row will have (absolute value)
	input: max_dec -> max decimal value any row will have
	input: max_str -> max string length any row will have

	return: (string with queries, list of dictionaries corresponding to inserted docs)
	'''
	# print max_int


	assert type(collection_name) == str
	assert type(num_docs) == int
	assert type(min_cols) == int
	assert type(max_cols) == int
	assert type(max_int) == int or float
	assert type(max_dec) == int or float
	assert type(max_str) == int
	assert min_cols >= 1

	# insert into <collection> <key_name>  {col_name1 : val1, col_name2: val2, ...}  

	str_ins_queries = '' # String of insert queries
	lst_ins_queries = [] # List of documents being inserted 

	# Each document
	for doc_num in range(num_docs):
		if doc_num % 100 == 0:
			print 'doc ' + str(doc_num) + '/' + str(num_docs) + ' created..'


		cur_ins_query = 'insert into ' + collection_name + ' "key' + str(doc_num) + '" {'
		cur_ins_dict = {'_key' : ('key' + str(doc_num))}

		# Each column
		num_cols = random.randrange(min_cols, max_cols+1)
		for col_num in range(num_cols):

			val_type = random.randrange(0, NUM_DATATYPES+1)



			val = ''
			
			def __base_type(val_type, cur_ins_dict, col_num):
				# int 
				if val_type == 0:
				# if False:
					ival = random.randrange(-max_int + 1, max_int)
					val = str(ival)
					cur_ins_dict[('column' + str(col_num))] = ival
					return val
				# dec
				elif val_type == 1:
				# if True:
					dval = random.uniform(-max_dec, max_dec)
					val = str(dval)
					cur_ins_dict[('column' + str(col_num))] = float(str(dval))
					return val
				# string
				elif val_type == 2:
				# if False:
					# sval = ''.join(random.choice(string.printable) for i in range(max_str)) # produces ugly strings
					sval = ''.join(random.choice(string.digits+string.letters+'-_') for i in range(max_str))
					val = '"' + sval + '"'
					cur_ins_dict[('column' + str(col_num))] = sval
					return val
				# bool
				elif val_type == 3:
				# TODO: problems with booleans 
				# if False:
					bval = random.choice([True, False])
					val = str(bval).lower()
					cur_ins_dict[('column' + str(col_num))] = bval
					return val

			if val_type in [0,1,2,3]:
				val = __base_type(val_type, cur_ins_dict, col_num)
			
			# embedded Doc
			elif val_type == 4:

				val = '{'
				val += '_key' +  ' : ' + '"keyyyy"' + ', '

				sub_cur_ins_dict = {}
				sub_cur_ins_dict['_key'] = 'keyyyy'
				sub_val = ''


				num_subcols = random.randrange(min_cols, max_cols+1)
				for sub_col_num in range(num_subcols):
					sub_val_type = random.randrange(0, 4)
					sub_val = __base_type(sub_val_type, sub_cur_ins_dict, sub_col_num)

					val += 'column' + str(sub_col_num) + ' : ' + sub_val + ', '

				val = val[:-2]
				val += '}'

				cur_ins_dict[('column' + str(col_num))] = sub_cur_ins_dict
				

			# reference Doc
			elif val_type == 5:
				collec = ''.join(random.choice(string.digits+string.letters+'-_') for i in range(20))
				keyname = ''.join(random.choice(string.digits+string.letters+'-_') for i in range(20))
				val = '<' + collec + ',' + keyname + '>'
				cur_ins_dict[('column' + str(col_num))] = (collec, keyname)

			# list
			elif val_type == 6:
				val = '['

				emb_lst = {}

				lst_val = '' # string repr of elements of list

				num_lst_elems = random.randrange(min_cols, max_cols+1)
				for i in range(num_lst_elems):
					sub_val_type = random.randrange(0, 4)
					sub_val = __base_type(sub_val_type, emb_lst, i)

					val += sub_val + ', '

				emb_lst = emb_lst.values()
				emb_lst.sort()

				val = val[:-2]
				val += ']'


				cur_ins_dict[('column' + str(col_num))] = emb_lst[:]


			cur_ins_query += 'column' + str(col_num) + ' : ' + val + ', '





		cur_ins_query = cur_ins_query[:-2]
		cur_ins_query += '}'
		str_ins_queries += cur_ins_query + '\n'

		lst_ins_queries.append(cur_ins_dict)


	# print lst_ins_queries
	return (str_ins_queries, lst_ins_queries)






if __name__ == '__main__':
	r = generate_inserts('test_collection', 2, min_cols=1, max_cols=10, max_int=(2**31), max_dec=(2**31), max_str=10)
	# print r[0]


