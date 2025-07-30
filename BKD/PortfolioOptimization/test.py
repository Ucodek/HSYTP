import requests
import json
from datetime import datetime, timedelta

url = 'http://127.0.0.1:8000/trainPortfolio'

date = datetime(2024, 5, 25).strftime('%Y-%m-%d')


# POST isteği için veri
data = {
    'stock_market': 'bist-100',
    'date': date,
    'train_days': 90,
    'opt_type': 4,  # Optimizasyon türü
    'numberOfStock': 10  # Seçilecek stok sayısı
    #'min_stock_weight': 0.01,  # Minimum stok ağırlığı
}


# Sertifika dosyasının yolu
#cert_path = 'cacert.pem'  # İndirilen sertifika dosyasının yolu

response = requests.post(url, json=data)

# Yanıtı kontrol etme
if response.status_code == 200:
    weights = response.json()
    print(json.dumps(weights, indent=2))
else:
    print(f'Error: {response.status_code}')

