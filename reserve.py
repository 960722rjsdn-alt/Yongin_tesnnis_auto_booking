from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys # Import sys module

# 용인시 공공체육시설 통합예약 웹사이트
URL = "https://publicsports.yongin.go.kr/publicsports/sports/index.do"

def main():
    # 사용자 정보 입력 받기 (명령줄 인수로 받음)
    if len(sys.argv) < 2:
        print("사용법: python reserve.py [안건우/박지은]")
        print("정보를 입력할 이름을 명령줄 인수로 제공해주세요.")
        return # 스크립트 종료

    user_choice = sys.argv[1]

    USER_NAME = ""
    USER_BIRTHDATE = ""
    USER_GENDER_DIGIT = ""
    USER_PHONE_NUMBER = ""

    if user_choice == "안건우":
        USER_NAME = "안건우"
        USER_BIRTHDATE = "960722"
        USER_GENDER_DIGIT = "1"
        USER_PHONE_NUMBER = "01088414913"
    elif user_choice == "박지은":
        USER_NAME = "박지은"
        USER_BIRTHDATE = "940813"
        USER_GENDER_DIGIT = "2"
        USER_PHONE_NUMBER = "01062945578"
    else:
        print("잘못된 이름입니다. '안건우' 또는 '박지은' 중 하나를 입력해주세요.")
        return # 스크립트 종료

    # Chrome 드라이버 설정
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 10)
    
    # 웹사이트 열기
    driver.get(URL)
    print("웹사이트를 열었습니다.")
    
    main_window = driver.current_window_handle

    try:
        # "개인로그인" 링크 클릭 (XPath 와 JavaScript 사용)
        login_link = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='gnb']//a[contains(@href, 'groupYn=N')]" )))
        driver.execute_script("arguments[0].click();", login_link)
        print("개인로그인 페이지로 이동합니다.")
        
        # "휴대폰 인증" 버튼 클릭
        phone_auth_button = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "휴대폰 인증")))
        phone_auth_button.click()
        print("휴대폰 인증 팝업을 열었습니다.")
        
        # 팝업 창으로 전환
        wait.until(EC.number_of_windows_to_be(2))
        for window_handle in driver.window_handles:
            if window_handle != main_window:
                driver.switch_to.window(window_handle)
                break
        
        print("팝업 창으로 전환했습니다.")
        
        # "KT 알뜰폰" 버튼 클릭
        kt_mvno_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[onclick*='KTM']")))
        kt_mvno_button.click()
        print("KT 알뜰폰 버튼을 클릭했습니다.")
        
        # "문자(SMS) 인증" 버튼 클릭
        sms_auth_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li[aria-label='문자(SMS) 인증'] button")))
        sms_auth_button.click()
        print("문자(SMS) 인증 버튼을 클릭했습니다.")
        
        # "본인확인 이용 동의" 체크박스 클릭
        agree_checkbox = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "mobileCertAgree")))
        agree_checkbox.click()
        print("본인확인 이용 동의에 체크했습니다.")
        
        # "다음" 버튼 클릭
        next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn_pass[data-action='next']")))
        next_button.click()
        print("다음 버튼을 클릭했습니다.")
        
        # 최종 폼에 정보 입력 (JavaScript로 값 설정 및 이벤트 트리거)
        user_name_field = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input.userName")))
        driver.execute_script("arguments[0].value = arguments[1];", user_name_field, USER_NAME)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", user_name_field) # Trigger change event

        birthdate_field_1 = driver.find_element(By.CSS_SELECTOR, "input.myNum1")
        driver.execute_script("arguments[0].value = arguments[1];", birthdate_field_1, USER_BIRTHDATE)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", birthdate_field_1) # Trigger change event

        gender_digit_field = driver.find_element(By.CSS_SELECTOR, "input.myNum2")
        driver.execute_script("arguments[0].value = arguments[1];", gender_digit_field, USER_GENDER_DIGIT)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", gender_digit_field) # Trigger change event

        phone_number_field = driver.find_element(By.CSS_SELECTOR, "input.mobileNo")
        driver.execute_script("arguments[0].value = arguments[1];", phone_number_field, USER_PHONE_NUMBER)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", phone_number_field) # Trigger change event
        
        print("사용자 정보를 입력했습니다.")
        
        # 사용자가 수동으로 캡차를 입력하고 다음 버튼을 누를 때까지 대기
        print("보안문자를 입력하고 다음 버튼을 60초 안에 눌러주세요...\n(이 단계는 자동화할 수 없으므로 수동으로 진행해야 합니다.)")
        time.sleep(60)
        
        print("로그인이 완료된 것으로 간주하고 다음 단계를 진행합니다.")

        # 메인 창으로 다시 전환 (팝업이 닫혔다고 가정)
        driver.switch_to.window(main_window)
        print("메인 창으로 전환했습니다.")

        # "구민우선" 예약 페이지로 이동
        driver.get("https://publicsports.yongin.go.kr/publicsports/sports/selectFcltyRceptResveListU.do?key=4290&searchResveType=RESIDENTRESVE")
        print("구민우선 예약 페이지로 이동했습니다.")
        time.sleep(5) # 페이지 로딩 대기

        # "분야" 선택 버튼 클릭 (XPath 사용)
        category_select_button = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='selectbox']/button[@class='select_btn']")))
        driver.execute_script("arguments[0].click();", category_select_button)
        print("분야 선택 버튼을 클릭했습니다.")
        time.sleep(1) # 드롭다운 메뉴가 나타날 때까지 대기

        # "테니스" 버튼 클릭 (XPath 사용)
        tennis_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='item_btn' and contains(@onclick, 'ITEM_01')]/span[text()='테니스']")))
        driver.execute_script("arguments[0].click();", tennis_button)
        print("테니스 필터를 적용했습니다.")
        time.sleep(5) # 페이지 업데이트 대기

        # 필터링 후 페이지 소스 출력 (코트 정보 확인용)
        print("--- 테니스 필터 적용 후 페이지 소스 ---")
        print(driver.page_source)
        print("--- 테니스 필터 적용 후 페이지 소스 끝 ---")

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

    # 드라이버 종료
    driver.quit()
    print("자동화 프로그램을 종료합니다.")

if __name__ == "__main__":
    main()