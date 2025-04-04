import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, time
from ics import Calendar, Event
from jinja2 import Environment, FileSystemLoader
import logging
import re

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

URL = "https://icmaria.es/menu-comedor/"

try:
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extraer el mes
    mes_btn = soup.select_one('.btn-color-742106')
    if mes_btn:
        mes_raw = mes_btn.text.strip().upper()
        año_actual = datetime.now().year
        meses_esp_to_eng = {
            "ENERO": "January",
            "FEBRERO": "February",
            "MARZO": "March",
            "ABRIL": "April",
            "MAYO": "May",
            "JUNIO": "June",
            "JULIO": "July",
            "AGOSTO": "August",
            "SEPTIEMBRE": "September",
            "OCTUBRE": "October",
            "NOVIEMBRE": "November",
            "DICIEMBRE": "December"
        }
        mes = meses_esp_to_eng.get(mes_raw, "January")  # Default to January if not found
        fecha_inicio = datetime.strptime(f"{mes} {año_actual}", "%B %Y")
    else:
        # Fallback si no se encuentra el botón del mes
        logger.warning("No se encontró el botón del mes, usando el mes actual")
        fecha_inicio = datetime.now().replace(day=1)
        mes = fecha_inicio.strftime("%B")

    menu_dict = {}
    cal = Calendar()

    # Encontrar todas las secciones de semana
    secciones = soup.find_all('div', class_=['vc_custom_1667304685876', 'vc_custom_1667304680052'])

    for seccion in secciones:
        # Obtener el rango de días
        btn_fecha = seccion.find('a', class_='btn-color-321949')
        if not btn_fecha:
            # Intentar con otro selector si el primero falla
            btn_fecha = seccion.find('a', class_='btn btn-lg border-width-0 btn-color-321949')

        if not btn_fecha:
            logger.warning("No se encontró el botón de fecha en esta sección, saltando")
            continue

        titulo = btn_fecha.text.strip()

        # Procesar el rango de fechas
        if "Dia" in titulo:
            dia = int(titulo.split("Dia")[1].strip())
            dia_inicio = dia
            dia_fin = dia
        elif "Del" in titulo and "al" in titulo:
            match = re.search(r'Del (\d+) al (\d+)', titulo)
            if match:
                dia_inicio = int(match.group(1))
                dia_fin = int(match.group(2))
            else:
                logger.warning(f"No se pudo extraer el rango de días de: {titulo}")
                continue
        else:
            logger.warning(f"Formato de título no reconocido: {titulo}")
            continue

        # Obtener los menús
        menus = []
        menu_elements = seccion.find_all('a', class_=['btn-color-145637', 'btn-color-112061'])

        for menu in menu_elements:
            menu_text = menu.text.strip()
            if menu_text and not menu_text.startswith("Del") and not menu_text.startswith("Dia"):
                menus.append(menu_text)

        # Contador para los menús de la semana
        menu_index = 0

        # Para cada día en el rango
        for dia in range(dia_inicio, dia_fin + 1):
            try:
                fecha = fecha_inicio.replace(day=dia)
                # Solo procesar días laborables
                if fecha.weekday() < 5:  # 0-4 son Lunes a Viernes
                    if menu_index < len(menus):
                        menu_texto = menus[menu_index]
                        menu_dict[fecha] = menu_texto

                        e = Event()
                        e.name = "Menú del Comedor"
                        # Crear fecha con hora específica (13:00)
                        fecha = datetime.combine(fecha.date(), time(13, 0))
                        e.begin = fecha
                        e.description = menu_texto
                        cal.events.add(e)

                        menu_index += 1
            except ValueError as ve:
                logger.warning(f"Error al procesar la fecha para el día {dia}: {ve}")

    # Ordenar el diccionario por fecha
    menu_dict = dict(sorted(menu_dict.items()))

    # Generar el calendario HTML
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('calendar_template.html')
    menu_dict_str = {k.strftime('%Y-%m-%d'): v for k, v in menu_dict.items()}
    json_str = json.dumps(menu_dict_str, ensure_ascii=False)
    json_str_escaped = json_str.replace('\n', '\\n').replace('\r', '\\r')
    html_output = template.render(mes=mes, menus=json_str_escaped)

    with open('calendar.html', 'w', encoding='utf-8') as file:
        file.write(html_output)

    with open('menu_calendario.ics', 'w', encoding='utf-8') as f:
        f.writelines(cal)

    print("Calendario creado exitosamente en 'menu_calendario.ics'")
    print("Calendario final:")
    for fecha, menu in menu_dict.items():
        print(f"Fecha: {fecha.strftime('%d-%m-%Y')}, Menú: {menu}")

except Exception as e:
    logger.error(f"Error: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())
    raise