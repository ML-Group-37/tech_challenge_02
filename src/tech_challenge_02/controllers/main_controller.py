import os
from datetime import datetime
import csv
import time
from fastapi import APIRouter, HTTPException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

router = APIRouter(
    prefix="/api",
    tags=["Main"]
)

@router.get("/scrape-b3")
async def scrape_b3_data():
    """
    Scrapes the B3 stock table using Selenium and saves it to a CSV file.
    Returns the path to the saved file.
    """
    driver = None
    try:
        # 1. Setup Chrome in headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Ensures GUI isn't needed
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # 2. Get the webpage
        url = "https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br"
        driver.get(url)
        
        # 3. Wait for table to be present and visible
        wait = WebDriverWait(driver, 20)  # Increased wait time to 20 seconds
        table = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "table.table-responsive-sm.table-responsive-md"))
        )
        
        # 4. Extract headers
        headers = []
        header_elements = table.find_elements(By.TAG_NAME, "th")
        for header in header_elements:
            headers.append(header.text.strip())
            
        # 5. Extract rows
        rows = []
        row_elements = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header row
        for row_element in row_elements:
            row = []
            cells = row_element.find_elements(By.TAG_NAME, "td")
            if cells:  # Only process rows with td elements
                for cell in cells:
                    # Get text and clean it up
                    value = cell.text.strip()
                    # Convert percentage values to proper decimal format
                    if "%" in value:
                        value = value.replace("%", "").replace(",", ".")
                    # Convert numeric values with Brazilian formatting
                    elif "." in value and "," in value:
                        value = value.replace(".", "").replace(",", ".")
                    row.append(value)
                rows.append(row)
                
        # 6. Create data directory if it doesn't exist
        if not os.path.exists('data'):
            os.makedirs('data')
            
        # 7. Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"b3_stocks_{timestamp}.csv"
        filepath = os.path.join('data', filename)
        
        # 8. Save to CSV file
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
            
        return {
            "message": "Data saved successfully",
            "file": filepath,
            "total_rows": len(rows)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Always close the browser
        if driver:
            driver.quit() 