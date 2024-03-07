import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common import exceptions
import time
import os
import csv
import json

class Client:

    def __init__(self, profile_path, driver_path):
        current_time = time.time()

        self.profile_path = profile_path
        self.driver_path = driver_path
        self.element_height = None
        self.network_logs = []
        self.driver = self.setup_driver()
        self.file_date = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(current_time))

        self.driver.execute_cdp_cmd('Network.enable', {})

        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S", filename=f"./logs/app_log_{self.file_date}.log")

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    def setup_driver(self):
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}

        chrome_options = Options()
        chrome_options.add_argument(f"user-data-dir={self.profile_path}")
        chrome_options.set_capability("goog:loggingPrefs", {'performance': 'ALL'})
        
        service = Service(executable_path=self.driver_path)


        # Inisialisasi WebDriver dengan opsi yang dikonfigurasi
        return webdriver.Chrome(options=chrome_options, service=service)
    
    def wait_for_selector(self, selector, by=By.CSS_SELECTOR, timeout=10, ):
        try:
            logging.info(f"Waiting for element with selector: '{selector}'")
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, selector))
            )
            return element
        except:
            logging.error(f"Timeout: Element with selector '{selector}' not found")
            return None

    def get_tweet_texts(self, container):
        try:
            tweet_texts = []
            # Temukan semua elemen <div> dengan data-testid="tweetText"
            tweet_elements = container.find_elements(by=By.XPATH, value='.//div[@data-testid="tweetText"]')
            # Iterasi melalui setiap elemen tweet dan ambil teksnya
            for tweet_element in tweet_elements:
                tweet_text_cleaned = tweet_element.get_attribute('innerText').encode('ascii', 'ignore').decode('ascii')
                tweet_texts.append(tweet_text_cleaned)
            
            if tweet_texts:
                return tweet_texts[0]
            else:
                return ""
        except:
            return ""
    
    def get_author(self, container):
        try:
            # aria_labelledby = container.get_attribute('aria-labelledby')
            reply_element = container.find_element(by=By.XPATH, value='.//div[@data-testid="User-Name"]//span/span')
            author_text = reply_element.text
            if author_text:
                return author_text
            else:
                return None
        except:
            return None
    
    def get_reply_count(self, container):
        try:
            # aria_labelledby = container.get_attribute('aria-labelledby')
            reply_element = container.find_element(by=By.XPATH, value='.//div[@data-testid="reply"]//span[@data-testid="app-text-transition-container"]/span')
            reply_count_text = reply_element.text
            if reply_count_text:
                return reply_count_text
            else:
                return 0
        except:
            return 0
        
    def get_date(self, container):
        try:
            # aria_labelledby = container.get_attribute('aria-labelledby')
            time_element = container.find_element(by=By.TAG_NAME, value='time')
            return time_element.get_attribute("datetime")
        except:
            return None
    
    def get_retweet_count(self, container):
        try:
            # aria_labelledby = container.get_attribute('aria-labelledby')
            retweet_element = container.find_element(by=By.XPATH, value='.//div[@data-testid="retweet"]//span[@data-testid="app-text-transition-container"]/span')
            retweet_count_text = retweet_element.text
            if retweet_count_text:
                return retweet_count_text
            else:
                return 0
        except:
            return None
    
    def get_like_count(self, container):
        try:
            # aria_labelledby = container.get_attribute('aria-labelledby')
            like_element = container.find_element(by=By.XPATH, value='.//div[@data-testid="like"]//span[@data-testid="app-text-transition-container"]/span')
            like_count_text = like_element.text
            if like_count_text:
                return like_count_text
            else:
                return 0
        except:
            return None

    def get_data_tweets(self, container):
        articles = container.find_elements(by=By.TAG_NAME, value='article')
        result = []
        for article in articles:
            # get textTweet
            text = self.get_tweet_texts(article)
            author = self.get_author(article)
            reply = self.get_reply_count(article)
            retweet = self.get_retweet_count(article)
            like = self.get_like_count(article)
            date = self.get_date(article)
            result.append({
                "text": text,
                "author": author,
                "reply": reply,
                "retweet": retweet,
                "like": like,
                "date": date,
            })

        logging.info(f"Retrieved {len(result)} tweet(s).")
        # for res in result:
        #     print(f"text: {res['text']}\nauthor: {res['author']}\nreply: {res['reply']}\nretweet: {res['retweet']}\nlike: {res['like']}\n")
        #     print()
        return result
    
    def checkLimitText(self):
        try:
            # Dapatkan keseluruhan konten HTML dari halaman web
            html_content = self.driver.page_source

            # Periksa apakah teks yang diinginkan ada di dalam konten HTML
            if "Something went wrong. Try reloading." in html_content:
                return True
            else:
                return False
        except Exception as e:
            print(f"error: {e}")
            return False

    
    def checkLimit(self):
        for log in filter(self.log_filter, self.network_logs):
            try:
                requestId = log["params"]["requestId"]
                body = self.driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': requestId})
                response_body = body.get("body", "").strip()
                print(f"response_body: {response_body[:50]}...")
                if response_body == "Rate limit exceeded":
                    self.network_logs = []
                    return True
            except exceptions.WebDriverException as e:
                pass
                # print('response.body is null')
                # print(f"error: {e}")
            
        # input("URGENT check network")
                
        self.network_logs = []
        return False
            
    
    def log_filter(self, log_):
        return (
            log_["method"] == "Network.responseReceived"
        )

    def search_tweets(self, query, recent=False, limit=1000):
        logging.info(f"Search tweet: {query}")
        # Membuat URL dengan query yang diencode
        results = []
        url = f"https://twitter.com/search?q={query}&src=typed_query"
        if recent:
            url = url + "&f=live"

        self.driver.get(url)
        self.wait_for_selector(by=By.XPATH, selector="//div[@aria-label='Timeline: Search timeline']", timeout=60)


        element = self.driver.find_element(By.XPATH, value="//div[@aria-label='Timeline: Search timeline']")

        csv_file_path = f"./results/{query}-{self.file_date}.csv"
        is_file_exists = os.path.exists(csv_file_path)

        # Membuka file CSV untuk menyimpan data
        with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
            fieldnames = ['text', 'author', 'reply', 'retweet', 'like', 'date']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            # Jika file CSV belum ada, tulis header terlebih dahulu
            
            if not is_file_exists:
                writer.writeheader()

            count_result = 0
            count_retries = 0
            button_retry = False

            while True:

                if button_retry == False:
                    data_result_get = self.get_data_tweets(container=element)
                    results.extend(data_result_get)

                    count_result = count_result + len(data_result_get)

                    logging.info(f"Results tweet: {count_result}")

                # if len(results) >= limit:
                #     break

                # input('Waiting confirmation (enter)')

                element_height = element.size['height']
                if element_height == self.element_height:
                    # time.sleep(15)
                    # browser_log = self.driver.get_log('performance')
                    # self.network_logs.extend([json.loads(lr["message"])["message"] for lr in browser_log])
                    logging.info(f"Scroll not affect, still check limit.")
                    hasExceeded = self.checkLimitText()
                    if hasExceeded:
                        if button_retry == False:
                            results_tuples = [tuple(d.items()) for d in results]
                            results_set = set(results_tuples)
                            results_unique = [dict(t) for t in results_set]
                            logging.info(f"Save current state: {len(results_unique)}")
                            for tweet in results_unique:
                                writer.writerow(tweet)
                            results = []
                        
                        logging.info(f"Rate limit exceeded, please wait for 10 minutes before retrying.")
                        time.sleep(60)
                        
                        logging.info(f"Button retry has clicked!")
                        retry_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and .//span[text()="Retry"]]'))
                        )
                        retry_button.click()
                        button_retry = True

                        # self.element_height = self.element_height + self.element_height
                    else:
                        count_retries = count_retries + 1
                        if count_retries == 3:
                            break
                        else:
                            logging.info(f"Try scroll again.")
                else:
                    button_retry = False
                        

                self.element_height = element_height
                self.driver.execute_script("window.scrollBy(0, arguments[0]);", self.element_height / 2)

                time.sleep(4)
            
            results_tuples = [tuple(d.items()) for d in results]
            results_set = set(results_tuples)
            results_unique = [dict(t) for t in results_set]
            logging.info(f"Search result: {len(results_unique)}")
            for tweet in results_unique:
                writer.writerow(tweet)

            logging.info(f"Tweet has ben saved!")
