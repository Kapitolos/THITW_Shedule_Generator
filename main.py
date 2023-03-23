import csv
import random
import datetime
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import Calendar
import calendar
from datetime import date, timedelta
import json
import tkinter.ttk as ttk



booked_dates = None


def display_calendar(listbox, staff_name):
    def update_calendar():
        # Get the current year and month from the Calendar widget
        month, _, year = cal.get_date().split('/')

        # Convert year and month to integers
        year = int(year)
        if year < 100:
            year += 2000
        month = int(month)
        # print(year)
        # print(month)

        # Create a calendar object and get the dates for the current month
        cal_obj = calendar.Calendar()
        month_dates = cal_obj.itermonthdates(year, month)

        # Keep track of the date labels that are created
        date_labels = []

        # Iterate through the dates and create labels for each date
        for i, date in enumerate(month_dates):
            if date.month == month:
                row, column = divmod(i, 7)
                date_label = tk.Label(cal_frame, text=date.strftime('%d').lstrip('0'))

                # Check if the date is booked off for the selected staff member
                staff_name = cal_frame.master.title()

                #toms try
                # for availability in staff_availability.items():
                #     booked_off_dates_list = availability.get("booked_off_dates", [])
                #     booked_off_dates_list = [datetime.datetime.strptime(d, '%Y-%m-%d') for d in booked_off_dates_list]
                #     booked_off_dates_list = [date.strftime('%Y-%m-%d') for date in booked_off_dates_list]
                #     booked_off_dates = []
                #     for d in booked_off_dates_list:
                #         booked_off_dates.append(str(d))

                #chattry
                booked_off_dates = []
                booked_off_dates_list = staff_availability[staff_name].get('booked_off_dates', [])
                # print("booked_off_dates_list", booked_off_dates_list)
                booked_off_dates_list = [datetime.datetime.strptime(d, '%Y-%m-%d') for d in booked_off_dates_list]
                booked_off_dates_list = [date.strftime('%Y-%m-%d') for date in booked_off_dates_list]
                for d in booked_off_dates_list:
                    booked_off_dates.append(str(d))
                    # print(booked_off_dates)
                date_str = date.strftime('%Y-%m-%d')
                if date_str in booked_off_dates:
                    date_label.config(fg='red')
                    # print("IT IS IN THERE")

                # print(f'staff_name: {staff_name}, booked_off_dates: {booked_off_dates}, date: {date_str}')
                if staff_name in staff_availability and date_str in booked_off_dates:
                    # print("THIS IS THE BIG ONE")
                    date_label.config(fg='yellow')

                date_label.grid(row=row, column=column)
                date_labels.append(date_label)

        # Destroy the date labels that were created in the previous call to update_calendar()
        for label in date_labels:
            label.destroy()

        # Update the calendar frame with the new dates
        cal_frame.update()


    def update_availability():
        # Get the selected date from the Calendar widget
        selected_date = cal.get_date()
        selected_date_obj = datetime.datetime.strptime(selected_date, "%m/%d/%y")
        selected_date = selected_date_obj.strftime("%Y-%m-%d")

        # Check if the staff member is already booked off for the selected date
        if selected_date in staff_availability[staff_name]["booked_off_dates"]:
            # If yes, remove the date from the booked_off_dates list
            staff_availability[staff_name]["booked_off_dates"].remove(selected_date)
            generate_json(staff_availability, 'staff_availability.json')
            print(f"{staff_name} is now available on {selected_date}")
        else:
            # If not, add the date to the booked_off_dates list
            staff_availability[staff_name]["booked_off_dates"].append(selected_date)
            generate_json(staff_availability, 'staff_availability.json')
            print(f"{staff_name} is now unavailable on {selected_date}")
        update_calendar()

    # Create a new top-level window for the calendar
    cal_win = tk.Toplevel(app)
    cal_win.title(staff_name)

    cal = Calendar(cal_win, selectmode="day")
    cal.pack(padx=10, pady=10)

    toggle_button = tk.Button(cal_win, text="Toggle Availability", command=update_availability)
    toggle_button.pack(pady=10)

    cal_frame = tk.Frame(cal_win)
    cal_frame.config(bg='blue')  # set the background color to blue
    cal_frame.pack()

    cal_style = ttk.Style(cal_win)
    cal_style.configure('Calendar', background='blue')  # set the background color of the calendar widget to blue


    update_calendar()

    def on_close():
        # update the staff name in the listbox when the calendar is closed
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(listbox.get(0, tk.END).index(staff_name))

        # destroy the calendar window
        cal_win.destroy()

    # code for creating the calendar window and widgets

    cal_win.protocol("WM_DELETE_WINDOW", on_close)

    # Keep the calendar window open until it is closed
    cal_win.wait_window(cal_win)



