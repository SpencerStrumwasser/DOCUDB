# set block size

import os


READ_SIZE = 4096

INT_SIZE = 8
DOUBLE_SIZE = 16
CHAR_SIZE = 1
BOOLEAN_SIZE = 1





# with open('asdf.d', 'wb') as f:
# 	f.seek(4)
# 	f.write(bytes(2314.123))
# 	f.seek(30)
# 	f.write('fuck this shit')
# 	f.close()



def search_memory_for_free(filename, size):
	with open(filename, 'rb') as f:
		start = 0
		end = start + READ_SIZE
		#check if file has anything written
		not_eof = (os.stat(filename).st_size != 0) 
		while(not_eof):
			f.seek(start)
			#load a subset of data
			data = f.read(end - start)
			size_of_data = len(data)
			#check if last loop
			if (size_of_data < READ_SIZE):
				not_eof = False
			# go through "block" of data	
			while(start <= size_of_data):

				dirty = int(data[start])
				allocated = int(data[start + BOOLEAN_SIZE: start + BOOLEAN_SIZE + INT_SIZE].rstrip('\0'))
				if (dirty == 0) and (allocated >= size):
					return start
				else:
					start += allocated
			end = start + READ_SIZE
		return start



def write_data_to_memory(filename, start, document):
	with open(filename, 'r+b') as f:
		f.seek(start)
		# show it has not been "deleted"
		f.write('1')
		start += BOOLEAN_SIZE
		f.seek(start)
		# write how much is allocated
		f.write(document.allocated_size)
		start += INT_SIZE
		f.seek(start)
		# write how much is being used
		f.write(document.filled_size)
		start += INT_SIZE

		values = document.values
		for key in values:
			# write column name lenght
			f.seek(start)
			f.write(values[key].col_name_len)
			start += 1
			# write column name
			f.seek(start)
			f.write(key)
			start += values[key.col_name_len]
			# write value type
			f.seek(start)
			f.write(values[key].val_type)
			start += 1
			# write value size
			f.seek(start)
			f.write(values[key].val_size)
			start += INT_SIZE
			# write value
			f.seek(start)
			f.write(values[key].val)
			start += values[key].val_type
	# return true to make sure it works
	return True	



# a = search_memory_for_free('asdf.d', 100)
# print a
# with open('asdf.d', 'r+b') as f:
# 	f.seek(a)
# 	f.write('1')
# 	f.seek(a+1)
# 	f.write(bytes(100000))
# 	f.seek(a+ BOOLEAN_SIZE+INT_SIZE)
# 	f.write('asfsdfsadf')
# 	f.close()
# a = search_memory_for_free('asdf.d', 30)
# print a
# with open('asdf.d', 'wb') as f:
# 	f.seek(a)
# 	f.write('1')
# 	f.seek(a+1)
# 	f.write(bytes(30))
# 	f.close()



# with open('asdf.d', 'wb') as f:
# 	f.seek(4)
# 	f.write(bytes(2314.123))
# 	f.seek(30)
# 	f.write('fuck this shit')
# 	f.close()

# with open('asdf.d', 'rb') as f:
# 	f.seek(4)
# 	a = f.read(16)
# 	print a
# 	f.close()

# print 1123.132
