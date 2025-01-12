import requests
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
import pdfquery
import json
import re

# Day translation dictionary at the global scope
day_translation = {
    'monday': 'MÅNDAG',
    'tuesday': 'TISDAG',
    'wednesday': 'ONSDAG',
    'thursday': 'TORSDAG',
    'friday': 'FREDAG',
    'saturday': 'LÖRDAG',
    'sunday': 'SÖNDAG'
}

# Function to get current weekday in Swedish
def get_current_day_swedish():
    current_weekday = datetime.now().strftime('%A').lower()
    return day_translation.get(current_weekday)

def clean_menus(menus):
    cleaned_menus = []
    
    # Regular expression pattern to match time ranges
    time_pattern = re.compile(r'\b\d{1,2}[:.]\d{2}\s*-\s*\d{1,2}[:.]\d{2}\b')
    
    # Define a function to clean up each menu item
    def clean_item(item):
        # Remove newline characters and hashtags
        item = item.replace('\n', ' ').replace('#', '')
        # Strip leading and trailing whitespace
        return item.strip()
    
    for restaurant in menus:
        cleaned_dishes = [
            {"name": clean_item(dish["name"]), "price": ""} 
            for dish in restaurant["menu"]["dishes"]
            if len(dish["name"]) >= 25 and not time_pattern.search(dish["name"])
        ]
        cleaned_menus.append({
            "name": restaurant["name"],
            "location": restaurant["location"],
            "menu": {"dishes": cleaned_dishes}
        })
    
    return cleaned_menus

# Initialize the JSON object
menus = []

# Garros
headers = {'User-Agent': 'Mozilla/5.0'}
garroshtml = requests.get("https://bistrogarros.se/menyer/meny", headers=headers)
garrosSoup = BeautifulSoup(garroshtml.content, 'html.parser')
class_name = f'Screen__day Screen__day--visible Screen__day--{datetime.now().strftime("%A").lower()}'
day_div = garrosSoup.find('div', {'class': class_name})

garros_menu = []
if day_div:
    menu_paragraph = day_div.find('p')
    lunch_menu = menu_paragraph.get_text(separator="\n", strip=True)
    # Split the menu into separate dishes based on newline characters
    garros_menu = [{"name": dish.strip(), "price": ""} for dish in lunch_menu.split('\n') if dish.strip()]

menus.append({
    "name": "Bistro Garros",
    "location": "Location details here",
    "menu": {"dishes": garros_menu}
})

# PokéBurger
pokeHtml = requests.get("https://pokeburger.se/meny/alvik/", headers=headers)
pokeSoup = BeautifulSoup(pokeHtml.content, 'html.parser')
AllPokeMenus = pokeSoup.find_all('div', class_='dine-menu-wrapper')

poke_dishes = []

# Map headings to the keys in poke_menu
heading_map = {
    'VECKANS NO BOWL': 'Veckans No Bowl',
    'POKÉ BOWLS': 'Poké Bowls',
    'THE BURGERS': 'The Burgers'
}

for menu in AllPokeMenus[:3]:
    heading = menu.find('h2', class_='dine-menu-heading').text
    key = heading_map.get(heading.upper(), None)
    
    if key:
        menu_items = menu.find_all('div', class_='dine-menu-item')
        for item in menu_items:
            name = item.find('h3', class_='menu-item-name').text.capitalize()
            description = item.find('div', class_='menu-item-desc').text.strip().lower()
            poke_dishes.append({"name": f"{name} - {description}", "price": ""})

menus.append({
    "name": "PokéBurger",
    "location": "Location details here",
    "menu": {"dishes": poke_dishes}
})

# Al Caminetto
alCamiHtml = requests.get("https://www.alcaminetto.se/lunch/", headers=headers)
alCamiSoup = BeautifulSoup(alCamiHtml.content, 'html.parser')
current_day_swedish = get_current_day_swedish()
todays_menu = []
current_day = None

for header in alCamiSoup.find_all('h3'):
    text = header.get_text(strip=True)
    if text in day_translation.values():
        current_day = text
    elif current_day == current_day_swedish:
        todays_menu.append({"name": text, "price": ""})

menus.append({
    "name": "Al Caminetto",
    "location": "Location details here",
    "menu": {"dishes": todays_menu}
})

# Gustafs
gustafsHtml = requests.get("https://www.gustafsrestaurang.se/index.php/lunch", headers=headers)
gustafsSoup = BeautifulSoup(gustafsHtml.content, 'html.parser')

