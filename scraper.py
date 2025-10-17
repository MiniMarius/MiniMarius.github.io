
import os
import requests
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import pdfquery
import json
import re
from pydantic import BaseModel

load_dotenv()
client = OpenAI()

class Dish(BaseModel):
    name: str
    description: str = "" 
    price: float
    allergens: list[str] = []  

class MenuSection(BaseModel):
    title: str
    dishes: list[Dish]

class Restaurant(BaseModel):
    name: str
    menu_url: str
    menu: list[MenuSection] = []
    address: str = ""
    website: str = ""

restaurants = [
    Restaurant(name="Bastard Burgers", menu_url="https://bastardburgers.com/se/dagens-lunch/bromma/"),
]

today_index = datetime.now().weekday()
swedish_days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]
today_swedish = swedish_days[today_index]
print(f"Today's day in Swedish is: {today_swedish}")

def fetch_and_process_menu(restaurant: Restaurant):
    print(f"Fetching menu for {restaurant.name} from URL: {restaurant.menu_url}")
    try:
        response = requests.get(restaurant.menu_url)
        response.raise_for_status()
        html_content = response.text
        print(f"HTML content fetched for {restaurant.name}")

        # Use OpenAI client to process HTML and extract today's menu
        prompt = f"Extract today's lunch menu for {today_swedish} from the following HTML content:\n\n{html_content}"
        print(f"Sending prompt to OpenAI for {restaurant.name}")
        response = client.responses.parse(
            model="gpt-4o-mini",
            input=[{"role": "user", "content": prompt}],
            text_format=MenuSection
        )
        
        if response and response.output_parsed:
            restaurant.menu = [response.output_parsed]
            print(f"Updated menu for {restaurant.name}:")
        else:
            print(f"No menu data extracted for {restaurant.name}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching menu for {restaurant.name}: {e}")

def fetch_melanders_menu(restaurant):
    print(f"Fetching Melanders menu from URL: {restaurant.menu_url}")
    try:
        melandersHtml = requests.get(restaurant.menu_url)
        melandersHtml.raise_for_status()
        melandersSoup = BeautifulSoup(melandersHtml.content, 'html.parser')
        print("Fetched HTML for Melanders")

        days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag"]
        pattern = '|'.join(days)
                
        pdf_link_tag = melandersSoup.find('a', text="DAGENS LUNCH")
        pdf_url = pdf_link_tag['href'] if pdf_link_tag else None
        print(f"PDF URL found: {pdf_url}")

        if pdf_url:
            pdf_path = "menu.pdf"
            urllib.request.urlretrieve(pdf_url, pdf_path)
            print(f"Downloaded PDF to {pdf_path}")
            pdf = pdfquery.PDFQuery(pdf_path)
            pdf.load()
            all_text = ""
            for page_number in range(len(pdf.pq('LTPage'))):
                pdf.load(page_number)
                page_text = pdf.pq('LTTextLineHorizontal').text()
                all_text += page_text + "\n"
            
            split_text = re.split(f'(?=({pattern}))', all_text)
            split_text = split_text[1:]
            menus_by_day = {}
            for i in range(0, len(split_text), 2):
                if i + 1 < len(split_text):
                    day = split_text[i].strip()
                    menu = split_text[i+1].strip()
                    if menu.startswith(day):
                        menu = menu[len(day):].strip()
                    menu = re.sub(r'\(.*?\)', '', menu)
                    menus_by_day[day] = menu
            today_menu = menus_by_day.get(today_swedish, "No menu available for today")
            print(f"Today's menu for Melanders: {today_menu}")
            
            if today_menu != "No menu available for today":
                dishes = [Dish(name=dish.strip(), price=149.0) for dish in re.split(r'(?=[A-ZÅÄÖ])', today_menu) if dish.strip()]
                restaurant.menu.append(MenuSection(title="Today's Menu", dishes=dishes))

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Melanders menu: {e}")

for restaurant in restaurants:
    if restaurant.name == "Melanders":
        fetch_melanders_menu(restaurant)
    else:
        fetch_and_process_menu(restaurant)

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
output_data = {
    "last_updated": timestamp,
    "restaurants": [restaurant.model_dump() for restaurant in restaurants]
}

output_path = os.path.join("public", "menus.json")
print(f"Saving menus to {output_path}")

# Save the menus to a JSON file
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print("Menus saved to menus.json")
