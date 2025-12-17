import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import config

def setup_google_sheets():
    print("🔌 Connecting to Google Sheets...")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(config.CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open(config.GOOGLE_SHEET_NAME).worksheet(config.WORKSHEET_NAME)
    return sheet

def setup_browser():
    print("🌐 Launching Chrome...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # This keeps the browser open even if the script finishes (helpful for testing)
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def login_orangehrm(driver):
    print("🔑 Logging in to OrangeHRM...")
    driver.get(config.TARGET_URL)
    
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTORS["login_user"])))
    
    driver.find_element(By.CSS_SELECTOR, config.SELECTORS["login_user"]).send_keys(config.USERNAME)
    driver.find_element(By.CSS_SELECTOR, config.SELECTORS["login_pass"]).send_keys(config.PASSWORD)
    driver.find_element(By.CSS_SELECTOR, config.SELECTORS["login_btn"]).click()
    
    print("✅ Login Clicked. Waiting for Dashboard...")
    time.sleep(4)

def process_candidates(sheet, driver):
    data = sheet.get_all_records()
    print(f"📄 Found {len(data)} rows to check.")

    for index, row in enumerate(data):
        row_number = index + 2
        
        # Check specific columns from your sheet
        status = row.get("Status", "")
        candidate_name = row.get("Candidate Name", "Unknown Candidate") # <--- FIXED THIS for you
        
        if status == "Ready for Upload":
            print(f"🚀 Adding Candidate: {candidate_name}")
            
            try:
                # 1. Click PIM (Employee List)
                driver.find_element(By.CSS_SELECTOR, config.SELECTORS["nav_pim"]).click()
                time.sleep(2)
                
                # 2. Click Add Button
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, config.SELECTORS["btn_add"]))).click()
                time.sleep(2)
                
                # 3. Handle Name (Split 'John Doe' into 'John' and 'Doe')
                full_name = str(candidate_name).split(" ")
                first_name = full_name[0]
                last_name = full_name[-1] if len(full_name) > 1 else "Candidate"
                
                driver.find_element(By.CSS_SELECTOR, config.SELECTORS["field_first_name"]).send_keys(first_name)
                driver.find_element(By.CSS_SELECTOR, config.SELECTORS["field_last_name"]).send_keys(last_name)
                
                # 4. Save
                driver.find_element(By.CSS_SELECTOR, config.SELECTORS["btn_save"]).click()
                print(f"✅ Success! Created profile for {candidate_name}")
                time.sleep(4)
                
                # 5. Update Status to 'Uploaded'
                # Finds the 'Status' column number dynamically
                header_row = sheet.row_values(1)
                status_col = header_row.index("Status") + 1
                sheet.update_cell(row_number, status_col, "Uploaded")
                
            except Exception as e:
                print(f"❌ Error on {candidate_name}: {e}")

def main():
    sheet = setup_google_sheets()
    driver = setup_browser()
    login_orangehrm(driver)
    process_candidates(sheet, driver)

if __name__ == "__main__":
    main()