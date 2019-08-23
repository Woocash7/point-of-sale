from tkinter import *

def makeFormRow(parent, label, unit_price=None, input=None, focus=False, extended=None, date=None, width=45):
	var = StringVar()
	row = Frame(parent)
	lab = Label(row, text=label + ':', relief=RIDGE, width=width)
	ent = Entry(row, relief=SUNKEN, textvariable=var, width=20)
	
	if input != None:
		var.set(input)
	
	if extended:
		pay = DoubleVar()
		pay.set(round(unit_price * input, 2))
		ent2 = Entry(row, textvariable=pay, relief=SUNKEN, width=5)
		
	row.pack(fill=X)
	lab.pack(side=LEFT)
	ent.pack(side=LEFT, expand=YES, fill=X)
	
	if extended:
		ent2.pack(side=LEFT)
	
	if focus or label[-1] == '1':
		ent.focus()

	if extended:
		return lab, var, pay, row
	elif date:
		return var, ent
	else:
		return var
