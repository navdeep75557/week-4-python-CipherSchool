# MDComputers Product Scraper

A Python script that searches MDComputers and extracts product details from search-result pages.

## Features

- Search by any product term
- Scrape product name, price, old price, image URL, and product URL
- Support multiple result pages
- Save results as JSON
- Uses `requests` and `BeautifulSoup`

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python mdcomputers_scraper.py "external harddrive"
```

Scrape multiple pages:

```bash
python mdcomputers_scraper.py "external harddrive" --pages 2 --output products.json
```

The script respects a delay between pages and uses a descriptive User-Agent. Before using the scraper in production, check the site's terms and robots.txt and make sure your usage complies with applicable rules.
