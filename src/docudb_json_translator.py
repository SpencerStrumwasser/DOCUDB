from keywords import LANGUAGE_KEYWORDS
from keywords import OPERATORS
from keywords import WORD_OPERATORS


import inspect

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
        print inspect.currentframe().f_back.f_lineno
        return None

    ret_dict = {}
    __parse(tokens, 0, ret_dict)

    return ret_dict

def __parse(tokens, idx, cur_dict, is_embedded_doc_parse=False):

    if __at_invalid_idx(tokens, idx):
        print 'JSON formatting error: Literally empty'
        print inspect.currentframe().f_back.f_lineno
        cur_dict.clear()
        return 

    cur_tok = tokens[idx]

    if cur_tok == '{':
        __col_val(tokens, idx + 1, cur_dict, is_embedded_doc_parse)

    else:
        pass
        print 'JSON formatting error near ' + cur_tok
        print '    Expected "{"'
        print inspect.currentframe().f_back.f_lineno
        cur_dict.clear()

    return


def __col_val(tokens, idx, cur_dict, is_embedded_doc_parse=False):
    # column name, colon, AND value

    if __at_invalid_idx(tokens, idx):
        print 'JSON formatting error near ' + tokens[idx]
        cur_dict.clear()
        print inspect.currentframe().f_back.f_lineno
        return
    elif __at_invalid_idx(tokens, idx + 1):
        print 'JSON formatting error near ' + tokens[idx + 1]
        cur_dict.clear()
        print inspect.currentframe().f_back.f_lineno
        return
    elif __at_invalid_idx(tokens, idx + 2):
        print 'JSON formatting error near ' + tokens[idx + 2]
        cur_dict.clear()
        print inspect.currentframe().f_back.f_lineno
        return


    col_tok = tokens[idx]
    colon_tok = tokens[idx + 1]
    val_tok = tokens[idx + 2]
    
    # Check column name constraints
    if col_tok in cur_dict:
        print 'JSON Error: Repeated column names disallowed'
        cur_dict.clear()
        print inspect.currentframe().f_back.f_lineno
        return        
    if len(col_tok) == 0:
        print 'JSON Error: Column names cannot be empty'
        cur_dict.clear()
        print inspect.currentframe().f_back.f_lineno
        return
    if len(col_tok) > 255:
        print 'JSON Error: Column names have 255 max character length'
        cur_dict.clear()
        print inspect.currentframe().f_back.f_lineno
        return
    if col_tok in LANGUAGE_KEYWORDS or col_tok in OPERATORS:
        if is_embedded_doc_parse and col_tok != '_key':
            print 'JSON Error: Column name cannot be a keyword or operator: ' + col_tok
            cur_dict.clear()
            print inspect.currentframe().f_back.f_lineno
            return
    for ch in col_tok:
        if not ch.isalnum() and ch != '_':
            print 'JSON Error: Column names can only contain A-Z, a-z, 0-9, and _'
            cur_dict.clear()
            print inspect.currentframe().f_back.f_lineno
            return
    if not col_tok[0].isalpha():
        if is_embedded_doc_parse and col_tok != '_key':
            print 'JSON Error: Column name has to start with a-z or A-Z character'
            cur_dict.clear()
            print inspect.currentframe().f_back.f_lineno
            return


    # Colon
    if colon_tok != ':':
        print 'JSON Error at: ' + col_tok + ' ' + colon_tok + ' ' + val_tok
        print '    Colon expected between column name and value'
        cur_dict.clear()
        print inspect.currentframe().f_back.f_lineno
        return

    ## TODO: code repeated in update_translator -> can put in seperate module
    # Parse value
    if val_tok[0] == '"' and val_tok[-1] == '"': # string
        cur_dict[col_tok] = val_tok[1:-1] # Stripping the quotes
        # TODO: probably should put some cap on string size?

    elif val_tok == '[': # List

        val_lst = []


        s_braces_open = 0
        lst_toks = []
        while True:
            lst_toks.append(tokens[idx + 2])

            if tokens[idx + 2] == '[':
                s_braces_open += 1
            elif tokens[idx + 2] == ']':
                s_braces_open -= 1

            if s_braces_open == 0:
                break

            idx += 1
        lst_toks.append(tokens[idx + 2])


        # Example list:
        # [     {_key : "sid1", name : "Jonny", age : 3}, 
        #       {_key : "sid2", name : "Jon", age : 6}, 
        #       666,
        #       "hello"     ]
        def __parse_list(lst_toks, lst_idx, val_lst):
            if __at_invalid_idx(lst_toks, lst_idx):
                raise BaseException
                # todo: handle BETTER

            if lst_toks[lst_idx] == '[':
                __value_list(lst_toks, lst_idx + 1, val_lst)

            else:
                raise BaseException
                #todo catch better

            return


        def __value_list(lst_toks, lst_idx, val_lst):
            # print 'lst_toks ' + str(lst_toks)
            # print lst_idx

            val_tok = lst_toks[lst_idx]


            #  This code is basically the 'value' section of __col_val
            if val_tok[0] == '"' and val_tok[-1] == '"': # string
                val_lst.append(val_tok[1:-1]) # Stripping the quotes
                # TODO: probably should put some cap on string size?

            elif val_tok == '[': # List
                pass

            elif val_tok == '{': # Embedded Document
                #  __parse(tokens, idx, cur_dict)
                # val_tok == tokens[idx + 2]

                emb_dic = {}
                emb_toks = []

                braces_open = 0


                while True:
                    
                    emb_toks.append(lst_toks[lst_idx])

                    if lst_toks[lst_idx] == '{':
                        braces_open += 1
                    elif lst_toks[lst_idx] == '}':
                        braces_open -= 1

                    if braces_open == 0:
                        break

                    lst_idx += 1

                # emb_toks.append(lst_toks[lst_idx])

                # print emb_toks

                __parse(emb_toks, 0, emb_dic, True)

                # print emb_dic

                val_lst.append(emb_dic.copy()) # todo: is copy neccesary?


            elif val_tok[0] == '<' and val_tok[-1] == '>': # document reference col
                def __d_lex(s):
                    
                    ct = ''
                    r = []
                    for i in range(len(s)):
                        c = s[i]

                        if c == ',' or c == '>':
                            r.append(ct)
                            ct = ''
                        else:
                            ct += c
                    return r[:]


                val_lst.append(tuple(__d_lex(val_tok[1:])) )   


            elif val_tok == 'true':
                val_lst.append(True)
            
            elif val_tok == 'false':
                val_lst.append(False)

            elif val_tok.isdigit() or (val_tok[1:].isdigit() and val_tok[0] == '-'):
                int_val = int(val_tok)


                # 4 bytes -> 32 bits for storing int. 1 bit for +/-
                if abs(int_val) >= 2**15:
                    print 'LIST Error: int values range from (-2**15, 2**15). 32 bit storage space'
                    raise BaseException # todo catch better
                    return
                else:
                    val_lst.append(int_val)

            else: 
                # float or undefined
                try:
                    float_val = float(val_tok)
                    val_lst.append(float_val)
                except:
                    print 'LIST Error: undefined value type: ' + col_tok + ' ' + colon_tok + ' ' + val_tok
                    raise BaseException # todo catch better
                    return

            # Check for comma or end of list
            if __at_invalid_idx(tokens, idx + 1):
                print 'list formatting error near ' + lst_toks[lst_idx]
                print '    Additional token expected '
                raise BaseException # todo catch better
                return
            sep_tok = lst_toks[lst_idx + 1]

            # print sep_tok

            if sep_tok == ',':
                __value_list(lst_toks, lst_idx + 2, val_lst)
            elif sep_tok == ']':
                return 
            else:
                print 'LIST formatting error near ' + tokens[idx]
                print '    Expecting either "," or "}"'
                raise BaseException # todo catch better
                return

        __parse_list(lst_toks, 0, val_lst)       

        cur_dict[col_tok] = val_lst[:] # todo: is copy neccesary?

    elif val_tok == '{': # Embedded Document
        #  __parse(tokens, idx, cur_dict)
        # val_tok == tokens[idx + 2]

        emb_dic = {}
        emb_toks = []

        braces_open = 0

        while True:
            emb_toks.append(tokens[idx + 2])

            if tokens[idx + 2] == '{':
                braces_open += 1
            elif tokens[idx + 2] == '}':
                braces_open -= 1

            if braces_open == 0:
                break

            idx += 1


        emb_toks.append(tokens[idx + 2])

        __parse(emb_toks, 0, emb_dic, True)

        cur_dict[col_tok] = emb_dic.copy() # todo: is copy neccesary?




    elif val_tok[0] == '<' and val_tok[-1] == '>': # document reference col
        def __d_lex(s):
            
            ct = ''
            r = []
            for i in range(len(s)):
                c = s[i]

                if c == ',' or c == '>':
                    r.append(ct)
                    ct = ''
                else:
                    ct += c
            return r[:]


        cur_dict[col_tok] = tuple(__d_lex(val_tok[1:]))    


    elif val_tok == 'true':
        cur_dict[col_tok] = True
    
    elif val_tok == 'false':
        cur_dict[col_tok] = False

    elif val_tok.isdigit():
        int_val = int(val_tok)

        # 4 bytes -> 32 bits for storing int. 1 bit for +/-
        if abs(int_val) >= 2**31:
            print 'JSON Error: int values range from (-2147483647, 2147483647). 32 bit storage space'
            cur_dict.clear()
            print inspect.currentframe().f_back.f_lineno
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
            print inspect.currentframe().f_back.f_lineno
            return

    # Check for comma or end of json
    if __at_invalid_idx(tokens, idx + 3):
        print 'JSON formatting error near ' + tokens[idx + 2]
        print '    Additional token expected '
        print inspect.currentframe().f_back.f_lineno
        cur_dict.clear()
        return
    sep_tok = tokens[idx + 3]

    if sep_tok == ',':
        __col_val(tokens, idx + 4, cur_dict, is_embedded_doc_parse)
    elif sep_tok == '}':
        return 
    else:
        print 'JSON formatting error near ' + tokens[idx + 2]
        print '    Expecting either "," or "}"'
        cur_dict.clear()
        print inspect.currentframe().f_back.f_lineno
        return


