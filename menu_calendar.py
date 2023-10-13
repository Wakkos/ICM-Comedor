import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event

# Parte 1: Web Scraping
URL = "https://icmaria.es/menu-comedor/"
response = requests.get(URL)
soup = BeautifulSoup(response.content, 'html.parser')

# Ajusta los selectores según la estructura del sitio web
fechas = soup.select("selector_de_fechas")
menus = soup.select("selector_de_menus")

menu_dict = {fecha.text: menu.text for fecha, menu in zip(fechas, menus)}

# Parte 2: Creación de Calendario
cal = Calendar()

for fecha, menu in menu_dict.items():
    e = Event()
    e.name = "Menú del Comedor"
    e.begin = fecha
    e.description = menu
    cal.events.add(e)

with open('menu_calendario.ics', 'w') as f:
    f.writelines(cal)

print("Calendario creado exitosamente en 'menu_calendario.ics'")
