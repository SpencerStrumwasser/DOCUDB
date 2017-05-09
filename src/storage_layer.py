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
            DB: python representation
            int -> int
            dec -> float
            bool -> bool
            string -> str


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

    # Size in bytes
    INT_SIZE = 4    
    DEC_SIZE = 8
    CHAR_SIZE = 1
    BOOLEAN_SIZE = 1
    VAL_TYPE_MAP = {0 : 'int' , 1 : 'dec', 2 : 'char', 3 : 'bool'}
    ROOT_DATA_DIRECTORY = '/Users/Spencer/CS123/DOCUDB/table_data' # Where the tables at

    def __init__(self, filename, read_size=4069):
        '''
        Filename is identical to collection name
        '''
        self.read_size = read_size
        self.filename = filename


    def byte_to_int(self, byte):
        
        ret = ''
        for k in range(0,4):
           ret += bin(ord(byte[k]))[2:]
        ret = int(ret,2)
        return ret



    def search_memory_for_free(self, size):
        '''
        TODO: method summary

        input: size ->
        return ->
        '''
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
                if size_of_data == 0:
                    return start
                if (size_of_data < self.read_size):
                    not_eof = False
                # go through "block" of data  
                init_start = start  
                data_start = 0
                while start <= init_start + size_of_data:

                    dirty = int(data[data_start])
                    allocated_temp = data[data_start + self.BOOLEAN_SIZE: data_start + self.BOOLEAN_SIZE + self.INT_SIZE]
                    allocated = self.byte_to_int(allocated_temp)
                    if (dirty == 0) and (allocated >= size):
                        return start
                    else:
                        data_start += allocated
                        start += allocated
                end = start + self.read_size

            return start


    def convert_int(self,number):
        a = bin(number)[2:]
        b = len(a)
        first = 0
        second = 0
        third = 0
        fourth = 0

        if(b <= 8):
            first = int(a[0:b],2)
            return first,second,third,fourth
        else:
            first = int(a[b-8:b],2)
            
        b = b-8
        if(b <= 8):
            second = int(a[0:b],2)
            return first,second,third,fourth
        else:
            second = int(a[b-8:b],2)
        b = b-8
        if(b <= 8):
            third = int(a[0:b],2)
            return first,second,third,fourth
        else:
            third = int(a[b-8:b],2)
        b = b-8
        if(b <= 8):
            fourth = int(a[0:b],2)

        else:
            fourth = int(a[b-8:b],2)    
        return first,second,third,fourth



    def convert_single_byte(self,number):
        a = bin(number)[2:]
        b = len(a)
        first = 0
        if(b < 8):
            first = int(a[0:b],2)
        return first


    def write_data_to_memory(self, start, document):
        '''
        todo: method summary

        input: start ->
        input document ->
        return ->
        '''

        # todo: record filled_space
        init_start = start
        with open(self.filename, 'r+b') as f:
            f.seek(start)
            # show it has not been "deleted"
            f.write(bytearray(document.allocated_size - 1))
            f.seek(start)
            f.write('1')
            start += self.BOOLEAN_SIZE
            f.seek(start)
            # write how much is allocated

            a,b,c,d = self.convert_int(document.allocated_size)

            f.write(str(chr(d)))
            f.write(str(chr(c)))
            f.write(str(chr(b)))
            f.write(str(chr(a)))
            start += self.INT_SIZE
            filled_loc = start
            start += self.INT_SIZE

            # document key is part of meta data
            f.seek(start)
            f.write(document.key_name)
            start += 30

            values = document.values
            for key in values:
                # write column name lenght
                f.seek(start)
                a = self.convert_single_byte(values[key].col_name_len)
                f.write(str(chr(a)))
                start += 1
                # write column name
                f.seek(start)
                f.write(key)
                start += values[key].col_name_len
                # write value type
                f.seek(start)
                a = self.convert_single_byte(values[key].val_type)
                f.write(str(chr(a)))
                start += 1
                # write value size
                f.seek(start)
                a,b,c,d = self.convert_int(values[key].val_size)

                f.write(str(chr(d)))
                f.write(str(chr(c)))
                f.write(str(chr(b)))
                f.write(str(chr(a)))
                start += self.INT_SIZE
                # write value
                f.seek(start)
                if values[key].val_type == 0:
                    a,b,c,d = self.convert_int(values[key].val)

                    f.write(str(chr(d)))
                    f.write(str(chr(c)))
                    f.write(str(chr(b)))
                    f.write(str(chr(a)))
                    start += values[key].val_size
                        
                else:
                    f.write(bytes(values[key].val))
                    start += values[key].val_size
        
            f.seek(filled_loc)
            # write how much is being used

            a,b,c,d = self.convert_int(start - init_start)

            f.write(str(chr(d)))
            f.write(str(chr(c)))
            f.write(str(chr(b)))
            f.write(str(chr(a)))
        # return true to make sure it works
        return True 



    def delete_by_keys(self, keys):
        '''
        todo: write methdo summary

        input: keys ->
        return ->

        '''
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
                init_start = start  
                data_start = 0
                while start <= init_start + size_of_data:
                    dirty = int(data[data_start])
                    allocated_temp = data[data_start + self.BOOLEAN_SIZE: data_start + self.BOOLEAN_SIZE + self.INT_SIZE]
                    allocated = self.byte_to_int(allocated_temp)
                    if dirty == 1:
                        datakey = data[data_start + self.BOOLEAN_SIZE + 2 * self.INT_SIZE:data_start + self.BOOLEAN_SIZE + 2 * self.INT_SIZE + 30].rstrip('\0')
                        if datakey in keys:
                            keys.remove(datakey)
                            f.seek(start)
                            f.write('0')
                    if len(keys) == 0:
                        return True
                    data_start += allocated
                    start +=allocated
            return False


    def get_tuples_by_key(self, keys, project=[]):
        '''
        Gets the documents corresponding to the desired keys. With optional projection
        
        input: keys -> List of keys to grab documents for 
        input: project -> List of columns to project. Empty list means select all
        return -> todo: what is the return? haha

        '''
        ret = [] # document.DocumentPresentation(key)

        with open(self.filename, 'rb') as f:
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
                if size_of_data == 0:
                    return False
                init_start = start
                data_start = 0  
                while start <= init_start + size_of_data:


                    if data[data_start] == '\0':
                        dirty = 0
                    else:   
                        dirty = int(data[data_start])

                    allocated_temp = data[data_start + self.BOOLEAN_SIZE: data_start + self.BOOLEAN_SIZE + self.INT_SIZE]
                    allocated = self.byte_to_int(allocated_temp)
                    if dirty == 1:
                        # print keys
                        datakey = data[data_start + self.BOOLEAN_SIZE + 2 * self.INT_SIZE:data_start + self.BOOLEAN_SIZE + 2 * self.INT_SIZE + 30].rstrip('\0')
                        # print datakey   
                        if str(datakey) in keys:
                            keys.remove(datakey)
                            
                            document_binary = data[data_start:data_start+allocated]
                            doc_data = self.binary_to_doc_data(document_binary)
                            ret.append(doc_data)

                    if len(keys) == 0:
                        return ret
                    data_start += allocated
                    start += allocated

            if ret == []:
                return False
            return ret


    def binary_to_doc_data(self, binary):
        # TODO: update when we store datatypes 
        # as NOT alll strings

        # print '--------'
        # print binary
        # print '--------'

        # TODO: .rstrip('\0') will not be neccesary once data is stored in 
        # binary format

        is_filled = bool(binary[0])
        allocated_temp = binary[1:5]
        allocated = self.byte_to_int(allocated_temp)
        filled_temp = binary[5:9]
        filled = self.byte_to_int(filled_temp)
        key_name = str(binary[9:39]).rstrip('\0')

        print 'is_filled: ' , is_filled
        print 'allocated: ' , allocated
        print 'filled: ' , filled
        print 'key_name: ' , key_name


        ret = document.DocumentData(allocated, filled, key_name)

