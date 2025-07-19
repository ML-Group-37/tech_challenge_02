import os
from datetime import datetime
import csv
from fastapi import APIRouter, HTTPException, Query
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

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
    chrome_options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=chrome_options)

def wait_for_element(driver, by, value, timeout=20, error_message=None):
    """Wrapper for WebDriverWait with error handling"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        error_msg = error_message or f"Timeout waiting for element: {value}"
        raise HTTPException(status_code=500, detail=error_msg)

def get_pagination_info(driver):
    """Get current page and total pages from pagination"""
    # Wait for small-screen element with text
    small_screen = wait_for_element(
        driver,
        By.CSS_SELECTOR,
        "li.small-screen",
        error_message="Could not find pagination info"
    )
    
    # Get text content
    text = small_screen.get_attribute("textContent").strip()
    if not text:
        raise HTTPException(status_code=500, detail="Pagination text is empty")
    
    try:
        parts = text.split("/")
        current_page = int(parts[0].strip())
        total_pages = int(parts[1].strip())
        
        return current_page, total_pages
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not parse pagination info from text '{text}': {str(e)}"
        )

def validate_page_number(driver, requested_page):
    """Check if the requested page is within valid range"""
    # Get current and total pages
    _, total_pages = get_pagination_info(driver)
    
    if requested_page < 1 or requested_page > total_pages:
        raise HTTPException(
            status_code=400,
            detail=f"Page number out of bounds. Available pages: 1 through {total_pages}"
        )

def select_page(driver, target_page):
    """Click on the specified page number"""
    # Get current page info
    current_page, total_pages = get_pagination_info(driver)
    
    # If already on target page, no need to click
    if current_page == target_page:
        return
        
    # Validate target page
    if target_page < 1 or target_page > total_pages:
        raise HTTPException(
            status_code=400,
            detail=f"Page number out of bounds. Available pages: 1 through {total_pages}"
        )
    
    # Find and click the target page number
    pagination = wait_for_element(
        driver,
        By.CLASS_NAME,
        "ngx-pagination",
        error_message="Could not find pagination"
    )
    
    target_found = False
    
    # Look for the page number in the pagination
    for item in pagination.find_elements(By.TAG_NAME, "li"):
        if item.text.strip() == str(target_page):
            try:
                # Find and click the link inside the li element
                link = item.find_element(By.TAG_NAME, "a")
                link.click()
                target_found = True
                
                # Wait for new page content
                wait = WebDriverWait(driver, 10)
                wait.until(
                    lambda d: get_pagination_info(d)[0] == target_page
                )
                break
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error clicking page {target_page}: {str(e)}"
                )
    
    if not target_found:
        raise HTTPException(
            status_code=500,
            detail=f"Could not find page {target_page} button"
        )

def extract_table_data(driver):
    """Extract data from the table"""
    # Wait for table with explicit error
    table = wait_for_element(
        driver,
        By.CLASS_NAME,
        "table.table-responsive-sm.table-responsive-md",
        timeout=20,
        error_message="Could not find table element"
    )
    
    # Get headers
    headers = []
    header_rows = table.find_elements(By.TAG_NAME, "th")
    if not header_rows:
        raise HTTPException(status_code=500, detail="Could not find table headers")
    
    for th in header_rows:
        headers.append(th.text.strip())
    
    # Get rows (excluding last 2 rows which are totals)
    rows = []
    data_rows = table.find_elements(By.TAG_NAME, "tr")[1:-2]  # Skip header row
    if not data_rows:
        raise HTTPException(status_code=500, detail="Could not find table rows")
    
    for row in data_rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells:
            row_data = []
            for i, cell in enumerate(cells):
                value = cell.text.strip()
                try:
                    if i == 3:  # Qtde. Teórica
                        value = float(value.replace(".", ""))
                    elif i == 4:  # Part. (%)
                        value = float(value.replace("%", "").replace(",", "."))
                except ValueError as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error converting value '{value}' at column {i}: {str(e)}"
                    )
                row_data.append(value)
            rows.append(row_data)
    
    return headers, rows

def save_to_csv(headers, rows):
    """Save the data to a CSV file"""
    try:
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
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving CSV file: {str(e)}"
        )

@router.get("/scrape-b3")
async def scrape_b3_data(page: int = Query(1, description="Page number to scrape")):
    """
    Scrapes the B3 stock table for a specific page and saves it to a CSV file.
    
    Parameters:
    - page: Page number to scrape (default: 1)
    """
    driver = None
    try:
        # 1. Setup and load initial page
        driver = setup_chrome_driver()
        driver.get("https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br")
        
        # 2. Validate requested page number
        validate_page_number(driver, page)
        
        # 3. Select the requested page if not on page 1
        if page > 1:
            select_page(driver, page)
        
        # 4. Extract and save data
        headers, rows = extract_table_data(driver)
        filepath = save_to_csv(headers, rows)
        
        # 5. Get current page info for response
        current_page, total_pages = get_pagination_info(driver)
        
        return {
            "message": "Data saved successfully",
            "file": filepath,
            "total_rows": len(rows),
            "current_page": current_page,
            "total_pages": total_pages
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
    
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass  # Ignore errors during cleanup 