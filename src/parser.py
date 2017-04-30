

LANGUAGE_KEYWORDS = set(
					[	'insert',
						'into',
						'select',
						'from',
						'where',
						'update',
						'set',
						'upsert',
						'delete',
						'create'
					])

# TODO: in the future, might have to seperate arithmetic, comparison, 
OPERATORS = set(
				[
				'+',	# Arithmetic
				'-',
				'*',
				'/',
				'%',
				'**',
				'==',	# Comparison
				'>',
				'<',
				'>=',
				'<=',
				'!=',
				'in',
				'and',	# Logical
				'or',
				'not',
				'='		# Assignment
				])

# These operators require a space between values, whereas 
# other operators do not: eg 1+1 is ok. trueandtrue is not.
WORD_OPERATORS = set(
				[
				'in',
				'and',	# Logical
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
		'''

		# Empty tokens list
		if len(self.tokens) != 0:
			self.tokens[:] = []

		double_quote_open = False
		curly_brace_open = False
		square_brace_open = False
		paren_open = False

		# OPERATORS
		# WORD_OPERATORS

		cur_tok = ''
		for c in query_str:
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
			# 	# Don't need space to seperate
			# 	self.tokens.append(cur_tok)
			# 	cur_tok = ''
			# 	self.tokens.append(c)

			elif c == ',':
				if cur_tok != '':
					self.tokens.append(cur_tok)
				cur_tok = ''
				self.tokens.append(c)

			elif c == ' ':
				if cur_tok != '':
					self.tokens.append(cur_tok)
				cur_tok = ''

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

	def __init__(self):
		pass





# print 'hello motherfucker\n'
print 'hello good gentleman\n'


test_ins1 = 'insert into people "john little" {age: 3, salary: 0}'
test_ins2 = 'insert into people "john cena" {age: 40, salary: 1000000}'

tets_sel = 'select     col1, (col3 + col 44) from collection1 where ("col1" == col1 and col5 == col4 and col5 in [1,3,"doggo"])'


def plist(lst):
	for thing in lst:
		print thing

lexy = Lexer()

# print lexy.lex(test_ins1)

plist(lexy.lex(test_ins1))
print ''
plist(lexy.lex(test_ins2))
print ''
plist(lexy.lex(tets_sel))