day_translationGustafs = {
    'monday': 'Måndag',
    'tuesday': 'Tisdag',
    'wednesday': 'Onsdag',
    'thursday': 'Torsdag',
    'friday': 'Fredag',
    'saturday': 'Lördag',
    'sunday': 'Söndag'
}

# Get the current weekday in Swedish
current_weekday = datetime.now().strftime('%A').lower()
current_day_swedish = day_translationGustafs.get(current_weekday)

# Initialize to store today's menu
todays_menu = []

current_day = None

# Iterate over all <h3> and <h5> elements
for element in gustafsSoup.find_all(['h3', 'h5']):
    text = element.get_text(strip=True)
    # Check if the text is a day of the week in Swedish
    if text in day_translationGustafs.values():
        current_day = text
    elif current_day == current_day_swedish:
        # If the current header is not a weekday and it matches today, add the item to today's menu
        todays_menu.extend({"name": item.strip(), "price": ""} for item in re.split(r'[.!?]', text) if item.strip())

menus.append({
    "name": "Gustafs",
    "location": "Location details here",
    "menu": {"dishes": todays_menu}
})

# Bastard Burgers
bastardHtml = requests.get("https://bastardburgers.com/se/dagens-lunch/bromma/", headers=headers)
bastardSoup = BeautifulSoup(bastardHtml.content, "html.parser")
menu_title = bastardSoup.find('h4').get_text(strip=True)
menu_description = bastardSoup.find('p').get_text(strip=True)

menus.append({
    "name": "Bastard Burgers",
    "location": "Location details here",
    "menu": {"dishes": [{"name": f"{menu_title}: {menu_description}", "price": ""}]}
})

# Sjöpaviljongen
sjoPaviljHtml = requests.get("https://sjopaviljongen.se/lunchmeny/", headers=headers)
sjoPaviljSoup = BeautifulSoup(sjoPaviljHtml.content, "html.parser")
first_table = sjoPaviljSoup.find('table')
menu_items = first_table.find_all('p')

sjopaviljongen_menu = []
for item in menu_items:
    text = item.get_text(separator="\n", strip=True)
    # Check if the dish starts with "DAGENS" and remove only the first line
    if text.startswith("DAGENS"):
        parts = text.split('\n', 1)  # Split only at the first newline
        if len(parts) > 1:
            text = parts[1]  # Keep everything after the first newline
    
    # Split at the first capital letter after a lowercase word
    split_pattern = re.compile(r'(?<=\s)[A-ZÅÄÖ]')
    parts = split_pattern.split(text, 1)
    # Use only the first part, which should be the Swedish description
    cleaned_text = parts[0].strip() if parts else text
    
    sjopaviljongen_menu.append({"name": cleaned_text, "price": ""})

menus.append({
    "name": "Sjöpaviljongen",
    "location": "Location details here",
    "menu": {"dishes": sjopaviljongen_menu}
})

# Melanders (Get PDF link and process)
melandersHtml = requests.get("https://melanders.se/restauranger/melanders-alvik/", headers=headers)
melandersSoup = BeautifulSoup(melandersHtml.content, 'html.parser')

# Find the PDF link
pdf_link_tag = melandersSoup.find('a', text="DAGENS LUNCH")
pdf_url = pdf_link_tag['href'] if pdf_link_tag else None

melanders_menu = []
if pdf_url:
    pdf_path = "menu.pdf"

    try:
        urllib.request.urlretrieve(pdf_url, pdf_path)
        pdf = pdfquery.PDFQuery(pdf_path)
        pdf.load()
        all_text = ""
        for page_number in range(len(pdf.pq('LTPage'))):
            pdf.load(page_number)
            page_text = pdf.pq('LTTextLineHorizontal').text()
            all_text += page_text + "\n"
        
        sections = all_text.split(current_day_swedish)
        if len(sections) > 1:
            today_section = sections[1].strip()
            # Remove all content within parentheses
            today_section = re.sub(r'\(.*?\)', '', today_section)
            # Split based on capitalized words
            melanders_menu = [{"name": dish.strip(), "price": ""} for dish in re.split(r'(?=[A-ZÅÄÖ])', today_section) if dish.strip() and dish.strip() not in day_translation.values()]
    except Exception as e:
        melanders_menu = [{"name": "Error", "price": str(e)}]

menus.append({
    "name": "Melanders",
    "location": "Location details here",
    "menu": {"dishes": melanders_menu}
})

# Output JSON data
menus = clean_menus(menus)
output_path = os.path.join("public", "menus.json")

# Save the menus to a JSON file
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(menus, f, ensure_ascii=False, indent=4)

print("Menus saved to menus.json")
