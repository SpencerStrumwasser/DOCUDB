

LANGUAGE_KEYWORDS = set(
                    [   'insert',
                        'into',
                        'select',
                        'from',
                        'where',
                        'update',
                        'set',
                        'upsert',
                        'delete',
                        'create',
                        'drop'
                    ])



# TODO: in the future, might have to seperate arithmetic, comparison, 
OPERATORS = set(
                [
                '+',    # Arithmetic
                '-',
                '*',
                '/',
                '%',
                '**',
                '==',   # Comparison
                '>',
                '<',
                '>=',
                '<=',
                '!=',
                'in',
                'and',  # Logical
                'or',
                'not',
                '='     # Assignment
                ])

# These operators require a space between values, whereas 
# other operators do not: eg 1+1 is ok. trueandtrue is not.
WORD_OPERATORS = set(
                [
                'in',
                'and',  # Logical
                'or',
                'not',
                ])

class Lexer:
    '''
    Takes an input query string and retuns a list of tokens.
    '''

    def __init__(self):
        self.tokens = []

    def lex(self, query_str):
        '''
        Breaks input query string apart by spaces: 
        These denote a continuous token (if multiple,
        which-ever comes first).
        1. ""
        2. {} 
        3. []
        4. ()

        In addition to spaces, commas seperate tokens. Assuming
        the lex is not in one of the 4 states above.

        input: query_str -> A docuDB query to be lexed.  
        return -> A list of tokens 
        '''

        # Empty tokens list
        if len(self.tokens) != 0:
            self.tokens[:] = []

        double_quote_open = False
        curly_brace_open = False
        square_brace_open = False
        paren_open = False


        cur_tok = ''
        for i in range(len(query_str)):
            c = query_str[i]

            # If inside a "", {}, [], or (): basically read until the 
            # closing symbol is found. 
            # TODO: implement escape sequences 

            if double_quote_open: # ""
                cur_tok += c
                if c == '"':
                    self.tokens.append(cur_tok)
                    cur_tok = ''
                    double_quote_open = False

            elif curly_brace_open: # {}
                cur_tok += c
                if c == '}':
                    self.tokens.append(cur_tok)
                    cur_tok = ''
                    curly_brace_open = False

            elif square_brace_open: # []
                cur_tok += c
                if c == ']':
                    self.tokens.append(cur_tok)
                    cur_tok = ''
                    square_brace_open = False

            elif paren_open: # ()
                cur_tok += c
                if c == ')':
                    self.tokens.append(cur_tok)
                    cur_tok = ''
                    paren_open = False

            # We are not inside a brack/paren or quote 


            # elif c in OPERATORS and c not in WORD_OPERATORS:
            #   # Don't need space to seperate
            #   self.tokens.append(cur_tok)
            #   cur_tok = ''
            #   self.tokens.append(c)

            elif c == ',':
                if cur_tok != '':
                    self.tokens.append(cur_tok)
                cur_tok = ''
                self.tokens.append(c)

            elif c == ' ' or c == '\n' or c == '\r' or c == '\t':
                if cur_tok != '':
                    self.tokens.append(cur_tok)
                cur_tok = ''

            elif c == '=':
                if cur_tok != '':
                    self.tokens.append(cur_tok)
                cur_tok = ''
                self.tokens.append('=')

            elif c == '"':
                cur_tok += c
                double_quote_open = True

            elif c == '{':
                cur_tok += c
                curly_brace_open = True

            elif c == '[':
                cur_tok += c
                square_brace_open = True

            elif c == '(':
                cur_tok += c
                paren_open = True

            else:
                # c should be a normal character hopefully!?!?!?!?!?!
                cur_tok += c

        if cur_tok != '' and cur_tok != ' ': # todo: should probably figure out why theres a empty space. 
            self.tokens.append(cur_tok)

        # make a copy of self.tokens to return
        return self.tokens[:]


