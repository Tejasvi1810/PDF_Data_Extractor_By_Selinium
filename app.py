
from flask import Flask, render_template_string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pdfplumber
import os

app = Flask(__name__)

DOWNLOAD_DIR = os.path.abspath("downloads")
PDF_URL = "https://www.w3.org/WAI/WCAG21/working-examples/pdf-table/table.pdf"
PDF_NAME = "table.pdf"
PDF_PATH = os.path.join(DOWNLOAD_DIR, PDF_NAME)

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.route('/')
def index():
    download_pdf()
    extracted_tables = extract_table_from_pdf(PDF_PATH)
    return render_template_string(TEMPLATE, tables=extracted_tables)

def download_pdf():
    options = Options()
    options.headless = True
    prefs = {"download.default_directory": DOWNLOAD_DIR,
             "download.prompt_for_download": False,
             "plugins.always_open_pdf_externally": True}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    driver.get(PDF_URL)
    time.sleep(5)  # Wait for download
    driver.quit()

def extract_table_from_pdf(path):
    tables = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                html_table = "<table border='1'>"
                for row in table:
                    html_table += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
                html_table += "</table><br>"
                tables.append(html_table)
    return tables

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Extracted Tables from PDF</title>
</head>
<body>
    <h2>📄 Extracted Tables from W3C PDF</h2>
    {% for table in tables %}
        {{ table | safe }}
    {% endfor %}
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)


