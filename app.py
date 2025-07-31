from flask import Flask, render_template, request
import os
import time
import pandas as pd
import tabula
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

app = Flask(__name__)
DOWNLOAD_DIR = os.path.join(os.getcwd(), "pdf_downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

PDF_URL = "https://drive.google.com/file/d/1KI7bqNEUKV07VntV3_tMYqw4YqZinY_Z/view"

def download_pdf_from_drive():
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless=new")  # run headless
    service = Service()

    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        driver.get(PDF_URL)
        time.sleep(5)
        download_button = driver.find_element(By.XPATH, '//div[@aria-label="Download"]')
        download_button.click()
        time.sleep(10)
        pdf_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".pdf")]
        if not pdf_files:
            return None
        return os.path.join(DOWNLOAD_DIR, pdf_files[0])
    except Exception as e:
        print("Download Error:", e)
        return None
    finally:
        driver.quit()

@app.route('/')
def index():
    return render_template("index.html", tables=None)

@app.route('/extract', methods=["POST"])
def extract():
    pdf_path = download_pdf_from_drive()
    if not pdf_path:
        return "PDF download failed."

    try:
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
        html_tables = [df.to_html(classes="table table-bordered", index=False) for df in tables]
        return render_template("index.html", tables=html_tables)
    except Exception as e:
        return f"Error reading PDF: {e}"

if __name__ == '__main__':
    app.run(debug=True)
