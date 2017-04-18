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


print int('40    ')

def search_memory_for_free(filename, size):
	with open(filename, 'rb') as f:
		start = 0
		end = start + FOUR_KILOBYTE
		not_eof = (os.stat(filename).st_size != 0) 
		print not_eof
		while(not_eof):
			f.seek(start)
			data = f.read(end - start)
			print data
			if (data < FOUR_KILOBYTE):
				not_eof = False
			while(start <= end):
				clean = bool(data[BOOLEAN_SIZE])
				allocated = int(data[BOOLEAN_SIZE: BOOLEAN_SIZE+ INT_SIZE])
				if clean and allocated >= size:
					return start
				else:
					start += allocated
			end = start + FOUR_KILOBYTE
		return start





a = search_memory_for_free('asdf.d', 30)
with open('asdf.d', 'wb') as f:
	f.seek(a)
	f.write('1')
	f.seek(a+1)
	f.write(bytes(30))
	f.seek(a+INT_SIZE)
	f.write('asfsdfsadf')
	f.close()
a = search_memory_for_free('asdf.d', 30)
with open('asdf.d', 'wb') as f:
	f.seek(a)
	f.write('1')
	f.seek(a+1)
	f.write(bytes(30))
	f.close()



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
