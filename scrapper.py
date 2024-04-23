import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider
from scrapy.utils.log import configure_logging
import multiprocessing
import logging

from settings import WikipediaItem, CUSTOM_SETTINGS, MAX_PAGES

class WikipediaSpider(scrapy.Spider):
    name = 'wikipedia'
    allowed_domains = ['wikipedia.org']  # Corrected domain
    start_urls = [
        'https://en.wikipedia.org/wiki/Artificial_intelligence'  # Corrected URL
    ]
    max_pages = MAX_PAGES
    max_depth = 2
    handle_httpstatus_list = [403, 404]
    custom_settings = CUSTOM_SETTINGS

    def parse(self, response):
        if response.status in self.handle_httpstatus_list:
            self.logger.error(f'Failed to retrieve {response.url}')
            return
        paragraphs = response.css('p::text').getall()
        text_content = ' '.join(paragraphs)
        yield WikipediaItem(url=response.url, text=text_content)

        with open('wikipedia_ai.txt', 'a', encoding='utf-8') as f:  # Corrected file name
            f.write(f'URL: {response.url}\n\nContent: {text_content}\n\n')

        links = LinkExtractor(deny=('facebook.com',)).extract_links(response)
        for link in links:
            if self.max_pages <= 0:
                raise CloseSpider('Maximum pages limit reached')
            self.max_pages -= 1
            yield scrapy.Request(link.url, callback=self.parse)

def run_spider(_):
    configure_logging()
    process = CrawlerProcess()
    process.crawl(WikipediaSpider)
    process.start()

if __name__ == "__main__":
    multiprocessing.log_to_stderr()
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.INFO)

    pool = multiprocessing.Pool(processes=4)
    pool.map(run_spider, range(4))
    pool.close()
    pool.join()
