import document
from document import DocumentData
from storage_layer import StorageLayer

import docudb_json_translator
import docudb_update_translator
import predicate_evaluator
from keywords import LANGUAGE_KEYWORDS
from keywords import OPERATORS
from keywords import WORD_OPERATORS




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
        curly_brace_open = 0 # there can be nested parens 
        square_brace_open = 0 # there can be nested parens
        paren_open = 0 # counts number of (, since there can be nested parens


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

            elif curly_brace_open > 0: # {}
                cur_tok += c
                if c == '}':
                    curly_brace_open -= 1
                    if curly_brace_open == 0:
                        self.tokens.append(cur_tok)
                        cur_tok = ''
                elif c == '{':
                    curly_brace_open += 1


            elif square_brace_open > 0: # []
                cur_tok += c
                if c == ']':
                    square_brace_open -= 1
                    if square_brace_open == 0:
                        self.tokens.append(cur_tok)
                        cur_tok = ''
                elif c == '[':
                    square_brace_open += 1

            elif paren_open > 0: # ()
                cur_tok += c
                if c == ')':
                    paren_open -= 1
                    if paren_open == 0:
                        self.tokens.append(cur_tok)
                        cur_tok = ''

                elif c == '(':
                    paren_open += 1

  

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
                curly_brace_open += 1

            elif c == '[':
                cur_tok += c
                square_brace_open += 1

            elif c == '(':
                cur_tok += c
                paren_open += 1

            else:
                # c should be a normal character hopefully!?!?!?!?!?!
                cur_tok += c

        if cur_tok != '' and cur_tok != ' ': # todo: should probably figure out why theres a empty space. 
            self.tokens.append(cur_tok)


        if double_quote_open == True:
            print 'Syntax Error: unclosed double quote'
            return None

        if curly_brace_open != 0:
            print 'Syntax Error: unclosed curly brace'
            return None        

        if square_brace_open != 0:
            print 'Syntax Error: unclosed square bracket'
            return None  

        if paren_open != 0:
            print 'Syntax Error: mismatching parenthesis'
            return None  

        # make a copy of self.tokens to return
        return self.tokens[:]


