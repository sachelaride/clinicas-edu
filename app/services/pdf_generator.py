from xhtml2pdf import pisa
from io import BytesIO

def generate_prontuario_pdf(html_content: str) -> BytesIO:
    pdf_file = BytesIO()
    pisa.CreatePDF(html_content, dest=pdf_file)
    pdf_file.seek(0)
    return pdf_file