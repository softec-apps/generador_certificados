import io
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageTk
import fitz  # PyMuPDF

# Registrar la fuente que quieres usar
pdfmetrics.registerFont(TTFont('fuente', 'fuente.ttf'))

# Crear la carpeta 'certificados_generados' si no existe
output_folder = 'certificados_generados'
os.makedirs(output_folder, exist_ok=True)

def ajustar_texto(can, texto, fuente, tamano_inicial, x, y, ancho_maximo):
    tamano = tamano_inicial
    while tamano > 10:
        can.setFont(fuente, tamano)
        text_width = can.stringWidth(texto, fuente, tamano)
        if text_width <= ancho_maximo:
            break
        tamano -= 1

    can.setFont(fuente, tamano)
    # Ajustar el color del texto a #BC242F
    can.setFillColorRGB(0.737, 0.141, 0.184)
    current_x = x
    for char in texto:
        char_width = can.stringWidth(char, fuente, tamano)
        if current_x + char_width > x + ancho_maximo:
            y -= tamano * 1.2  # Nueva línea
            current_x = x
        can.drawString(current_x, y, char)
        current_x += char_width

def open_pdf_preview(pdf_path):
    global start_x, start_y, end_x, end_y, root, canvas_widget, img_tk, preview_rect_id, preview_text_id
    start_x, start_y, end_x, end_y = None, None, None, None
    root = tk.Tk()
    root.title("Seleccionar área del texto")

    # Maximizar la ventana
    root.state('zoomed')

    # Convertir la primera página del PDF a una imagen
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img_tk = ImageTk.PhotoImage(img)

    # Crear un frame para contener los widgets
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

    canvas_widget = tk.Canvas(frame, width=img.width, height=img.height)
    canvas_widget.pack(fill=tk.BOTH, expand=True)
    canvas_widget.create_image(0, 0, anchor=tk.NW, image=img_tk)

    preview_rect_id = None
    preview_text_id = None

    def on_mouse_down(event):
        global start_x, start_y
        start_x, start_y = event.x, event.y
        if preview_rect_id:
            canvas_widget.delete(preview_rect_id)
        if preview_text_id:
            canvas_widget.delete(preview_text_id)

    def on_mouse_up(event):
        global end_x, end_y, preview_rect_id, preview_text_id
        end_x, end_y = event.x, event.y
        if preview_rect_id:
            canvas_widget.delete(preview_rect_id)
        if preview_text_id:
            canvas_widget.delete(preview_text_id)
        preview_rect_id = canvas_widget.create_rectangle(start_x, start_y, end_x, end_y, outline="black")
        preview_text_id = canvas_widget.create_text(start_x, (start_y + end_y) // 2,
                                           text="NOMBRE1 NOMBRE2 APELLIDO1 APELLIDO2", fill="red",
                                           font=("Verdana", 15, "bold"), anchor=tk.W)



    canvas_widget.bind("<ButtonPress-1>", on_mouse_down)
    canvas_widget.bind("<ButtonRelease-1>", on_mouse_up)

    def confirmar_posicion():
        if start_x is not None and start_y is not None and end_x is not None and end_y is not None:
            if messagebox.askyesno("Confirmar área", "¿Desea utilizar esta área para los nombres?"):
                root.quit()
            else:
                canvas_widget.delete(preview_rect_id)
                canvas_widget.delete(preview_text_id)
                canvas_widget.create_image(0, 0, anchor=tk.NW, image=img_tk)
                canvas_widget.bind("<ButtonPress-1>", on_mouse_down)
                canvas_widget.bind("<ButtonRelease-1>", on_mouse_up)
        else:
            messagebox.showerror("Error", "Debe seleccionar un área para los nombres.")

    confirmar_button = tk.Button(frame, text="Confirmar área", command=confirmar_posicion)
    confirmar_button.pack(side=tk.BOTTOM, pady=10)

    root.mainloop()

    if start_x is not None and start_y is not None and end_x is not None and end_y is not None:
        # Asegurar que start_x/y sean las coordenadas superiores izquierdas y end_x/y las inferiores derechas
        if start_x > end_x:
            start_x, end_x = end_x, start_x
        if start_y > end_y:
            start_y, end_y = end_y, start_y
        inverted_start_y = img.height - start_y
        inverted_end_y = img.height - end_y
        return start_x, inverted_start_y, end_x, inverted_end_y
    else:
        return None, None, None, None

def generate_certificates(x1, y1, x2, y2):
    if x1 is None or y1 is None or x2 is None or y2 is None:
        messagebox.showerror("Error", "Debe seleccionar un área para el nombre.")
        return

    # Leer los nombres del archivo de texto
    with open('nombres.txt', 'r', encoding='utf-8') as f:
        nombres = f.read().splitlines()

    # Dimensiones de una página A4 en horizontal
    a4_width, a4_height = A4
    a4_width, a4_height = a4_height, a4_width  # Intercambiar para orientación horizontal

    for nombre in nombres:
        # Crear una nueva instancia de PdfReader para cada nombre
        plantilla = PdfReader(open('plantilla.pdf', 'rb'))
        output = PdfWriter()

        # Crear un nuevo PDF en memoria
        packet = io.BytesIO()
        can = rl_canvas.Canvas(packet, pagesize=(a4_width, a4_height))

        # Ancho máximo para el texto
        ancho_maximo = x2 - x1
        start_y = min(y1, y2)

        # Usar la nueva función para ajustar el texto
        ajustar_texto(can, nombre, 'fuente', 30, x1, start_y, ancho_maximo)

        can.save()

        # Mover al comienzo del StringIO buffer
        packet.seek(0)
        nuevo_pdf = PdfReader(packet)

        # Fusionar la primera página de la plantilla con el nuevo PDF
        pagina = plantilla.pages[0]
        pagina.merge_page(nuevo_pdf.pages[0])
        output.add_page(pagina)

        # Añadir las páginas restantes de la plantilla, si las hay
        for i in range(1, len(plantilla.pages)):
            output.add_page(plantilla.pages[i])

        # Guardar el PDF resultante en la carpeta 'certificados_generados'
        output_filename = os.path.join(output_folder, f'{nombre}.pdf'.replace(' ', '_').replace(',', ''))
        with open(output_filename, 'wb') as outputStream:
            output.write(outputStream)

    messagebox.showinfo("Información", f"Certificados generados correctamente en '{output_folder}'.")



# Ejecutar la previsualización para seleccionar la posición
while True:
    x1, y1, x2, y2 = open_pdf_preview('plantilla.pdf')
    if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
        if messagebox.askyesno("Generar certificados", "¿Desea generar los certificados con el área seleccionada?"):
            generate_certificates(x1, y1, x2, y2)
            break

root.destroy()  # Cerrar la ventana principal de Tkinter al finalizar
