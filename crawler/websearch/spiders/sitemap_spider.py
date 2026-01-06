import scrapy
from bs4 import BeautifulSoup
from pathlib import Path

class SitemapSpider(scrapy.Spider):
    name = "sitemap"

    def start_requests(self):
        sitemap_file = Path(__file__).parents[3] / "data" / "sitemaps.txt"

        with open(sitemap_file) as f:
            sitemaps = [line.strip() for line in f if line.strip()]

        for sitemap_url in sitemaps:
            yield scrapy.Request(sitemap_url, callback=self.parse_sitemap)

    def parse_sitemap(self, response):
        soup = BeautifulSoup(response.text, "xml")

        for loc in soup.find_all("loc"):
            url = loc.get_text()
            yield scrapy.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string if soup.title else ""
        paragraphs = [p.get_text() for p in soup.find_all("p")]
        content = " ".join(paragraphs)

        yield {
            "url": response.url,
            "title": title,
            "content": content
        }
