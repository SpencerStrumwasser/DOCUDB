
root_dir = '/Users/Spencer/CS123/DOCUDB/src'

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


to_insert = DocumentData(1000, 0, 'hello')
to_insert.add_value('col122', 6, 2, 455 , 'asdfasf')
to_insert.add_value('col23', 5, 0, 4 , 10)

to_insert2 = DocumentData(1000, 0, 'goodbye')
to_insert2.add_value('col1', 4, 2, 7 , 'asdfasf')
to_insert2.add_value('col', 3, 0, 4 , 10)



sl.write_data_to_memory(sl.search_memory_for_free(1000), to_insert)

sl.write_data_to_memory(sl.search_memory_for_free(1000), to_insert2)


with open(filename, 'rb') as f:
	fff = f.read()

	print fff


sl.delete_by_keys(['goodbye'])

with open(filename, 'rb') as f:
	fff = f.read()

	print fff

sl.write_data_to_memory(sl.search_memory_for_free(1000), to_insert)

with open(filename, 'rb') as f:
	fff = f.read()

	print fff

