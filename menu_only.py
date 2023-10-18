import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from ics import Calendar, Event
from jinja2 import Environment, FileSystemLoader

URL = "https://icmaria.es/menu-comedor/"
response = requests.get(URL)
soup = BeautifulSoup(response.content, 'html.parser')

# Extraer el mes
mes = soup.select_one('.btn-color-742106').text.strip()
año_actual = datetime.now().year
meses_esp_to_eng = {
    "Enero": "January",
    "Febrero": "February",
    "Marzo": "March",
    "Abril": "April",
    "Mayo": "May",
    "Junio": "June",
    "Julio": "July",
    "Agosto": "August",
    "Septiembre": "September",
    "Octubre": "October",
    "Noviembre": "November",
    "Diciembre": "December"
}

mes_ingles = meses_esp_to_eng.get(mes, mes)
fecha_inicio = datetime.strptime(f"{mes_ingles} {año_actual}", "%B %Y")

# Ajustar la fecha_inicio al primer lunes del mes
while fecha_inicio.strftime('%A') != 'Monday':
    fecha_inicio += timedelta(days=1)

# Extraer las comidas
comidas = soup.select('.btn-color-145637, .btn-color-112061')

# Asociar comidas con fechas
días = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
menu_dict = {}


# Inicializar índice para las comidas
idx_comida = 0
# Fecha de inicio
fecha = fecha_inicio
# Extraer la información nutricional
valores_nutricionales = [element.text.strip() for element in soup.select('[style="text-align: right;"]')]
# Asociar comidas con fechas y valores nutricionales
semana_actual = 0
cal = Calendar()


while idx_comida < len(comidas):
    # Si el día actual no es un fin de semana
    if fecha.strftime('%A') in días:
        menu_dict[fecha] = comidas[idx_comida].text.strip()

        e = Event()
        e.name = "Menú del Comedor"
        e.begin = fecha
        e.description = f"{comidas[idx_comida].text.strip()}\n\nValor Nutricional: {valores_nutricionales[semana_actual]}"
        cal.events.add(e)

        # Si el día actual es un viernes, avanza al siguiente valor nutricional
        if fecha.strftime('%A') == 'Friday' and semana_actual < len(valores_nutricionales) - 1:
            semana_actual += 1

        idx_comida += 1  # Solo incrementa el índice de comida si hemos procesado un día de la semana

    fecha += timedelta(days=1)  # Avanza al siguiente día



# Imprimir las fechas, menús y valores nutricionales
semana_actual = 0
for fecha, menu in menu_dict.items():
    print(f"Fecha: {fecha.strftime('%d-%m-%Y')}")
    print(f"Menú: {menu}")
    print(f"Valor Nutricional:\n {valores_nutricionales[semana_actual]}\n")

    # Si el día actual es un viernes, avanzar al siguiente valor nutricional
    if fecha.strftime('%A') == 'Friday' and semana_actual < len(valores_nutricionales) - 1:
        semana_actual += 1


# Configura Jinja2 para cargar la plantilla
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('calendar_template.html')
# Rellena la plantilla con los datos del calendario
# Convertir las claves datetime a strings en formato ISO
menu_dict_str_keys = {k.strftime('%Y-%m-%d'): v for k, v in menu_dict.items()}
# Suponiendo que menu_dict ya está definido y lleno de datos
menu_dict = {k: v for k, v in menu_dict.items() if k.weekday() < 5 and k.month == datetime.now().month}

def escape_control_characters(s):
    return s.replace('\n', '\\n').replace('\r', '\\r')

# Convertir el diccionario a una cadena JSON
json_str = json.dumps(menu_dict_str_keys, ensure_ascii=False)

# Escapar los caracteres de control
json_str_escaped = escape_control_characters(json_str)

# Luego pasas este nuevo diccionario al template
html_output = template.render(mes=mes_ingles, menus=json_str_escaped)



# Escribe el HTML resultante en un archivo
with open('calendar.html', 'w', encoding='utf-8') as file:
    file.write(html_output)


# Guardar el calendario en un archivo .ics
with open('menu_calendario.ics', 'w', encoding='utf-8') as f:
    f.writelines(cal)

print("Calendario creado exitosamente en 'menu_calendario.ics'")