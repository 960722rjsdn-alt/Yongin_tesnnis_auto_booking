# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import json
import os
import datetime
import calendar

# --- Constants ---
CONFIG_FILENAME = "C:\\Users\\96072\\Desktop\\TIL\\용인 테니스 예약\\reservation_config.json"
COURTS_MASTER_LIST_FILENAME = "C:\\Users\\96072\\Desktop\\TIL\\용인 테니스 예약\\all_courts_master_list.json"

# --- Helper Functions ---
def get_next_month_days():
    """Generates a list of strings for each day of the next month, formatted with the day of the week."""
    today = datetime.date.today()
    # Move to the first day of the current month, then add 32 days to guarantee getting into the next month.
    next_month_date = today.replace(day=1) + datetime.timedelta(days=32)
    year = next_month_date.year
    month = next_month_date.month
    
    _, num_days = calendar.monthrange(year, month)
    days_list = []
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    
    for day in range(1, num_days + 1):
        date_obj = datetime.date(year, month, day)
        day_of_week = weekdays[date_obj.weekday()]
        days_list.append(f"{day:02d} ({day_of_week})")
    return days_list

def get_time_slots():
    """Returns a list of standard 2-hour time slots."""
    return [f"{h:02d}:00 ~ {h+2:02d}:00" for h in range(6, 22, 2)]

