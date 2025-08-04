from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf_file = request.files["pdf"]
        firma_file = request.files["firma"]

        # Guardamos archivos temporales
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
        firma_path = os.path.join(UPLOAD_FOLDER, firma_file.filename)
        pdf_file.save(pdf_path)
        firma_file.save(firma_path)

        # Leer PDF original
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        for i in range(len(reader.pages)):
            writer.add_page(reader.pages[i])

        # Crear una página con la firma como overlay
        overlay = BytesIO()
        c = canvas.Canvas(overlay, pagesize=letter)
        c.drawImage(firma_path, 400, 100, width=100, preserveAspectRatio=True)
        c.save()
        overlay.seek(0)

        # Convertir overlay a PDF y fusionar con la última página
        overlay_reader = PdfReader(overlay)
        last_page = writer.pages[-1]
        last_page.merge_page(overlay_reader.pages[0])

        output_path = os.path.join(UPLOAD_FOLDER, "firmado.pdf")
        with open(output_path, "wb") as f_out:
            writer.write(f_out)

        return send_file(output_path, as_attachment=True)

    return render_template("index.html")
