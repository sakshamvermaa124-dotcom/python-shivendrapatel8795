import csv
import requests
import time
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
OUTPUT_FILE = "books.csv"


def fetch_page(url: str, retries: int = 3) -> str | None:
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                return response.text

            if response.status_code in (429, 503):
                print(
                    f"HTTP {response.status_code}: "
                    f"Retry {attempt}/{retries}"
                )
                time.sleep(1)
                continue

            response.raise_for_status()

        except requests.RequestException as error:
            print(f"Request failed: {error}")

            if attempt < retries:
                time.sleep(2)

    print(f"Failed to fetch: {url}")
    return None


def scrape_pages(start_page: int, end_page: int) -> list[dict[str, str]]:
    all_books: list[dict[str, str]] = []

    for page_number in range(start_page, end_page + 1):
        url = BASE_URL.format(page_number)

        print(f"\nScraping page {page_number}...")

        html = fetch_page(url)

        if html is None:
            continue

        soup = BeautifulSoup(html, "html.parser")

        books = soup.select("article.product_pod")

        print(f"Books found: {len(books)}")

        for book in books:
            title = book.h3.a["title"]
            price = book.select_one(".price_color").text.strip()
            price = price.replace("Â£", "£")
            rating = book.select_one(".star-rating")["class"][1]

            all_books.append(
                {
                    "title": title,
                    "price": price,
                    "rating": rating,
                }
            )

        time.sleep(1)

    return all_books


def save_to_csv(books: list[dict[str, str]]) -> None:
    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["title", "price", "rating"]
        )

        writer.writeheader()
        writer.writerows(books)

    print(f"\nSaved {len(books)} books to {OUTPUT_FILE}")


def main() -> None:
    books = scrape_pages(1, 5)
    save_to_csv(books)


if __name__ == "__main__":
    main()