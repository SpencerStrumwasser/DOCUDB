import os
import document


class StorageLayer:
    '''
    Code for manipulating the data at a low level.

    Document Storage Format
        Rows (aka documents) are stored in the following format:
        | metadata | row data | extra padding |

        The meta data is structured as follows:
        | 1B - filled flag | 4B - space allocated for row | 4B - space filled in row | 30B key_name|

        The row data is structured as follows (this is one row):
        | 1B - col name length | 1~255B - col name | 1B - value type | 4B - value size| ?B - value|
        Since we use 1B to store column name length, columns are restricted to 255 max characters.
        Value type is 1B, so we can accomodate 256 possible values

        The extra padding is just extra padding in case we want to change the document size.

        * Python's default encoding is ASCII

        Document should be small enough to fit in memory. Max doc size is 16MB (in order
        to not use excssive amounts of RAM). 

        Docs start with a minimum allocation of 1KB.

    Collection Storage Method
        Tables/collections are currently organized in a heap file format. 

        There are no pages; rows are just inserted one after the other into the file. 
        We depend on the filesystem to adjust the size of the file. 

        There is a "read size," which is the number of bytes we read at a time from the file.

    Data Access Method
        We read from the file in chunks of size READ_SIZE. 

        TODO: talk aobut coalescing and shit later.

    Data Types
        There are 4 types of data this database accepts:
            Int: corresponding to a 

    Functionality
        - Add documents to collections
        - Delete based on comparisons of the form:
            (key value or value) (operator) (constant)
            (key value or value) (operator) (or value)  --> with respect to the same document
        - Update based of same comparisons as supported delete
            - update a column's value
            - add a new column if it doesn't exist
        - Select based of same comparisons supported in delete.
            - all
            - only certain columns 

    '''

    INT_SIZE = 4    
    DEC_SIZE = 8
    CHAR_SIZE = 1
    BOOLEAN_SIZE = 1
    Val_type_map = {0 : 'int' , 1 : 'dec', 2 : 'char', 3 : 'bool'}
    ROOT_DATA_DIRECTORY = '/Users/Spencer/CS123/DOCUDB/table_data' # Where the tables at

    def __init__(self, filename, read_size=4069):
        '''
        Filename is identical to collection name
        '''
        self.read_size = read_size
        self.filename = filename


    def search_memory_for_free(self, size):
        with open(self.filename, 'rb') as f:
            start = 0
            end = start + self.read_size
            #check if file has anything written
            not_eof = (os.stat(self.filename).st_size != 0) 
            while(not_eof):
                f.seek(start)
                #load a subset of data
                data = f.read(end - start)
                size_of_data = len(data)
                #check if last loop
                if (size_of_data < self.read_size):
                    not_eof = False
                # go through "block" of data    
                while(start <= size_of_data):

                    dirty = int(data[start])
                    allocated = int(data[start + self.BOOLEAN_SIZE: start + self.BOOLEAN_SIZE + self.INT_SIZE].rstrip('\0'))
                    if (dirty == 0) and (allocated >= size):
                        return start
                    else:
                        start += allocated
                end = start + self.read_size
            return start



    def write_data_to_memory(self, start, document):
        with open(self.filename, 'r+b') as f:
            f.seek(start)
            # show it has not been "deleted"
            f.write(bytearray(document.allocated_size - 1))
            f.seek(start)
            f.write('1')
            start += self.BOOLEAN_SIZE
            f.seek(start)
            # write how much is allocated
            f.write(bytes(document.allocated_size))
            start += self.INT_SIZE
            f.seek(start)
            # write how much is being used
            f.write(bytes(document.filled_size))
            start += self.INT_SIZE

            # document key is part of meta data
            f.seek(start)
            f.write(document.key_name)
            start += 30

            values = document.values
            for key in values:
                # write column name lenght
                f.seek(start)
                f.write(bytes(values[key].col_name_len))
                start += 1
                # write column name
                f.seek(start)
                f.write(key)
                start += values[key].col_name_len
                # write value type
                f.seek(start)
                f.write(bytes(values[key].val_type))
                start += 1
                # write value size
                f.seek(start)
                f.write(bytes(values[key].val_size))
                start += self.INT_SIZE
                # write value
                f.seek(start)
                f.write(bytes(values[key].val))
                start += values[key].val_size
        # return true to make sure it works
        return True 



    def delete_by_keys(self, keys):
        with open(self.filename, 'r+b') as f:
            start = 0
            end = start + self.read_size
            #check if file has anything written
            not_eof = True
            if (os.stat(self.filename).st_size == 0):
                return False
            while not_eof:
                f.seek(start)
                data = f.read(end - start)
                size_of_data = len(data)
                if (size_of_data < self.read_size):
                    not_eof = False
                while start <= size_of_data:
                    dirty = int(data[start])
                    allocated = int(data[start + self.BOOLEAN_SIZE: start + self.BOOLEAN_SIZE + self.INT_SIZE].rstrip('\0'))
                    if dirty == 1:
                        datakey = data[start + self.BOOLEAN_SIZE + 2 * self.INT_SIZE:start + self.BOOLEAN_SIZE + 2 * self.INT_SIZE + 30].rstrip('\0')
                        if datakey in keys:
                            keys.remove(datakey)
                            f.seek(start)
                            f.write('0')
                    if len(keys) == 0:
                        return True
                    start +=allocated
            return False



    def update_by_keys(self, keys, columns, news):
        with open(self.filename, 'r+b') as f:
            start = 0
            end = start + self.read_size
            #check if file has anything written
            not_eof = True
            if (os.stat(self.filename).st_size == 0):
                return False
            while not_eof:
                f.seek(start)
                data = f.read(end - start)
                size_of_data = len(data)
                if (size_of_data < self.read_size):
                    not_eof = False
                while start <= size_of_data:
                    dirty = int(data[start])
                    allocated = int(data[start + self.BOOLEAN_SIZE: start + self.BOOLEAN_SIZE + self.INT_SIZE].rstrip('\0'))
                    if dirty == 1:
                        datakey = data[start + self.BOOLEAN_SIZE + 2 * self.INT_SIZE:start + self.BOOLEAN_SIZE + 2 * self.INT_SIZE + 30].rstrip('\0')
                        if datakey in keys:
                            traversal = start + self.BOOLEAN_SIZE + 2 * self.INT_SIZE + 30
                            keys.remove(datakey)
                            f.seek(traversal)
                            copy_columns = columns
                            copy_news = news
                            while len(copy_columns) != 0:
                                col_len = f.read(1)
                                traversal += 1
                                print 'safd' + col_len
                                if col_len == '\0' :
                                    break
                                col_name = f.read(int(col_len))
                                traversal += int(col_len)
                                f.seek(traversal + 1)
                                val_size = int(f.read(self.INT_SIZE).rstrip('\0'))
                                traversal += 1 + self.INT_SIZE
                                for i in range(0, len(copy_columns)):
                                    if col_name == copy_columns[i]:
                                        f.write(bytearray(val_size))
                                        f.seek(traversal)
                                        f.write(bytes(copy_news[i]))
                                        copy_columns.remove(col_name)
                                        del copy_news[i]

                                        break
                                traversal += val_size
                                f.seek(traversal)
                                        
                            if len(copy_columns) != 0:
                                print 'seeerrrrr'
                                f.seek(traversal)
                                for i in range(0, len(copy_columns)):
                                    temp_len = len(copy_columns[i])
                                    f.write(bytes(temp_len))
                                    f.write(copy_columns[i])
                                    f.write('0')
                                    f.write(bytes(len(copy_news[i])))
                                    traversal += 1 + temp_len + 1 + 4
                                    f.seek(traversal)
                                    f.write(bytes(copy_news[i]))
                    if len(keys) == 0:
                        return True
                    start +=allocated
            return False






            