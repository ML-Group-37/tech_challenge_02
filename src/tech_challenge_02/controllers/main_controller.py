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

def setup_chrome_driver():
    """Configure and return a headless Chrome driver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

def get_table_element(driver):
    """Wait for and return the B3 stocks table element"""
    wait = WebDriverWait(driver, 20)
    return wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "table.table-responsive-sm.table-responsive-md"))
    )

def extract_headers(table):
    """Extract column headers from the table"""
    header_elements = table.find_elements(By.TAG_NAME, "th")
    return [header.text.strip() for header in header_elements]

def convert_value(value, column_index):
    """Convert string values to appropriate number types"""
    if column_index == 3:  # Qtde. Teórica
        return float(value.replace(".", ""))
    elif column_index == 4:  # Part. (%)
        return float(value.replace("%", "").replace(",", "."))
    return value

def extract_rows(table):
    """Extract and convert row data from the table"""
    rows = []
    row_elements = table.find_elements(By.TAG_NAME, "tr")[1:-2]  # Skip header and last 2 rows
    
    for row_element in row_elements:
        cells = row_element.find_elements(By.TAG_NAME, "td")
        if cells:
            row = [
                convert_value(cell.text.strip(), i)
                for i, cell in enumerate(cells)
            ]
            rows.append(row)
    
    return rows

def save_to_csv(headers, rows):
    """Save the data to a CSV file and return the filepath"""
    if not os.path.exists('data'):
        os.makedirs('data')
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"b3_stocks_{timestamp}.csv"
    filepath = os.path.join('data', filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    return filepath

@router.get("/scrape-b3")
async def scrape_b3_data():
    """
    Scrapes the B3 stock table using Selenium and saves it to a CSV file.
    Returns the path to the saved file.
    """
    driver = None
    try:
        # 1. Setup and get data
        driver = setup_chrome_driver()
        driver.get("https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br")
        
        # 2. Get table and extract data
        table = get_table_element(driver)
        headers = extract_headers(table)
        rows = extract_rows(table)
        
        # 3. Save data
        filepath = save_to_csv(headers, rows)
        
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