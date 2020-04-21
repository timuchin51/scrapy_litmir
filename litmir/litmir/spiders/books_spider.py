from urllib.parse import urljoin, urlparse

from scrapy.spiders import CrawlSpider, Rule
from litmir.items import Author, Book, AuthorItemLoader, BookItemLoader
from scrapy.linkextractors import LinkExtractor
from scrapy.loader.processors import MapCompose


class BooksSpider(CrawlSpider):

    name = "books"
    allowed_domains = ['www.litmir.me']
    start_urls = ['https://www.litmir.me/bs/?rs=5%7C1%7C0&p=1']

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//td[@style="padding-right: 10px"]'), follow=True),
        Rule(LinkExtractor(restrict_xpaths='//div[@class="book_name"]/a'), callback='parse_book', follow=True),
    )

    def parse_book(self, response):
        self.logger.info(f'url of books: {response.url}, '
                         f'item count {self.crawler.stats.get_value("item_scraped_count")}')
        loader = BookItemLoader(item=Book(), response=response)
        loader.add_xpath('title', '//div[@itemprop="name"]/text()')
        loader.add_xpath('author', '//td[@class="bd_desc2"]/div/span[@itemprop="author"]/span/meta/@content')
        loader.add_xpath('genre', '//span[@itemprop="genre"]/text()')
        loader.add_xpath('number_of_pages', '//span[@itemprop="numberOfPages"]/text()')
        loader.add_xpath('in_language', '//span[@itemprop="inLanguage"]/text()')
        loader.add_xpath('info_block', '//td[@class="bd_desc2"][2]/div')
        loader.add_xpath('isbn', '//span[@itemprop="isbn"]/text()')
        loader.add_xpath('description', '//div[@itemprop="description"]/p/text()')
        loader.add_xpath('image_urls', '//img[@jq="BookCover"]/@src',
                         MapCompose(lambda x: urljoin(response.url, x)))
        loader.add_value('book_id', response.url)
        loader.add_xpath('author_book_id', '//meta[@property="book:author"]/@content')
        author_page = response.xpath('//td[@class="bd_desc2"]/div[1]/a/@href').getall()
        yield loader.load_item()
        for page in author_page:
            yield response.follow(page, self.parse_author)

    def parse_author(self, response):
        self.logger.info(f'url of author: {response.url}, '
                         f'item count: {self.crawler.stats.get_value("item_scraped_count")}')
        loader = AuthorItemLoader(item=Author(), response=response)
        loader.add_xpath('name', '//div[@itemprop="name"]/descendant::*/text()')
        loader.add_xpath('gender', '//span[@itemprop="gender"]/text()')
        loader.add_xpath('birth_date', '//span[@itemprop="birthDate"]/text()')
        loader.add_xpath('birth_place', '//span[@itemprop="birthPlace"]/text()')
        loader.add_xpath('death_date', '//span[@itemprop="deathDate"]/text()')
        loader.add_xpath('death_place', '//span[@itemprop="deathPlace"]/text()')
        loader.add_xpath('author_bio', '//div[@itemprop="description"]/div/div/descendant::*/text()')
        loader.add_value('author_id', response.url)
        yield loader.load_item()