def save_schedule_to_csv(schedule, start_date, filename, shifts_assigned_count):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)

        # Write header row
        header_row = ["Shift"]
        for day in schedule.keys():
            current_date = start_date + datetime.timedelta(days=list(schedule.keys()).index(day))
            holiday_name = holidays.get(current_date, "")
            holiday_str = f' ({holiday_name})' if holiday_name else ""
            header_row.append(f'{day} ({current_date}){holiday_str}')
        header_row.append("Shift Counts")  # Add a new column for shift counts
        csvwriter.writerow(header_row)

        # Write the schedule data
        shifts = ["Bothams_lunch", "Bothams_evening", "Hole_evening"]
        max_rows = max(len(shifts), len(shifts_assigned_count))
        for i in range(max_rows):
            row = []

            if i < len(shifts):
                shift = shifts[i]
                row.append(shift)
                for day, shifts_in_day in schedule.items():
                    assigned_staff = shifts_in_day[shift]

                    # Join assigned staff and their start times
                    shift_times = {
                        "Bothams_lunch": ["10am", "11am"],
                        "Bothams_evening": ["4pm", "5pm"],
                        "Hole_evening": ["4pm", "6pm"]
                    }[shift]
                    assigned_staff_with_start_times = [f'{staff} ({shift_times[i % len(shift_times)]})' for i, staff in
                                                       enumerate(assigned_staff)]

                    # Sort the assigned staff by their start times
                    assigned_staff_with_start_times.sort(key=lambda x: x.split(' ')[-1])
                    row.append(", ".join(assigned_staff_with_start_times))
            else:
                row.extend([''] * (len(schedule) + 1))

            # Add the shift counts vertically
            if i < len(shifts_assigned_count):
                staff_member, count = list(shifts_assigned_count.items())[i]
                row.append(f'{staff_member}: {count}')
            csvwriter.writerow(row)

        # Write a row with empty cells to add spacing
        csvwriter.writerow([''] * (len(schedule) + 2))

def get_start_date(year, month, day):
    date = datetime.date(year, month, day)
    start_date = date - datetime.timedelta(days=date.weekday())
    return start_date

def get_end_date(start_date):
    end_date = start_date + datetime.timedelta(days=6)
    return end_date

def get_servers_needed(day, shift_type, shift):
    # Determine how many servers are needed for a given shift
    if shift_type == "lunch":
        if shift == "Bothams_lunch":
            if day in ["Friday", "Saturday", "Sunday"]:
                return 2
            else:
                return 1
    elif shift_type == "evening":
        if shift == "Hole_evening":
            return 2
        elif shift == "Bothams_evening":
            if day in ["Friday", "Saturday"]:
                return 3
            else:
                return 2
    return 0

