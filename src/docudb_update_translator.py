from keywords import LANGUAGE_KEYWORDS
from keywords import OPERATORS
from keywords import WORD_OPERATORS

INT_SIZE = 4 # from storage layer. TODO: put this in one unified place

'''
Syntax of update lists:
    [col1, col2, ...] = [val1, val2, ...]

'''

# This is the only public function in this module
def strlists_to_dict(cols_str, vals_str):
    '''
    todo: fill in funciton docstirng


    returns a dictionary
    '''
    cols =  [] # Column names
    __col_lex(cols_str, cols) 

    vals = [] # values to set
    __val_lex(vals_str, vals)

    update_dict = {}
    if cols == None or vals == None: # some error
        return None
    __make_dict(cols, vals, update_dict)


    return {'update_dict' : update_dict, 'cols' : cols, 'vals' : vals}

    
def __make_dict(cols, vals, cur_dict):

    if len(cols) != len(vals):
        print 'Update Syntax Error: number of cols and values do not match: ' + str(cols) + ' = ' + str(vals)
        cur_dict.clear()
        return

    for i in range(len(cols)):
        col_tok = cols[i]
        val_tok = vals[i]

        # Check column name constraints
        if col_tok in cur_dict:
            print 'Update Error: Repeated column names disallowed'
            cur_dict.clear()
            return        
        if len(col_tok) == 0:
            print 'Update Error: Column names cannot be empty'
            cur_dict.clear()
            return
        if col_tok in LANGUAGE_KEYWORDS or col_tok in OPERATORS:
            print 'Update Error: Column name cannot be a keyword or operator: ' + col_tok
            cur_dict.clear()
            return
        if len(col_tok) > 255:
            print 'Update Error: Column names have 255 max character length'
            cur_dict.clear()
            return
        for ch in col_tok:
            if not ch.isalnum() and ch != '_':
                print 'Update Error: Column names can only contain A-Z, a-z, 0-9, and _'
                cur_dict.clear()
                return
        if not col_tok[0].isalpha():
            print 'Update Error: Column name has to start with a-z or A-Z character'
            cur_dict.clear()
            return

        # Parse value
        if val_tok[0] == '"' and val_tok[-1] == '"': # string
            cur_dict[col_tok] = val_tok[1:-1] # Stripping the quotes
            # TODO: probably should put some cap on string size?

        elif val_tok == 'true':
            cur_dict[col_tok] = True
        
        elif val_tok == 'false':
            cur_dict[col_tok] = False

        elif val_tok.isdigit():
            int_val = int(val_tok)
            # 4 bytes -> 32 bits for storing int. 1 bit for +/-
            if abs(int_val) >= 2**31:
                print 'Update Syntax Error: int values range from (-2147483647, 2147483647). 32 bit storage space'
                cur_dict.clear()
                return
            else:
                cur_dict[col_tok] = int_val

        else: 
            # float or undefined
            try:
                float_val = float(val_tok)
                cur_dict[col_tok] = float_val
            except:
                print 'Update Syntax Error: undefined value type: ' + col_tok + ' = ' + val_tok
                cur_dict.clear()
                return




def __val_lex(vals_str, vals):


    if len(vals_str) <= 1:
        print 'Update Syntax Error: ' + vals_str
        vals = None
        return      
    if vals_str[0] != '[' or vals_str[-1] != ']':
        print 'Update Syntax Error: missing square brackets '
        vals = None
        return 

    vals_str = vals_str[1:-1] # strip []
    vals_str += ',' # for ease of parsing


    double_quote_open = False
    cur = ''
    for i in range(len(vals_str)):
        c = vals_str[i]

        if double_quote_open:
            cur += c
            if c == '"':
                vals.append(cur)
                cur = ''
                double_quote_open = False

        elif c == ',':
            if cur != '':
                vals.append(cur)
                cur = ''

        elif c == '"':
            cur += c
            double_quote_open = True

        elif c != ' ': # or c != '\n' or c != '\t' or c != '\r': # TODO
            cur += c




def __col_lex(cols_str, cols):

    if len(cols_str) <= 1:
        print 'Update Syntax Error: ' + cols_str
        cols = None
        return      
    if cols_str[0] != '[' or cols_str[-1] != ']':
        print 'Update Syntax Error: missing square brackets '
        cols = None
        return 

    cols_str = cols_str[1:-1] # strip []
    cols_str += ',' # for ease of parsing
    cur = ''

    for i in range(len(cols_str)):
        c = cols_str[i]

        if c == ',':
            cols.append(cur)
            cur = ''
        elif c != ' ':
            cur += c



# For testing 
if __name__ == '__main__':

    col_str1 = '[      col1,col2, col3   ,col4   ,    col5]'
    val_str1 = '[1,2,        "threee"      ,    4.0,      true]'

    col_str2= '[col1, col2, col3]'

    dicc = strlists_to_dict(col_str1, val_str1)

    for key in dicc:
        print key + ': ' + str(dicc[key]) + ': ' + str(type(dicc[key]))





