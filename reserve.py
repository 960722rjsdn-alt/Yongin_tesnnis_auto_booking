# -*- coding: utf-8 -*-
from gui import get_preferences_from_gui
from booking_logic import run_booking_process

def main():
    """메인 실행 함수: GUI를 호출하고, 예약 프로세스를 시작합니다."""
    
    # GUI를 통해 사용자 설정 가져오기 (코트, 날짜, 시간 등)
    prefs = get_preferences_from_gui()
    
    if not prefs:
        print("GUI에서 설정을 완료하지 않았거나 창을 닫았습니다. 프로그램을 종료합니다.")
        return

    user_choice = prefs.get("user")
    court_prefs = prefs.get("courts")
    datetime_pairs = prefs.get("datetime_pairs") # New: list of {"date_display": ..., "date_num": ..., "times": [...]} 

    # courts를 booking_logic이 기대하는 형식으로 변환: [{"name": "...", "courts_to_book": 1}]
    court_preferences_obj = [{"name": name, "courts_to_book": 1} for name in court_prefs]

    print(f"'{user_choice}' 사용자로 예약을 시작합니다.")
    print(f"설정된 코트 우선순위: {court_prefs}")
    print(f"선택된 날짜/시간 조합: {datetime_pairs}")

    # 예약 프로세스 실행
    run_booking_process(user_choice, court_preferences_obj, datetime_pairs) # Updated arguments

if __name__ == "__main__":
    main()