class Parser:
    '''
    Takes a query string and parses it.
    '''
    class Command:
        '''
        Represents a command for the storage layer to execute

        Note: Our use of 'json' here is not official json. It is based on json,
        but has slightly different details (syntax and data types)

        '''
        def __init__(self):

            # Attributes of the command. Not all of these are used for 
            # a specific command

            # Generic 
            self.verb = None # create, insert, select, update, upsert, delete, drop
            self.collection = None # The collection to operate on

            self.invalid = False # Set to true if there is a syntax error: TODO: idk if needed

            # Insert specific
            self.insert_key_name = None # Key value for the document to be inserted
            self.json_doc = None

            # Update/upsert specific
            self.update = {} # dictionary containing the updates: eg -> 
                             # {updated_col : updated_value, ...}
            self.temp_cols = None # Later processed to fill up self.update
            self.temp_vals = None

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
        Parses the query into a Command (nested class in Parser) object
        representing the command for the storage layer to execute. Also
        checks for syntax errors along the way.

        input: query_str -> The docuDB language query string.
        return -> 
        '''

        self.command = self.Command() # reset command object

        tokens = self.lexer.lex(query_str)

        if tokens != None:
            self.__start_parse(tokens, 0)
        else:
            # print 'empty queries should not get here.'
            return 

        if self.command.invalid == True:
            print 'Syntax Error'
            return 

        ## todo: before calling storage layer, check if self.command.invalid == True
        # todo call storage layer? 
        self.__process_cmd()
        self.__call_storage_layer()



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
            if cur_tok.lower() in LANGUAGE_KEYWORDS:
                print '    Hint: all keywords must be lowercase'
            return 


    def __create(self, token_list, idx):

        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx - 1] + '" '
            print '    Maybe specify the collection you are trying to create.'
            return 

        cur_tok = token_list[idx]

        self.command.collection = cur_tok

        self.__create_collection(token_list, idx + 1)

    def __create_collection(self, token_list, idx):
        if not self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx] + '" '
            print '    Expected query to end after "' + token_list[idx - 1] + '"'
            return

        self.__create_end(token_list, -1)

    def __create_end(self, token_list, idx):

        # print 'calling command....'
        # print self.command.to_string()

        return



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
        if cur_tok[0] != '"' or len(cur_tok) < 2:
            self.command.invalid = True
            print 'Syntax error near "' + cur_tok + '"'
            print '    _key can only be a string '
            return
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

        # String form of json. Will parse into dict later
        self.command.json_doc = cur_tok

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

        # print 'calling command...'
        # print self.command.to_string()

        return 

    def __select(self, token_list, idx):
        if self.__at_invalid_idx(token_list, idx):
            self.command.invalid = True 
            print 'Syntax error near: "' + token_list[idx - 1] + '" '
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
            print 'Syntax error near: "' + token_list[idx - 1] + '" '
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
            print 'Syntax error near "' + token_list[idx - 1] + ' ' + cur_tok + '"'
            print '    Maybe expecting a "," or "from"'

            if cur_tok in OPERATORS:
                print '    Hint: expressions should be enclosed in () for correct parsing. eg: (col1 + 1), not col1 + 1'

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

        # print 'calling command...'
        # print self.command.to_string()

        return


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

        # print 'calling command...'
        # print self.command.to_string()

        return 

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
            print 'Syntax error near: "' + token_list[idx] + '" '
            print '    Expected query to end after "' + token_list[idx - 1] + '"'

            if token_list[idx] in OPERATORS:
                print '    Hint: expressions should be enclosed in () for correct parsing. eg: (col1 + 1), not col1 + 1'

            return 

        self.__where_end(token_list, -1)


    def __where_end(self, token_list, idx):

        # print 'calling command...'
        # print self.command.to_string()

        return

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

        # print 'calling command...'
        # print self.command.to_string()

        return

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

        # print 'calling command...'
        # print self.command.to_string()

        return 

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
        return


    def __process_cmd(self):
        '''
        Called after __start_parse. Does additional processing to prepare the 
        command for execution

        Gets the command.json_doc or command.update attributes ready 
        Also checks for language constraint violations

        * Column name constraints for insert are checked in docudb_json_translator/docudb_update_translator
        '''

        # todo delete
        # print '__process_cmd() called'
        # print ''
        # #

        # Process self.command.json_doc if necessary - insert
        if self.command.verb == 'insert':
            ins_dict = docudb_json_translator.json_to_dict(self.command.json_doc)  
            if len(ins_dict) != 0: # len0 signals that an error has occured 
                self.command.json_doc = ins_dict
            else:
                self.command.invalid = True
                print 'Error in json parse' # todo delete
                return 

            # todo delete
            print 'the insert json:'
            print self.command.json_doc
            print ''
            #

        # Process self.command.update if necessary - update/upsert
        if self.command.verb == 'update' or self.command.verb == 'upsert':
             #  {'update_dict' : update_dict, 'cols' : cols, 'vals' : vals}
            upd_dict = docudb_update_translator.strlists_to_dict(self.command.temp_cols, self.command.temp_vals)
            if len(upd_dict['update_dict']) != 0: # len 0 signals an error occurred 
                self.command.update = upd_dict['update_dict']
                self.command.temp_cols = upd_dict['cols']
                self.command.temp_vals = upd_dict['vals']
            else:
                self.command.invalid = True
                print 'Error in update format'
                return 

            # todo delete
            print 'the update dict:'
            print self.command.update
            print ''
            #

        # TODO: probably cannot check this
        # All expressions with 2 or more elements enclosed with ()
        

        # Key:
        #   - only strings -> enclosed by quotes 
        #   - max length == 30
        #   - cannot be a language keyword or operator
        if self.command.verb == 'insert':
            if self.command.insert_key_name[0] != '"' or self.command.insert_key_name [-1] != '"':
                print 'Syntax Error: Key should be enclosed by quotes: ' + str(self.command.insert_key_name)
                self.command.invalid = True
                return            
            self.command.insert_key_name = self.command.insert_key_name[1:-1] # strip quotes
            if self.command.insert_key_name in LANGUAGE_KEYWORDS.union(WORD_OPERATORS):
                print 'Syntax Error: Key cannot be a keyword or operator: ' + str(self.command.insert_key_name)
                self.command.invalid = True
                return
            if len(self.command.insert_key_name) >= 30 or len(self.command.insert_key_name) == 0:
                print 'Syntax Error: Key must be at least 1 and max 30 chars long: ' + str(self.command.insert_key_name)
                self.command.invalid = True
                return            



        # Collection names:
        #   - todo: define length constraint
        #   - only consists of alpha-numeric and '_'
        #   - has to start with a-z
        #   - cannot be a language keyword or operator, or '_key'
        if len(self.command.collection) == 0:
            print 'Parsing Error: Collection with empty name'
            self.command.invalid = True
            return
        for ch in self.command.collection:
            if not ch.isalnum() and ch != '_':
                print 'Syntax Error: Collection names can only contain A-Z, a-z, 0-9, and _'
                self.command.invalid = True
                return
        if not self.command.collection[0].isalpha():
            print 'Syntax Error: Collection names must start with alphabetical char.'
            self.command.invalid = True
            return 
        if self.command.collection in LANGUAGE_KEYWORDS.union(WORD_OPERATORS):
            print 'Syntax Error: Collection name cannot be a keyword or operator: ' + str(self.command.collection)
            self.command.invalid = True
            return

        # todo. there are probably  other constraints... esp semantic ones
        
        # print self.command.to_string()
        
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


    ######################################################################
    ######################################################################
    ######################################################################
    #     EXECUTE IN STORAGE LAYER
    ######################################################################
    ######################################################################
    ######################################################################
    def __create_embedded_doc(self, columns):

        file_to_insert = DocumentData(0,0, columns[_key])
        memory_needed = 0
        for key, value in columns.iteritems():
            insert_key = str(key)
            col_size = len(str(key))
            memory_needed += col_size + 4
            if isinstance(value, (str,str)):
                value_size = len(value)
                file_to_insert.add_value(insert_key, col_size, 4, value_size, value)
                memory_needed += 1 + value_size + 4
            elif isinstance(value, str):
                value_size = len(value)
                file_to_insert.add_value(insert_key, col_size, 2, value_size, value)
                memory_needed += 1 + value_size + 4
            elif isinstance(value, bool):
                file_to_insert.add_value(insert_key, col_size, 3, 1, value)
                memory_needed += 1 + 4 + 1
            elif isinstance(value, int):
                file_to_insert.add_value(insert_key, col_size, 0, 4, value)
                memory_needed += 1 + 4 + 4
            elif isinstance(value, float):
                value_size = len(str(value))
                file_to_insert.add_value(insert_key, col_size, 1, value_size, str(value))
                memory_needed += 1 + value_size + 4
            elif isinstance(value, dict):
                embed_doc = self.__create_embedded_doc(value)
                value_size = embed_doc.allocated_size
                file_to_insert.add_value(insert_key, col_size, 5, value_size, embed_doc)
                memory_needed += 1 + value_size + 4
        for ite in range(10, 25):
            if (memory_needed < 2**ite):
                break
        file_to_insert.allocated_size = 2**ite-1
        # print file_to_insert.allocated_size
        return file_to_insert








    def __insert_storage_layer(self, filename):

        sl = StorageLayer(filename)
        print self.command.insert_key_name
        file_to_insert = DocumentData(0,0, self.command.insert_key_name)
        memory_needed = 0
        columns = self.command.json_doc
        for key, value in columns.iteritems():
            insert_key = str(key)
            col_size = len(str(key))
            memory_needed += col_size + 4
            if isinstance(value, (str,str)):
                value_size = len(value)
                file_to_insert.add_value(insert_key, col_size, 4, value_size, value)
                memory_needed += 1 + value_size + 4
            elif isinstance(value, str):
                value_size = len(value)
                file_to_insert.add_value(insert_key, col_size, 2, value_size, value)
                memory_needed += 1 + value_size + 4
            elif isinstance(value, bool):
                file_to_insert.add_value(insert_key, col_size, 3, 1, value)
                memory_needed += 1 + 4 + 1
            elif isinstance(value, int):
                file_to_insert.add_value(insert_key, col_size, 0, 4, value)
                memory_needed += 1 + 4 + 4
            elif isinstance(value, float):
                value_size = len(str(value))
                file_to_insert.add_value(insert_key, col_size, 1, value_size, str(value))
                memory_needed += 1 + value_size + 4
            elif isinstance(value, dict):
                embed_doc = self.__create_embedded_doc(value)
                value_size = embed_doc.allocated_size
                file_to_insert.add_value(insert_key, col_size, 5, value_size, embed_doc)
                memory_needed += 1 + value_size + 4
        for ite in range(10, 25):
            if (memory_needed < 2**ite):
                break
        file_to_insert.allocated_size = 2**ite-1
        # print file_to_insert.allocated_size
        sl.write_data_to_memory(sl.search_memory_for_free(file_to_insert), file_to_insert)



    def __print_select(self, gettt):
        if gettt == False:
            print "No Documents Exists"
        else:
            proj = self.command.projection
            if proj == []:
                print "\n \n Documents Selected: \n"
                for dicc in gettt:
                    print "---------------------------------------------------------------"
                    print "Document Key:" , dicc['_key']
                    for key in dicc:
                        if key == '_key':
                            continue
                        else: 
                            print key, " : ", dicc[key]
                    print '\n \n'
            else:
                print "\n \n Documents Selected: \n"
                for dicc in gettt:
                    print "---------------------------------------------------------------"
                    print "Document Key:" , dicc['_key']
                    for item in proj:
                        if item != "_key":
                            try:
                                print item, " : ", dicc[item]
                            except KeyError:
                                try:
                                    print predicate_evaluator.eval_pred(item, dicc)
                                except NameError:
                                    print "Projection", item, "is not possible"

                    print '\n \n'


    def __select_storage_layer(self, filename):

        sl = StorageLayer(filename)
        if self.command.predicate == None:
            print 'Finding All Documents'
            gettt = sl.get_all_tuples(self.command.predicate)
            self.__print_select(gettt)


            return
        # elif self.command.predicate[:9] == "(_key == ":
        #     if self.command.predicate.count('"', 0, len(self.command.predicate)) == 2:
        #         for i in range(10, len(self.command.predicate)):
        #             if self.command.predicate[i:i+1] == '"' :
        #                 key_val = self.command.predicate[10:i]
        #                 print "Finding Document for Key: " + key_val
        #                 gettt = sl.get_tuples_by_key([key_val.lower()])
        #                 self.__print_select(gettt)
    
        print "Finding Document for predicate: " + self.command.predicate
        gettt = sl.get_all_tuples(self.command.predicate)
        self.__print_select(gettt)


    def __update_storage_layer(self, filename):

        sl = StorageLayer(filename)
        if self.command.predicate == None:
            print "Updating All Documents"
            sl.update_by_predicate(self.command.predicate, self.command.temp_cols, self.command.temp_vals, 0)
            return
        # elif self.command.predicate[:9] == "(_key == ":
        #     if self.command.predicate.count('"', 0, len(self.command.predicate)) == 2:
        #         for i in range(10, len(self.command.predicate)):
        #             if self.command.predicate[i:i+1] == '"' :
        #                 key_val = self.command.predicate[10:i]
        #                 print "Updating Document for Key: " + key_val

        #                 sl.update_by_keys([key_val.lower()], self.command.temp_cols, self.command.temp_vals, 0)
        #                 return
        print "Updating All Documents Satisfying Predicate" , self.command.predicate
        sl.update_by_predicate(self.command.predicate, self.command.temp_cols, self.command.temp_vals, 0)
            

    def __upsert_storage_layer(self, filename):

        sl = StorageLayer(filename)
        if self.command.predicate == None:
            print "Upserting All Documents"
            sl.update_by_predicate(self.command.predicate, self.command.temp_cols, self.command.temp_vals, 1)
            return
        # elif self.command.predicate[:9] == "(_key == ":
        #     if self.command.predicate.count('"', 0, len(self.command.predicate)) == 2:
        #         for i in range(10, len(self.command.predicate)):
        #             if self.command.predicate[i:i+1] == '"' :
        #                 key_val = self.command.predicate[10:i]
        #                 print "Upseting Document for Key: " + key_val

        #                 sl.update_by_keys([key_val.lower()], self.command.temp_cols, self.command.temp_vals, 1)
        #                 return
        print "Upserting All Documents Satisfying Predicate" , self.command.predicate
        sl.update_by_predicate(self.command.predicate, self.command.temp_cols, self.command.temp_vals, 1)
    

    def __delete_storage_layer(self, filename):

        sl = StorageLayer(filename)
        if self.command.predicate == None:
             print "Deleting all documents"
             sl.delete_by_predicate(self.command.predicate)
             return
        # elif self.command.predicate[:9] == "(_key == ":
        #     if self.command.predicate.count('"', 0, len(self.command.predicate)) == 2:
        #         for i in range(10, len(self.command.predicate)):
        #             if self.command.predicate[i:i+1] == '"' :
        #                 key_val = self.command.predicate[10:i]
        #                 print "Deleting Document for Key: " + key_val
        #                 sl.delete_by_keys([key_val.lower()])
        #                 return

        print "Deleting All Documents Satisfying Predicate", self.command.predicate
        sl.delete_by_predicate(self.command.predicate)
 
    def __drop_storage_layer(self, filename):
        sl = StorageLayer(filename)
        sl.drop_table()



    # Accessing storage layer
    def __call_storage_layer(self):
        '''
        This will convert a command to a call on the storage layer
        '''
        if (self.command.invalid == True):
            return False

        verb = self.command.verb
        filename = "../data/" + str(self.command.collection) + ".es"

        if verb == 'create':
            with open(filename, 'wb') as f:
                f.close()

        # Check if colleciton exists
        sl = StorageLayer(filename)
        if sl.no_file == True:
            return False


        if verb == 'insert':
            self.__insert_storage_layer(filename)
        elif verb == 'select':
            self.__select_storage_layer(filename)
        elif verb == 'update':
            self.__update_storage_layer(filename)
        elif verb == 'upsert':
            self.__upsert_storage_layer(filename)
        elif verb == 'delete':
            self.__delete_storage_layer(filename)
        elif verb == 'drop':
            self.__drop_storage_layer(filename)


        return True
            




    # def __process_cmd(self):
    #     '''
    #     Called after __start_parse. Does additional processing to prepare the 
    #     command for execution

    #     Gets the command.json_doc or command.update attributes ready 
    #     Also checks for language constraint violations

    #     * Column name constraints for insert are checked in docudb_json_translator/docudb_update_translator
    #     '''

    #     # todo delete
    #     # print '__process_cmd() called'
    #     # print ''
    #     # #

    #     # Process self.command.json_doc if necessary - insert
    #     if self.command.verb == 'insert':
    #         ins_dict = docudb_json_translator.json_to_dict(self.command.json_doc)  
    #         if len(ins_dict) != 0: # len0 signals that an error has occured 
    #             self.command.json_doc = ins_dict
    #         else:
    #             self.command.invalid = True
    #             print 'Error in json parse' # todo delete
    #             return 

    #         # todo delete
    #         print 'the insert json:'
    #         print self.command.json_doc
    #         print ''
    #         #

    #     # Process self.command.update if necessary - update/upsert
    #     if self.command.verb == 'update' or self.command.verb == 'upsert':
    #          #  {'update_dict' : update_dict, 'cols' : cols, 'vals' : vals}
    #         upd_dict = docudb_update_translator.strlists_to_dict(self.command.temp_cols, self.command.temp_vals)
    #         if len(upd_dict['update_dict']) != 0: # len 0 signals an error occurred 
    #             self.command.update = upd_dict['update_dict']
    #             self.command.temp_cols = upd_dict['cols']
    #             self.command.temp_vals = upd_dict['vals']
    #         else:
    #             self.command.invalid = True
    #             print 'Error in update format'
    #             return 

    #         # todo delete
    #         print 'the update dict:'
    #         print self.command.update
    #         print ''
    #         #

    #     # TODO: probably cannot check this
    #     # All expressions with 2 or more elements enclosed with ()
        

    #     # Key:
    #     #   - only strings -> enclosed by quotes 
    #     #   - max length == 30
    #     #   - cannot be a language keyword or operator
    #     if self.command.verb == 'insert':
    #         if self.command.insert_key_name[0] != '"' or self.command.insert_key_name [-1] != '"':
    #             print 'Syntax Error: Key should be enclosed by quotes: ' + str(self.command.insert_key_name)
    #             self.command.invalid = True
    #             return            
    #         self.command.insert_key_name = self.command.insert_key_name[1:-1] # strip quotes
    #         if self.command.insert_key_name in LANGUAGE_KEYWORDS.union(WORD_OPERATORS):
    #             print 'Syntax Error: Key cannot be a keyword or operator: ' + str(self.command.insert_key_name)
    #             self.command.invalid = True
    #             return
    #         if len(self.command.insert_key_name) >= 30 or len(self.command.insert_key_name) == 0:
    #             print 'Syntax Error: Key must be at least 1 and max 30 chars long: ' + str(self.command.insert_key_name)
    #             self.command.invalid = True
    #             return            



    #     # Collection names:
    #     #   - todo: define length constraint
    #     #   - only consists of alpha-numeric and '_'
    #     #   - has to start with a-z
    #     #   - cannot be a language keyword or operator, or '_key'
    #     if len(self.command.collection) == 0:
    #         print 'Parsing Error: Collection with empty name'
    #         self.command.invalid = True
    #         return
    #     for ch in self.command.collection:
    #         if not ch.isalnum() and ch != '_':
    #             print 'Syntax Error: Collection names can only contain A-Z, a-z, 0-9, and _'
    #             self.command.invalid = True
    #             return
    #     if not self.command.collection[0].isalpha():
    #         print 'Syntax Error: Collection names must start with alphabetical char.'
    #         self.command.invalid = True
    #         return 
    #     if self.command.collection in LANGUAGE_KEYWORDS.union(WORD_OPERATORS):
    #         print 'Syntax Error: Collection name cannot be a keyword or operator: ' + str(self.command.collection)
    #         self.command.invalid = True
    #         return

    #     # todo. there are probably  other constraints... esp semantic ones

    #     # print self.command.to_string()
        
    # # Helper functions

    # def __at_invalid_idx(self, token_list, idx):
    #     '''
    #     True if idx is out of bounds
    #     '''
    #     return len(token_list) <= idx

    # def __tokens_to_str(self, token_list):
    #     ret = ''
    #     for t in token_list:
    #         ret += t
    #         ret += ' '
    #     return ret


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

    # plist(lexy.lex(test_ins))
    # print ''
    # plist(lexy.lex(test_ins1))
    # print ''
    # plist(lexy.lex(test_ins2))
    # print ''
    # plist(lexy.lex(test_sel))
    # print ''
    # plist(lexy.lex(test_update))
    # print ''
    # plist(lexy.lex(test_delete))
    # print ''

    # plist(lexy.lex(test_sel2))

    test_emb1 = 'insert into c_emb "id1" {name: "joe", child : {_key : "sid1", name : "Jonny", age : 3}, pay : 90000} '
    test_emb2 = 'insert into c_emb "id2" {name: "dick", child : <c_emb, child1>, pay : 90000} '
    test_emb3 = 'insert into c_emb "id3" {name: "joe", children: : [{_key : "sid1", name : "Jonny", age : 3}, {_key : "sid2", name : "Jon", age : 6}], pay : 90000} '

    plist(lexy.lex(test_emb1))
    print ''
    plist(lexy.lex(test_emb2))
    print ''
    plist(lexy.lex(test_emb3))

