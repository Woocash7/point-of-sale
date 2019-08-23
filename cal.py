from tkinter import *
import calendar
from datetime import datetime, date

class GraphicCalendar(Toplevel):
	def __init__(self, parent=None):
		Toplevel.__init__(self, parent, relief=SOLID, bd=2)
		self.parent = parent
		self.geometry('+600+150')
		self.color = 'SystemButtonFace'
		self.rows = []
		self.days = []
		self.yearVar = IntVar()
		self.monthVar = IntVar()
		self.return_date = StringVar()
		self.months = list(calendar.month_name)
		self.today_date = date.today()
		self.year = self.today_date.year
		self.month = self.today_date.month
		self.day =self.today_date.day
		self.cal = calendar.Calendar().yeardayscalendar(self.year, width=1)
		self.cal = [self.cal[i].pop() for i in range(len(self.cal))]
		self.overrideredirect(1)
		self.makeCalendar(self.year, self.month)
		self.grab_set()
		self.focus_set()
		self.wait_window()

	def makeCalendar(self, year, month):
		for row in self.rows:
			row.pack_forget()
		for row in self.days:
			for col in row:
				col.pack_forget()
		if month == 13:
			month = 13 % 12
			year += 1
			self.cal = calendar.Calendar().yeardayscalendar(year, width=1)
			self.cal = [self.cal[i].pop() for i in range(len(self.cal))]
		if month == 0:
			month = 12
			year -= 1
			self.cal = calendar.Calendar().yeardayscalendar(year, width=1)
			self.cal = [self.cal[i].pop() for i in range(len(self.cal))]
		
		self.yearVar.set(year)
		self.monthVar.set(month)
		mark_today = [False, False]
		
		year_row = Frame(self)
		year_row.pack(expand=YES, fill=X)
		self.rows.append(year_row)
		Label(year_row, text=self.yearVar.get(), width=42, height=2, relief=SOLID, bd=1).pack(fill=X)

		month_row = Frame(self)
		month_row.pack(expand=YES, fill=X)
		self.rows.append(month_row)
		Button(month_row, text='<', command= lambda: self.makeCalendar(year, month-1)).pack(fill=X, side=LEFT)
		Label(month_row, text=self.months[self.monthVar.get()], width=30).pack(expand=YES, fill=X, side=LEFT, anchor=CENTER)
		Button(month_row, text='>', command= lambda: self.makeCalendar(year, month+1)).pack(fill=X, side=LEFT)
		
		day_row = Frame(self, relief=SOLID, bd=1)
		day_row.pack(side=TOP, expand=YES, fill=X)
		for day in list(calendar.day_name):
			Label(day_row, text=day[:2], width=6).pack(side=LEFT, expand=YES, fill=X)
		self.rows.append(day_row)
		
		if self.yearVar.get() == self.year:
			mark_today[0] = True
		if self.monthVar.get() == self.month:
			mark_today[1] = True

		cal_month = month - 1
		for row in range(len(self.cal[cal_month])):
			new_row = Frame(self)
			new_row.pack(expand=YES, fill=X)
			self.rows.append(new_row)
			cols = []
			for col in range(len(self.cal[cal_month][row])):
				if self.cal[cal_month][row][col] == 0:
					lab = Label(new_row, text=' ', width=6)
					lab.pack(expand=YES, side=LEFT, fill=X)
					cols.append(lab)
				else:
					lab = Label(new_row, text=self.cal[cal_month][row][col], width=6)
					lab.pack(expand=YES, side=LEFT, fill=X)
					if all(mark_today) and self.cal[cal_month][row][col] == self.day:
						lab.config(relief=SOLID)
					cols.append(lab)
					lab.bind('<Enter>', self.highlight)
					lab.bind('<Button-1>', self.get_day)
					lab.bind('<Leave>', self.normal)
				self.days.append(cols)
		
		cancel_row = Frame(self)
		cancel_row.pack(expand=YES, fill=X)
		Button(cancel_row, text='Cancel', command=self.destroy, relief=SOLID, bd=1).pack(expand=YES, fill=X)
		self.rows.append(cancel_row)

	def get_day(self, event):
		d = [self.yearVar.get(), self.monthVar.get(), int(event.widget['text'])]
		d = date(d[0], d[1], d[2])
		mydate = date.isoformat(d)
		self.return_date.set(mydate)
		self.destroy()


	def highlight(self, event):
		event.widget.config(bg='#42a1f5')

	def normal(self, event):
		event.widget.config(bg=self.color)


if __name__ == '__main__':
	root = Tk()
	gc = GraphicCalendar(root)
	root.mainloop()
