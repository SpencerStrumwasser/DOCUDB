import os


FOUR_KILOBYTE = 4096

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
		end = start + FOUR_KILOBYTE
		not_eof = (os.stat(filename).st_size != 0) 
		print not_eof
		while(not_eof):
			f.seek(start)
			data = f.read(end - start)
			size_of_data = len(data)
			print 'size data'
			print size_of_data
			if (size_of_data < FOUR_KILOBYTE):
				not_eof = False
			while(start <= size_of_data):
				print 'clean'
				print data[start]

				dirty = int(data[start])
				
				print data[start + BOOLEAN_SIZE: BOOLEAN_SIZE+ INT_SIZE]
				allocated = int(data[start + BOOLEAN_SIZE: BOOLEAN_SIZE + INT_SIZE].rstrip('\0'))
				print allocated
				if (dirty == 0) and (allocated >= size):
					return start
				else:
					start += allocated
			end = start + FOUR_KILOBYTE
		return start





a = search_memory_for_free('asdf.d', 100)
print a
with open('asdf.d', 'r+b') as f:
	f.seek(a)
	f.write('1')
	f.seek(a+1)
	f.write(bytes(100))
	f.seek(a+ BOOLEAN_SIZE+INT_SIZE)
	f.write('asfsdfsadf')
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
