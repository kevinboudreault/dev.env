import os,requests,csv,re
from bs4 import BeautifulSoup
from dotenv import load_dotenv

headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                          "AppleWebKit/537.36 (KHTML, like Gecko)"
                          "Chrome/140.0.0.0 Safari/537.36" }

directory_url = os.environ.get('directory_url')

response = requests.get(directory_url, headers=headers)

soupy = BeautifulSoup(response.text,features="html.parser")

cards = soupy.select('.card')

field_names = ["Name","Address","Phone","Details"]
company = []

for c in cards:
    companyName = c.select('.cardTitle')
    if 0 < len(companyName):
        cname = companyName[0].get_text()
    else:
        cname = "N\\A"

    companyAddress = c.select('.cardDetails')
    if 0 < len(companyAddress):
        address = companyAddress[0].get_text()
    else:
        address = "N\\A"

    rawCompanyPhone = c.select('.cardContact')
    if 0 < len(rawCompanyPhone):
        phone = re.sub(r'\D', '', rawCompanyPhone[0].get_text())
    else:
        phone = "N\\A"

    if c.has_attr('href'):
        url = c['href']
    else:
        url = "N\\A"

    company.append([cname,address,phone,url])


with open('./belleville_company.csv', 'ab', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=field_names)
    writer.writeheader()
    writer = csv.writer(csvfile)
    writer.writerows(company)

print("Belleville companies scrapped")
