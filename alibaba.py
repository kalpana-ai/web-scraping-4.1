from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from datetime import datetime

# === Setup WebDriver ===
service = Service(r"C:\Webdrivers\chromedriver.exe")  # ✅ your path
driver = webdriver.Chrome(service=service)

results = []
scraping_date = datetime.now().strftime("%Y-%m-%d")

for page in range(1, 101):  # ✅ Pages 1 to 100
    print(f"Scraping page {page}...")
    url = f"https://sourcing.alibaba.com/rfq/rfq_search_list.htm?page={page}&country=AE&recently=Y&tracelog=newest"
    driver.get(url)
    time.sleep(4)  # give time to load page

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    rfq_blocks = soup.select(".brh-rfq-item")

    for rfq in rfq_blocks:
        title_tag = rfq.select_one(".brh-rfq-item__subject-link")
        title = title_tag.text.strip() if title_tag else ''
        inquiry_url = "https:" + title_tag['href'] if title_tag else ''
        rfq_id_match = re.search(r"p=(\w+)", inquiry_url)
        rfq_id = rfq_id_match.group(1) if rfq_id_match else ''

        buyer_name_tag = rfq.select_one(".avatar .text")
        buyer_name = buyer_name_tag.text.strip().replace(",", "") if buyer_name_tag else ''

        buyer_img_tag = rfq.select_one(".avatar .img-con img")
        if buyer_img_tag and buyer_img_tag.has_attr("src"):
            buyer_img = buyer_img_tag["src"]
        else:
            buyer_img_initial = rfq.select_one(".avatar .default-img")
            buyer_img = buyer_img_initial.text.strip() if buyer_img_initial else ''

        inquiry_time_tag = rfq.select_one(".brh-rfq-item__publishtime")
        inquiry_time = inquiry_time_tag.text.strip().replace("Date Posted:", "").strip() if inquiry_time_tag else ''
        inquiry_date = scraping_date if inquiry_time else ''

        quotes_left_tag = rfq.select_one(".brh-rfq-item__quote-left")
        quotes_left = quotes_left_tag.text.strip() if quotes_left_tag else ''

        country_tag = rfq.select_one(".brh-rfq-item__country")
        country = country_tag.text.strip() if country_tag else ''

        quantity_text = ''
        for div in rfq.select(".brh-rfq-item__text"):
            if "Quantity Required" in div.text:
                try:
                    quantity_text = div.text.split(":", 1)[1].strip()
                except:
                    quantity_text = ''
                break

        def tag_exists(text):
            return 'Yes' if rfq.find(string=re.compile(text)) else 'No'

        email_confirmed = tag_exists("Email Confirmed")
        experienced_buyer = tag_exists("Experienced Buyer")
        complete_order = tag_exists("Complete Order via RFQ")
        typical_replies = tag_exists("Typically replies")
        interactive_user = tag_exists("Interactive User")

        results.append({
            "RFQ ID": rfq_id,
            "Title": title,
            "Buyer Name": buyer_name,
            "Buyer Image": buyer_img,
            "Inquiry Time": inquiry_time,
            "Quotes Left": quotes_left,
            "Country": country,
            "Quantity Required": quantity_text,
            "Email Confirmed": email_confirmed,
            "Experienced Buyer": experienced_buyer,
            "Complete Order via RFQ": complete_order,
            "Typical Replies": typical_replies,
            "Interactive User": interactive_user,
            "Inquiry URL": inquiry_url,
            "Inquiry Date": inquiry_date,
            "Scraping Date": scraping_date
        })

driver.quit()

# === Save to CSV ===
df = pd.DataFrame(results)
filename = f"alibaba_rfq_data_{scraping_date}.csv"
df.to_csv(filename, index=False)
print(f"✅ Data saved to {filename}")
