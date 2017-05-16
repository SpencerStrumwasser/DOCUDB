
class DocumentData:
	'''
	Represents how the document is being stored in the database. Stores both 
	document data and metadata.

	| 1B - filled flag | 4B - space allocated for row | 4B - space filled in row | 30B - Key_name|
	| 1B - col name length | 1~255B - col name | 1B - value type | 4B - value size| ?B - value|
	'''

	class ValueData:
		'''
		Encapsulates the data needed to store a col-val pair in a document
		'''
		def __init__(self, col_name_len, val_type, val_size, val):
			self.col_name_len = col_name_len
			self.val_type = val_type
			self.val_size = val_size
			self.val = val

		def __str__(self):
			return 'col_name_len: ' + str(self.col_name_len) + ', val_type: ' + str(self.val_type) + ', val_size: ' + str(self.val_size) + ', val: ' + str(self.val)

	def __init__(self, allocated_size, filled_size, key_name):
		self.allocated_size = allocated_size
		self.filled_size = filled_size
		self.key_name = key_name
		self.values = {}
		self.user_values_dict = {} # just the values for display. no storage layer info
		self.values_order = None # TODO1: implement later

	def add_value(self, col_name, col_name_len, val_type, val_size, val):
		self.values[col_name] = self.ValueData(col_name_len, val_type, val_size, val)
		self.user_values_dict[col_name] = val


class DocumentPresentation:
	'''
	Document that is presented to user. Does not include storage level data.
	'''

	def __init__(self, key):
		self.key = key
		self.values = {}
		self.values_order = None # TODO1: implement later


	def add_value(self, col_name, value):
		self.values[col_name] = value


	def alter_order():
		raise NotImplementedError('implement later')



