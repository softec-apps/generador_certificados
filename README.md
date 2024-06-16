### Generador de Certificados PDF

Este script de Python utiliza la biblioteca Tkinter para permitir al usuario seleccionar un área específica en un PDF, donde se generan certificados personalizados utilizando nombres extraídos de un archivo de texto.

#### Requisitos Previos

Asegúrate de tener instaladas las siguientes bibliotecas Python:

- `tkinter`
- `PyPDF2`
- `reportlab`
- `PIL` (Pillow)
- `fitz` (PyMuPDF)

Puedes instalar estas bibliotecas usando pip:
pip install -r requirements.txt


#### Uso del Script

1. **Seleccionar Área del Texto:**
   - Ejecuta el script y selecciona un área en la primera página del PDF de plantilla donde se colocará el nombre.
   - Confirma el área seleccionada.

2. **Generar Certificados:**
   - Una vez seleccionada el área, el script generará certificados personalizados para cada nombre listado en `nombres.txt`.
   - Los certificados se guardarán en la carpeta `certificados_generados`.

#### Detalles Técnicos

- **Ajuste de Texto:** El texto del nombre se ajusta dinámicamente para encajar dentro del área seleccionada en el PDF.
- **Manejo de PDF:** Utiliza `PyPDF2` para cargar y manipular PDFs, y `reportlab` para generar contenido de PDF personalizado.
- **Interfaz Gráfica:** Se utiliza `tkinter` para la interacción gráfica, permitiendo al usuario seleccionar un área específica en la página del PDF.

#### Archivos Necesarios

- `plantilla.pdf`: PDF de plantilla donde se insertará el nombre.
- `nombres.txt`: Archivo de texto que contiene los nombres que se colocarán en los certificados.

#### Ejecución

Para ejecutar el script, simplemente corre el archivo Python desde la línea de comandos o desde tu IDE favorito.

```bash
python certificados.py
