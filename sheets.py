import datetime 

class Gspread():

    def __init__(self,sheet):
        self.sheet = sheet

        self.part_threshold = [10, 10, 10, 10]

        self.part_dict = {
            "part1": "C",
            "part2": "D",
            "part3": "E",
            "part4": "F",
        }

    def get_row_col(self,passed_date=None):

        if passed_date is None:
            today = datetime.date.today()
            cell = self.sheet.find(str(today))
            return cell
        else:
            # Find date which is passed 
            print("working on it")
            pass

    def get_slots(self):

        ls = ["8-11", "11-2", "2-5", "5-8"]
        cell = self.get_row_col()
        parts_list = self.sheet.row_values(cell.row)[2:6]
        slots_list = []
        for i in enumerate(parts_list):
            if self.part_threshold[i[0]] > int(i[1]):
                slots_list.append(ls[i[0]])

        return slots_list


    def add_appointment(self,part,details,barber):
        # Also add which barber 
        cell = self.get_row_col()
        _row = cell.row if barber == "1" else cell.row + 1

        part_cell = self.part_dict[part] + str(_row)
        parts_1 = self.sheet.acell(part_cell).value

        len_row = self.sheet.row_values(_row)

        self.sheet.update_cell(_row, (len(len_row) + 1), details)
        self.sheet.update_acell(part_cell, str(int(parts_1)+1))