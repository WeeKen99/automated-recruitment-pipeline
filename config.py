# config.py

# ======================================================
# CONFIGURATION SETTINGS
# ======================================================

# 1. GOOGLE SHEETS SETTINGS
GOOGLE_SHEET_NAME = "CV Processing Dashboard"
WORKSHEET_NAME = "Sheet1"
CREDENTIALS_FILE = "credentials.json"

# 2. ORANGE HRM SETTINGS (The "Fake" BrioHR)
TARGET_URL = "https://opensource-demo.orangehrmlive.com/"
USERNAME = "Admin"
PASSWORD = "admin123"

# 3. CSS SELECTORS (The Map for the Robot)
SELECTORS = {
    # Login Page
    "login_user": "input[name='username']",
    "login_pass": "input[name='password']",
    "login_btn": "button[type='submit']",
    
    # Dashboard Navigation (PIM = Employee Management)
    "nav_pim": "a[href='/web/index.php/pim/viewPimModule']",
    
    # The "Add" Button
    "btn_add": "div.orangehrm-header-container > button",
    
    # Add Employee Form
    "field_first_name": "input[name='firstName']",
    "field_last_name": "input[name='lastName']",
    
    # The Save Button
    "btn_save": "button[type='submit']"
}
