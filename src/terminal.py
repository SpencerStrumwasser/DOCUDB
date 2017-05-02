import parser


print 'Hello. Welcome to the DocuDB Terminal...'

p = parser.Parser()

while(True):


	user_input = raw_input('ddb> ')

	if user_input == 'exit' or user_input == 'quit':
		print 'Goodbye, come again!'
		break
	elif user_input == 'gtfo':
		print 'WOW! that was rude.. Bye.'
		break
	
	elif user_input != '':
		p.parse(user_input)


