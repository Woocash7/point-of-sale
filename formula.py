from tkinter.messagebox  import *
from settings import Settings
pos_settings = Settings()
import shelve

class Formula():
	def __init__(self, name=None, pos_settings=pos_settings):
		self.pos_settings = pos_settings
		self.name = name
		self.formula = {}
	
	def add_formula(self, products, parent):
		with shelve.open(pos_settings.formulas) as db:
			if self.name in db:
				parent.destroy()
				showerror('Error', 'This item already has formula')
			elif all(label.get() == '' for label, q in products):
				showerror('Error', 'Invalid data')
			else:
				for label, quantity in products:
					if label.get() != '':
						self.formula[label.get()] = quantity.get()
				db[self.name] = self.formula
				parent.destroy()
				showinfo('%s' % self.name, 'Formula has been added')


	def remove_formula(self, silence=None): #mode:a = autonomous
		print(self.name)
		with shelve.open(pos_settings.formulas) as db:
			if not self.name in db:
				if not silence:
					showerror('Error', 'This item does not have formula')
			else:
				db.pop(self.name)
				if not silence:
					showinfo('%s' % self.name, 'Formula has been removed')

	def get_formula(self, parent=None, silence=None): #silence dont trigger dialogs
		formula = []
		with shelve.open(pos_settings.formulas) as db:
			if not self.name in db:
				if parent:
					parent.destroy()
				if not silence:
					showerror('Error', 'This item does not have formula')
			else:
				for key in db[self.name]:
					formula.append((key, db[self.name][key]))
				return formula # return list((product_name, quantity))

	def modify_formula(self, new, parent=None):
		with shelve.open(pos_settings.formulas) as db:
			for label, quantity in new:
				if label.get() != '':
					self.formula[label.get()] = quantity.get()
			db[self.name] = self.formula
			parent.destroy()
			showinfo('%s' % self.name, 'Formula has been modified')

