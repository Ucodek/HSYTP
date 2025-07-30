import requests
import calendar

api_key = '142dca7d8e41dbab0356ecf347dcd5d0'
base_url = f'https://api.stlouisfed.org/fred/series/observations?series_id=TB3MS&api_key={api_key}&file_type=json&'

def get_last_day_of_month(year, month):
    """Belirtilen yıl ve ay için son günü döndürür."""
    last_day = calendar.monthrange(year, month)[1]
    return last_day

# This function returns the risk free rate for ABD stock markets
def get_tb3ms_value(year, month):
    """Belirtilen yıl ve ay için TB3MS değerini alır."""
    start_date = f'{year}-{month:02d}-01'
    end_date = f'{year}-{month:02d}-{get_last_day_of_month(year, month)}'
    
    url = f'{base_url}observation_start={start_date}&observation_end={end_date}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP hata kodlarını kontrol et
        data = response.json()
        
        # Verileri kontrol et ve değeri döndür
        observations = data.get('observations', [])
        if observations:
            # Son gözlemi al
            last_observation = observations[-1]
            value = last_observation.get('value', 'No data')
            return value
        else:
            return None
    except requests.exceptions.RequestException as e:
        return f'An error occurred: {e}'