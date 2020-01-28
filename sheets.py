import datetime

class Gspread():

    def __init__(self, sheet, duration=20):
        self.sheet = sheet
        self.duration = duration
        self.part_threshold = [10, 10, 10, 10]

        self.part_dict = {
            "8-11": "C",
            "11-14": "D",
            "14-17": "E",
            "17-20": "F",
        }
        self.part_time = {
            "8-11": "8",
            "11-14": "11",
            "14-17": "14",
            "17-20": "17",
        }
        self.time_range = [11,14,17,20]
    def get_row_col(self, passed_date=None):

        if passed_date is None:
            today = datetime.date.today()
            return self.sheet.find(str(today))

        else:
            return self.sheet.find(str(passed_date))

    def get_slots(self, date, barber):

        ls = ["8-11", "11-14", "14-17", "17-20"]
        slots_list = []

        today = datetime.datetime.now()
        cur_hour = today.time().hour

        cell = self.get_row_col(date)
        _row = cell.row if barber == "1" else cell.row + 1
        parts_list = self.sheet.row_values(_row)[2:6]

        if str(today.date()) == date:
            for j,i in zip(range(len(ls)),enumerate(parts_list)):
                if cur_hour <= self.time_range[j] and self.part_threshold[i[0]] > int(i[1]):
                    slots_list.append(ls[j])
            return slots_list
        
        for i in enumerate(parts_list):
            if self.part_threshold[i[0]] > int(i[1]):
                slots_list.append(ls[i[0]])

        return slots_list

    def add_appointment(self, part, details, barber, date):

        cell = self.get_row_col(date)
        _row = cell.row if barber == "1" else cell.row + 1

        part_cell = self.part_dict[part] + str(_row)
        part_value = self.sheet.acell(part_cell).value

        len_row = self.sheet.row_values(_row)

        self.sheet.update_cell(_row, (len(len_row) + 1), details)
        self.sheet.update_acell(part_cell, str(int(part_value)+1))

        hour_added = int(self.part_time[part]) 
        minute_added = int(part_value) * self.duration
        
        today = datetime.datetime.now()
        cur_hour = today.time().hour
        print(today)
        cur = datetime.datetime.strptime(date,'%Y-%m-%d') + datetime.timedelta(hours=hour_added,minutes=minute_added)
        if str(today.date()) == date and cur_hour < cur.hour:
            cur = today + datetime.timedelta(minutes=20+int(part_value) * self.duration)
            
        return cur