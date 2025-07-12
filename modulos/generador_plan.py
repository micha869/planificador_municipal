from reportlab.pdfgen import canvas
import os

def generar_plan_pdf():
    ruta = os.path.join("data", "plan_municipal.pdf")
    os.makedirs("data", exist_ok=True)
    c = canvas.Canvas(ruta)
    c.drawString(100, 750, "Plan Municipal Generado")
    c.save()
