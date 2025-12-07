from scrapy import Spider
from scrapy.exceptions import CloseSpider
import os

class QuotesToScrapeSpider(Spider):
    name = "quote_spider"
    allowed_domains = ["azquotes.com"]
    start_urls = ["https://www.azquotes.com/top_quotes.html"]

    output_file = "../quotes_output.html"

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "FEED_EXPORT_ENCODING": "utf-8"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write('<html><head><meta charset="utf-8"><title>Quotes</title></head><body>\n')

    def closed(self, spider):
        with open(self.output_file, "a", encoding="utf-8") as f:
            f.write("</body></html>")

    def parse(self, response):
        blocks = response.css("ul.list-quotes > li > div.wrap-block")

        found = 0
        with open(self.output_file, "a", encoding="utf-8") as f:
            for block in blocks:
                text = block.css("a.title::text").get(default="").strip()
                author = block.css("div.author a::text").get(default="").strip()
                tags = block.css("div.tags a::text").getall()

                if text and author:
                    found += 1
                    f.write(f"""
                    <p>
                        <strong>{text}</strong><br>
                        — {author}<br>
                        Tags: {", ".join(tags)}
                    </p>
                    """)

        self.logger.info(f"Extracted {found} quotes from {response.url}")