# def __comma(tokens, idx, cur_dict):
#     pass


# def __close_brack(tokens, idx, cur_dict):
#     pass


def __lex(json_string):

    tokens = []

    double_quote_open = False
    angle_brack_open = False

    curly_brace_open = 0
    square_brace_open = 0

    cur_tok = ''
    for i in range(len(json_string)):
        c = json_string[i]

        if double_quote_open:
            cur_tok += c
            if c == '"':
                tokens.append(cur_tok)
                cur_tok = ''
                double_quote_open = False

        elif angle_brack_open:
            cur_tok += c
            if c == '>':
                tokens.append(cur_tok)
                cur_tok = ''
                angle_brack_open = False

        elif c == ':' or c == ',' or c == '{' or c == '}' or c == '[' or c == ']':
            if cur_tok != '':
                tokens.append(cur_tok)
            cur_tok = ''
            tokens.append(c)
            if c == '{':
                curly_brace_open += 1
            elif c == '}':
                curly_brace_open -= 1
            elif c == '[':
                square_brace_open += 1
            elif c == ']':
                square_brace_open -= 1


        elif c == '"':
            cur_tok += c
            double_quote_open = True

        elif c == '<':
            cur_tok += c
            angle_brack_open = True

        elif c == ' ' or c == '\n' or c == '\t' or c == '\r':
            if cur_tok != '':
                tokens.append(cur_tok)
            cur_tok = ''

        else:
            cur_tok += c

    if curly_brace_open != 0 or square_brace_open != 0:
        print 'something went wrong!'
        print '  oh noooo!'
        exit()

    # print tokens

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

    j_emb1 = '{name: "dick", child : <c_emb, child1>, pay : 90000}'

    j_emb2 = '{name: "joe", child : {_key : "sid1", name : "Jonny", age : 3}, pay : 90000} '
    j_emb3 = ' {name: "grandfather", child : {_key : "sss", name: "joe", child : {_key : "sid1", name : "Jonny", age : 3}, pay : 90000} } '
    j_lst = '{name: "joe", children : [{_key : "sid1", name : "Jonny", age : 3}, {_key : "sid2", name : "Jon", age : 6}, 666], pay : 90000} '

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

    def pdick(dick):
        for thing in dick:
            print thing + ':' + str(dick[thing])
        print ''


    # plist(__lex(j1))
    # plist(__lex(j_wrong1))
    # plist(__lex(j_wrong2))
    # plist(__lex(j_wrong3))
    # plist(__lex(j_wrong4))


    # print 'lex'
    # plist(__lex(j_lst))


    print '\n\nparse'
    emb_dd = json_to_dict(j_lst)

    # print emb_dd
    pdick(emb_dd)


