import os, shelve, glob
from tkinter.messagebox  import * 
from settings import Settings
pos_settings = Settings()

class Item():
	def __init__(self, name=None, price=None, cat=None, pos_settings=pos_settings):
		self.pos_settings = pos_settings
		self.name = name
		#self.add_image()

	def save_item(self, name, price, cat, parent, listbox, menu):
		"""add record to shelve file. Update items' submenu and mainmenu"""
		if name == '' or price == '':
			showerror('Error', 'Invalid data')
			return False
		else:
			self.name = name
			self.price = price
			if cat == '':
				self.cat = 'Other' #auto category
			else:
				self.cat = cat
			with shelve.open(pos_settings.items) as db:
				if self.name in db:
					showerror('Error', 'Item already exists') 
				else:
					parent.destroy()
					db[self.name] = self
					listbox.insert('end', self.name)
					menu.can.destroy() #remake menu
					menu.vbar.destroy() # /\
					menu.makeMenu() # //\\
					showinfo('%s' % self.name, 'Item has been added')
					listbox.select_set('end')
									
				
	def remove_item(self): #remove all items(to add) == remove all recipes too
		with shelve.open(pos_settings.items) as db:
			if not self.name in db:
				showerror('Error', 'Item does not exist')
			else:
				db.pop(self.name)
				showinfo('%s' % self.name, 'Item has been removed')
				
	def modify_item(self, oldname, name, price, cat, index, parent, listbox, menu):
		if name == '' or price == '':
			showerror('Error', 'Invalid data')
			return False
		else:
			self.name = name
			self.price = price
			if cat == '':
				self.cat = 'Other' #auto category
			else:
				self.cat = cat
			with shelve.open(pos_settings.items) as db:
				if self.name != oldname and self.name in db.keys():
					showerror('Error', 'Item already exists')
					parent.grab_set()
					parent.focus_set()
					parent.wait_window()
				else:
					parent.destroy()
					db.pop(oldname)
					db[self.name] = self
					listbox.delete(index)
					listbox.insert(index, self.name)
					listbox.select_set(0)
					menu.can.destroy() #remake menu
					menu.vbar.destroy() # /\
					menu.makeMenu() # //\\
					showinfo('%s' % self.name, 'Item has been modified')

	def get_item(self):
		with shelve.open(pos_settings.items) as db:
			return db[self.name]

	# def update_categories_order(self):
		# with open(self.pos_settings.settings, 'r+') as file:
			

	def __str__(self):
		return 'name: %s, price: %s, category: %s' % (self.name, self.price, self.cat)