class Parser:
    '''
    Takes a query string and parses it.
    '''
    class Command:
        '''
        Represents a command for the storage layer to execute
        '''
        def __init__(self):

            # Attributes of the command. Not all of these are used for 
            # a specific command

            # Generic 
            self.verb = None # create, insert, select, ...
            self.collection = None # The collection to operate on

            self.invalid = False # Set to true if there is a syntax error: TODO: idk if needed

            # Insert specific
            self.insert_key_name = None # Key value for the document to be inserted
            self.json_doc = None

            # Update/upsert specific
            self.update = {} # dictionary containing the updates: eg -> 
                             # {updated_col : updated_value, ...}
            self.temp_cols = [] # Later processed to fill up self.update
            self.temp_vals = []

            # Projection - select and delete
            self.projection = [] # List of cols/expressions, or empty for *

            # Delete specific
            self.delete_collection = None # boolean. Deleting collection, or only documents inside

            # Predicate - select, delete, update/upsert
            self.predicate = None # String representation of the boolean expression

        def to_string(self):
            ret =   'verb : ' + str(self.verb) + \
                    '\ncollection : ' + str(self.collection) + \
                    '\ninvalid : ' + str(self.invalid) + \
                    '\ninsert_key_name : ' + str(self.insert_key_name) + \
                    '\njson_doc : ' + str(self.json_doc) + \
                    '\nupdate : ' + str(self.update) + \
                    '\ntemp_cols : ' + str(self.temp_cols) + \
                    '\ntemp_vals : ' + str(self.temp_vals) + \
                    '\nprojection : ' + str(self.projection) + \
                    '\ndelete_collection : ' + str(self.delete_collection) + \
                    '\npredicate : ' + str(self.predicate)
            return ret


    def __init__(self):
        self.lexer = Lexer()
        self.command = self.Command()

    def parse(self, query_str):
        '''
        Parses the query into a (todo: either object or dict, or somethign)
        representing the command for the storage layer to execute. Also
        checks for syntax errors along the way.

        input: query_str -> The docuDB language query string.
        return -> 
        '''

        self.command = self.Command() # reset command object

        tokens = self.lexer.lex(query_str)

        # TODO! can put some constraint checking (col length, ect.)
        self.__start_parse(tokens, 0)



    # All possible variations of valid syntax can be represented 
    # by a finite-sized tree.
    # The methods below each represent a node in the tree
    def __start_parse(self, token_list, idx):
        '''
        input: token_list -> List of tokens to parse
        input: idx -> Where we are in the token list
        return -> 
        '''

        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error: there is no query...'
            return 

        cur_tok = token_list[idx]

        if cur_tok == 'create':
            self.command.verb = cur_tok
            self.__create(token_list, idx + 1)
            return

        elif cur_tok == 'insert':
            self.command.verb = cur_tok
            self.__insert(token_list, idx + 1)
            return

        elif cur_tok == 'select':
            self.command.verb = cur_tok
            self.__select(token_list, idx + 1)
            return

        elif cur_tok == 'update':
            self.command.verb = cur_tok
            self.__update(token_list, idx + 1)
            return

        elif cur_tok == 'upsert':
            self.command.verb = cur_tok
            self.__upsert(token_list, idx + 1)
            return

        elif cur_tok == 'delete':
            self.command.verb = cur_tok
            self.__delete(token_list, idx + 1)
            return 

        elif cur_tok == 'drop':
            self.command.verb = cur_tok
            self.__drop(token_list, idx + 1)

        # The first token can ONLY be those 7 things above..
        else:
            self.command.invalid = True
            print 'Syntax error near: "' + cur_tok + '", '
            return 


    def __create(self, token_list, idx):

        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx - 1] + '", '
            print '    Maybe specify the collection you are trying to create.'
            return 

        cur_tok = token_list[idx]

        self.command.collection = cur_tok

        self.__create_collection(token_list, idx + 1)

    def __create_collection(self, token_list, idx):
        if not self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx] + '", '
            print '    Expected query to end after "' + token_list[idx - 1] + '"'
            return

        self.__create_end(token_list, -1)

    def __create_end(self, token_list, idx):
        print 'calling command....'
        print self.command.to_string()

        # TODO: call the storage layer 

    def __insert(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near "' + token_list[idx - 1] + '"'
            print '    Query is not expected to end after "' + token_list[idx - 1] + '" keyword'
            return 

        cur_tok = token_list[idx]
        if cur_tok != 'into':
            self.command.invalid = True 
            print 'Syntax error near "' + cur_tok + '"'
            print '    Expected to see "into" after "insert"'
            return
        else:
            self.__into(token_list, idx + 1)
            return

    def __into(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near "' + token_list[idx - 1] + '"'
            print '    Query is not expected to end after "' + token_list[idx - 1] + '" keyword'
            print '    Maybe specify the collection you are trying to insert into'
            return 

        cur_tok = token_list[idx]
        self.command.collection = cur_tok

        self.__insert_collection(token_list, idx + 1)
        return

    def __insert_collection(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near "' + token_list[idx - 1] + '"'
            print '    Query is not expected to end after "' + token_list[idx - 1] + '" keyword'
            print '    Maybe specify the key name for the document you are trying to insert'
            return

        cur_tok = token_list[idx]
        self.command.insert_key_name = cur_tok

        self.__insert_key_name(token_list, idx + 1)
        return 

    def __insert_key_name(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near "' + token_list[idx - 1] + '"'
            print '    Query is not expected to end after "' + token_list[idx - 1] + '" keyword'
            print '    Probably missing the json document to be inserted'
            return

        cur_tok = token_list[idx]

        # TODO: parse JSON
        self.command.json_doc = "TODO: NEED TO PARSE"

        self.__insert_json(token_list, idx + 1)
        return 

    def __insert_json(self, token_list, idx):
        if not self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx] + '", '
            print '    Expected query to end after "' + token_list[idx - 1] + '"'
            return 

        self.__insert_end(token_list, -1)
        return

    def __insert_end(self, token_list, idx):
        print 'calling command...'
        print self.command.to_string()

        # TODO: call the stoarage layer
        return 

    def __select(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx - 1] + '", '
            print '    Maybe missing projection specification'
            return 

        cur_tok = token_list[idx]

        if cur_tok == '*':
            self.command.projection = []
            self.__select_star(token_list, idx + 1)

        else:
            self.command.projection.append(cur_tok)
            self.__select_col_or_exp(token_list, idx + 1)

        return 

    def __select_star(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx - 1] + '", '
            print '    Probably expecting the "from" keyword'
            return 

        cur_tok = token_list[idx]

        if cur_tok != 'from':
            self.command.invalid = True 
            print 'Syntax error near "' + cur_tok + '"'
            print '    Expected to see "from" after "select *"'
            return
        else:
            self.__select_from(token_list, idx + 1)
            return 


    def __select_col_or_exp(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.__select_no_collection_end(token_list, -1)
            return

        cur_tok = token_list[idx]

        if cur_tok == ',':
            self.__select_col_or_exp_comma(token_list, idx + 1) 
            return 
        elif cur_tok == 'from':
            self.__select_from(token_list, idx + 1)
            return 
        else:
            self.command.invalid = True 
            print 'Syntax error near "' + token_list[idx - 1] + cur_tok + '"'
            print '    Probably expecting a "," or "from"'
            return 

    def __select_col_or_exp_comma(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx - 1] + '" '
            print '    Probably expecting another expression/column'
            return 

        cur_tok = token_list[idx]

        self.command.projection.append(cur_tok)
        self.__select_col_or_exp(token_list, idx + 1)

        return


    def __select_no_collection_end(self, token_list, idx):
        print 'calling command...'
        print self.command.to_string()

        # TODO: call storage layer

    def __select_from(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near "' + token_list[idx - 1] + '"'
            print '    Query is not expected to end after the "' + token_list[idx - 1] + '" keyword'
            return 

        cur_tok = token_list[idx]
        self.command.collection = cur_tok

        self.__select_collection(token_list, idx + 1)
        return 

    def __select_collection(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.__select_no_pred_end(token_list, -1)
            return 

        cur_tok = token_list[idx]

        if cur_tok == 'where':
            self.__where(token_list, idx + 1)
            return
        else:
            self.command.invalid = True 
            print 'Syntax error near "' + token_list[idx - 1] + cur_tok + '"'
            print '    Probably expecting a "where"'
            return 


    def __select_no_pred_end(self, token_list, idx):
        print 'calling command...'
        print self.command.to_string()

        # TODO CALL STORAGE LAYER

    def __where(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near "' + token_list[idx - 1] + '"'
            print '    Query is not expected to end after the "' + token_list[idx - 1] + '" keyword'
            return

        cur_tok = token_list[idx]
        self.command.predicate = cur_tok

        self.__where_exp(token_list, idx + 1)
        return 

    def __where_exp(self, token_list, idx):
        if not self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx] + '", '
            print '    Expected query to end after "' + token_list[idx - 1] + '"'
            return 

        self.__where_end(token_list, -1)


    def __where_end(self, token_list, idx):
        print 'calling command...'
        print self.command.to_string()

        # TODO: call storage layer!!!!!!


    def __update(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx - 1] + '", '
            print '    Maybe specify the collection you are trying to update.'
            return 

        cur_tok = token_list[idx]
        self.command.collection = cur_tok

        self.__update_collection(token_list, idx + 1)
        return

    def __upsert(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx - 1] + '", '
            print '    Maybe specify the collection you are trying to upsert.'
            return 

        cur_tok = token_list[idx]
        self.command.collection = cur_tok

        self.__update_collection(token_list, idx + 1)
        return

    def __update_collection(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx - 1] + '", '
            print '    Unexpected end of query. Probably expecting "set"'
            return 

        cur_tok = token_list[idx]

        if cur_tok == 'set':
            self.__set(token_list, idx + 1)
            return
        else:
            self.command.invalid = True 
            print 'Syntax error near "' + cur_tok + '"'
            print '    Expected to see "set" after <collection name>'
            return


    def __set(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx - 1] + '", '
            print '    Unexpected end of query. Probably expecting [column names]'
            return 

        cur_tok = token_list[idx]

        self.command.temp_cols = cur_tok

        self.__update_col_names(token_list, idx + 1)
        return 


    def __update_col_names(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx - 1] + '", '
            print '    Unexpected end of query. Probably expecting "="'
            return 

        cur_tok = token_list[idx]

        if cur_tok == '=':
            self.__assign(token_list, idx + 1)
            return 
        else:
            self.command.invalid = True 
            print 'Syntax error near "' + token_list[idx - 1] + cur_tok + '"'
            print '    Expected to see "="'
            return


    def __assign(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx - 1] + '", '
            print '    Unexpected end of query. Probably expecting a values list'
            return         

        cur_tok = token_list[idx]

        self.command.temp_vals = cur_tok

        self.__update_vals(token_list, idx + 1)
        return 


    def __update_vals(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.__update_no_pred_end(token_list, -1)
            return

        cur_tok = token_list[idx]

        if cur_tok == 'where':
            self.__where(token_list, idx + 1)
            return
        else:
            self.command.invalid = True 
            print 'Syntax error near "' + token_list[idx - 1] + cur_tok + '"'
            print '    Expected to see end of query or "where"'
            return

    def __update_no_pred_end(self, token_list, idx):
        print 'calling command...'
        print self.command.to_string()

        #TODO: call stoarl layersrrrrrrrrrrr 

    def __delete(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx - 1] + '", '
            print '    Maybe missing projection specification'
            return 

        cur_tok = token_list[idx]

        if cur_tok == '*':
            self.command.projection = []
            self.__delete_star(token_list, idx + 1)
            return 

        else:
            self.command.projection.append(cur_tok)
            self.__delete_cols(token_list, idx + 1)


    def __delete_star(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx - 1] + '", '
            print '    Probably expecting the "from" keyword'
            return 

        cur_tok = token_list[idx]

        if cur_tok != 'from':
            self.command.invalid = True 
            print 'Syntax error near "' + cur_tok + '"'
            print '    Expected to see "from" after "delete *"'
            return
        else:
            self.__delete_from(token_list, idx + 1)
            return


    def __delete_cols(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx - 1] + '", '
            print '    Unexpected end of query. Probably expecting the "from" keyword or a comma'
            return

        cur_tok = token_list[idx]

        if cur_tok == ',':
            self.__delete_commas(token_list, idx + 1)
            return
        elif cur_tok == 'from':
            self.__delete_from(token_list, idx + 1)
            return
        else:
            self.command.invalid = True 
            print 'Syntax error near "' + token_list[idx - 1] + cur_tok + '"'
            print '    Probably expecting a "," or "from"'
            return 


    def __delete_commas(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx - 1] + '" '
            print '    Probably expecting another column'
            return 

        cur_tok = token_list[idx]

        self.command.projection.append(cur_tok)
        self.__delete_cols(token_list, idx + 1)
        return 

    def __delete_from(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near "' + token_list[idx - 1] + '"'
            print '    Query is not expected to end after the "' + token_list[idx - 1] + '" keyword'
            return 

        cur_tok = token_list[idx]

        self.command.collection = cur_tok

        self.__delete_collection(token_list, idx + 1)
        return 

    def __delete_collection(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.__delete_no_pred_end(token_list, -1)
            return

        cur_tok = token_list[idx]

        if cur_tok == 'where':
            self.__where(token_list, idx + 1)
            return
        else:
            self.command.invalid = True 
            print 'Syntax error near "' + token_list[idx - 1] + cur_tok + '"'
            print '    Probably expecting a "where"'
            return 

    def __delete_no_pred_end(self, token_list, idx):
        print 'calling command...'
        print self.command.to_string()

        # TODO: call storage layer

    def __drop(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx - 1] + '", '
            print '    Maybe specify the collection you are trying to drop.'
            return 

        cur_tok = token_list[idx]

        self.command.collection = cur_tok

        self.__drop_collection(token_list, idx + 1)

        return 

    def __drop_collection(self, token_list, idx):
        if not self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx] + '", '
            print '    Expected query to end after "' + token_list[idx - 1] + '"'
            return

        self.__drop_end(token_list, idx + 1)

    def __drop_end(self, token_list, idx):
        print 'calling command ...'
        print self.command.to_string()

        # TODO: connect to dtorage layer


    # Helper functions

    def __at_invalid_idx(self, token_list, idx):
        '''
        True if idx is out of bounds
        '''
        return len(token_list) <= idx

    def __tokens_to_str(self, token_list):
        ret = ''
        for t in token_list:
            ret += t
            ret += ' '
        return ret


#### FOR TESTING
if __name__ == "__main__":
    # print 'hello motherfucker\n'
    print 'hello good gentleman\n'

    test_ins = 'create people'

    test_ins1 = 'insert into people "john little" {age: 3, salary: 0}'
    test_ins2 = 'insert into people "john cena" {age: 40, salary: 1000000}'

    test_sel = 'select     _key, (age * salary) from people where (_key == "john cena")'

    test_update = 'update people set [salary] =[5] where (salary == 0)'

    test_delete = 'delete * from people where (age == 3)'



    # ----------------------
    test_sel2 = 'select     col1, (col3 + col 44) from collection1 where \
                ("col1" == col1 and col5 == col4 and col5 in [1,3,"doggo"])'


    # For testing 

    def plist(lst):
        for thing in lst:
            print thing

    lexy = Lexer()

    # print lexy.lex(test_ins1)

    plist(lexy.lex(test_ins))
    print ''
    plist(lexy.lex(test_ins1))
    print ''
    plist(lexy.lex(test_ins2))
    print ''
    plist(lexy.lex(test_sel))
    print ''
    plist(lexy.lex(test_update))
    print ''
    plist(lexy.lex(test_delete))
    print ''

    plist(lexy.lex(test_sel2))


