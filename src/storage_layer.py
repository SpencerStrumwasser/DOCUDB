import os
import document
import predicate_evaluator
import listdata
# import sys


# TODO: maybe make a static class. seems unecesary and waste of space to make new instanece for each new filename

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
    VAL_TYPE_MAP = {0 : 'int' , 1 : 'dec', 2 : 'char', 3 : 'bool', 4: 'RefDoc', 5: 'EmbedDoc', 6 : 'List'}

    # TODO: defined in terminal also.
    ROOT_DATA_DIRECTORY = '../data' # Where the tables at


    def __init__(self, filename, read_size=4069):
        '''
        Filename is identical to collection name
        '''
        self.read_size = read_size
        self.filename = filename
        self.no_file = False

        if not os.path.isfile(self.filename):
            print 'Error: the file ' + self.filename + ' does not exist'
            self.no_file = True


    def byte_to_int(self, byte):
        
        ret = ''
        for k in range(0,4):
            item = bin(ord(byte[k]))[2:]
            num_mult = 8 - len(item)
            item = ('0'*num_mult) + item
            ret += item
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
                    if values[key].val >= 0:
                        f.write('0')
                        a,b,c,d = self.convert_int(values[key].val)
                    else:
                        f.write('1')
                        a,b,c,d = self.convert_int(-values[key].val)


                    f.write(str(chr(d)))
                    f.write(str(chr(c)))
                    f.write(str(chr(b)))
                    f.write(str(chr(a)))
                    start += values[key].val_size
                elif values[key].val_type == 3:
                    if values[key].val:
                        f.write('1')
                    else:
                        f.write('0')
                    start += values[key].val_size
                elif values[key].val_type == 0:       
                    f.write(str(values.val))
                    start += values[key].val_size

                elif values[key].val_type == 5:
                    self.write_data_to_memory(start, values[key].val)
                    start += values[key].val_size  
                elif values[key].val_type == 6:
                    self.write_list_to_memory(start, values[key].val)
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




    def write_list_to_memory(self, start, lis):
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
            f.write(bytearray(lis.allocated_size - 1))
            f.seek(start)
            f.write('1')
            start += self.BOOLEAN_SIZE
            f.seek(start)
            # write how much is allocated

            a,b,c,d = self.convert_int(lis.allocated_size)

            f.write(str(chr(d)))
            f.write(str(chr(c)))
            f.write(str(chr(b)))
            f.write(str(chr(a)))
            start += self.INT_SIZE
            filled_loc = start
            start += self.INT_SIZE

            values = lis.values
            for val in values:
                print val
                # write value type
                f.seek(start)
                a = self.convert_single_byte(val.val_type)
                f.write(str(chr(a)))
                start += 1
                # write value size
                f.seek(start)
                a,b,c,d = self.convert_int(val.val_size)

                f.write(str(chr(d)))
                f.write(str(chr(c)))
                f.write(str(chr(b)))
                f.write(str(chr(a)))
                start += self.INT_SIZE
                # write value
                f.seek(start)




                if val.val_type == 0:
                    if val.val >= 0:
                        f.write('0')
                        a,b,c,d = self.convert_int(val.val)
                    else:
                        f.write('1')
                        a,b,c,d = self.convert_int(-val.val)

                    f.write(str(chr(d)))
                    f.write(str(chr(c)))
                    f.write(str(chr(b)))
                    f.write(str(chr(a)))
                    start += val.val_size
                elif val.val_type == 3:
                    if val.val:
                        f.write('1')
                    else:
                        f.write('0')
                elif val.val_type == 5:
                    self.write_data_to_memory(start, val.val)
                    start += val.val_size 
                elif val.val_type == 6:
                    self.write_list_to_memory(start, val.val)
                    start += val.val_size    
                else:
                    f.write(bytes(val.val))
                    start += val.val_size
        
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

        deletes whole document

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


    def delete_by_predicate(self, proj, exp, ignore_no_col=True):
        '''
        todo: write methdo summary

        deletes columns or whole document

        input: proj -> list of cols to delete, or [] to delete the whole row
        exp -> prediacte in where
        ignore_no_col -> if should ignore user error of specifying col that does not exist
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
                if size_of_data == 0:
                    break
                while start <= init_start + size_of_data:
                    dirty = int(data[data_start])
                    allocated_temp = data[data_start + self.BOOLEAN_SIZE: data_start + self.BOOLEAN_SIZE + self.INT_SIZE]
                    allocated = self.byte_to_int(allocated_temp)
                    if dirty == 1:

                        # datakey = data[data_start + self.BOOLEAN_SIZE + 2 * self.INT_SIZE:data_start + self.BOOLEAN_SIZE + 2 * self.INT_SIZE + 30].rstrip('\0')
                        # if datakey in keys:
                        f.seek(start)   
                        data_temp = f.read(allocated)
                    
                        
                        document_binary = data_temp
                        doc_data = self.binary_to_doc_data(document_binary)
                        cols = doc_data.user_values_dict
                        if predicate_evaluator.eval_pred(exp, cols) == True:
                            if len(proj) == 0: # delete whole row
                                # keys.remove(datakey)
                                f.seek(start)
                                f.write('0')
                            else: # deleting cols
                                for col_to_delete in proj:
                                    if doc_data.has_col(col_to_delete):
                                        doc_data.delete_col(col_to_delete)
                                    else:
                                        if ignore_no_col:
                                            print 'Warning: Column specified does not exist. Continuing.'
                                        else:
                                            pass # oops cannot roll back
                                            # print 'Error: Column specified does not exist. Delete not executed.'
                                            # return False

                                self.write_data_to_memory(start, doc_data)              

                    # if len(keys) == 0:
                    #     return True
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
                    break
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
                            
                            f.seek(start)   
                            data_temp = f.read(allocated)
                        
                            
                            document_binary = data_temp
                            doc_data = self.binary_to_doc_data_sel(document_binary)
                            ret.append(doc_data.user_values_dict)

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

        # print 'is_filled: ' , is_filled
        # print 'allocated: ' , allocated
        # print 'filled: ' , filled
        # print 'key_name: ' , key_name


        ret = document.DocumentData(allocated, filled, key_name)

# | 1B - col name length | 1~255B - col name | 1B - value type | 4B - value size| ?B - value|

        # print binary
        # print 'start data'

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
                flag = binary[i]

                value = self.byte_to_int(binary[i+1:i+val_size])
                if int(flag) == 1:
                    value = -value
            elif(val_type == 3):
                value = binary[i:i+val_size]
                if int(value) == 1:
                    value = True
                else:
                    value = False
            elif val_type == 5:
                valuetemp = self.binary_to_doc_data(binary[i:i+val_size]).user_values_dict
                value = self.__create_embedded_doc(valuetemp)
            elif val_type == 6:
                valuetemp = self.binaryList_to_doc_data(binary[i:i+val_size]).user_values
                valuetemp.sort()
                value = self.__create_list(valuetemp)
                # print "meow", value
            elif val_type == 4:
                value = eval(binary[i:i+val_size].rstrip('\0'))
            elif val_type == 1:
                value = float(binary[i:i+val_size].rstrip('\0'))
            else:
                value = binary[i:i+val_size].rstrip('\0')
            i += val_size
            
            ret.add_value(col_name, col_name_len, val_type, val_size, value)


        return ret




    def binary_to_doc_data_sel(self, binary):
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

        # print 'is_filled: ' , is_filled
        # print 'allocated: ' , allocated
        # print 'filled: ' , filled
        # print 'key_name: ' , key_name


        ret = document.DocumentData(allocated, filled, key_name)

# | 1B - col name length | 1~255B - col name | 1B - value type | 4B - value size| ?B - value|

        # print binary
        # print 'start data'

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
                flag = binary[i]

                value = self.byte_to_int(binary[i+1:i+val_size])
                if int(flag) == 1:
                    value = -value
            elif(val_type == 3):
                value = binary[i:i+val_size]
                if int(value) == 1:
                    value = True
                else:
                    value = False
            elif val_type == 5:
                value = self.binary_to_doc_data(binary[i:i+val_size]).user_values_dict
                
            elif val_type == 6:
                value = self.binaryList_to_doc_data(binary[i:i+val_size]).user_values
                value.sort()
                # print "meow", value
            elif val_type == 4:
                value = eval(binary[i:i+val_size].rstrip('\0'))
            elif val_type == 1:
                value = float(binary[i:i+val_size].rstrip('\0'))
            else:
                value = binary[i:i+val_size].rstrip('\0')
            i += val_size
            
            ret.add_value(col_name, col_name_len, val_type, val_size, value)


        return ret



    def binaryList_to_doc_data(self, binary):
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


        ret = listdata.ListData(allocated, filled)

        # 1B - value type | 4B - value size| ?B - value|
        i = 9
        while(i < len(binary)):
            val_type = int(bin(ord(binary[i])),2)
            i += 1
            val_size = self.byte_to_int(binary[i:i+4])
            i += 4
            print val_type, val_size
            if(val_type == 0):
                flag = binary[i]

                value = self.byte_to_int(binary[i+1:i+val_size])
                if int(flag) == 1:
                    value = -value
            elif val_type == 5:
                valuetemp = self.binary_to_doc_data(binary[i:i+val_size]).user_values_dict
                value = self.__create_embedded_doc(valuetemp)
            elif val_type == 6:
                valuetemp = self.binaryList_to_doc_data(binary[i:i+val_size]).user_values
                valuetemp.sort()
                value = self.__create_list(valuetemp)
            elif val_type == 4:
                value = eval(binary[i:i+val_size].rstrip('\0'))
            elif val_type == 1:
                value = float(binary[i:i+val_size].rstrip('\0'))
            elif(val_type == 3):
                value = binary[i:i+val_size]
                if int(value) == 1:
                    value = True
                else:
                    value = False
            else:
                value = binary[i:i+val_size].rstrip('\0')
            i += val_size
            
            ret.add_value(val_type, val_size, value)

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
                            copy_columns = columns[:]
                            copy_news = news[:]
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
                                            if int(copy_news[i]) >= 0:
                                                f.write('0')
                                                a,b,c,d = self.convert_int(int(copy_news[i]))
                                            else:
                                                f.write('1')
                                                a,b,c,d = self.convert_int(-int(copy_news[i]))
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



    def update_by_predicate(self, exp, columns, news, insert_flag):
        '''
        updates tupples in file based on the passed in predicate

        replace: 
        keys
        
        exp -> predicate in where
        columns -> list of cols
        news -> list of new values
        insert_flag -> 1 for upsert, 0 for update

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
                if size_of_data == 0:
                    break
                while start <= init_start + size_of_data:

                    dirty = int(data[data_start])
                    allocated_temp = data[data_start + self.BOOLEAN_SIZE: data_start + self.BOOLEAN_SIZE + self.INT_SIZE]
                    allocated = self.byte_to_int(allocated_temp)                    
                    
                    if dirty == 1:
                        # datakey = data[data_start + self.BOOLEAN_SIZE + 2 * self.INT_SIZE:data_start + self.BOOLEAN_SIZE + 2 * self.INT_SIZE + 30].rstrip('\0')
                        f.seek(start)   
                        data_temp = f.read(allocated)
                    
                        
                        document_binary = data_temp
                        doc_data = self.binary_to_doc_data(document_binary)
                        cols = doc_data.user_values_dict
                        if predicate_evaluator.eval_pred(exp, cols) == True:
                            #  (self, exp, columns, news, insert_flag)

                            for i in range(len(columns)):
                                col = columns[i]
                                new_val = news[i]

                                if doc_data.has_col(col): # update this col
                                    col_size = int(doc_data.values[col].col_name_len)
                                    doc_data.delete_col(col)
                                    
                                    if isinstance(new_val, tuple):
                                        value_size = len(str(value))
                                        doc_data.add_value(col, col_size, 4, value_size, str(new_val))
                                    elif isinstance(new_val, str):
                                        value_size = len(new_val)
                                        doc_data.add_value(col, col_size, 2, value_size, new_val)
                                    elif isinstance(new_val, bool):
                                        doc_data.add_value(col, col_size, 3, 1, new_val)
                                    elif isinstance(new_val, int):
                                        doc_data.add_value(col, col_size, 0, 4, new_val)
                                    elif isinstance(new_val, float):
                                        value_size = len(str(new_val))
                                        doc_data.add_value(col, col_size, 1, value_size, str(new_val))
                                    elif isinstance(new_val, dict):
                                        embed_doc = self.__create_embedded_doc(new_val)
                                        value_size = embed_doc.allocated_size
                                        doc_data.add_value(col, col_size, 5, value_size, embed_doc)
                                    elif isinstance(new_val, list):
                                        embed_lis = self.__create_list(new_val)
                                        value_size = embed_lis.allocated_size
                                        doc_data.add_value(col, col_size, 6, value_size, embed_lis)

                                else:
                                    if insert_flag: # upsert

                                        if isinstance(new_val, tuple):
                                            value_size = len(str(value))
                                            doc_data.add_value(col, len(col), 4, value_size, str(new_val))
                                        elif isinstance(new_val, str):
                                            value_size = len(new_val)
                                            doc_data.add_value(col, len(col), 2, value_size, new_val)
                                        elif isinstance(new_val, bool):
                                            doc_data.add_value(col, len(col), 3, 1, new_val)
                                        elif isinstance(new_val, int):
                                            doc_data.add_value(col, len(col), 0, 4, new_val)
                                        elif isinstance(new_val, float):
                                            value_size = len(str(new_val))
                                            doc_data.add_value(col, len(col), 1, value_size, str(new_val))
                                        elif isinstance(new_val, dict):
                                            embed_doc = self.__create_embedded_doc(new_val)
                                            value_size = embed_doc.allocated_size
                                            doc_data.add_value(col, len(col), 5, value_size, embed_doc)
                                        elif isinstance(new_val, list):
                                            embed_lis = self.__create_list(new_val)
                                            value_size = embed_lis.allocated_size
                                            doc_data.add_value(col, len(col), 6, value_size, embed_lis)

                                    else: # give warning
                                        pass


                            # traversal = start + self.BOOLEAN_SIZE + 2 * self.INT_SIZE + 30
                            # f.seek(traversal)
                            # filled_loc = start + self.BOOLEAN_SIZE + self.INT_SIZE
                            # filled_start = start
                            # copy_columns = columns[:]
                            # copy_news = news[:]
                            # while len(copy_columns) != 0:
                            #     col_len = f.read(1)
                                                             
                            #     if col_len == '\0' :
                            #         break
                            #     col_len = int(bin(ord(col_len)),2)
                            #     traversal += 1
                            #     col_name = f.read(col_len)
                            #     traversal += col_len
                            #     val_type = int(bin(ord(f.read(1))),2)
                            #     f.seek(traversal + 1)
                            #     val_size = self.byte_to_int(f.read(self.INT_SIZE))
                            #     traversal += 1 + self.INT_SIZE
                            #     for i in range(0, len(copy_columns)):
                            #         if (col_name) == copy_columns[i]:
                            #             f.seek(traversal)
                            #             #write new value
                            #             if val_type == 0:
                            #                 a,b,c,d = self.convert_int(int(copy_news[i]))

                            #                 f.write(str(chr(d)))
                            #                 f.write(str(chr(c)))
                            #                 f.write(str(chr(b)))
                            #                 f.write(str(chr(a)))
                                            
                                                
                            #             else:
                            #                 f.write(bytes(copy_news[i]))
                                                                                    
                            #             copy_columns.remove(col_name)
                            #             del copy_news[i]

                            #             break
                            #     traversal += val_size
                            #     f.seek(traversal)
                                        
                            # if len(copy_columns) != 0 and insert_flag == 1:

                            #     f.seek(traversal)
                            #     for i in range(0, len(copy_columns)):
                            #         temp_len = len(copy_columns[i])
                            #         a = self.convert_single_byte(temp_len)
                            #         f.write(str(chr(a)))
                            #         f.write(copy_columns[i])
                            #         f.write(str(chr(self.convert_single_byte(2))))


                            #         a,b,c,d = self.convert_int(len(copy_news[i]))

                            #         f.write(str(chr(d)))
                            #         f.write(str(chr(c)))
                            #         f.write(str(chr(b)))
                            #         f.write(str(chr(a)))

                            #         traversal += 1 + temp_len + 1 + 4
                            #         f.seek(traversal)
                            #         f.write(copy_news[i])
                            #     f.seek(filled_loc)
                            #     a,b,c,d = self.convert_int(traversal - filled_start)

                            #     f.write(str(chr(d)))
                            #     f.write(str(chr(c)))
                            #     f.write(str(chr(b)))
                            #     f.write(str(chr(a)))

                            if doc_data.filled_size > doc_data.allocated_size:
                                # if exceed current allocation, double allocation in documentData object,
                                # then delete current block in memory, and write to a new block.
                                for ite in range(10, 26):
                                    if (doc_data.filled_size < 2**ite):
                                        break
                                if ite == 25:
                                    print ("Document is now Too Big - Document Unchanged")
                                    return False
                                doc_data.allocated_size = 2**ite

                                f.seek(start)
                                f.write('0')

                                new_size = self.search_memory_for_free(doc_data.allocated_size)
                                self.write_data_to_memory(new_size, doc_data)

                            else:
                                self.write_data_to_memory(start, doc_data)

                    data_start += allocated
                    start +=allocated
            return False


    # for select 
    def get_all_tuples(self, exp):
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
                init_start = start
                if size_of_data == 0:
                    break
                data_start = 0  
                while start <= init_start + size_of_data:
                    if data[data_start] == '\0':
                        dirty = 0
                    else:   
                        dirty = int(data[data_start])

                    allocated_temp = data[data_start + self.BOOLEAN_SIZE: data_start + self.BOOLEAN_SIZE + self.INT_SIZE]
                    allocated = self.byte_to_int(allocated_temp)
                    if dirty == 1:
                        # print datakey
                        f.seek(start)   
                        data_temp = f.read(allocated)
                    
                        
                        document_binary = data_temp
                        doc_data = self.binary_to_doc_data_sel(document_binary)
                        cols = doc_data.user_values_dict
                        if predicate_evaluator.eval_pred(exp, cols) == True:
                            ret.append(doc_data.user_values_dict)
                    data_start += allocated
                    start += allocated

            if ret == []:
                return False
            return ret


    def drop_table(self):
        '''
        ROOT_DIRECTORY is already appended to filename when passed in from myparser
        '''
        if os.path.isfile(self.filename):
            os.remove(self.filename)
        else:
            print 'Error: The collection file ' + self.filename + ' you are trying to remove don\'t exist.'

        


        # TODO: write functino to convert all datatypes for correct
        # storage
            

    ## TODO: This function is defined twice (second time in myparser.py). oops
    def __create_embedded_doc(self, columns):

        file_to_insert = document.DocumentData(0,0, columns['_key'])
        memory_needed = 39
        for key, value in columns.iteritems():
            insert_key = str(key)
            if insert_key == '_key':
                continue
            col_size = len(str(key))
            memory_needed += col_size + 4
            if isinstance(value, tuple):
                value_size = len(str(value))
                file_to_insert.add_value(insert_key, col_size, 4, value_size, str(value))
                memory_needed += 1 + value_size + 4
            elif isinstance(value, str):
                value_size = len(value)
                file_to_insert.add_value(insert_key, col_size, 2, value_size, value)
                memory_needed += 1 + value_size + 4
            elif isinstance(value, bool):
                if value:
                    value = 1
                else:
                    value = 0
                file_to_insert.add_value(insert_key, col_size, 3, 1, value)
                memory_needed += 1 + 4 + 1
            elif isinstance(value, int):
                file_to_insert.add_value(insert_key, col_size, 0, 5, value)
                memory_needed += 1 + 4 + 5
            elif isinstance(value, float):
                value_size = len(str(value))
                file_to_insert.add_value(insert_key, col_size, 1, value_size, str(value))
                memory_needed += 1 + value_size + 4
            elif isinstance(value, dict):
                embed_doc = self.__create_embedded_doc(value)
                value_size = embed_doc.allocated_size
                file_to_insert.add_value(insert_key, col_size, 5, value_size, embed_doc)
                memory_needed += 1 + value_size + 4
            elif isinstance(value, list):
                embed_lis = self.__create_list(value)
                value_size = embed_lis.allocated_size
                file_to_insert.add_value(insert_key, col_size, 6, value_size, embed_lis)
                memory_needed += 1 + value_size + 4

        for ite in range(10, 25):
            if (memory_needed < 2**ite):
                break
        file_to_insert.allocated_size = 2**ite
        # print file_to_insert.allocated_size
        return file_to_insert

    ## TODO: This function is defined twice(second time in myparser.py). oops
    def __create_list(self, columns):

        file_to_insert = listdata.ListData(0,0)
        memory_needed = 9
        for value in columns:
            if isinstance(value, tuple):
                value_size = len(str(value))
                file_to_insert.add_value(4, value_size, str(value))
                memory_needed += 1 + value_size + 4
            elif isinstance(value, str):
                value_size = len(value)
                file_to_insert.add_value(2, value_size, value)
                memory_needed += 1 + value_size + 4
            elif isinstance(value, bool):
                if value:
                    value = 1
                else:
                    value = 0
                file_to_insert.add_value(3, 1, value)
                memory_needed += 1 + 4 + 1
            elif isinstance(value, int):
                file_to_insert.add_value(0, 5, value)
                memory_needed += 1 + 4 + 5

            elif isinstance(value, float):
                value_size = len(str(value))
                file_to_insert.add_value(1, value_size, str(value))
                memory_needed += 1 + value_size + 4
            elif isinstance(value, dict):
                embed_doc = self.__create_embedded_doc(value)
                value_size = embed_doc.allocated_size
                file_to_insert.add_value(5, value_size, embed_doc)
                memory_needed += 1 + value_size + 4
            elif isinstance(value, list):
                embed_lis = self.__create_list(value)
                value_size = embed_lis.allocated_size
                file_to_insert.add_value(6, value_size, embed_lis)
                memory_needed += 1 + value_size + 4
        file_to_insert.allocated_size = memory_needed
        # print file_to_insert.allocated_size
        return file_to_insert





