import csv
import time
import os
import html
from langdetect import detect
from googletrans import Translator
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Initialize Google Translator
translator = Translator()


# 1. Configure Chrome headless mode

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)


# 2. Define the 10 YouTube video URLs

video_urls = [
    "https://www.youtube.com/watch?v=d9YlU5vwoB4",
    "https://www.youtube.com/watch?v=BO1XXRwp3mc",
    "https://www.youtube.com/watch?v=deWN8SZF7N8",
    "https://www.youtube.com/watch?v=j0z4FweCy4M",
    "https://www.youtube.com/watch?v=tlThdr3O5Qo",
    "https://www.youtube.com/watch?v=IkSw2SZQENU",
    "https://www.youtube.com/watch?v=hif8pe80Xxs",
    "https://www.youtube.com/watch?v=jWreyC2l-dw",
    "https://www.youtube.com/watch?v=XB2g7-HgE_g",
    "https://www.youtube.com/watch?v=sQuJ8GKTjFM",
]


# 3. Scrape video comments one by one

save_path = "D:/CC/UoB/Social Media/期末作业/youtube_comments"

for index, video_url in enumerate(video_urls):
    print(f"Scraping video {index + 1} ：{video_url}")
    driver.get(video_url)

    # Waiting for the comments area to load
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except Exception as e:
        print(f"The comments area for video {index + 1} fail to load within the expected time：", e)
        continue  # Skip this video and continue to the next one


    # 4. Enhance scroll times to ensure more comments are loaded

    scroll_times = 70  # Increase the number of scrolls
    scroll_pause = 3   # Increase waiting time

    for _ in range(scroll_times):
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(scroll_pause)

    # Wait an extra 10 seconds to ensure YouTube has finished loading
    time.sleep(10)


    # 5. Get comment content

    comments = driver.find_elements(By.CSS_SELECTOR, "#content-text")

    # If still get 0 comments, try reloading
    if len(comments) == 0:
        print(f"⚠️ First crawl of video {index + 1} 0 comments, try to reload...")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(10)
        comments = driver.find_elements(By.CSS_SELECTOR, "#content-text")

    print(f"There are {len(comments)} comments found for video {index + 1}.")

    # Extract review text and translate non-English reviews
    comment_data = []
    for comment in comments:
        original_text = comment.text.strip()
        original_text = html.unescape(original_text)  # Parsing HTML special characters
        original_text = original_text.encode("utf-8", "ignore").decode("utf-8")  # 处理编码问题

        # Detect language and translate
        try:
            # Identify language
            detected_lang = detect(original_text)
            # Translate only non-English comments
            if detected_lang != "en":
                translated_text = translator.translate(original_text, dest="en").text
            else:
                translated_text = original_text
        except Exception as e:
            print(f"⚠️ Translation error, skip this comment: {original_text}")
            translated_text = original_text  # If the translation fails, keep the original text

        comment_data.append([original_text, translated_text])


    # 6. Save comments to CSV file
    # ----------------------------
    filename = os.path.join(save_path, f"Tesla_video_comments_{index + 1}.csv")
    with open(filename, "w", newline="", encoding="utf-8-sig", errors="replace") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Original Comment", "Translated Comment"])
        writer.writerows(comment_data)

    print(f"Comments for video {index + 1} have saved to file {filename} .")


# 7. Close the browser
driver.quit()
print("All video crawling is completed.")