import shelve
import mysql.connector
from tkinter import *
from tkinter.messagebox import showerror, askokcancel
from formrows import makeFormRow
from cal import GraphicCalendar
from item import Item
from formula import Formula
from storage import Storage

def fetch_formulas(pos_settings):
	with shelve.open(pos_settings.formulas) as db:
		for key in db:
			print('Formula for',  key + ':', db[key])

def fetch_items(pos_settings):
	with shelve.open(pos_settings.items) as db:
		for key in db:
			print(db[key])

def fetch_item(key, pos_settings):
	with shelve.open(pos_settings.items) as db:
		return db[key]

class ItemMenu(Toplevel):
	def __init__(self, parent=None, pos_settings=None):
		Toplevel.__init__(self, parent)
		self.title('Items')
		self.geometry('+75+75')
		self.pos_settings = pos_settings
		self.makeWidgets()
		self.grab_set()
		self.focus_set()
		self.wait_window()

	def makeWidgets(self):
		scrolledlist = Frame(self)
		scrolledlist.pack(expand=YES, fill=BOTH, side=LEFT)
	
		vbar = Scrollbar(scrolledlist)
		itemslist = Listbox(scrolledlist, relief=SUNKEN)

		vbar.config(command=itemslist.yview)
		itemslist.config(yscrollcommand=vbar.set, selectmode=EXTENDED)

		vbar.pack(side=RIGHT, fill=Y)
		itemslist.pack(side=LEFT, expand=YES, fill=BOTH)
		pos = 0
		with shelve.open(self.pos_settings.items) as db:
			for key in sorted(list(db.keys())):
					itemslist.insert(pos, key)
					pos += 1
			self.listbox = itemslist

		buttons = Frame(self)
		buttons.pack(side=RIGHT, expand=YES, fill=BOTH)
		
		Button(buttons, text='Close', command=self.destroy).pack(side=BOTTOM, fill=X)
		Button(buttons, text='Help', command=lambda subject='items': self.onHelp(subject)).pack(side=BOTTOM, fill=X)
		
		itembuttons = LabelFrame(buttons, text='Items')
		itembuttons.pack(expand=YES, fill=BOTH)
		Button(itembuttons, text='Add', command=self.add_item).pack(fill=X)
		Button(itembuttons, text='Remove', command=self.remove_item).pack(fill=X)
		Button(itembuttons, text='Modify', command=self.modify_item).pack(fill=X)
		
		formulabuttons = LabelFrame(buttons, text='Formulas')
		formulabuttons.pack(expand=YES, fill=BOTH)
		Button(formulabuttons, text='Formula', command=self.check_formula).pack(fill=X)
		Button(formulabuttons, text='Add formula', command=self.add_formula).pack(fill=X)
		Button(formulabuttons, text='Remove formula', command=self.remove_formula).pack(fill=X)
		Button(formulabuttons, text='Modify formula', command=self.modify_formula).pack(fill=X)

	def add_item(self):
		win = Toplevel(self)
		win.title('Add item')
		win.geometry('+100+100')
				
		var1 = makeFormRow(win, label='Enter the name of the item', focus=True)
		var2 = makeFormRow(win, label='Enter the price of the item')
		var3 = makeFormRow(win, label='Enter the category of the item')
		Button(win, text='Save', command=(lambda: Item().save_item(name=var1.get(), price=var2.get(), cat=var3.get(), parent=win, listbox=self.listbox, menu=self.master))).pack(side=LEFT, expand=YES, fill=X)
		Button(win, text='Cancel', command=win.destroy).pack(side=RIGHT, expand=YES, fill=X)
		win.bind('<Return>', lambda event: Item().save_item(name=var1.get(), price=var2.get(), cat=var3.get(), parent=win, listbox=self.listbox, menu=self.master))
		win.grab_set()
		win.focus_set()
		win.wait_window()
		self.grab_set()
		self.focus_set()
		self.wait_window()
	

	def remove_item(self):
		index = self.listbox.curselection()
		if len(index) == 0:
			showerror('Error', 'No items selected')
		elif len(index) == 1:
			label = self.listbox.get(index)
			answer = askokcancel('Verify remove', 'Are you sure you want to remove ' + label + '?\nRemoving selected item will remove its formula')
			if answer == True:
				Item(name=label).remove_item()
				self.remove_formula(name=label, standalone=False)
				self.listbox.delete(index)
			else:
				return False
		else:
			deleted_positions = 0
			for position in index:
				if position == 0:
					pass
				else:
					position -= deleted_positions
				label = self.listbox.get(position)
				answer = askokcancel('Verify remove', 'Are you sure you want to remove ' + label + '?\nRemoving selected item will remove its formula')
				if answer == True:
					Item(name=label).remove_item()
					self.remove_formula(name=label, standalone=False)
					self.listbox.delete(position)
					deleted_positions += 1
				else:
					pass
		self.master.can.destroy() #def remakemenu
		self.master.vbar.destroy() # /\
		self.master.makeMenu() # //\\
		self.grab_set()
		self.focus_set()
		self.wait_window()

	def modify_item(self):
		index = self.listbox.curselection()
		if len(index) != 1:
			showerror('Error', 'Select one item to modify')
		else:
			label = self.listbox.get(index)
			
			win = Toplevel(self)
			win.title('Modify item')
			win.geometry('+100+100')
			
			item = fetch_item(label, self.pos_settings)
			var1 = makeFormRow(win, label='Enter the new name of the item', input=item.name, focus=True)
			var2 = makeFormRow(win, label='Enter the new price of the item', input=item.price)
			var3 = makeFormRow(win, label='Enter the new category of the item', input=item.cat)
			Button(win, text='Save', command=(lambda: Item().modify_item(oldname= label, name=var1.get(), price=var2.get(), cat=var3.get(), index=index, parent=win, listbox=self.listbox, menu=self.master))).pack(side=LEFT, expand=YES, fill=X)
			Button(win, text='Cancel', command=win.destroy).pack(side=RIGHT, expand=YES, fill=X)

			win.bind('<Return>', lambda event: Item().modify_item(oldname= label, name=var1.get(), price=var2.get(), cat=var3.get(), index=index, parent=win, listbox=self.listbox, menu=self.master))
		self.grab_set()
		self.focus_set()
		self.wait_window()

	def check_formula(self):
		index = self.listbox.curselection()
		if len(index) == 0:
			showerror('Error', 'No items selected')
		elif len(index) == 1:
			itemlabel = self.listbox.get(index)
			win = Toplevel(self)
			win.title("%s's formula" % itemlabel)
			win.geometry('+100+100')
			products = Formula(itemlabel).get_formula(parent=win)
			if products == None:
				return False
			text = '{:>20}{:>20}\n'.format('Name:', 'Quanity:')
			for product, quantity in products:
				text += '{:>20}{:>20}\n'.format(product, quantity)
				msg = Message(win, text=text, width=200)
			msg.pack(fill=X, expand=YES)
			button = Button(win, text='OK', command=win.destroy)
			button.pack(fill=X)
			button.config(relief=RIDGE)

	def add_formula(self):
		index = self.listbox.curselection()
		if len(index) != 1:
			showerror('Error', 'Select one item to add formula')
		else:
			win = Toplevel(self)
			win.title('Add formula')
			win.geometry('+100+100')			
			defaultnumproducts = 5
			products = []
			itemlabel = self.listbox.get(index)
			for i in range(defaultnumproducts):
				var1 = makeFormRow(win, label='Enter the name of the product %d' % (i+1))
				var2 = makeFormRow(win, label='Enter the name of the quantity')
				products.append((var1, var2))

			Button(win, text='OK', command=lambda: Formula(itemlabel).add_formula(products, parent=win)).pack(side=LEFT, expand=YES, fill=X)
			Button(win, text='Cancel', command=win.destroy).pack(side=RIGHT, expand=YES, fill=X)
			win.bind('<Return>', lambda event: Formula(itemlabel).add_formula(products, parent=win))
	
	def remove_formula(self, name=None, standalone=True):
		if standalone:
			index = self.listbox.curselection()
			if len(index) == 0:
				showerror('Error', 'No items selected')
			elif len(index) == 1:
				itemlabel = self.listbox.get(index)
				answer = askokcancel('Verify remove', 'Are you sure you want to remove ' + itemlabel + ' formula?')
				if answer == True:
					Formula(name=itemlabel).remove_formula()
				else:
					pass
			else:
				for position in index:
					itemlabel = self.listbox.get(position)
					answer = askokcancel('Verify remove', 'Are you sure you want to remove ' + itemlabel + ' formula?')
					if answer == True:
						Formula(name=itemlabel).remove_formula()
					else:
						pass
		else:
			Formula(name=name).remove_formula(silence=True)

	def modify_formula(self):
		index = self.listbox.curselection()
		if len(index) != 1:
			showerror('Error', 'Select one item')
		else:
			win = Toplevel(self)
			win.title('Modify formula')
			win.geometry('+100+100')
			itemlabel = self.listbox.get(index)
			products = Formula(itemlabel).get_formula(parent=win)
			defaultnumproducts = 5
			new = []
			for i in range(defaultnumproducts):
				if products:
					var1 = makeFormRow(win, label='Enter the name of the product %d' % (i+1), input=products[0][0])
					var2 = makeFormRow(win, label='Enter the name of the quantity', input=products[0][1])
					new.append((var1, var2))
					products.pop(0)
				else:
					var1 = makeFormRow(win, label='Enter the name of the product %d' % (i+1))
					var2 = makeFormRow(win, label='Enter the name of the quantity')
					new.append((var1, var2))

			Button(win, text='OK', command=lambda: Formula(itemlabel).modify_formula(new, parent=win)).pack(side=LEFT, fill=X, expand=YES)
			Button(win, text='Cancel', command=win.destroy).pack(side=RIGHT, fill=X, expand=YES)
			win.bind('<Return>', lambda event: Formula(itemlabel).modify_formula(new, parent=win))

	def onHelp(self, subject):
		win = Toplevel(self)
		win.title('Help')
		win.geometry('+100+100')
		if subject == 'items':
			help = '''Manage items and their formulas. To add item press "Add" button. Adding formula to item, by pressing "Add formula" is independent.
					 To modify item or formula press "Modify/Modify formula" with selected one item.
					 You can remove multiple items/formulas by selecting more items on list with Ctrl+LMB. Removing item removes its formula'''
			msg = Message(win, text=help)
			msg.pack(fill=X, expand=YES)
			Button(win, text='OK', command=win.destroy).pack(expand=YES, fill=X)

