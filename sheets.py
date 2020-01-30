import datetime
import helper
from IPython.core.debugger import set_trace

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
        self.time_range = [11, 14, 17, 20]

    def get_row_col(self, passed_date=None):

        if passed_date is None:
            today = helper.cur_time()
            today = today.date()
            return self.sheet.find(str(today))

        else:
            return self.sheet.find(str(passed_date))

    def get_slots(self, date, barber):

        ls = ["8-11", "11-14", "14-17", "17-20"]
        slots_list = []

        today = helper.cur_time()
        cur_hour = today.time().hour

        cell = self.get_row_col(date)
        _row = cell.row if barber == "1" else cell.row + 1
        parts_list = self.sheet.row_values(_row)[2:6]

        if str(today.date()) == date:
            for j, i in zip(range(len(ls)), enumerate(parts_list)):
                num_book = i[1].split('-')[0]
                if cur_hour < self.time_range[j] and self.part_threshold[i[0]] > int(num_book):
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
        temp = self.sheet.acell(part_cell).value
        part_value = temp.split("-")[0]  # get number of booking done uptil now
        part_last_value = temp.split("-")[1]
        len_row = self.sheet.row_values(_row)

        # enter details to last + 1 cell
        self.sheet.update_cell(_row, (len(len_row) + 1), details)

        hour_added = int(part_last_value.split(":")[0])
        minute_added = int(part_last_value.split(":")[0])

        cur_time = helper.cur_time()
        last_given_time = datetime.datetime.strptime(
            date, '%Y-%m-%d') + datetime.timedelta(hours=hour_added, minutes=minute_added)
        next_given_time = last_given_time + datetime.timedelta(minutes=20)
        next_given_time = helper.convert_timezone(next_given_time)

        print(cur_time,last_given_time,next_given_time)

        if str(cur_time.date()) == date and next_given_time < cur_time:

            next_given_time = cur_time + datetime.timedelta(minutes=20)
            next_given_time = helper.convert_timezone(next_given_time)
            print("TOday:",cur_time,last_given_time,next_given_time)

            # temp = self.sheet.acell(part_cell).value
            # last_time = temp.split("-")[1]
            # last_hour = int(last_time.split(":")[0])
            # last_minute = int(last_time.split(":")[1])
            # last_date_time = datetime.datetime(
            #     cur_time.year, cur_time.month, cur_time.day, last_hour, last_minute)
            # set_trace()s
            # if given_time < cur_time:
            #     given_time = cur_time + datetime.timedelta(minutes=20)

        self.sheet.update_acell(part_cell, str(
            int(part_value)+1) + "-" + str(next_given_time.time()))  # update value

        return next_given_time
