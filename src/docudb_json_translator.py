from keywords import LANGUAGE_KEYWORDS
from keywords import OPERATORS
from keywords import WORD_OPERATORS

INT_SIZE = 4 # from storage layer. TODO: put this in one unified place

'''
Module for converting 'json' strings to python dictionaries. 

json is in quotes because the strings are not in true json form,
but rather a json-like format we have designed.


Datatypes:
    int
    dec
    bool
    string

    (in the fututre maybe) arrays, sub-json objects

Syntax:
    {int_col : 123, dec_col : 1.2333, bool_col : true, string_col : "helllooo"}
    * no quotes around column names
    * strings have double quotes around them

    Regular Expression for syntax
        { (<col_name> : <value> , )* (<col_name> : <value>) } | {}



'''



def json_to_dict(json_string):

    tokens = __lex(json_string)
    if '' in tokens:
        print 'Json Lex error in docudb_json_translator.'
        return None

    ret_dict = {}
    __parse(tokens, 0, ret_dict)

    return ret_dict

def __parse(tokens, idx, cur_dict):

    if __at_invalid_idx(tokens, idx):
        print 'JSON formatting error: Literally empty'
        cur_dict.clear()
        return 

    cur_tok = tokens[idx]

    if cur_tok == '{':
        __col_val(tokens, idx + 1, cur_dict)

    else:
        pass
        print 'JSON formatting error near ' + cur_tok
        print '    Expected "{"'
        cur_dict.clear()

    return


def __col_val(tokens, idx, cur_dict):
    # column name, colon, AND value

    if __at_invalid_idx(tokens, idx):
        print 'JSON formatting error near ' + tokens[idx]
        cur_dict.clear()
        return
    elif __at_invalid_idx(tokens, idx + 1):
        print 'JSON formatting error near ' + tokens[idx + 1]
        cur_dict.clear()
        return
    elif __at_invalid_idx(tokens, idx + 2):
        print 'JSON formatting error near ' + tokens[idx + 2]
        cur_dict.clear()
        return


    col_tok = tokens[idx]
    colon_tok = tokens[idx + 1]
    val_tok = tokens[idx + 2]
    
    # Check column name constraints
    if col_tok in cur_dict:
        print 'JSON Error: Repeated column names disallowed'
        cur_dict.clear()
        return        
    if len(col_tok) == 0:
        print 'JSON Error: Column names cannot be empty'
        cur_dict.clear()
        return
    if len(col_tok) > 255:
        print 'JSON Error: Column names have 255 max character length'
        cur_dict.clear()
        return
    if col_tok in LANGUAGE_KEYWORDS or col_tok in OPERATORS:
        print 'JSON Error: Column name cannot be a keyword or operator: ' + col_tok
        cur_dict.clear()
        return
    for ch in col_tok:
        if not ch.isalnum() and ch != '_':
            print 'JSON Error: Column names can only contain A-Z, a-z, 0-9, and _'
            cur_dict.clear()
            return
    if not col_tok[0].isalpha():
        print 'JSON Error: Column name has to start with a-z or A-Z character'
        cur_dict.clear()
        return


    # Colon
    if colon_tok != ':':
        print 'JSON Error at: ' + col_tok + ' ' + colon_tok + ' ' + val_tok
        print '    Colon expected between column name and value'
        cur_dict.clear()
        return

    ## TODO: code repeated in update_translator -> can put in seperate module
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
        if abs(int_val) >= 2^31:
            print 'JSON Error: int values range from (-2147483647, 2147483647). 32 bit storage space'
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
            print 'JSON Error: undefined value type: ' + col_tok + ' ' + colon_tok + ' ' + val_tok
            cur_dict.clear()
            return

    # Check for comma or end of json
    if __at_invalid_idx(tokens, idx + 3):
        print 'JSON formatting error near ' + tokens[idx + 2]
        print '    Additional token expected '
        cur_dict.clear()
        return
    sep_tok = tokens[idx + 3]

    if sep_tok == ',':
        __col_val(tokens, idx + 4, cur_dict)
    elif sep_tok == '}':
        return 
    else:
        print 'JSON formatting error near ' + tokens[idx + 2]
        print '    Expecting either "," or "}"'
        cur_dict.clear()
        return


# def __comma(tokens, idx, cur_dict):
#     pass


# def __close_brack(tokens, idx, cur_dict):
#     pass


def __lex(json_string):

    tokens = []

    double_quote_open = False

    cur_tok = ''
    for i in range(len(json_string)):
        c = json_string[i]

        if double_quote_open:
            cur_tok += c
            if c == '"':
                tokens.append(cur_tok)
                cur_tok = ''
                double_quote_open = False

        elif c == ':' or c == ',' or c == '{' or c == '}':
            if cur_tok != '':
                tokens.append(cur_tok)
            cur_tok = ''
            tokens.append(c)

        elif c == '"':
            cur_tok += c
            double_quote_open = True

        elif c == ' ' or c == '\n' or c == '\t' or c == '\r':
            if cur_tok != '':
                tokens.append(cur_tok)
            cur_tok = ''

        else:
            cur_tok += c

    return tokens

def __at_invalid_idx(token_list, idx):
    '''
    True if idx is out of bounds
    '''
    return len(token_list) <= idx


# For testing
if __name__ == '__main__':
    

    j1 = '{col1 : 1, col__2 : "helloooo",col3:True,collloooo        :    ":::::,,,,,"}'

    j_wrong1 = 'col1 : 1, col__2 : "helloooo",col3:True,collloooo        :    ":::::,,,,,"}' # missing {
    j_wrong2 = '{col1 : 1, col__2 : "helloooo",col3:True,collloooo        :    ":::::,,,,,"' # missing }
    j_wrong3 = '{col1 : 1, col__2 : "helloooo"col3:True,collloooo        :    ":::::,,,,,"}' # missing ,
    j_wrong4 = '{col1 : 1, col__2 : "helloooo", col3    True,collloooo        :    ":::::,,,,,"}' #missing :

    # print __lex(j1)
    # print ''
    # print __lex(j_wrong1)
    # print ''
    # print __lex(j_wrong2)
    # print ''
    # print __lex(j_wrong3)
    # print ''
    # print __lex(j_wrong4)

    def plist(lst):
        for thing in lst:
            print thing
        print ''

    plist(__lex(j1))
    plist(__lex(j_wrong1))
    plist(__lex(j_wrong2))
    plist(__lex(j_wrong3))
    plist(__lex(j_wrong4))










