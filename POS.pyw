try:
	import os
	import time, datetime as dt
	import math
	from settings import Settings
	from tkinter import *
	from tkinter.messagebox import *
	from PIL.ImageTk import PhotoImage
	from formrows import makeFormRow
	import Pmw
	from shop import *
	from utils import update_sell
except:
	import traceback
	print(traceback.print_exc())
	input()

# from PIL.ImageTk import PhotoImage

class Menu(Frame):
	def __init__(self, parent=None, pos_settings=None):
		Frame.__init__(self, parent)
		self.master.title('Point of Sale')
		self.pack(expand=YES, fill=BOTH)
		self.pos_settings = pos_settings
		self.bills = [{} for i in range(5)] 
		self.bill_num = IntVar()
		self.products_to_use = {}
		
		self.balloon = Pmw.Balloon(parent, relmouse='both')
		
		self.makeSideBar()
		self.makeTopBar()
		self.makeMenu()
		self.makeBottomBar()
		
	def sell(self, name):
		bill_index = self.bill_num.get()
		for elements in self.bills[bill_index]:
			if key not in elements[0]:
				self.bills[bill_index].append([key, 1])
			else:
				elements[1] += 1
				break

	def makeSideBar(self):
		sideBar = Frame(self)
		sideBar.pack(side=RIGHT, fill=BOTH)
		sideBar.config(bd=1, relief=SOLID, width=100)
		Button(sideBar, text='Items', command=lambda: ItemMenu(self, self.pos_settings)).pack(fill=X)
		Button(sideBar, text='Products', command=lambda: ProductMenu(self, self.pos_settings, self.products_to_use)).pack(fill=X)
		Button(sideBar, text='Quit', command= self.quit).pack(fill=X)

	def makeMenu(self):
		rootsize = '841x500'
		button_width = 14
		button_height = 5 #organize static parameters
		numcols = 7 # /\
		wraptextlen = 80 # //\\
		width, height = 760, 400 # ///\\\
		
		self.rows = []
		self.can = Canvas(self)
		self.vbar = Scrollbar(self)

		self.vbar.pack(side=RIGHT, fill=Y)
		self.can.pack(side=TOP, fill=BOTH, expand=YES)

		self.vbar.config(command=self.can.yview)
		self.can.config(yscrollcommand=self.vbar.set)
		self.can.config(width=width, height=height, bg='white')
		
		items = []
		with shelve.open(pos_settings.items) as db:
			for key in db:
				items.append((key, db[key].price, db[key].cat))
			
		categories = []
		for item in items:
			if not item[2] in categories:
				categories.append(item[2])
				# open('settings.txt') 

		if items == []:
			self.master.geometry(rootsize)
			Label(self.can, text='There are no items yet', bg='white').pack(fill=BOTH, expand=YES, anchor=CENTER)
		else:
			# print(self.master.winfo_width(), self.master.winfo_height())
			all_frames_height = 0
			framepos_x = 0
			framepos_y = 0
			for category in categories:
				keys = []
				for item in items:
					if item[2] == category: #item = [name, price, category]
						keys.append(item)
				numrows = int(math.ceil(len(keys) / numcols))
				LF = LabelFrame(self.can, text=category, bg='#f5dd42')
				LF.pack(anchor=NW, expand=YES, fill=X)
				keys.sort()
				while keys:
					keysrow, keys = keys[:numcols], keys[numcols:]
					row = Frame(LF)
					row.pack(anchor= NW, expand=YES, fill=X)
					row.config(bg='#f5dd42')
					for key in keysrow:
						item = Button(row, text=key[0]) #key = [name, category]
						handler = lambda key=key: self.addToBill(key[0])
						item.config(command=handler, wraplength=wraptextlen, width=button_width, height=button_height, bg='#42a1f5')
						item.pack(anchor=NW, side=LEFT)
						self.balloon.bind(item, 'Name: %s\nPrice: %s\nCategory: %s' %(key[0], key[1], key[2]))
				LF.update()
				frame_width, frame_height = LF.winfo_width(), LF.winfo_height()
				# print(self.master.winfo_width(), self.master.winfo_height())
				all_frames_height += frame_height
				self.can.create_window(framepos_x, framepos_y, anchor=NW, window=LF, width=frame_width, height=frame_height)
				framepos_y += frame_height
			
			self.can.config(scrollregion=(0, 0, frame_width, all_frames_height))
			if height < all_frames_height:
				self.master.bind("<MouseWheel>", self._on_mousewheel)
		# print(self.master.winfo_width(), self.master.winfo_height())
		
	def makeBottomBar(self):
		buttonsBar = Frame(self)
		buttonsBar.pack(fill=X, side=BOTTOM)
		
		bottomBar = Frame(self)
		bottomBar.pack(fill=X, side=BOTTOM)
		bottomBar.config(bd=1, relief=SOLID)
		
		Button(buttonsBar, text='Sell', command=self.sell).pack(side=LEFT, fill=X, expand=YES)
		Button(buttonsBar, text='Clear', command=self.clear).pack(side=LEFT, fill=X, expand=YES)
		num_bills = len(self.bills)
		for bill in range(num_bills):
			Radiobutton(bottomBar, text='Bill %d' % (bill+1), value=bill, variable=self.bill_num, indicatoron=0).pack(side=LEFT, expand=YES, fill=X)
	
	def _on_mousewheel(self, event):
		self.can.yview_scroll(int(-1*(event.delta/120)), "units")

	def makeTopBar(self):
		topBar = Frame(self)
		topBar.pack(side=TOP, fill=X)
		topBar.config(relief=GROOVE, bd=1)
		def clock(lab=None):
			if lab != None:
				lab.pack_forget()
			date = time.asctime()
			lab = Label(topBar, text=date)
			lab.pack(side=RIGHT)
			topBar.after(1000, clock, lab)
		clock()
	
	def addToBill(self, name):
		bill_index = self.bill_num.get()
		formula = Formula(name).get_formula()
		if name in self.bills[bill_index]:
			avaiable = Storage().check_product(formula, name, self.products_to_use, 1)
			if avaiable:
				self.bills[bill_index][name] += 1
		else:
			avaiable = Storage().check_product(formula, name, self.products_to_use, 1)
			if avaiable:
				self.bills[bill_index][name] = 1

	def sell(self): #all data in Item, Formula, Storage instances are strings
		def add(label, amount, pay, unit_price, sign, tp):
			label = label['text'][:-1]
			i = int(amount.get()) #get current quantity
			i += sign # add or subtract this item
			formula = Formula(label).get_formula(silence=True)
			avaiable = Storage().check_product(formula, name, self.products_to_use, sign)
			if avaiable:
				self.bills[bill_index][name] += 1
				price = round(unit_price * i, 2) #new price #better round in progress
				amount.set(i) #set new amount
				pay.set(price) #set new price to pay
				temp = round(tp.get() + sign * unit_price, 2) #new total price[tp] for bill #better round in progress
				tp.set(temp) #set new tp
			
		def subtract(label, amount, pay, unit_price, sign, tp):
			label = label['text'][:-1]
			i = int(amount.get()) #get current quantity
			if i == 0:
				price = unit_price * i
				amount.set(i)
				pay.set(price)
				temp = round(tp.get() + price, 2) #better round in progress
				tp.set(temp)
			else:
				i += sign 
				formula = Formula(label).get_formula(silence=True)
				avaiable = Storage().check_product(formula, name, self.products_to_use, sign)
				self.bills[bill_index][name] -= 1
				price = unit_price * i 
				amount.set(i) 
				pay.set(price) 
				temp = round(tp.get() + price, 2)  #better round in progress
				tp.set(temp) 

		bill_index = self.bill_num.get()
		if list(self.bills[bill_index].keys()) == []:
			showerror('Error', 'Add items to bill')
			return False
		win = Toplevel(self)
		win.title('Summary Bill' + str(bill_index))
		win.geometry('+90+90')
		total = Label(win, text="Total:")
		tp = DoubleVar()
		total_price = Entry(win, textvariable=tp)
		order = []
		changes = []
		price_all = []
		try:
			for name in self.bills[bill_index]:
				item = Item(name).get_item()
				summary = [name, self.bills[bill_index][name], float(item.price)] #[name, quantity, unit_price]
				label, amount, pay, row = makeFormRow(win, label=summary[0], unit_price=summary[2], input=summary[1], extended=True, width=20)
				Button(row, text='+', command=lambda label=label, amount=amount, pay=pay, unit_price=summary[2], tp=tp: add(label, amount, pay, unit_price, 1, tp), relief=RIDGE).pack(side=LEFT)
				Button(row, text='-', command=lambda label=label, amount=amount, pay=pay, unit_price=summary[2], tp=tp: subtract(label, amount, pay, unit_price, -1, tp), relief=RIDGE).pack(side=LEFT)
				order.append(summary)
				changes.append(amount)
				price_all.append(pay)
		except SyntaxError:
			showerror('Error', "Check if items price is a number")
		total_price_label = sum(list(map(lambda x: x.get(), price_all)))
		tp.set(round(total_price_label, 2)) #better round in progress
		total_price.pack(side=RIGHT)
		total.pack(side=RIGHT)
		Button(win, text='Submit', command=lambda: self.submit_sell(win, order, changes)).pack(side=LEFT, fill=X)
		Button(win, text='Cancel', command=win.destroy).pack(side=LEFT, fill=X)
		win.grab_set()
		win.focus_set()
		win.wait_window()

	def submit_sell(self, win, order, changes):
		bill_index = self.bill_num.get()
		changes = [int(i.get()) for i in changes]
		for i in range(len(order)):
			order[i][1] = changes[i]
		for name, quantity, unit_price in order:
				formula = Formula(name).get_formula(silence=True)
				Storage().sell(formula, name, quantity)			
		update_sell(order, self.pos_settings.data)
		self.products_to_use = {}
		self.bills[bill_index] = {}
		win.destroy()
			
	def clear(self):
		bill_index = self.bill_num.get()
		for name in self.bills[bill_index]:
			num_restored = self.bills[bill_index][name]
			formula = Formula(name).get_formula(silence=True)
			if formula:
				for product, quantity in formula:
					self.products_to_use[product] += float(quantity) * num_restored
		self.bills[bill_index] = {}
		self.products_to_use = {}

# WYKRES SPRZEDAZY
# DOKUMENTACJA
	
if __name__ == '__main__':
	pos_settings = Settings()
	root = Tk()
	root.geometry('+%d+%d' % (pos_settings.root_geometry, pos_settings.root_geometry))
	try:
		c = Menu(root, pos_settings)
		# print(root.winfo_x(), root.winfo_y())
		# a = root.winfo_width(), root.winfo_height()
		root.mainloop()
	except Exception:
		import traceback
		print(traceback.print_exc())
		input()