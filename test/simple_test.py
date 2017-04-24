
root_dir = '/Users/ethanlo1/Documents/15th/3rd Term/CS123/DOCUDB/src'

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


to_insert = DocumentData(100, 0)
to_insert.add_value('col1', 4, 'watev', 4 , 5)



sl.write_data_to_memory(sl.search_memory_for_free(100), to_insert)

sl.write_data_to_memory(sl.search_memory_for_free(100), to_insert)


with open(filename, 'rb') as f:
	fff = f.read()

	print fff