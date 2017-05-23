
class ListData:
	'''
	Represents how a List is being stored in the database. Stores both 
	List data and metadata.

	| 1B - filled flag | 4B - space allocated for row | 4B - space filled in row |
	| 1B - value type | 4B - value size| ?B - value|
	'''

	class ValueData:
		'''
		Encapsulates the data needed to store a col-val pair in a document
		'''
		def __init__(self, col_name_len, val_type, val_size, val):
			self.val_type = val_type
			self.val_size = val_size
			self.val = val

		def __str__(self):
			return 'val_type: ' + str(self.val_type) + ', val_size: ' + str(self.val_size) + ', val: ' + str(self.val)

	def __init__(self, allocated_size, filled_size):
		self.allocated_size = allocated_size
		self.filled_size = filled_size
		self.values = []
		 #  just the values for display. no storage layer info
		self.values_order = None # TODO1: implement later

	def add_value(self, val_type, val_size, val):
		self.values.append(self.ValueData(val_type, val_size, val))
