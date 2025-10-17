
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
    # Restaurant(name="Al Caminetto", menu_url="https://www.alcaminetto.se/index.php/lunch"),
    Restaurant(name="Bastard Burgers", menu_url="https://bastardburgers.com/se/dagens-lunch/bromma/"),
    # Restaurant(name="Bistro Garros", menu_url="https://bistrogarros.se/menyer/meny"),
    # Restaurant(name="Brioche", menu_url="https://brioche.se/lunchmeny"),
    # Restaurant(name="Gustafs Matsal", menu_url="https://gustafs.kvartersmenyn.se/"),
    # Restaurant(name="Melanders", menu_url="https://melanders.se/restauranger/melanders-alvik/"),
    # Restaurant(name="Poké Burger", menu_url="https://pokeburger.se/meny/alvik/"),
    # Restaurant(name="Sjöpaviljongen", menu_url="https://sjopaviljongen.se/lunchmeny/"),
    # Restaurant(name="Vedugnen", menu_url="https://www.vedugnenialvik.se/meny"),
]

today_index = datetime.now().weekday()
swedish_days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]
today_swedish = swedish_days[today_index]

def fetch_and_process_menu(restaurant):
    try:
        response = requests.get(restaurant.menu_url)
        response.raise_for_status()
        html_content = response.text
        
        # Use OpenAI client to process HTML and extract today's menu
        prompt = f"Extract today's lunch menu for {today_swedish} from the following HTML content:\n\n{html_content}"
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            text_format=Restaurant
        )
        
        menu_data = response.get('choices', [{}])[0].get('message', {}).get('content', {})
        restaurant.menu = menu_data.get('menu_sections', [])
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching menu for {restaurant.name}: {e}")

def fetch_melanders_menu(restaurant):
    try:
        melandersHtml = requests.get(restaurant.menu_url)
        melandersHtml.raise_for_status()
        melandersSoup = BeautifulSoup(melandersHtml.content, 'html.parser')

        # Define the Swedish days of the week
        days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag"]

        # Create a regular expression pattern to split the text based on the days
        pattern = '|'.join(days)
                
        # Find the PDF link
        pdf_link_tag = melandersSoup.find('a', text="DAGENS LUNCH")
        pdf_url = pdf_link_tag['href'] if pdf_link_tag else None

        if pdf_url:
            pdf_path = "menu.pdf"
            urllib.request.urlretrieve(pdf_url, pdf_path)
            pdf = pdfquery.PDFQuery(pdf_path)
            pdf.load()
            all_text = ""
            for page_number in range(len(pdf.pq('LTPage'))):
                pdf.load(page_number)
                page_text = pdf.pq('LTTextLineHorizontal').text()
                all_text += page_text + "\n"
            
            split_text = re.split(f'(?=({pattern}))', all_text)
            # Remove any leading text before the first day
            split_text = split_text[1:]
            menus_by_day = {}
            for i in range(0, len(split_text), 2):
                if i + 1 < len(split_text):
                    day = split_text[i].strip()
                    menu = split_text[i+1].strip()
                    # Remove the day's name from the menu
                    if menu.startswith(day):
                        menu = menu[len(day):].strip()
                    menu = re.sub(r'\(.*?\)', '', menu)  # Remove text in parentheses
                    menus_by_day[day] = menu
            # Determine today's day in Swedish
            today_index = datetime.now().weekday()  # Monday is 0, Sunday is 6
            swedish_days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]
            today_swedish = swedish_days[today_index]
            today_menu = menus_by_day.get(today_swedish, "No menu available for today")
            
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
    "restaurants": [restaurant.dict() for restaurant in restaurants]
}

output_path = os.path.join("public", "menus.json")

# Save the menus to a JSON file
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print("Menus saved to menus.json")
