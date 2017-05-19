import myparser
import os

# TODO: repeated in storage layer: consolidate
ROOT_DATA_DIRECTORY = '../data' # Where the tables at


print 'Hello. Welcome to the DocuDB Terminal...'

p = myparser.Parser()

with open('demodb.txt', 'r') as f:
	for user_input in f:
		if user_input[0] == '-' and user_input[1] == '-':
			pass  # comment
		else:
			p.parse(user_input)



