
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

    ROOT_DIRECTORY = 

    def __init__(self, ):
        '''
        
        '''
    
        # set block/read size
        self.read_size = 4096

        


        








        