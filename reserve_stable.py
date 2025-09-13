# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import time
import sys
import datetime

URL = "https://publicsports.yongin.go.kr/publicsports/sports/index.do"

def main():
    if len(sys.argv) < 2:
        print("사용법: python reserve.py [안건우/박지은]")
        return

    user_choice = sys.argv[1]
    USER_NAME, USER_BIRTHDATE, USER_GENDER_DIGIT, USER_PHONE_NUMBER, USER_MVNO_CODE, USER_MVNO_NAME = "", "", "", "", "", ""

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
    main_window = driver.current_window_handle

    try:
        login_link = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='gnb']//a[contains(@href, 'groupYn=N')]")))
        driver.execute_script("arguments[0].click();", login_link)
        print("개인로그인 페이지로 이동합니다.")
        
        phone_auth_button = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "휴대폰 인증")))
        phone_auth_button.click()
        print("휴대폰 인증 팝업을 열었습니다.")
        
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
        time.sleep(1)

        for field_class, value in [("input.userName", USER_NAME), ("input.myNum1", USER_BIRTHDATE), ("input.myNum2", USER_GENDER_DIGIT), ("input.mobileNo", USER_PHONE_NUMBER)]:
            field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, field_class)))
            driver.execute_script("arguments[0].value = arguments[1];", field, value)
            for event in ['input', 'keyup', 'change', 'blur']:
                driver.execute_script(f"arguments[0].dispatchEvent(new Event('{event}', {{ bubbles: true }}));", field)
            print(f"{field_class} 정보를 입력했습니다.")

        print("휴대폰 인증 및 로그인이 완료될 때까지 기다립니다...")
        long_wait = WebDriverWait(driver, 120) # 2-minute timeout for manual authentication
        long_wait.until(EC.number_of_windows_to_be(1))
        driver.switch_to.window(main_window)
        long_wait.until(EC.presence_of_element_located((By.XPATH, "//a[text()='로그아웃']")))
        print("로그인 성공 및 메인 페이지 로딩을 확인했습니다.")

        print("일반예약 메뉴로 이동합니다 (강제클릭 방식)...")
        general_reservation_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'searchResveType=GNRLRESVE')]")))
        driver.execute_script("arguments[0].click();", general_reservation_link)
        
        wait.until(EC.presence_of_element_located((By.ID, "searchFcltyGu")))
        print("일반예약 페이지로 이동했습니다.")

        print("필터링을 시작합니다...")
        location_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "searchFcltyGu"))))
        location_dropdown.select_by_value("GIHEGU")
        print("'기흥구'를 선택했습니다.")
        
        tennis_filter_label = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[text()='테니스']")))
        driver.execute_script("arguments[0].click();", tennis_filter_label)
        print("'테니스' 필터를 적용합니다.")
        
        search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(@class, 'search_btn')]")))
        search_button.click()
        print("'검색' 버튼을 클릭합니다.")
        
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "reserve_box_item")))

        TARGET_COURT_NAME = "기흥 테니스장(D코트)"
        print(f"'{TARGET_COURT_NAME}' 코트를 찾아서 '상세보기'를 클릭합니다...")
        court_items = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "reserve_box_item")))
        target_found = False
        for item in court_items:
            try:
                title_element = item.find_element(By.CLASS_NAME, "reserve_title")
                if TARGET_COURT_NAME in title_element.text:
                    print(f"타겟 '{title_element.text.strip()}'을 찾았습니다.")
                    details_button = item.find_element(By.PARTIAL_LINK_TEXT, "상세보기")
                    driver.execute_script("arguments[0].click();", details_button)
                    target_found = True
                    break
            except Exception as e:
                print(f"리스트 항목 처리 중 오류: {e}")
        
        if not target_found:
            print(f"'{TARGET_COURT_NAME}'을 찾을 수 없습니다.")
        else:
            print("상세보기 페이지로 이동했습니다.")
            
            # Wait until 09:00
            target_time = datetime.datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
            now = datetime.datetime.now()
            if now < target_time:
                wait_seconds = (target_time - now).total_seconds()
                print(f"09:00까지 {wait_seconds:.0f}초 동안 대기합니다...")
                time.sleep(wait_seconds)
            
            print("09:00이 되었습니다. '예약하기' 버튼이 나타날 때까지 새로고침을 시작합니다.")
            
            # Refresh loop to find the button
            while True:
                try:
                    short_wait = WebDriverWait(driver, 2)
                    reserve_button = short_wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='예약하기']")))
                    print("'예약하기' 버튼을 찾았습니다. 클릭합니다.")
                    reserve_button.click()
                    break
                except:
                    print("'예약하기' 버튼을 찾을 수 없습니다. 1초 후 새로고침합니다.")
                    time.sleep(1)
                    driver.refresh()

            TARGET_DAY = "24"
            # Wait for the calendar page to be ready by waiting for the date button to be clickable
            day_button_xpath = f"//td[@attr='202509{TARGET_DAY}']//button"
            wait.until(EC.element_to_be_clickable((By.XPATH, day_button_xpath)))
            print("최종 예약 달력 페이지로 이동했습니다.")

            # --- Select Date and Save Page ---
            print(f"9월 {TARGET_DAY}일을 선택합니다.")
            day_button_xpath = f"//td[@attr='202509{TARGET_DAY}']//button"
            day_button = wait.until(EC.element_to_be_clickable((By.XPATH, day_button_xpath)))
            day_button.click()
            
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".time_cell:not([disabled])")))
            print("날짜를 선택했습니다. 시간 슬롯을 확인합니다.")

            available_slots = driver.find_elements(By.CSS_SELECTOR, ".time_cell:not([disabled])")
            if available_slots:
                print(f"{len(available_slots)}개의 예약 가능한 시간대를 찾았습니다.")
                # Click the first available slot
                first_slot = available_slots[0]
                slot_time = first_slot.text
                print(f"시간대 '{slot_time}'를 선택합니다.")
                first_slot.click()
                print("시간대를 클릭했습니다.")
                time.sleep(3) # Increased wait time

                # Manually trigger the javascript function
                print("자바스크립트 함수를 직접 호출합니다.")
                driver.execute_script("convertTmPicker();")
                time.sleep(1)

                # Submit the form directly
                print("폼을 직접 제출합니다.")
                driver.execute_script("document.getElementById('fcltyRceptRsvctmVO').submit();")
                
                wait.until(EC.presence_of_element_located((By.ID, "purposeOfUse")))

                # --- Final Reservation Step ---
                print("최종 예약 단계로 이동했습니다.")

                try:
                    # Check agreement checkboxes
                    print("약관에 동의합니다.")
                    agree_labels = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//label[contains(., '위 내용에 동의합니다.')]")))
                    for label in agree_labels:
                        driver.execute_script("arguments[0].click();", label)

                    # Enter purpose of use
                    print("사용 목적을 입력합니다.")
                    purpose_input = wait.until(EC.presence_of_element_located((By.ID, "purposeOfUse")))
                    purpose_input.send_keys("테니스 연습")

                    # Handle CAPTCHA
                    captcha_image = wait.until(EC.presence_of_element_located((By.ID, "image")))
                    captcha_text = captcha_image.text
                    print(f"CAPTCHA 텍스트를 추출했습니다: {captcha_text}")
                    
                    captcha_input = wait.until(EC.presence_of_element_located((By.ID, "captcha")))
                    captcha_input.send_keys(captcha_text)
                    print("CAPTCHA를 자동으로 입력했습니다.")

                    # Click the final submit button
                    print("신청완료 버튼을 클릭합니다.")
                    submit_button = wait.until(EC.element_to_be_clickable((By.ID, "registSubmit")))
                    submit_button.click()

                    # Handle the confirmation alert
                    alert = wait.until(EC.alert_is_present())
                    print(f"Alert text: {alert.text}")
                    alert.accept()
                    print("확인 창을 수락했습니다.")

                    # Handle the completion alert
                    alert = wait.until(EC.alert_is_present())
                    print(f"Alert text: {alert.text}")
                    alert.accept()
                    print("완료 창을 수락했습니다.")

                    print("예약 신청이 완료되었습니다.")
                    time.sleep(5)
                except Exception as e:
                    print(f"최종 예약 단계에서 오류 발생: {e}")
                    with open("final_page_error.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    print("오류 발생 시점의 페이지를 final_page_error.html 로 저장했습니다.")
                    raise e

            else:
                print("예약 가능한 시간대가 없습니다.")

            with open("timeslot_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("timeslot_page.html 파일이 저장되었습니다.")

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
    finally:
        print("자동화 프로그램을 종료합니다.")
        driver.quit()

if __name__ == "__main__":
    main()