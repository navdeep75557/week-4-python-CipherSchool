#!/usr/bin/env python3
"""Scrape product details from MDComputers search results.

Usage:
    python mdcomputers_scraper.py "external harddrive"
    python mdcomputers_scraper.py "external harddrive" --pages 2 --output products.json
"""

from __future__ import annotations

import argparse
import json
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://mdcomputers.in/"
SEARCH_URL = BASE_URL + "?route=product/search"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    )
}


def clean_text(value: str | None) -> str | None:
    if not value:
        return None
    return " ".join(value.split()) or None


def first_text(element, selectors: list[str]) -> str | None:
    for selector in selectors:
        match = element.select_one(selector)
        if match:
            text = clean_text(match.get_text(" ", strip=True))
            if text:
                return text
    return None


def scrape_page(session: requests.Session, search_term: str, page: int = 1) -> list[dict]:
    params = {"search": search_term}
    if page > 1:
        params["page"] = page

    response = session.get(SEARCH_URL, params=params, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    products = []

    # MDComputers uses product-grid/list cards. The selectors below include
    # common OpenCart-style selectors and fallbacks for minor markup changes.
    cards = soup.select(
        ".product-layout, .product-thumb, .product-grid .product-item, "
        ".product-list .product-item"
    )

    seen_urls = set()
    for card in cards:
        link = card.select_one("a[href]")
        if not link:
            continue

        product_url = urljoin(BASE_URL, link.get("href", ""))
        if not product_url or product_url in seen_urls:
            continue
        seen_urls.add(product_url)

        name = first_text(card, [
            ".caption h4",
            ".product-name",
            ".name",
            "h4",
            "h3",
        ]) or clean_text(link.get("title"))

        price = first_text(card, [
            ".price-new",
            ".price",
            ".product-price",
        ])

        old_price = first_text(card, [
            ".price-old",
            "del",
            "s",
        ])

        image = card.select_one("img[src], img[data-src]")
        image_url = None
        if image:
            image_url = image.get("data-src") or image.get("src")
            image_url = urljoin(BASE_URL, image_url)

        if name:
            products.append({
                "name": name,
                "price": price,
                "old_price": old_price,
                "image_url": image_url,
                "product_url": product_url,
                "search_term": search_term,
                "page": page,
            })

    return products


def scrape(search_term: str, pages: int = 1, delay: float = 1.0) -> list[dict]:
    session = requests.Session()
    session.headers.update(HEADERS)

    results = []
    for page in range(1, pages + 1):
        page_results = scrape_page(session, search_term, page)
        results.extend(page_results)

        if not page_results:
            break
        if page < pages:
            time.sleep(delay)

    # Remove duplicates while preserving order.
    unique = {}
    for product in results:
        unique[product["product_url"]] = product
    return list(unique.values())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape product details from MDComputers search results."
    )
    parser.add_argument("search_term", help="Product search term")
    parser.add_argument("--pages", type=int, default=1, help="Number of result pages")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between pages")
    parser.add_argument("--output", default="products.json", help="Output JSON file")
    args = parser.parse_args()

    if args.pages < 1:
        parser.error("--pages must be at least 1")

    products = scrape(args.search_term, args.pages, args.delay)
    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(products, file, indent=2, ensure_ascii=False)

    print(f"Scraped {len(products)} products.")
    print(f"Saved results to {args.output}")


if __name__ == "__main__":
    main()
