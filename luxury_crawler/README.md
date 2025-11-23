# Luxury Car Crawler (CYS-493)

A benign, educational web crawler designed for the Secure Software Design
course (CYS-493). The crawler targets pre-approved luxury car inventory pages
and demonstrates secure, polite crawling practices.

## Features
- Respects `robots.txt` and uses a custom User-Agent for transparency.
- Enforces TLS verification, timeouts, and per-domain rate limiting.
- Extracts structured car data (brand, model, year, price, URL, source).
- Stores results in CSV for easy inspection and grading.
- Modular 3-tier design (presentation/config, application logic, storage).

## Getting Started
### Prerequisites
- Python 3.10+
- `venv` module available

### Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration
Edit `configs/config.json` to provide seed URLs, rate limits, and user-agent
settings. Example:
```json
{
  "seed_urls": ["https://example-luxurycars.com/inventory"],
  "max_pages_per_domain": 10,
  "crawl_delay_seconds": 1.0,
  "user_agent": "CYS493-LuxuryCrawler/0.1 (+https://example.edu/secure-crawler)"
}
```

### Running the crawler
```bash
python -m luxury_crawler.src.main --config luxury_crawler/configs/config.json
```

Logs are written to `logs/crawler.log`, and CSV output is saved to
`data/cars.csv`.

## Limitations
- Only intended for educational use on pre-approved luxury car sites.
- Parser contains placeholder selectors and is tuned for demonstration, not
production scraping.
- Does not bypass authentication or rate limits imposed by target sites.

## Ethical Use
Always ensure you have permission to crawl target domains and respect their
`robots.txt` policies. This project is built to encourage responsible crawling
practices.
