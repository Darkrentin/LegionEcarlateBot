from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import lib

URL = 'https://contestedzonetimers.com/'

def get_seed_time():
    driver = None
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    
    start_time = time.time()
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(URL)

        wait = WebDriverWait(driver, 10)
        timer_element = wait.until(
            EC.visibility_of_element_located((By.ID, "timer"))
        )

        timer_text = timer_element.text

        end_time = time.time()
        latency = end_time - start_time

        h, m, s = map(int, timer_text.split(':'))
        total_seconds = h * 3600 + m * 60 + s
        
        corrected_seconds = total_seconds - latency
        
        if corrected_seconds < 0:
            corrected_seconds = 0

        actual_time = int(time.time())

        time_seed = int(actual_time + corrected_seconds)
                    
        return time_seed

    except Exception as e:
        return f"error : {e}"

    finally:
        if driver:
            driver.quit()

def save_time_seed(time_seed):
    data = lib.load_json()

    data['time_seed'] = time_seed

    lib.save_json(data)

def update_time_seed():
    time_seed = get_seed_time()
    save_time_seed(time_seed)
    return time_seed