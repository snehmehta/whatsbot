import gspread
import datetime
import string

from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "E:\\whatsbot\\New folder\\Whatsbot-58a18b101200.json", scopes=scope)

client = gspread.authorize(creds)
all_sheet = client.open("Whatsbot appointment")
sheet = all_sheet.worksheet("Sheet1")

part_threshold = [10, 10, 10, 10]

part_dict = {
    "part1": "C",
    "part2": "D",
    "part3": "E",
    "part4": "F",
}


def get_row_col(passed_date=None):

    if passed_date is None:
        today = datetime.date.today()
        cell = sheet.find(str(today))
        return cell
    else:
        # Find date which is passed 
        print("working on it")
        pass

def get_slots():

    ls = ["8-11", "11-2", "2-5", "5-8"]
    cell = get_row_col()
    parts_list = sheet.row_values(cell.row)[2:6]
    slots_list = []
    for i in enumerate(parts_list):
        if part_threshold[i[0]] > int(i[1]):
            slots_list.append(ls[i[0]])

    return slots_list


def add_appointment(part,details,barber):
    # Also add which barber 
    cell = get_row_col()
    _row = cell.row if barber == "1" else cell.row + 1

    part_cell = part_dict[part] + str(_row)
    parts_1 = sheet.acell(part_cell).value

    len_row = sheet.row_values(_row)

    sheet.update_cell(_row, (len(len_row) + 1), details)
    sheet.update_acell(part_cell, str(int(parts_1)+1))
add_appointment("part1","Awesome","1")