# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
import time
import datetime
import calendar
import re

URL = "https://publicsports.yongin.go.kr/publicsports/sports/index.do"

def get_next_month_str():
    """Gets the next month in YYYYMM format."""
    today = datetime.date.today()
    next_month_date = today.replace(day=1) + datetime.timedelta(days=32)
    return next_month_date.strftime('%Y%m')

def finish_booking(driver, wait, booked_slots, datetime_pairs):
    """
    현재 탭에서 사용자가 선택한 날짜와 시간으로 예약을 시도합니다.
    중복 예약을 방지하고, 예약 불가능한 날짜를 건너뜁니다.
    """
    try:
        print(f"Tab {driver.current_window_handle}: 예약 절차 진행...")
        next_month_str = get_next_month_str()

        for pair in datetime_pairs:
            day = pair["date_num"]
            times_to_try = pair["times"]

            try:
                day_button_xpath = f"//td[@attr='{next_month_str}{day}']//button"
                day_button = wait.until(EC.element_to_be_clickable((By.XPATH, day_button_xpath)))
                print(f"날짜 '{day}일'을 선택합니다.")
                day_button.click()
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".time_cell:not([disabled])")))
            except TimeoutException:
                print(f"날짜 '{day}일'은 선택할 수 없습니다 (예약 마감 등).")
                continue

            available_slots = driver.find_elements(By.CSS_SELECTOR, ".time_cell:not([disabled])")
            for slot in available_slots:
                slot_time = slot.text
                if slot_time not in times_to_try:
                    continue

                if (day, slot_time) in booked_slots:
                    print(f"시간대 '{day}일 {slot_time}'는 이미 다른 코트에서 예약되었습니다. 건너뜁니다.")
                    continue

                try:
                    print(f"시간대 '{day}일 {slot_time}' 예약을 시도합니다.")
                    slot.click()
                    time.sleep(1)

                    driver.execute_script("convertTmPicker();")
                    time.sleep(1)
                    driver.execute_script("document.getElementById('fcltyRceptRsvctmVO').submit();")
                    
                    wait.until(EC.presence_of_element_located((By.ID, "purposeOfUse")))
                    
                    driver.find_element(By.XPATH, "//label[contains(., '위 내용에 동의합니다.')]").click()
                    driver.find_element(By.ID, "purposeOfUse").send_keys("테니스 연습")
                    
                    captcha_text = driver.find_element(By.ID, "image").text
                    driver.find_element(By.ID, "captcha").send_keys(captcha_text)
                    
                    driver.find_element(By.ID, "registSubmit").click()

                    wait.until(EC.alert_is_present()).accept()
                    wait.until(EC.alert_is_present()).accept()

                    booked_slots.add((day, slot_time))
                    print(f"Tab {driver.current_window_handle}: '{day}일 {slot_time}' 예약 신청이 완료되었습니다.")
                    return True

                except Exception as e:
                    print(f"시간대 '{day}일 {slot_time}' 예약 시도 중 오류({type(e).__name__}) 발생. 다음 시간대를 시도합니다.")
                    driver.refresh()
                    try:
                        re_day_button = wait.until(EC.element_to_be_clickable((By.XPATH, day_button_xpath)))
                        re_day_button.click()
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".time_cell:not([disabled])")))
                        available_slots = driver.find_elements(By.CSS_SELECTOR, ".time_cell:not([disabled])")
                    except Exception as refresh_e:
                        print(f"페이지 리셋 중 오류({type(refresh_e).__name__}). 이 날짜의 예약을 포기합니다.")
                        break
            
        print(f"'{day}일'에 예약 가능한 시간이 없습니다.")

    except Exception as e:
        print(f"Tab {driver.current_window_handle}: 예약 마무리 중 예측하지 못한 오류가 발생했습니다: {e}")
    
    return False

