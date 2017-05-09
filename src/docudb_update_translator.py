from keywords import LANGUAGE_KEYWORDS
from keywords import OPERATORS
from keywords import WORD_OPERATORS

from csv import reader 

INT_SIZE = 4 # from storage layer. TODO: put this in one unified place

'''
TODO: write

'''

def strlists_to_dict(cols_str, vals_str):
	cols = [] # Column names
	for line in reader(cols_str):
		cols.append(line)




if __name__ == '__main__':

	col_str1 = '[col1, col2, col3]'

	col_str2= '[col1, col2, col3]'