import os
from datetime import datetime
import csv
import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/api",
    tags=["Main"]
)

@router.get("/scrape-b3")
async def scrape_b3_data():
    """
    Scrapes the B3 stock table and saves it to a CSV file.
    Returns the path to the saved file.
    """
    try:
        # 1. Get the webpage content
        url = "https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br"
        response = requests.get(url)  # Set a breakpoint here to inspect the response
        
        # 2. Parse the HTML and find the table
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='table table-hover')  # And another breakpoint here to check the table
        
        if not table:
            raise HTTPException(status_code=404, detail="Could not find the stocks table")
            
        # 3. Extract headers and rows
        headers = []
        rows = []
        
        # Get headers from thead
        for th in table.find('thead').find_all('th'):
            headers.append(th.text.strip())
            
        # Get rows from tbody
        for tr in table.find('tbody').find_all('tr'):
            row = []
            for td in tr.find_all('td'):
                row.append(td.text.strip())
            if row:  # Only add non-empty rows
                rows.append(row)
                
        # 4. Create data directory if it doesn't exist
        if not os.path.exists('data'):
            os.makedirs('data')
            
        # 5. Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"b3_stocks_{timestamp}.csv"
        filepath = os.path.join('data', filename)
        
        # 6. Save to CSV file
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