# | 1B - col name length | 1~255B - col name | 1B - value type | 4B - value size| ?B - value|

        # print binary
        print 'start data'

        i = 39
        while(i < len(binary)):
            if binary[i] == '\0':
                break

            col_name_len = int(bin(ord(binary[i])),2)
            i += 1
            col_name = binary[i:i+col_name_len]
            i += col_name_len
            val_type = int(bin(ord(binary[i])),2)
            i += 1
            val_size = self.byte_to_int(binary[i:i+4])
            i += 4

            if(val_type == 0):

                value = self.byte_to_int(binary[i:i+val_size])
                i += val_size
            else:
                value = binary[i:i+val_size].rstrip('\0')
                i += val_size

            ret.add_value(col_name, col_name_len, val_type, val_size, value)


            print 'col_name_len: ' , col_name_len
            print 'col_name: ' , col_name
            print 'val_type: ' , val_type
            print 'val_size: ' , val_size
            print 'value: ' , value



        return ret


    def update_by_keys(self, keys, columns, news, insert_flag):
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
                init_start = start  
                data_start = 0
                while start <= init_start + size_of_data:

                    dirty = int(data[data_start])
                    allocated_temp = data[data_start + self.BOOLEAN_SIZE: data_start + self.BOOLEAN_SIZE + self.INT_SIZE]
                    allocated = self.byte_to_int(allocated_temp)                    
                    if dirty == 1:
                        datakey = data[data_start + self.BOOLEAN_SIZE + 2 * self.INT_SIZE:data_start + self.BOOLEAN_SIZE + 2 * self.INT_SIZE + 30].rstrip('\0')
                        if datakey in keys:
                            traversal = start + self.BOOLEAN_SIZE + 2 * self.INT_SIZE + 30
                            keys.remove(datakey)
                            f.seek(traversal)
                            filled_loc = start + self.BOOLEAN_SIZE + self.INT_SIZE
                            filled_start = start
                            copy_columns = columns
                            copy_news = news
                            while len(copy_columns) != 0:
                                col_len = f.read(1)
                                                             
                                if col_len == '\0' :
                                    break
                                col_len = int(bin(ord(col_len)),2)
                                traversal += 1
                                col_name = f.read(col_len)
                                traversal += col_len
                                val_type = int(bin(ord(f.read(1))),2)
                                f.seek(traversal + 1)
                                val_size = self.byte_to_int(f.read(self.INT_SIZE))
                                traversal += 1 + self.INT_SIZE
                                for i in range(0, len(copy_columns)):
                                    if (col_name) == copy_columns[i]:
                                        f.seek(traversal)
                                        #write new value
                                        if val_type == 0:
                                            a,b,c,d = self.convert_int(int(copy_news[i]))

                                            f.write(str(chr(d)))
                                            f.write(str(chr(c)))
                                            f.write(str(chr(b)))
                                            f.write(str(chr(a)))
                                            
                                                
                                        else:
                                            f.write(bytes(copy_news[i]))
                                                                                    
                                        copy_columns.remove(col_name)
                                        del copy_news[i]

                                        break
                                traversal += val_size
                                f.seek(traversal)
                                        
                            if len(copy_columns) != 0 and insert_flag == 1:

                                f.seek(traversal)
                                for i in range(0, len(copy_columns)):
                                    temp_len = len(copy_columns[i])
                                    a = self.convert_single_byte(temp_len)
                                    f.write(str(chr(a)))
                                    f.write(copy_columns[i])
                                    f.write(str(chr(self.convert_single_byte(2))))


                                    a,b,c,d = self.convert_int(len(copy_news[i]))

                                    f.write(str(chr(d)))
                                    f.write(str(chr(c)))
                                    f.write(str(chr(b)))
                                    f.write(str(chr(a)))

                                    traversal += 1 + temp_len + 1 + 4
                                    f.seek(traversal)
                                    f.write(copy_news[i])
                                f.seek(filled_loc)
                                a,b,c,d = self.convert_int(traversal - filled_start)

                                f.write(str(chr(d)))
                                f.write(str(chr(c)))
                                f.write(str(chr(b)))
                                f.write(str(chr(a)))

                    if len(keys) == 0:
                        return True
                    data_start += allocated
                    start +=allocated
            return False




        


        # TODO: write functino to convert all datatypes for correct
        # storage
            