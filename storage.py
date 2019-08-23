import mysql.connector
from settings import Settings
pos_settings = Settings()
from tkinter.messagebox import showerror, showinfo

class Storage():
	def __init__(self, pos_settings=pos_settings):
		self.pos_settings = pos_settings
		self.conn, self.cursor = self.connect_db()
		
	def connect_db(self):
		try:
			conn = mysql.connector.connect(**self.pos_settings.db_config)
		except mysql.connector.errors.ProgrammingError as err:
			if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
				db_name = pos_settings.db_config.pop('database')
				conn = mysql.connector.connect(**self.pos_settings.db_config)
				cursor = conn.cursor()
				cursor.execute('CREATE DATABASE %s' % db_name)
				print('Connected to database')
				cursor.execute('USE %s' % db_name)
				return conn, cursor
		else:
			cursor = conn.cursor()
			return conn, cursor

	def fetch_products(self, label=None):
		try:
			if label == None:
				self.cursor.execute('SELECT * from %s' % self.pos_settings.table_name)
				return list(self.cursor.fetchall())
			else:
				sql_stmt = 'SELECT * from %s WHERE name =' % self.pos_settings.table_name + '%s'
				self.cursor.execute(sql_stmt, (label,))
				return self.cursor.fetchall()
				self.conn.close()
		except mysql.connector.errors.ProgrammingError as err:
			if err.errno == mysql.connector.errorcode.ER_NO_SUCH_TABLE:
				self.create_table()
				self.conn.close()

	def add_product(self, name, quantity, pur_data, exp_data, products, parent, listbox): # check if product exists
		if name == '':
			showerror('Error', 'Invalid data')
			return False
		elif (name,) in products:
			showerror('Error', 'Product already exists')
			return False
		try:
			temp_labels = []
			temp_data = []
			for key in self.pos_settings.table_labels:
				temp_labels.append(key)
			temp_labels.insert(0,self.pos_settings.table_name)
			template = 'INSERT INTO %s (%s, %s , %s, %s) VALUES' % tuple(temp_labels)
			template += '(%s, %s , %s, %s)'
			temp_data = [name, quantity, pur_data, exp_data]
			for index in range(len(temp_data)):
				if temp_data[index] == '':
					temp_data[index] = None
			self.cursor.execute(template, tuple(temp_data))
			self.conn.commit()
			self.conn.close()
			parent.destroy()
			listbox.insert('end', name)
			showinfo('%s' % name, 'Product has been added')
		except mysql.connector.errors.ProgrammingError as err:
			if err.errno == mysql.connector.errorcode.ER_NO_SUCH_TABLE:
				self.create_table()
				self.conn.close()
		except mysql.connector.errors.DataError as err:
					if err.errno == mysql.connector.errorcode.ER_TRUNCATED_WRONG_VALUE:
						showerror('Error', 'Incorrect date value')
		except mysql.connector.errors.DatabaseError as err:
					if err.errno == mysql.connector.errorcode.WARN_DATA_TRUNCATED:
						showerror('Error', 'Incorrect quantity value')

	def remove_product(self, label):
		sql_stmt = 'DELETE FROM %s WHERE name = ' % self.pos_settings.table_name + '%s'
		print(label)
		self.cursor.execute(sql_stmt, (label,))
		self.conn.commit()
		self.conn.close()
		showinfo('%s' % label, 'Product has been removed')
		
	def modify_product(self, label, products, new, index, listbox, products_to_use, parent): # new = [name, quantity, weight, purchase date, expiration date]
		if new[0].get() != label and new[0].get() in products:
			showerror('Error', 'Product already exists')
			parent.grab_set()
			parent.focus_set()
			parent.wait_window()
		elif new[0].get() == '':
			showerror('Error', 'Invalid data')
		else:
			temp_labels = []
			new = [data.get() if data.get() != '' else None for data in new]
			new.append(label)
			sql_stmt = '''UPDATE storage 
							SET name = %s, quantity = %s, purchase_data = %s, expiration_data = %s
							WHERE name = %s'''
			try:
				self.cursor.execute(sql_stmt, tuple(new))
				self.conn.commit()
				self.conn.close()
				listbox.delete(index)
				listbox.insert(index, new[0])
				products_to_use[new[0]] = float(new[1])
				parent.destroy()
				showinfo('%s' % new[0], 'Product has been modified')

			except mysql.connector.errors.DataError as err:
					if err.errno == mysql.connector.errorcode.ER_TRUNCATED_WRONG_VALUE:
						showerror('Error', 'Incorrect date value')
			except mysql.connector.errors.DatabaseError as err:
					if err.errno == mysql.connector.errorcode.WARN_DATA_TRUNCATED:
						showerror('Error', 'Incorrect quantity value')
	
	def create_table(self):
		temp = [key + ' ' + self.pos_settings.table_labels[key] for key in self.pos_settings.table_labels]
		sql_data = ', '.join(temp)
		sql_stmt = 'CREATE TABLE IF NOT EXISTS %s (id INT PRIMARY KEY AUTO_INCREMENT, %s)' % (self.pos_settings.table_name, sql_data)
		self.cursor.execute(sql_stmt)
		self.conn.commit()

	def sell(self, formula, name, number=1, parent=None):
		sql_stmt = """UPDATE storage 
						SET quantity = quantity - %s
						WHERE name = %s"""
		try:
			if formula:
				for product, quantity in formula:
					quantity = str(round(float(quantity) * number, 2))
					self.cursor.execute(sql_stmt, (quantity, product))
				self.conn.commit()
				self.conn.close()
				if parent:
					parent.destroy()
					return True
			else:
				showerror('Error', name + ' has no formula')
				self.conn.close()
				return False
		except mysql.connector.errors.DataError as err:
			if err.errno == mysql.connector.errorcode.ER_WARN_DATA_OUT_OF_RANGE:
				showerror('Error', 'error')
				return False

	def check_product(self, formula, name, products_to_use, number=1):
		try:
			if formula:
				for product, quantity in formula:
					if product in products_to_use:
						if number < 0:
							products_to_use[product] += float(quantity) # howmany =  // float(quantity)
						else:
							avaiable = products_to_use[product] // float(quantity)
							if avaiable >= 1:
								products_to_use[product] -= float(quantity)
								self.conn.close()
								return True
							else:
								howmany = avaiable // float(quantity)
								errortext = "Not enough %s to make %s" % (product, name)
								showerror('Error', errortext)
								self.conn.close()
								return False
					else:
						avaiable = self.fetch_products(product).pop(0)
						products_to_use[product] = float(avaiable[2])
						avaiable = products_to_use[product] // float(quantity) #howmany = int(avaiable[2]) // float(quantity))
						if avaiable >= 1:
							products_to_use[product] -= float(quantity)
							self.conn.close()
							return True
						else:
							errortext = "Not enough %s to make %s" % (product, name)
							showerror('Error', errortext)
							self.conn.close()
							return False
		except IndexError:
			showerror('Error', 'There is no products in storage to make this item')
if __name__ == '__main__':
	Storage()