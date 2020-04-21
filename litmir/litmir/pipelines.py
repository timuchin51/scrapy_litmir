# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
from w3lib import html
import re
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .models import Base, Book, Author, Genre, Interpreter, Isbn, Image, BookAuthor, BookGenre, BookInterpreter


class ParserPipeline(object):

    def process_item(self, item, spider):
        if item.get('info_block'):
            info_block_list = []
            for i in item.get('info_block'):
                i = html.remove_tags(i)
                i = re.sub(r' \.\.\.', ' ', i)
                info_block_list.append(i)
                item['info_block'] = info_block_list
            for i in item.get('info_block'):
                i = i.partition(':')
                el = {i[0]: i[2].strip() for x in i}
                if el.get('Язык оригинальной книги'):
                    item['original_language'] = el['Язык оригинальной книги']
                if el.get('Переводчик(и)'):
                    item['interpreter'] = el['Переводчик(и)'].split(', ')
                if el.get('Издатель'):
                    item['publisher'] = el['Издатель']
                if el.get('Город печати'):
                    item['city_publish'] = el['Город печати']
                if el.get('Год печати'):
                    item['year_publish'] = el['Год печати']
                if el.get('Название печатной книги'):
                    item['printed_name'] = el['Название печатной книги']
                if el.get('ISBN'):
                    item['isbn'] = el['ISBN'].split(', ')
        if item.get('name'):
            item['name'] = item['name'].strip()
        return item


class DataBasePipeline(object):
    Session = sessionmaker()

    def __init__(self, db_name):
        self.db_name = db_name
        self.engine = create_engine('sqlite:///%s' % self.db_name, echo=False)
        if not os.path.exists(db_name):
            Base.metadata.create_all(self.engine)

    @classmethod
    def from_crawler(cls, crawler):
        db_name = crawler.settings.get('DB_NAME')
        return cls(db_name)

    def open_spider(self, spider):
        self.session = self.Session(bind=self.engine)

    def process_item(self, item, spider):
        if item.get('book_id'):
            book = Book(
                id=item.get('book_id'),
                title=item.get('title'),
                number_of_pages=item.get('number_of_pages'),
                printed_name=item.get('printed_name'),
                description=item.get('description'),
                year_publish=item.get('year_publish'),
                city_publish=item.get('city_publish'),
                publisher=item.get('publisher'),
                in_language=item.get('in_language'),
                original_language=item.get('original_language')
            )

            if item.get('book_id'):
                book_author = BookAuthor()
                book_author.book_id = item['book_id']
                book_author.author_id = item['author_book_id']

            if item.get('interpreter'):
                inter = [el[0] for el in self.session.query(Interpreter.name).all()]
                for i in item['interpreter']:
                    book_inter = BookInterpreter()
                    if i not in inter:
                        interp = Interpreter(name=i)
                        self.session.add(interp)
                        self.session.commit()

                    interp_id = self.session.query(Interpreter.id).filter_by(name=i).first()[0]
                    book_inter.book_id = item['book_id']
                    book_inter.interpreter_id = interp_id
                    self.session.add(book_inter)

            if item.get('genre'):
                genres = [el[0] for el in self.session.query(Genre.name).all()]
                for i in item['genre']:
                    book_genre = BookGenre()
                    if i not in genres:
                        genre = Genre(name=i)
                        self.session.add(genre)
                        self.session.commit()

                    g_id = self.session.query(Genre.id).filter_by(name=i).first()[0]
                    book_genre.book_id = item['book_id']
                    book_genre.genre_id = g_id
                    self.session.add(book_genre)

            if item.get('isbn'):
                book.isbn = [Isbn(name=el) for el in item['isbn']]

            if item.get('images'):
                book.image = Image(checksum=item['images'][0].get('checksum'),
                                   path=item['images'][0].get('path'))

            self.session.add(book)
            self.session.add(book_author)
            self.session.commit()

        if item.get('author_id'):
            author = Author(
                id=item.get('author_id'),
                name=item.get('name'),
                gender=item.get('gender'),
                birth_date=item.get('birth_date'),
                birth_place=item.get('birth_place'),
                death_date=item.get('death_date'),
                death_place=item.get('death_place'),
                author_bio=item.get('author_bio'),

            )

            self.session.add(author)
            self.session.commit()

    def close_spider(self, spider):
        self.session.commit()
        self.session.close()
