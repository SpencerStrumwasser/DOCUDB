
'''
Reserved keywords in the DocuDB query language
'''


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
                        'drop',
                        '_key'
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
