import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config  # Imports your settings

# --- PAGE SETUP ---
st.set_page_config(page_title="HR Auto-Bot", page_icon="🤖")

st.title("🤖 HR Candidate Uploader")
st.markdown("This tool reads from the **CV Processing Dashboard** and uploads candidates to **OrangeHRM**.")

# --- HELPER FUNCTIONS ---
@st.cache_resource
def get_google_sheet_data():
    """Fetches data from Google Sheets without re-running every time"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(config.CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open(config.GOOGLE_SHEET_NAME).worksheet(config.WORKSHEET_NAME)
    return sheet

def run_automation(selected_rows, sheet_object):
    """The main robot logic"""
    
    # 1. Setup Browser
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    status_text.text("🌐 Launching Browser...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # 2. Login
        status_text.text("🔑 Logging into HR Portal...")
        driver.get(config.TARGET_URL)
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTORS["login_user"])))
        
        driver.find_element(By.CSS_SELECTOR, config.SELECTORS["login_user"]).send_keys(config.USERNAME)
        driver.find_element(By.CSS_SELECTOR, config.SELECTORS["login_pass"]).send_keys(config.PASSWORD)
        driver.find_element(By.CSS_SELECTOR, config.SELECTORS["login_btn"]).click()
        time.sleep(3) # Wait for dashboard

        # 3. Process Candidates
        total = len(selected_rows)
        for i, row in enumerate(selected_rows):
            name = row['Candidate Name']
            status_text.text(f"🚀 Processing {i+1}/{total}: {name}...")
            
            try:
                # Navigate to Add Employee
                driver.find_element(By.CSS_SELECTOR, config.SELECTORS["nav_pim"]).click()
                time.sleep(2)
                
                # Click Add
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, config.SELECTORS["btn_add"]))).click()
                time.sleep(2)
                
                # Type Data
                full_name = str(name).split(" ")
                first = full_name[0]
                last = full_name[-1] if len(full_name) > 1 else "Candidate"
                
                driver.find_element(By.CSS_SELECTOR, config.SELECTORS["field_first_name"]).send_keys(first)
                driver.find_element(By.CSS_SELECTOR, config.SELECTORS["field_last_name"]).send_keys(last)
                
                # Save
                driver.find_element(By.CSS_SELECTOR, config.SELECTORS["btn_save"]).click()
                time.sleep(3)
                
                # Update Google Sheet (Optional - removed for speed in UI demo, but you can add back)
                # finding the row index in a filtered view is tricky, so we skip updating sheet for now
                # to keep this simple for the demo.
                
            except Exception as e:
                st.error(f"Error on {name}: {str(e)}")
            
            # Update Progress Bar
            progress_bar.progress((i + 1) / total)

        status_text.text("✅ All Done!")
        st.success("Automation Complete!")
        time.sleep(5)
        
    except Exception as e:
        st.error(f"Critical Error: {str(e)}")
    finally:
        driver.quit()

# --- MAIN APP UI ---
try:
    sheet = get_google_sheet_data()
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    st.subheader("📊 Candidate Overview")
    st.dataframe(df)

    st.write("---")
    st.subheader("🚀 Direct Upload")
    
    # NEW: Dropdown to select candidates directly from the "Candidate Name" column
    candidate_list = df['Candidate Name'].tolist()
    selected_names = st.multiselect("Select candidates to upload to BrioHR:", candidate_list)

    if st.button("Submit to BrioHR"):
        if not selected_names:
            st.warning("Please select at least one candidate first!")
        else:
            # Filter the data based on the names you picked in the UI
            rows_to_process = df[df['Candidate Name'].isin(selected_names)].to_dict('records')
            
            with st.spinner(f"Robot is processing {len(selected_names)} candidates..."):
                run_automation(rows_to_process, sheet)
                st.success("Selected candidates have been processed!")

except Exception as e:
    st.error(f"Error: {e}")