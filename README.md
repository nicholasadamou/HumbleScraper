# HumbleScraper

> A small script to retrieve **Name**, **Price/Sale**, and **Time** information from [Humble Bundle](https://www.humblebundle.com) store links for use in bots or web-hooks. uses [selenium](https://selenium-python.readthedocs.io/).

---

## Install

```bash
yarn install # install dependencies
```

## Usage
**Getting the time left for a promotion**

```python
import webscraper

page = webscraper.Page("https://www.humblebundle.com/store/LIMITED_TIME_OFFER_PAGE")
timer = page.get_time_left()

# >> ('1 days 16 hours 46 mins 56 secs',
#    {'days': '1', 'hours': '16', 'mins': '46', 'secs': '56'})
```

**Getting a product's name**
```python
import webscraper

page = webscraper.Page("https://www.humblebundle.com/store/PRODUCT_PAGE")
name = page.get_product_name()

# >> DOOM®
```

**Getting a product's price information**
```python
import webscraper

page = webscraper.Page("https://www.humblebundle.com/store/PRODUCT_PAGE")
name = page.get_price_data()

# On sale
# >> {'price_preview': '$14.99 USD', 'price_full': '$24.99', 'price_currency': 'USD', 'price': '14.99', 'price_modifier': '-40%', 'availability': 'InStock'}

# Limited Free offer
# >> {'price_preview': 'FREE!', 'price_full': '$14.99', 'price_currency': 'USD', 'price': '0', 'price_modifier': '-100%', 'availability': 'InStock'}
```

## License

MIT © [Nicholas Adamou](https://nicholasadamou.com/)