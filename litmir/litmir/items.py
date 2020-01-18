# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Join, Compose, MapCompose


def description_clean(values):
    for value in values:
        yield value.strip('\n').strip().strip('\t').replace('"', '\'')


def description_join(values):
    return ' '.join(values)


class Book(scrapy.Item):
    book_name = scrapy.Field()
    author = scrapy.Field()
    genre = scrapy.Field()
    number_of_pages = scrapy.Field()
    in_language = scrapy.Field()
    original_language = scrapy.Field()
    interpreter = scrapy.Field()
    publisher = scrapy.Field()
    printed_name = scrapy.Field()
    city_publish = scrapy.Field()
    year_publish = scrapy.Field()
    isbn = scrapy.Field()
    info_block = scrapy.Field()
    description = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    author_from_book_id = scrapy.Field()
    book_id = scrapy.Field()


class BookItemLoader(ItemLoader):
    book_name_out = TakeFirst()
    number_of_pages_out = TakeFirst()
    number_of_pages_in = Join()
    in_language_out = TakeFirst()
    description_in = Compose(description_clean, description_join)
    description_out = TakeFirst()
    # images_out = TakeFirst()
    # author_from_book_id_out = TakeFirst()
    book_id_out = TakeFirst()


class Author(scrapy.Item):
    author_name = scrapy.Field()
    gender = scrapy.Field()
    birth_date = scrapy.Field()
    birth_place = scrapy.Field()
    death_date = scrapy.Field()
    death_place = scrapy.Field()
    author_bio = scrapy.Field()
    author_id = scrapy.Field()


class AuthorItemLoader(ItemLoader):
    author_bio_in = Compose(description_clean, description_join)
    author_bio_out = TakeFirst()
    author_name_out = TakeFirst()
    gender_out = TakeFirst()
    birth_date_out = TakeFirst()
    birth_place_out = TakeFirst()
    death_date_out = TakeFirst()
    death_place_out = TakeFirst()
    author_id_out = TakeFirst()