class ProductMenu(Toplevel):
	def __init__(self, parent=None, pos_settings=None, products_to_use=None):
		Toplevel.__init__(self, parent)
		self.title('Products')
		self.geometry('+75+75')
		self.pos_settings = pos_settings
		self.products_to_use =  products_to_use
		self.makeWidgets()
		self.grab_set()
		self.focus_set()
		self.wait_window()

	def makeWidgets(self):
		scrolledlist = Frame(self)
		scrolledlist.pack(expand=YES, fill=BOTH, side=LEFT)
	
		vbar = Scrollbar(scrolledlist)
		productslist = Listbox(scrolledlist, relief=SUNKEN)

		vbar.config(command=productslist.yview)
		productslist.config(yscrollcommand=vbar.set, selectmode=EXTENDED)

		vbar.pack(side=RIGHT, fill=Y)
		productslist.pack(side=LEFT, expand=YES, fill=BOTH)
		pos = 0
		products = Storage().fetch_products()
		if products == None:
			pass
		else:
			for product in products:
				productslist.insert(pos, product[1])
				pos += 1
			self.listbox = productslist
			self.listbox.select_set(0)

		buttons = Frame(self)
		buttons.pack(side=RIGHT, expand=YES, fill=BOTH)
		
		Button(buttons, text='Close', command=self.destroy).pack(side=BOTTOM, fill=X)
		Button(buttons, text='Help', command=lambda subject='storage': self.onHelp(subject)).pack(side=BOTTOM, fill=X)
		
		Button(buttons, text='Fetch product', command=self.fetch_products).pack(fill=X)
		Button(buttons, text='Add product', command=lambda: self.add_product(products)).pack(fill=X)
		Button(buttons, text='Remove product', command=self.remove_product).pack(fill=X)
		Button(buttons, text='Modify product', command=lambda: self.modify_product(products)).pack(fill=X)
		Button(buttons, text='Delivery').pack(fill=X)

	def fetch_products(self):
		index = self.listbox.curselection()
		if len(index) != 1:
			showerror('Error', 'Select one product')
		else:
			win = Toplevel(self)
			productlabel = self.listbox.get(index)
			win.title('productlabel')
			win.geometry('+100+100')
			product = Storage().fetch_products(productlabel)
			product = product.pop(0)
			text = 'Name: %s\nQuantity: %s\nPurchase date: %s\nExpiration date: %s' % (product[1], product[2], product[3], product[4])
			Message(win, text=text, width=200).pack()
			Button(win, text='OK', command=win.destroy).pack(expand=YES, fill=X)
		
	def add_product(self, products):
		win = Toplevel(self)
		win.title('Add product')
		win.geometry('+100+100')

		var1 = makeFormRow(win, label='Enter the name of the product', focus=True)
		var2 = makeFormRow(win, label='Enter the quantity of the item[pieces/volume/wieght]')
		var3, ent3 = makeFormRow(win, label='Enter the purchase data of the item[YYYY-MM-DD]', date=True)
		var4, ent4 = makeFormRow(win, label='Enter the expiration data of the item[YYYY-MM-DD]', date=True)

		date_entries = [[var3, ent3], [var4, ent4]]

		Button(win, text='Save', command=(lambda: Storage().add_product(name=var1.get(), quantity=var2.get(), pur_data=var3.get(), exp_data=var4.get(), products=products, parent=win, listbox=self.listbox))).pack(side=LEFT, expand=YES, fill=X)
		Button(win, text='Cancel', command=win.destroy).pack(side=RIGHT, expand=YES, fill=X)
		win.bind('<Return>', lambda event: Storage().add_product(name=var1.get(), quantity=var2.get(), pur_data=var3.get(), exp_data=var4.get(), products=products, parent=win, listbox=self.listbox))
		for var, ent in date_entries:
			ent.bind('<Double-Button-1>', lambda event, var=var: self.focusin(event, var))
		win.grab_set()
		win.focus_set()
		win.wait_window()
		self.grab_set()
		self.focus_set()
		self.wait_window()

	def remove_product(self):
		index = self.listbox.curselection()
		if len(index) == 0:
			showerror('Error', 'No products selected')
		elif len(index) == 1:
			label = self.listbox.get(index)
			answer = askokcancel('Verify remove', 'Are you sure you want to remove ' + label + '?')
			if answer == True:
				Storage().remove_product(label)
				self.listbox.delete(index)
			else:
				return False
		else:
			deleted_positions = 0
			for position in index:
				if position == 0:
					pass
				else:
					position -= deleted_positions
				label = self.listbox.get(position)
				answer = askokcancel('Verify remove', 'Are you sure you want to remove ' + label + '?')
				if answer == True:
					Storage().remove_product(label)
					self.listbox.delete(position)
					deleted_positions += 1
				else:
					pass

		self.grab_set()
		self.focus_set()
		self.wait_window()

	def modify_product(self, products):
		index = self.listbox.curselection()
		if len(index) != 1:
			showerror('Error', 'Select one product')
		else:
			win = Toplevel(self)
			win.title('Modify product')
			win.geometry('+100+100')
			productlabel = self.listbox.get(index)
			product = Storage().fetch_products(productlabel)
			product = product.pop(0)
			productslist = [data[1] for data in products]

			var1 = makeFormRow(win, label='Enter the name of the product', input=product[1], focus=True)
			var2 = makeFormRow(win, label='Enter the quantity of the item[pieces/volume/wieght]', input=product[2])
			var3, ent3 = makeFormRow(win, label='Enter the purchase data of the item[YYYY-MM-DD]', input=product[3], date=True)
			var4, ent4= makeFormRow(win, label='Enter the expiration data of the item[YYYY-MM-DD]', input=product[4], date=True)

			new = [var1, var2, var3, var4]
			date_entries = [[var3, ent3], [var4, ent4]]

			Button(win, text='OK', command=lambda: Storage().modify_product(label=productlabel, products=productslist, new=new, index=index, listbox=self.listbox, products_to_use=self.products_to_use, parent=win)).pack(side=LEFT, expand=YES, fill=X)
			Button(win, text='Cancel', command=win.destroy).pack(side=RIGHT, expand=YES, fill=X)
			win.bind('<Return>', lambda event: Storage().modify_product(label=productlabel, products=productslist, new=new, index=index, listbox=self.listbox, products_to_use=self.products_to_use, parent=win))
			for var, ent in date_entries:
				ent.bind('<Double-Button-1>', lambda event, var=var: self.focusin(event, var))
	
	def focusin(self, event, var):
		gc = GraphicCalendar(self)
		var.set(gc.return_date.get())

	def onHelp(self, subject):
		pass

# JAK MA WYGLADAC SELL 2/3
# KOLEJNOSC KATEGORII
# WYKRES SPRZEDAZY
# KALENDARZ, GODZINA from datetime import date => date.isoformat(date.today())
