import os
import document


class StorageLayer:
    '''
    Code for manipulating the data at a low level.

    Document Storage Format
        Rows (aka documents) are stored in the following format:
        | metadata | row data | extra padding |

        The meta data is structured as follows:
        | 1B - filled flag | 4B - space allocated for row | 4B - space filled in row | 

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

    INT_SIZE = 8    
    DEC_SIZE = 16
    CHAR_SIZE = 1
    BOOLEAN_SIZE = 1

    ROOT_DATA_DIRECTORY = '/Users/ethanlo1/Documents/15th/3rd Term/CS123/DOCUDB/table_data' # Where the tables at

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
                f.write(values[key].val_type)
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










            