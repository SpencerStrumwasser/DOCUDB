import myparser
import os

# TODO: repeated in storage layer: consolidate
ROOT_DATA_DIRECTORY = '../data' # Where the tables at


print 'Hello. Welcome to the DocuDB Terminal...'

p = myparser.Parser()
os.system('')
while(True):


	user_input = raw_input('ddb> ')

	if user_input == 'exit' or user_input == 'quit' or user_input == 'bye':
		print 'Goodbye, come again!'
		break
	elif user_input == 'EXIT' or user_input == 'QUIT':
		print 'Goodbye, come again!'.upper()
		break	
	elif user_input == 'hello':
		print 'Hi'	

	elif user_input == 'show collections' or user_input == 'ls':
		files = os.listdir(ROOT_DATA_DIRECTORY)
		for f in files:
			print '\t' + f[:-3] # strip the .es file extension

	elif user_input != '':
		if user_input[0] == '-' and user_input[1] == '-':
			pass  # comment
		else:
			p.parse(user_input)