# --- Main GUI Function ---
def get_preferences_from_gui():
    """GUI to set user, court priorities, dates, and times."""
    root = tk.Tk()
    root.title("테니스 예약 설정")
    root.geometry("1000x800") # Increased size for new elements

    # --- Data Variables ---
    final_preferences = {}
    user_choice = tk.StringVar(value="안건우")

    # --- Main Frames ---
    top_frame = tk.Frame(root)
    top_frame.pack(pady=10, padx=10, fill="x")
    
    middle_frame = tk.Frame(root)
    middle_frame.pack(pady=10, padx=10, fill="x", expand=True)
    
    bottom_frame = tk.Frame(root)
    bottom_frame.pack(pady=10, padx=10, fill="x", expand=True) # Expanded for new listbox

    # --- User Selection ---
    user_frame = tk.LabelFrame(top_frame, text="사용자 선택")
    user_frame.pack(fill="x")
    tk.Radiobutton(user_frame, text="안건우", variable=user_choice, value="안건우").pack(side=tk.LEFT, padx=10)
    tk.Radiobutton(user_frame, text="박지은", variable=user_choice, value="박지은").pack(side=tk.LEFT, padx=10)

    # --- Court Selection ---
    courts_frame = tk.Frame(middle_frame)
    courts_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5)

    tk.Label(courts_frame, text="예약 가능 코트").pack()
    available_courts_listbox = tk.Listbox(courts_frame, selectmode=tk.MULTIPLE, exportselection=False)
    available_courts_listbox.pack(fill="both", expand=True)

    # --- Priority Selection ---
    priority_frame = tk.Frame(middle_frame)
    priority_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5)
    
    tk.Label(priority_frame, text="예약 우선순위").pack()
    priority_listbox = tk.Listbox(priority_frame, exportselection=False)
    priority_listbox.pack(fill="both", expand=True)

    # --- Court Control Buttons ---
    court_buttons_frame = tk.Frame(middle_frame)
    court_buttons_frame.pack(side=tk.LEFT, fill="y", padx=5)
    tk.Button(court_buttons_frame, text="추가 >>", command=lambda: add_selection(available_courts_listbox, priority_listbox)).pack(pady=5)
    tk.Button(court_buttons_frame, text="<< 제거", command=lambda: remove_selection(priority_listbox)).pack(pady=5)
    tk.Button(court_buttons_frame, text="▲ 위로", command=lambda: move_selection(priority_listbox, -1)).pack(pady=5)
    tk.Button(court_buttons_frame, text="▼ 아래로", command=lambda: move_selection(priority_listbox, 1)).pack(pady=5)

    # --- Date and Time Selection ---
    datetime_selection_frame = tk.Frame(bottom_frame)
    datetime_selection_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5)

    date_frame = tk.LabelFrame(datetime_selection_frame, text="날짜 선택 (다음 달)")
    date_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5)
    date_listbox = tk.Listbox(date_frame, selectmode=tk.SINGLE, exportselection=False) # Changed to SINGLE select
    date_listbox.pack(fill="both", expand=True)

    time_frame = tk.LabelFrame(datetime_selection_frame, text="시간 선택")
    time_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5)
    time_listbox = tk.Listbox(time_frame, selectmode=tk.MULTIPLE, exportselection=False)
    time_listbox.pack(fill="both", expand=True)

    # --- Date-Time Pair Control Buttons ---
    datetime_buttons_frame = tk.Frame(bottom_frame)
    datetime_buttons_frame.pack(side=tk.LEFT, fill="y", padx=5)
    tk.Button(datetime_buttons_frame, text="날짜/시간 추가 >>", command=lambda: add_datetime_pair()).pack(pady=5)
    tk.Button(datetime_buttons_frame, text="<< 날짜/시간 제거", command=lambda: remove_selection(datetime_pair_listbox)).pack(pady=5)

    # --- Selected Date-Time Pairs ---
    datetime_pair_frame = tk.LabelFrame(bottom_frame, text="선택된 날짜/시간 조합")
    datetime_pair_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5)
    datetime_pair_listbox = tk.Listbox(datetime_pair_frame, exportselection=False)
    datetime_pair_listbox.pack(fill="both", expand=True)


    # --- Populate Listboxes ---
    try:
        with open(COURTS_MASTER_LIST_FILENAME, 'r', encoding='utf-8') as f:
            for court in json.load(f):
                available_courts_listbox.insert(tk.END, court)
    except Exception as e:
        available_courts_listbox.insert(tk.END, "오류: 코트 목록 로딩 실패")
        print(f"마스터 코트 목록 로딩 오류: {e}")

    for day in get_next_month_days():
        date_listbox.insert(tk.END, day)
    
    for time_slot in get_time_slots():
        time_listbox.insert(tk.END, time_slot)

    # --- Listbox Control Functions ---
    def add_selection(source_box, dest_box):
        for i in source_box.curselection():
            item = source_box.get(i)
            if item not in dest_box.get(0, tk.END):
                dest_box.insert(tk.END, item)

    def remove_selection(box):
        for i in reversed(box.curselection()):
            box.delete(i)

    def move_selection(box, direction):
        for i in box.curselection():
            if 0 <= i + direction < box.size():
                text = box.get(i)
                box.delete(i)
                box.insert(i + direction, text)
                box.selection_set(i + direction)

    def add_datetime_pair():
        selected_dates_indices = date_listbox.curselection()
        selected_times_indices = time_listbox.curselection()

        if not selected_dates_indices or not selected_times_indices:
            messagebox.showerror("입력 오류", "날짜와 시간을 모두 선택해주세요.")
            return

        selected_date_str = date_listbox.get(selected_dates_indices[0]) # Only single selection for date
        selected_times = [time_listbox.get(i) for i in selected_times_indices]
        
        pair_display_str = f"{selected_date_str}: {', '.join(selected_times)}"
        
        # Store the actual data as a dictionary for easier processing later
        pair_data = {
            "date_display": selected_date_str, # For display in listbox
            "date_num": selected_date_str.split(' ')[0], # For booking logic
            "times": selected_times
        }

        # Check if this exact pair (date and times) already exists
        existing_pairs_data = [datetime_pair_listbox.get(i) for i in range(datetime_pair_listbox.size())]
        if pair_display_str in existing_pairs_data: # Simple string check for display
            messagebox.showinfo("중복", "이미 추가된 날짜/시간 조합입니다.")
            return

        datetime_pair_listbox.insert(tk.END, pair_display_str)
        # Store the actual data in a hidden way or re-parse from display string later
        # For now, we'll rely on re-parsing from the display string or storing in a global list.
        # Let's use a global list to store the actual data.
        # This requires changing final_preferences to be a list of these dicts.
        # Or, we can just re-parse from the display string in on_submit.
        # Re-parsing is simpler for now.

    # --- Load Saved Config ---
    if os.path.exists(CONFIG_FILENAME):
        try:
            with open(CONFIG_FILENAME, 'r', encoding='utf-8') as f:
                config = json.load(f)
                user_choice.set(config.get("user", "안건우"))
                
                for court in config.get("courts", []):
                    priority_listbox.insert(tk.END, court)
                
                for i, day_str in enumerate(date_listbox.get(0, tk.END)):
                    day_num = day_str.split(' ')[0]
                    if day_num in config.get("dates", []):
                        date_listbox.selection_set(i)

                for i, time_str in enumerate(time_listbox.get(0, tk.END)):
                    if time_str in config.get("times", []):
                        time_listbox.selection_set(i)
        except Exception as e:
            print(f"설정 파일 로딩 오류: {e}")

    # --- Submit Button and Logic ---
    def on_submit():
        nonlocal final_preferences
        
        courts = list(priority_listbox.get(0, tk.END))
        
        # Parse datetime pairs from the listbox
        datetime_pairs_raw = [datetime_pair_listbox.get(i) for i in range(datetime_pair_listbox.size())]
        datetime_pairs_processed = []
        for pair_str in datetime_pairs_raw:
            try:
                date_part, times_part = pair_str.split(': ', 1)
                date_num = date_part.split(' ')[0] # Extract just the number
                times = [t.strip() for t in times_part.split(', ')]
                datetime_pairs_processed.append({"date_display": date_part, "date_num": date_num, "times": times})
            except Exception as e:
                print(f"날짜/시간 조합 파싱 오류: {pair_str} - {e}")
                continue


        if not all([courts, datetime_pairs_processed]):
            messagebox.showerror("입력 오류", "코트와 날짜/시간 조합을 각각 하나 이상 선택해야 합니다.")
            return

        final_preferences = {
            "user": user_choice.get(),
            "courts": courts,
            "datetime_pairs": datetime_pairs_processed
        }
        
        try:
            with open(CONFIG_FILENAME, 'w', encoding='utf-8') as f:
                json.dump(final_preferences, f, ensure_ascii=False, indent=4)
            print("예약 설정을 저장했습니다.")
        except Exception as e:
            print(f"설정 파일 저장 오류: {e}")
        
        root.destroy()

    submit_button = tk.Button(root, text="예약 시작", command=on_submit, font=("Helvetica", 12, "bold"))
    submit_button.pack(pady=20)

    root.mainloop()
    return final_preferences

if __name__ == '__main__':
    # For testing the GUI directly
    prefs = get_preferences_from_gui()
    if prefs:
        print("\n--- GUI Selections ---")
        print(json.dumps(prefs, indent=4, ensure_ascii=False))