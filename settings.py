import os, sys

class Settings():
	def __init__(self):
		self.settings = 'settings.txt'
		itemsDir = 'items'
		if not os.path.exists(itemsDir):
			os.mkdir(itemsDir)
		self.items = os.path.join(itemsDir, 'items')

		formulasDir = 'formulas'
		if not os.path.exists(formulasDir):
			os.mkdir(formulasDir)
		self.formulas = os.path.join(formulasDir, 'formulas')
		self.db_config = {'host': 'localhost', 'user': 'root', 'passwd': 'pimpek102', 'database': 'pos'}
		self.data = 'data'
		self.table_name = 'storage'
		self.table_labels = {'name': 'VARCHAR(255)', 'quantity': 'FLOAT(5,2) UNSIGNED',
							'purchase_data': 'DATE', 'expiration_data': 'DATE'}
		self.set_items_cat_order()
		self.root_geometry = 50
	
	def set_items_cat_order(self):
		pass
		# self.category_order