def run_booking_process(user_choice, court_preferences, datetime_pairs):
    if user_choice == "안건우":
        USER_NAME, USER_BIRTHDATE, USER_GENDER_DIGIT, USER_PHONE_NUMBER, USER_MVNO_CODE, USER_MVNO_NAME = "안건우", "960722", "1", "01088414913", "LGM", "LGU+ 알뜰폰"
    elif user_choice == "박지은":
        USER_NAME, USER_BIRTHDATE, USER_GENDER_DIGIT, USER_PHONE_NUMBER, USER_MVNO_CODE, USER_MVNO_NAME = "박지은", "940813", "2", "01062945578", "SKM", "SKT 알뜰폰"
    else:
        print("잘못된 이름입니다. '안건우' 또는 '박지은' 중 하나를 입력해주세요.")
        return

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 10)
    driver.get(URL)
    print("웹사이트를 열었습니다.")

    try:
        # --- 로그인 과정 (reserve_stable.py 로직 적용) ---
        login_link = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='gnb']//a[contains(@href, 'groupYn=N')] ")))
        driver.execute_script("arguments[0].click();", login_link)
        print("개인로그인 페이지로 이동합니다.")
        
        phone_auth_button = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "휴대폰 인증")))
        phone_auth_button.click()
        print("휴대폰 인증 팝업을 열었습니다.")
        
        main_window = driver.current_window_handle
        wait.until(EC.number_of_windows_to_be(2))
        for window_handle in driver.window_handles:
            if window_handle != main_window:
                driver.switch_to.window(window_handle)
                break
        print("팝업 창으로 전환했습니다.")
        
        mvno_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"button[onclick*='{USER_MVNO_CODE}']")))
        mvno_button.click()
        print(f"{USER_MVNO_NAME} 버튼을 클릭했습니다.")
        
        sms_auth_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li[aria-label='문자(SMS) 인증'] button")))
        sms_auth_button.click()
        print("문자(SMS) 인증 버튼을 클릭했습니다.")
        
        agree_checkbox = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "mobileCertAgree")))
        agree_checkbox.click()
        print("본인확인 이용 동의에 체크했습니다.")
        
        next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn_pass[data-action='next']")))
        next_button.click()
        print("다음 버튼을 클릭했습니다.")
        
        print("사용자 정보 입력을 시작합니다 (JS 값 설정 + 이벤트)...")
        time.sleep(1) # Added sleep from stable version

        for field_class, value in [("input.userName", USER_NAME), ("input.myNum1", USER_BIRTHDATE), ("input.myNum2", USER_GENDER_DIGIT), ("input.mobileNo", USER_PHONE_NUMBER)]:
            field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, field_class)))
            driver.execute_script("arguments[0].value = arguments[1];", field, value)
            for event in ['input', 'keyup', 'change', 'blur']:
                driver.execute_script(f"arguments[0].dispatchEvent(new Event('{event}', {{ bubbles: true }}));", field)
            print(f"{field_class} 정보를 입력했습니다.")

        # --- 사용자 수동 입력 (보안문자 및 최종 인증) ---
        print("\n!!! 사용자 직접 입력 필요 !!!")
        print("------------------------------------------------------------------")
        print("1. 브라우저에 보이는 '보안문자'를 직접 입력해주세요.")
        print("2. '다음' 버튼을 눌러주세요.") # Changed from '인증번호 요청'
        print("3. 휴대폰으로 전송된 인증번호를 입력하여 본인인증을 완료해주세요.")
        print("------------------------------------------------------------------")

        print("휴대폰 인증 및 로그인이 완료될 때까지 기다립니다...")
        long_wait = WebDriverWait(driver, 120)
        long_wait.until(EC.number_of_windows_to_be(1))
        driver.switch_to.window(main_window)
        long_wait.until(EC.presence_of_element_located((By.XPATH, "//a[text()='로그아웃']")))
        print("로그인 성공 및 메인 페이지 로딩을 확인했습니다.")

        # --- 코트 목록 페이지로 이동 및 필터링 ---
        driver.execute_script("arguments[0].click();", wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'searchResveType=RESIDENT')] "))))
        wait.until(EC.presence_of_element_located((By.ID, "searchFcltyGu")))
        Select(wait.until(EC.presence_of_element_located((By.ID, "searchFcltyGu")))).select_by_value("GIHEGU")
        driver.execute_script("arguments[0].click();", wait.until(EC.element_to_be_clickable((By.XPATH, "//label[text()='테니스']"))))
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(@class, 'search_btn')] "))).click()
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "reserve_box_item")))
        
        # --- 모든 페이지의 코트 정보 수집 ---
        all_courts_data = []
        page = 1
        while True:
            for item in driver.find_elements(By.CLASS_NAME, "reserve_box_item"):
                try:
                    all_courts_data.append({"name": item.find_element(By.CLASS_NAME, "reserve_title").text, "url": item.find_element(By.PARTIAL_LINK_TEXT, "상세보기").get_attribute('href')})
                except: pass
            try:
                page += 1
                driver.find_element(By.XPATH, f"//a[@class='p-page__link' and text()='{page}']").click()
                time.sleep(2)
            except: break
        print(f"총 {len(all_courts_data)}개의 코트 정보를 수집했습니다.")

        # --- 예약 대상 URL 수집 ---
        target_urls = []
        added_court_names = set()
        for pref in court_preferences:
            desired_court_identifier = pref["name"]
            if desired_court_identifier in added_court_names: continue
            for court_data in all_courts_data:
                if desired_court_identifier in court_data["name"]:
                    target_urls.append(court_data["url"])
                    added_court_names.add(desired_court_identifier)
                    print(f"'{desired_court_identifier}' 코트의 URL을 수집했습니다.")
                    break

        # --- 새 탭에서 상세 페이지 열기 ---
        original_window = driver.current_window_handle
        for url in target_urls:
            driver.switch_to.new_window('tab')
            driver.get(url)
        all_tabs = driver.window_handles
        if original_window in all_tabs: all_tabs.remove(original_window)
        try:
            driver.switch_to.window(original_window)
            driver.close()
        except: pass
        print(f"{len(all_tabs)}개의 코트 상세 페이지를 새 탭에서 열었습니다.")

        # --- 지정 시간까지 대기 ---
        target_time = datetime.datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        if datetime.datetime.now() < target_time:
            print(f"09:00까지 {(target_time - datetime.datetime.now()).total_seconds():.0f}초 동안 대기합니다...")
            time.sleep((target_time - datetime.datetime.now()).total_seconds())
        print("09:00이 되었습니다. 모든 탭을 새로고침하고 예약을 시도합니다.")

        # --- 병렬 예약 시도 (Shotgun) ---
        successful_tabs = []
        for tab in all_tabs:
            driver.switch_to.window(tab)
            driver.refresh()
            try:
                short_wait = WebDriverWait(driver, 1)
                short_wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='예약하기']"))).click()
                print(f"Tab {tab}: '예약하기' 버튼 클릭 성공.")
                successful_tabs.append(tab)
            except:
                print(f"Tab {tab}: '예약하기' 버튼을 찾지 못함.")
        
        # --- 예약 마무리 작업 ---
        print(f"\n--- 총 {len(successful_tabs)}개의 예약 가능 탭을 확인했습니다. ---")
        booked_courts_count = 0
        total_courts_to_book = sum(p['courts_to_book'] for p in court_preferences)
        booked_slots = set()

        for tab in successful_tabs:
            if booked_courts_count >= total_courts_to_book:
                print("목표한 모든 코트의 예약이 완료되었습니다.")
                break
            
            driver.switch_to.window(tab)
            if finish_booking(driver, wait, booked_slots, datetime_pairs):
                booked_courts_count += 1

        print(f"\n--- 최종 예약 결과 ---")
        print(f"총 {booked_courts_count}개 코트 예약 성공")

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
    finally:
        print("자동화 프로그램을 종료합니다.")
        driver.quit()