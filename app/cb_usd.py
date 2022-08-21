import requests
from pprint import pprint
from lxml import etree

# Функция для получения текущего курса доллара
def get_exchange_rate():
    try:
        response = requests.get(url='https://www.cbr-xml-daily.ru/daily_utf8.xml')

        tree = etree.XML(response.content)

        dollar_value = tree.xpath(f'/ValCurs/Valute[CharCode="USD"]/Value')[0].text
        dollar_value = float(dollar_value.replace(',', '.'))

        dollar_nominal = tree.xpath(f'/ValCurs/Valute[CharCode="USD"]/Nominal')[0].text
        dollar_nominal = float(dollar_nominal)
        
        coeff = dollar_value / dollar_nominal
    
    except (Exception, Error) as error:
        print("Error:", error)
        coeff = None
    
    return coeff



if __name__ == '__main__':
    print(get_exchange_rate())