
# root_dir = '/Users/ethanlo1/Documents/15th/3rd Term/CS123/DOCUDB/src'
# '/Users/ethanlo1/Documents/15th/3rd Term/CS123/DOCUDB/src'
root_dir ='/Users/Spencer/CS123/DOCUDB/src'

import sys
sys.path.insert(0, root_dir)

from storage_layer import StorageLayer
from document import DocumentData


filename = 'test_table.haha'

with open(filename, 'wb') as f:
	f.close()


sl = StorageLayer(filename)

# should be 0 since file starts empty
print sl.search_memory_for_free(100)


to_insert = DocumentData(1000, 0, 'Joe')
to_insert.add_value('age', 3, 2, 1 , '1')
to_insert.add_value('pay', 3, 0, 4 , 100)

to_insert2 = DocumentData(1000, 0, 'goodbye')
to_insert2.add_value('col1', 4, 2, 7 , 'asdfasf')
to_insert2.add_value('col', 3, 0, 4 , 10)

 #110000goodbye3col04904col127asdfasf8hiithere03100


sl.write_data_to_memory(sl.search_memory_for_free(1000), to_insert)

sl.write_data_to_memory(sl.search_memory_for_free(1000), to_insert2)


# print 'File we just inserted to'

# with open(filename, "rb") as f:
#     byte = f.read(1)
#     while byte != b"":
#         print byte
#         byte = f.read(1)

print 'TESTING GET'
gettt = sl.get_tuples_by_key(['goodbye'])

print 'HHHHHHHHHHHNNGGGG'
dicc =  gettt[0].values
print dicc
for key in dicc:
	print dicc[key]




#This is testing upsert
sl.update_by_keys(['goodbye'], ['col', 'hiithereyou home boy dog man LOLOLOLOL12'], [90, '100'], 1)
# #  #110000goodbye3col04904col127asdfasf8hiithere03100



# with open(filename, 'rb') as f:
# 	fff = f.read()

# 	print fff


print 'TESTING GET after update'
gettt = sl.get_tuples_by_key(['goodbye'])

print 'HHHHHHHHHHHNNGGGG'
dicc =  gettt[0].values
print dicc
for key in dicc:
	print dicc[key]


sl.delete_by_keys(['goodbye'])

# print 'TESTING GET after delere'
# # gettt = sl.get_tuples_by_key(['goodbye'])

# # print 'HHHHHHHHHHHNNGGGG'
# # dicc =  gettt[0].values
# # print dicc
# # for key in dicc:
# # 	print dicc[key]



with open(filename, 'rb') as f:
	fff = f.read()

	print fff

print "asdfassadfsadfsaddd"
print "fasdfsfuckasdf"
sl.write_data_to_memory(sl.search_memory_for_free(1000), to_insert)

with open(filename, 'rb') as f:
	fff = f.read()

	print fff


