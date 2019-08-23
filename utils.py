import datetime as dt
import calendar
import os

def update_sell(data, data_dir):
		month, year = dt.date.today().month, str(dt.date.today().year)
		month = list(calendar.month_name)[month]
		subdirs = os.path.join(year, month)
		data_dir = os.path.join(data_dir, subdirs)
		if not os.path.exists(data_dir):
			os.makedirs(data_dir)
		try:
			with open(os.path.join(data_dir, dt.date.isoformat(dt.date.today())) + '.txt', 'r+') as file:
				read = file.readlines()
				for item in data:
					name = item[0]
					names = [labels.split(',')[0] for labels in read]
					if name in names:
						index = names.index(name)
						temp = read[index].split(',')
						amount, price = temp[1].strip(), temp[2].strip()
						amount = int(amount) + item[1]
						price = round(float(price) + item[1] * item[2], 2) #better round in progress
						temp[1] = str(amount)
						temp[2] = str(price)
						temp = ','.join(temp) + '\n'
						read[index] = temp
					else:
						item[2] = rond(item[1] * item[2], 2) #better round in progress
						item = [str(i) for i in item]
						new_line = ','.join(item) + '\n'
						read.append(new_line)
				file.seek(0)
				for line in read:
					file.write(line)
				file.truncate()
		except OSError:
			with open(os.path.join(data_dir, dt.date.isoformat(dt.date.today())) + '.txt', 'w') as file:
				file.write('Name,Quantity,Total price\n')
				for item in data:
					item[2] = item[1] * item[2]
					item = [str(i) for i in item]
					new_line = ','.join(item) + '\n'
					file.write(new_line)
					file.truncate()

# def make_csv_file(file):
# 	directory = pos_settings.data
# 	os.path.join(directory, file)
# 	file_csv = os.path.splitext(file)[0]
# 	from shutil import copy2
# 	file_csv += '.csv'
# 	copy2(file, file_csv)