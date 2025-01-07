from flask import Flask, render_template, request, redirect, url_for
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import os

app = Flask(__name__)

# Websites' status check function
def check_website_status(url):
    
   
    try:
        # Belirtilen URL'ye istek gönder ve yanıt al
        response = requests.get(url, timeout=5)
        
        # Durum kodu 200 ise "Erişilebilir" mesajını döndür
        if response.status_code == 200:
            return "Erişilebilir"
        # Durum kodu 200 değilse durumu belirt
        else:
            return f"Durum Kodu: {response.status_code}"
    
    # Zaman aşımı hatasını yakala ve mesaj döndür
    except requests.exceptions.Timeout:
        return "Zaman Aşımı (Timeout)"
    
    # Bağlantı hatasını yakala ve mesaj döndür
    except requests.exceptions.ConnectionError:
        return "Bağlantı Hatası (Connection Error)"
    
    # Genel bir istek hatası durumunda hata mesajını döndür
    except requests.exceptions.RequestException as e:
        return f"Hata: {str(e)}"

# Write data to an XML file
def write_to_xml(data):
    file_name = "web_resources.xml"

    if os.path.exists(file_name):
        tree = ET.parse(file_name)
        root = tree.getroot()
    else:
        root = ET.Element("WebResources")

    for item in data:
        resource = ET.SubElement(root, "Resource")
        ET.SubElement(resource, "kaynakID").text = str(item["kaynakID"])
        ET.SubElement(resource, "kaynakAdi").text = item["kaynakAdi"]
        ET.SubElement(resource, "kaynakDetay").text = item["kaynakDetay"]
        ET.SubElement(resource, "KaynakURL").text = item["KaynakURL"]
        ET.SubElement(resource, "kaynakZamanDamgasi").text = item["kaynakZamanDamgasi"]

    tree = ET.ElementTree(root)
    tree.write(file_name, encoding="utf-8", xml_declaration=True)

# Log results to a TXT file
def log_to_txt(log_data):
    with open("results_log.txt", "a", encoding="utf-8") as file:
        file.write(log_data + "\n")

@app.route('/')
def index():
    if os.path.exists("web_resources.xml"):
        tree = ET.parse("web_resources.xml")
        root = tree.getroot()
        resources = [
            {
                "kaynakID": resource.find("kaynakID").text,
                "kaynakAdi": resource.find("kaynakAdi").text,
                "kaynakDetay": resource.find("kaynakDetay").text,
                "KaynakURL": resource.find("KaynakURL").text,
                "kaynakZamanDamgasi": resource.find("kaynakZamanDamgasi").text,
            }
            for resource in root.findall("Resource")
        ]
    else:
        resources = []
    return render_template('index.html', resources=resources)

@app.route('/add_resource', methods=['GET', 'POST'])
def add_resource():
    if request.method == 'POST':
        kaynakID = request.form['kaynakID']
        kaynakAdi = request.form['kaynakAdi']
        kaynakDetay = request.form['kaynakDetay']
        KaynakURL = request.form['KaynakURL']
        kaynakZamanDamgasi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Prepare data for XML
        data = [{
            "kaynakID": kaynakID,
            "kaynakAdi": kaynakAdi,
            "kaynakDetay": kaynakDetay,
            "KaynakURL": KaynakURL,
            "kaynakZamanDamgasi": kaynakZamanDamgasi
        }]

        # Write data to XML
        write_to_xml(data)

        return redirect(url_for('index'))
    return render_template('add_resource.html')

@app.route('/check_status')
def check_status():
    if os.path.exists("web_resources.xml"):
        tree = ET.parse("web_resources.xml")
        root = tree.getroot()
        results = []

        for resource in root.findall("Resource"):
            url = resource.find("KaynakURL").text
            status = check_website_status(url)
            results.append({
                "kaynakID": resource.find("kaynakID").text,
                "kaynakAdi": resource.find("kaynakAdi").text,
                "KaynakURL": url,
                "status": status
            })

            # Log result to a TXT file
            log_to_txt(f"{datetime.now()}: {url} - {status}")

        return render_template('status.html', results=results)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
