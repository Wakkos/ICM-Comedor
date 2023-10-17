# ICM Comedor Calendario

Este proyecto permite a los padres acceder y tener a mano las comidas diarias de sus hijos del ICM ya que actualmente la accesibilidad de la web no cumple con los [estándares de accesibilidad W3C](https://www.w3.org/WAI/standards-guidelines/es).

Se hace scrapping del [Menú Comedor](https://icmaria.es/menu-comedor/) en la web del ICM y genera automáticamente un calendario.

El script de Python se ejecuta con una [Action de Github](https://github.com/Wakkos/ICM-Comedor/blob/main/.github/workflows/update_calendar.yml) configurada para ejecutarse cada día. Si el calendario cambia - actualizan la web con un menú nuevo al mes siguiente -  este crea un calendario distinto que se comitea y se publica actualizado.


### Configuración del Proyecto

1. Clone el repositorio:
   ```bash
   git clone https://github.com/Wakkos/ICM-Comedor.git
   ```
2. Instale las dependencias:
  ```bash
  pip install -r requirements.txt
  ```
3. Ejecute el script para generar el calendario:
  ```
  python script_name.py
  ```


### Contribuir

Si vas mejorar o añadir características, por favor:

1. Haz un fork del proyecto.
2. Crea una nueva rama.
3. Realiza tus cambios y crea un pull request.
