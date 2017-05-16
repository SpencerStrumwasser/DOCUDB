

'''
Example predicates

	(5 == 90)

	(col1 == "hello")
	(col1 == 1)
	(col1 == 1.1)
	(col1 == True)

	(True = col1) -- value can come before column reference

	(col1 = 1 and col4 = "jello")
	(col1 = 1 or col4 = "jello")
	(col1 = 1 or col4 = "jello" and ...)

	(col1 in [1,2,3,4,...])

	(col1 = "col1") -- strings that have the same name as a column should NOT cause a problem



'''


def eval_pred(exp, cols):
	'''
	Takes a predicate boolean expression and the column values for a particular document(row) 
	and evaluates to true or false.

	Evaluated with Python's eval function: so the boolean expression must be valid python
	syntax.

	** I think eval() has no side effects when run with global and local variables supplied.
		TODO: One possibility is if the user supplied a python function in the predicate...
	'''

	# TODO: add exception handling and security checks
	if exp == '' or exp == None:
		return True
	return eval(exp, {}, cols)






# For testing
if __name__ == '__main__':
	exp1 = '(5 == 90)'
	vals1 = {}

	exp2 = '(col1 == "hello")'
	exp3 = '(col1 == 1)'
	exp4 = '(col1 == 1.1)'
	exp5 = '(col1 == True)'
	vals2 = {'col1' : 'hello'}
	vals3 = {'col1' : 1}
	vals4 = {'col1' : 1.1}
	vals5 = {'col1' : True}

	exp6 = '(True == col1)'

	exp7 = '(col1 = 1 and col4 = "jello")'
	exp8 = '(col1 = 1 or col4 = "jello")'
	exp9 = '(col1 = 1 or col4 = "jello" and True)'

	exp10 = '(col1 in [1,2,3,4])'

	exp11 = '(col1 == "col1") '


	print False == eval_pred(exp1, vals1)
	print True == eval_pred(exp2, vals2)
	print False == eval_pred(exp2, vals3)
	print False == eval_pred(exp11, vals2)
	print True == eval_pred(exp11, {'col1' : 'col1'})