holidays = {
    datetime.date(2023, 1, 1): "New Year's Day",
    datetime.date(2023, 2, 20): "Family Day",
    datetime.date(2023, 3, 17): "St. Patrick's Day",
    datetime.date(2023, 4, 7): "Good Friday",
    datetime.date(2023, 4, 10): "Easter Monday",
    datetime.date(2023, 5, 22): "Victoria Day",
    datetime.date(2023, 7, 1): "Canada Day",
    datetime.date(2023, 8, 7): "Civic Holiday",
    datetime.date(2023, 9, 4): "Labour Day",
    datetime.date(2023, 10, 9): "Thanksgiving Day",
    datetime.date(2023, 10, 31): "Halloween",
    datetime.date(2023, 11, 11): "Remembrance Day",
    datetime.date(2023, 12, 25): "Christmas Day",
    datetime.date(2023, 12, 26): "Boxing Day",
}

staff_availability = {}

def read_availability_from_json():
    with open('staff_availability.json', 'r') as file:
        availability = json.load(file)
    return availability

staff_availability = read_availability_from_json()
# print(staff_availability)

def parse_date(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

def generate_schedule(staff_availability, start_date):

    end_date = get_end_date(start_date)
    # print("FUNCTION TERMS")
    # Define the shifts and their start times
    shifts = {
        "Bothams_lunch": ["Bothams", "lunch", ["10am", "11am"]],
        "Bothams_evening": ["Bothams", "evening", ["4pm", "5pm"]],
        "Hole_evening": ["Hole", "evening", ["4pm", "6pm"]]
    }
    # print(shifts)

    schedule = {
        "Monday": {shift: [] for shift in shifts},
        "Tuesday": {shift: [] for shift in shifts},
        "Wednesday": {shift: [] for shift in shifts},
        "Thursday": {shift: [] for shift in shifts},
        "Friday": {shift: [] for shift in shifts},
        "Saturday": {shift: [] for shift in shifts},
        "Sunday": {shift: [] for shift in shifts}
    }

    # Define the max shifts per week for each staff member
    max_shifts_per_week = {
        "Thomas": 4,
        "Erica": 1,
        "Dayle": 3,
        "Chad": 2
    }
    for staff in staff_availability.keys():
        if staff not in max_shifts_per_week:
            max_shifts_per_week[staff] = 5

    shifts_assigned_count = {staff: 0 for staff in staff_availability.keys()}

    for day, shifts_in_day in schedule.items():
        for shift, assigned_staff in shifts_in_day.items():
            assigned_staff = []  # Initialize assigned_staff outside of the loop
            venue, shift_type = shifts[shift][:2]

            servers_needed = get_servers_needed(day, shift_type, shift)

            available_staff = []

            for staff, availability in staff_availability.items():
                if venue in availability and shift_type in availability[venue] and day in availability[venue][shift_type]:
                    booked_off_dates_list = availability.get("booked_off_dates", [])
                    current_date = start_date + datetime.timedelta(days=list(schedule.keys()).index(day))
                    booked_off_dates_list = [datetime.datetime.strptime(d, '%Y-%m-%d') for d in booked_off_dates_list]
                    booked_off_dates_list = [date.strftime('%Y-%m-%d') for date in booked_off_dates_list]
                    booked_off_dates = []
                    for d in booked_off_dates_list:
                        booked_off_dates.append(str(d))
                    if str(current_date) not in booked_off_dates:
                        available_staff.append(staff)


            random.shuffle(available_staff)
            available_staff.sort(key=lambda staff: shifts_assigned_count[staff])

            for staff in available_staff:
                if shifts_assigned_count[staff] < max_shifts_per_week[staff] and len(assigned_staff) < servers_needed:
                    assigned_staff.append(staff)
                    shifts_assigned_count[staff] += 1

            # Add the assigned staff to the schedule for the current shift and day
            schedule[day][shift] = assigned_staff


    # Print the schedule for the week
    print("Weekly Schedule:")
    print("---------------")
    for day, shifts_in_day in schedule.items():
        current_date = start_date + datetime.timedelta(days=list(schedule.keys()).index(day))
        holiday_name = holidays.get(current_date, "")
        holiday_str = f' ({holiday_name})' if holiday_name else ""
        print(f'{day} ({current_date}){holiday_str}:')
        for shift, assigned_staff in shifts_in_day.items():
            shift_times = shifts[shift][2]
            if shift == "Bothams_evening":
                assigned_staff_with_start_times = [f'{staff} ({shift_times[i % len(shift_times)]})' for i, staff in
                                                   enumerate(assigned_staff)]
            elif shift == "Hole_evening":
                assigned_staff_with_start_times = [f'{staff} ({shift_times[i % 2]})' for i, staff in
                                                   enumerate(assigned_staff)]
            else:
                assigned_staff_with_start_times = [f'{staff} ({shift_times[i % len(shift_times)]})' for i, staff in
                                                   enumerate(assigned_staff)]
            # Sort the assigned staff by their start times
            assigned_staff_with_start_times.sort(key=lambda x: x.split(' ')[-1])
            print("\t" + shift + ": " + ", ".join(assigned_staff_with_start_times))

    # Print the number of shifts for each staff member
    print("Shift Counts:")
    print("-------------")
    for staff_member, count in shifts_assigned_count.items():
        print(staff_member + ": " + str(count))

    return schedule, shifts_assigned_count  # Return both schedule and shifts_assigned_count

#pick your dates! Year, Month, Day.
start_date = get_start_date(2023, 3, 27)
schedule, shifts_assigned_count = generate_schedule(staff_availability, start_date)
save_schedule_to_csv(schedule, start_date, 'schedule.csv', shifts_assigned_count)



import tkinter as tk
from tkinter import filedialog



def browse_folder():
    folder_selected = filedialog.askdirectory()
    folder_path.set(folder_selected)

def generate_schedule_and_save():
    start_date_input = start_date_entry.get()
    year, month, day = map(int, start_date_input.split("-"))
    start_date = get_start_date(year, month, day)
    staff_availability = read_availability_from_json()
    schedule, shifts_assigned_count = generate_schedule(staff_availability, start_date)
    save_schedule_to_csv(schedule, start_date, folder_path.get() + "/schedule.csv", shifts_assigned_count)

#This is for the days off section
# Function to create the widgets
def create_widgets():
    global staff_listbox, booked_dates

    # Create the staff listbox
    staff_listbox = tk.Listbox(app)
    staff_listbox.pack(side=tk.LEFT, padx=10, pady=10)

    # Create a new frame for the booked dates
    booked_dates_frame = tk.Frame(app)
    booked_dates_frame.pack(side=tk.LEFT, padx=10, pady=10)
    booked_dates_frame.configure(bg="#FFFFCC")  # Set the background color

    # Create the booked dates Text widget inside the new frame
    booked_dates = tk.Text(booked_dates_frame, height=10, width=30)
    booked_dates.pack(side=tk.LEFT, padx=10, pady=10)

    # Add a scrollbar to the Text widget
    scrollbar = tk.Scrollbar(booked_dates_frame, orient=tk.VERTICAL)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar.config(command=booked_dates.yview)
    booked_dates.config(yscrollcommand=scrollbar.set)


def display_booked_days_off(event):
    # Get the selected staff member from the listbox
    try:
        staff_name = staff_listbox.get(staff_listbox.curselection())
    except:
        messagebox.showerror("Error", "Please select a staff member.")
        return

    # Get the booked days off for the selected staff member
    try:
        booked_days_off = staff_availability[staff_name]["booked_off_dates"]
    except:
        messagebox.showerror("Error", "No booked days off found for selected staff member.")
        return

    # Clear the existing text in the Text widget
    booked_dates.delete(1.0, tk.END)

    # Display the booked days off in the Text widget
    if booked_days_off:
        for date in booked_days_off:
            booked_dates.insert(tk.END, str(date) + "\n")
    else:
        booked_dates.insert(tk.END, "No booked days off for selected staff member.")



# Create the main app window
app = tk.Tk()
app.title("THITW Schedule Generator")
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", background="blue")
style.configure(".", foreground="white")
app.configure(bg="#cc3b33")

start_date_entry = tk.Entry(app)
start_date_entry.grid(row=0, column=1)

# Set the default start date to the next Monday
def next_monday():
    today = date.today()
    days_until_monday = (7 - today.weekday()) % 7
    return today + timedelta(days=days_until_monday)

start_date_entry.delete(0, tk.END)
start_date_entry.insert(0, next_monday().strftime("%Y-%m-%d"))

def create_staff_booked_days_off_window():
    global staff_listbox, booked_dates

    # Create the staff booked days off frame inside the main app window
    staff_frame = tk.Frame(app)
    staff_frame.grid(row=0, column=1, padx=5, pady=5)

    staff_frame.configure(bg="#cc3b33")

    # Create the staff listbox inside the staff frame
    # staff_listbox = tk.Listbox(staff_frame, height=10, width=20)
    # staff_listbox.pack(side=tk.TOP, padx=10, pady=10)

    for staff in staff_availability:
        staff_listbox.insert(tk.END, staff)

    staff_listbox.bind("<<ListboxSelect>>", display_booked_days_off)

    # Create the booked dates Text widget inside the staff frame
    booked_dates = tk.Text(staff_frame, height=10, width=15, wrap="word")
    booked_dates.pack(padx=10, pady=10)

def open_calendar(staff_listbox):
    # Check if a staff member has been selected
    if staff_listbox.curselection():
        # Get the selected staff member from the listbox
        staff_name = staff_listbox.get(staff_listbox.curselection())

        # Call the function to create the staff booked days off window
        # create_staff_booked_days_off_window()

        # Call the display_calendar function with the staff name as an argument
        display_calendar(staff_listbox, staff_name)
    else:
        messagebox.showerror("Error", "Please select a staff member.")


# Create the start date input widgets
start_date_label = tk.Label(app, text="Enter start date (YYYY-MM-DD):")
start_date_label.grid(row=1, column=1, padx=10)
start_date_entry = tk.Entry(app)
start_date_entry.grid(row=2, column=1)

# Set the default start date to next Monday
start_date_entry.delete(0, tk.END)
start_date_entry.insert(0, next_monday().strftime("%Y-%m-%d"))

# Create the staff listbox
staff_listbox = tk.Listbox(app)
for staff_name in staff_availability.keys():
    staff_listbox.insert(tk.END, staff_name)
staff_listbox.grid(row=0, column=0, padx=20, pady=20)

#create staff days off window
create_staff_booked_days_off_window()

# Create the Open Calendar button
open_calendar_button = tk.Button(app, text="Open Calendar", command=lambda: open_calendar(staff_listbox), bg="#87CEFA", fg="white", font=("Arial", 12))
open_calendar_button.grid(row=3, column=3, padx=10, pady=10)

# Create the Select Folder label and button
folder_label = tk.Label(app, text="Select folder to save schedule:")
folder_label.grid(row=1, column=0, padx=20)
folder_path = tk.StringVar()
folder_path_entry = tk.Entry(app, textvariable=folder_path, width=20)
folder_path_entry.grid(row=2, column=0, pady=10)
browse_button = tk.Button(app, text="Browse", command=browse_folder, bg="#87CEFA", fg="white", font=("Arial", 12))
browse_button.grid(row=3, column=0)

# Create the Generate Schedule button
generate_button = tk.Button(app, text="Generate Schedule", command=generate_schedule_and_save, bg="#23dca6", fg="white", font=("Arial", 12))
generate_button.grid(row=3, column=1, pady=10)

def generate_json(staff_availability, filename):
    # print(staff_availability)
    with open(filename, 'w') as f:
        json.dump(staff_availability, f, indent=4)
    print(f'Shifts saved to {filename}.')

def save_and_exit():
    generate_json(staff_availability, 'staff_availability.json')
    app.destroy()

app.protocol("WM_DELETE_WINDOW", save_and_exit)
app.mainloop()

