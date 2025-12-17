import streamlit as st
import pandas as pd
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json

# --- GOOGLE AUTHENTICATION LOGIC ---
def get_credentials():
    """
    Safely retrieves Google credentials. 
    Checks Streamlit Cloud Secrets first, then falls back to local file.
    """
    # 1. Check Streamlit Cloud Secrets (Recommended for Deployment)
    if "gcp_service_account" in st.secrets:
        return dict(st.secrets["gcp_service_account"])
    
    # 2. Fallback to Local File (For testing on your laptop)
    try:
        with open("credentials.json", "r") as f:
            content = f.read().strip()
            if not content:
                st.error("The credentials.json file is empty.")
                return None
            return json.loads(content)
    except FileNotFoundError:
        st.error("Credentials not found! Please add them to Streamlit Secrets or provide credentials.json.")
        return None
    except json.JSONDecodeError:
        st.error("The credentials.json file contains invalid JSON. Check for extra spaces or missing brackets.")
        return None

# --- CONFIG ---
TARGET_URL = "https://opensource-demo.orangehrmlive.com/"
USERNAME = "Admin"
PASSWORD = "admin123"
GOOGLE_SHEET_NAME = "CV Processing Dashboard"
WORKSHEET_NAME = "Sheet1"

SELECTORS = {
    "login_user": "input[name='username']",
    "login_pass": "input[name='password']",
    "login_btn": "button[type='submit']",
    "nav_pim": "a[href='/web/index.php/pim/viewPimModule']",
    "btn_add": "div.orangehrm-header-container > button",
    "field_first_name": "input[name='firstName']",
    "field_last_name": "input[name='lastName']",
    "btn_save": "button[type='submit']"
}

# --- PAGE CONFIG ---
st.set_page_config(page_title="HR Automation Dashboard", layout="wide")
st.title("🤖 BrioHR Automated Uploader")

@st.cache_resource
def get_google_sheet():
    creds_dict = get_credentials()
    if not creds_dict:
        return None
    
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open(GOOGLE_SHEET_NAME).worksheet(WORKSHEET_NAME)
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets: {e}")
        return None

def run_automation(selected_rows):
    status_box = st.info("Initializing Robot...")
    progress = st.progress(0)
    
    # Setup Chrome (Cloud Mode)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 10)
        
        status_box.info("Logging into HR Portal...")
        driver.get(TARGET_URL)
        
        # Login
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["login_user"])))
        driver.find_element(By.CSS_SELECTOR, SELECTORS["login_user"]).send_keys(USERNAME)
        driver.find_element(By.CSS_SELECTOR, SELECTORS["login_pass"]).send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, SELECTORS["login_btn"]).click()
        time.sleep(3)

        total = len(selected_rows)
        for i, row in enumerate(selected_rows):
            name = row.get("Candidate Name", "Unknown")
            status_box.info(f"Processing ({i+1}/{total}): {name}")
            
            # Nav to Add Employee
            driver.find_element(By.CSS_SELECTOR, SELECTORS["nav_pim"]).click()
            time.sleep(2)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS["btn_add"]))).click()
            time.sleep(2)
            
            # Split Name
            parts = str(name).split(" ")
            f_name = parts[0]
            l_name = parts[-1] if len(parts) > 1 else "Candidate"
            
            driver.find_element(By.CSS_SELECTOR, SELECTORS["field_first_name"]).send_keys(f_name)
            driver.find_element(By.CSS_SELECTOR, SELECTORS["field_last_name"]).send_keys(l_name)
            driver.find_element(By.CSS_SELECTOR, SELECTORS["btn_save"]).click()
            time.sleep(3)
            
            progress.progress((i + 1) / total)
            
        st.success(f"Successfully uploaded {total} candidates!")
        driver.quit()
        
    except Exception as e:
        st.error(f"Robot Error: {e}")

# --- MAIN APP LOGIC ---
sheet = get_google_sheet()

if sheet:
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        st.subheader("📋 Current Candidate Sheet")
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        st.subheader("⚡ Bulk Upload Control")
        
        # UI Selection
        all_names = df["Candidate Name"].tolist()
        selection = st.multiselect("Select candidates to push to BrioHR:", all_names)
        
        if st.button("🚀 Start Automated Upload"):
            if not selection:
                st.warning("Please select at least one candidate first.")
            else:
                rows_to_push = df[df["Candidate Name"].isin(selection)].to_dict("records")
                run_automation(rows_to_push)
                
    except Exception as e:
        st.error(f"Could not read spreadsheet data: {e}")