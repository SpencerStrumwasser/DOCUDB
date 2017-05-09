import myparser



print 'Hello. Welcome to the DocuDB Terminal...'

p = myparser.Parser()

while(True):


	user_input = raw_input('ddb> ')

	if user_input == 'exit' or user_input == 'quit':
		print 'Goodbye, come again!'
		break
	elif user_input == 'EXIT' or user_input == 'QUIT':
		print 'Goodbye, come again!'.upper()
		break
	elif user_input == 'hello':
		print 'Hi'	
	elif user_input != '':
		if user_input[0] == '-' and user_input[1] == '-':
			pass  # comment
		else:
			p.parse(user_input)


