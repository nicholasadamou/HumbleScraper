from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# LOGGING
import logging

log = logging.getLogger()
logging.getLogger("selenium").setLevel(logging.WARNING)
console = logging.StreamHandler()
format_str = '%(asctime)s\t%(levelname)s -- Line:%(lineno)s | %(message)s'
console.setFormatter(logging.Formatter(format_str))
log.addHandler(console)  # prints to console.
log.setLevel(logging.DEBUG)  # DEBUG -> INFO -> WARNING -> ERROR -> CRITICAL


class Page:
    # Has to be a store page
    def __init__(self, url, timeout=5):
        assert "humblebundle.com/store/" in url, "Are you sure this is a store page?"
        self.url = url.split("?")[0]  # Strip off any referral/redirect/useless http params
        self.timeout = timeout  # How long to wait for an element before timing out

        self.driver = webdriver.PhantomJS(executable_path="./node_modules/.bin/phantomjs")
        self.wait = WebDriverWait(self.driver, self.timeout)
        self.driver.get(self.url)

    def get_time_left(self):
        """
        Gets time left for promo. Works for free game promotions, limited time sales, and anything with a timer.
        Returns tuple   (string as seen on website, dictionary with string keys)
        """
        try:
            timer = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='promo-timer-view']/div[@class='timer']")))

        except TimeoutException:
            log.critical("Promo-Timer-View timed out, are you sure this is a limited promotion?")
            return False

        else:
            # Gets all numbers and days/minutes/seconds labels. Gets re-refreshed when called below
            timedivs = timer.find_elements_by_tag_name("span")
            time_left = []

            # 8 since 4 time/time-format pairs. If the numbers were not detected, scan for them again
            # (slippery javascript dynamic clock ticking down)
            while len(time_left) != 8:
                time_left = []
                for i in timedivs:
                    time_left.append(i.text)
                time_left = list(filter(None, time_left))
                log.debug("NOT 8, re-scanning")
                log.debug(time_left)

            d = dict([(k, v) for v, k in zip(time_left[::2], time_left[1::2])])
            print(d)
            return " ".join(time_left), d

    def get_product_name(self):
        """
        Gets product/game name.
        Returns string
        """
        try:
            header = self.wait.until(EC.presence_of_element_located((By.XPATH, "//h1[@data-entity-kind='product']")))
        except TimeoutException:
            log.critical("Header timed out", exc_info=1)
            return False
        else:
            return header.text

    def get_price_data(self):
        """
        Gets information about price such as amount and currency
        Returns dict:
                price_preview  :   The price as seen on the website       - eg: "$19.99 USD"
                price          :   price metadata                         - eg: "19.99"
                price_currency :   currency metadata                      - eg: "USD"
                availability   :   availability status
                -------------------------------
                Below is if the item is on sale
                -------------------------------
                price_modifier : Price modifier in percent or sale amount - eg: "-50%"
                price_full     : Original item price, usually striked out - eg: "$40.00"
        """
        try:  # Wait till parent container loads in
            parent_div = "//div[@class='price-info']"
        except TimeoutException:
            log.critical("price-info timed out", exc_info=1)
            return False
        else:
            # Get price data and build output dict
            price_preview = self.driver.find_element(By.XPATH, "{}/span[@itemprop='offers']".format(parent_div)).text
            price = self.driver.find_element(By.XPATH, "{}/meta[@itemprop='price']".format(parent_div)).get_attribute(
                "content")
            price_currency = self.driver.find_element(By.XPATH, "{}/meta[@itemprop='priceCurrency']".format(
                parent_div)).get_attribute("content")
            availability = self.driver.find_element(By.XPATH, "{}/link[@itemprop='availability']".format(
                parent_div)).get_attribute("href")

            # log.debug("{} and& {} and& {}".format(price, price_currency, availability))
            data = {"price_preview": price_preview,
                    "price": price,
                    "price_currency": price_currency,
                    "availability": availability
                    }

            # Get sale data
            try:
                self.driver.find_element(By.XPATH, "//span[@class='discount-amount']")

            except NoSuchElementException:
                log.debug("Didn't find any sale data, passing...")

            else:
                price_modifier = self.driver.find_element(By.XPATH, "//span[@class='discount-amount']").text
                price_full = self.driver.find_element(By.XPATH, "//span[@class='full-price']").text
                data.update({"price_modifier": price_modifier, "price_full": price_full})

            return data

    def get_data(self):
        return {"price_info": self.get_price_data(), "name": self.get_product_name(), "time_info": self.get_time_left()}

    def close(self):
        self.driver.quit()
