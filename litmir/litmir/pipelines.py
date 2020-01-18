# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from w3lib import html
import re
from scrapy.exceptions import NotConfigured
import sqlite3


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
        if item.get('author_name'):
            item['author_name'] = item['author_name'].strip()

        if item.get('author_from_book_id'):
            list_of_id = []
            for el in item['author_from_book_id']:
                el = re.search(r'(?<=/a/\?id=)\d+', el)
                if el is not None:
                    list_of_id.append(el.group(0))
            item['author_from_book_id'] = list_of_id

        if item.get('author_id'):
            item['author_id'] = re.search(r'(?<=id=)\d+', item['author_id']).group(0)
        if item.get('book_id'):
            item['book_id'] = re.search(r'(?<=b=)\d+', item['book_id']).group(0)
        return item


class DataBasePipeline(object):

    def __init__(self, db):
        self.db = db
        self.con = sqlite3.connect(self.db)
        self.cursor = self.con.cursor()

    @classmethod
    def from_crawler(cls, crawler):
        db = crawler.settings.get("DB_NAME")
        if not db:
            raise NotConfigured('we have no db_name')
        return cls(db)

    def open_spider(self, spider):
        self.cursor.executescript("""
            pragma foreign_keys=on;
            create table if not exists book (
                                id integer not null primary key,
                                name text not null, 
                                number_of_pages integer, 
                                printed_name text, 
                                description text,
                                year_publish date,
                                city_publish text,
                                publisher text,
                                in_language integer,
                                original_language integer,
                                foreign key (in_language) references language (id),
                                foreign key (original_language) references language (id));

            create table if not exists author (
                                id integer not null primary key,
                                name text not null,
                                gender text,
                                birth_date date,
                                birth_place text,
                                death_date date,
                                death_place text,
                                author_bio text);

            create table if not exists book_author (
                                book_id integer not null,
                                author_id integer not null,
                                foreign key (book_id) references book (id),
                                foreign key (author_id) references author (id)
                                unique (book_id, author_id));

            create table if not exists genre (
                                id integer not null primary key autoincrement,
                                name text not null,
                                unique (name));

            create table if not exists book_genre (
                                book_id integer not null,
                                genre_id integer not null ,
                                foreign key (book_id) references book (id),
                                foreign key (genre_id) references genre (id));

            create table if not exists interpreter (
                                id integer primary key autoincrement,
                                name text,
                                unique (name));

            create table if not exists book_interpreter (
                                book_id integer not null,
                                interpreter_id integer not null,
                                foreign key (book_id) references book (id),
                                foreign key (interpreter_id) references interpreter (id));

            create table if not exists isbn (
                                name text not null primary key ,
                                book_id integer,
                                foreign key (book_id) references book (id));

            create table if not exists language (
                                id integer not null primary key autoincrement,
                                name text not null,
                                unique (name));
            
            create table if not exists tmp (
                                book_id integer not null,
                                author_id integer not null,
                                foreign key (book_id) references book(id),
                                unique(book_id, author_id));
            
            create table if not exists book_images (
                                checksum integer,
                                path text not null default "full/no_cover.jpg",
                                book_id integer primary key,
                                foreign key (book_id) references book (id));
                                
                                """)

        self.cursor.execute("""create trigger if not exists after_tmp_insert after insert
                                on author
                                begin
                                insert or ignore into book_author (book_id, author_id)
                                    select book_id, author_id from tmp, author
                                    where author.id=tmp.author_id;
                                delete from tmp
                                    where book_id in (select book_id from book_author) and author_id in
                                    (select id from author, book_author where id=book_author.author_id);
                                end;""")

    def process_item(self, item, spider):

        interpreter_insert = """insert or ignore into interpreter (name) values (?)"""
        genre_insert = """insert or ignore into genre (name) values (?)"""
        language_insert = """insert or ignore into language (name) values (?)"""
        book_insert = """insert or ignore into book (
                                       id, name, number_of_pages, printed_name, description, year_publish,city_publish, 
                                       publisher, in_language, original_language
                                       ) 
                                       select ?, ?, ?, ?, ?, ?, ?, ?, 
                                       (select id  from language where name = (?)),
                                       (select id from language where name = (?))
                                       """
        tmp_insert = """insert into tmp(author_id, book_id) values (?, ?)"""
        book_genre_insert = """insert into book_genre (book_id, genre_id) 
                                            select book.id, genre.id from book, genre 
                                            where book.name = (?) and genre.name = (?)"""
        book_interpreter_insert = """insert into book_interpreter(book_id, interpreter_id)
                                                select book.id, interpreter.id from book, interpreter
                                                where book.name = (?) and interpreter.name = (?)"""
        isbn_insert = """insert or ignore into isbn (name, book_id)
                                        select (?), book.id from book
                                        where book.name = (?)"""
        book_images_insert = """insert or ignore into book_images(checksum, path, book_id) 
                                            select ?, ?, id from book;"""
        author_insert = """insert into author (
                                        id, name, gender, birth_date, birth_place, death_date, death_place, author_bio
                                        ) values (?, ?, ?, ?, ?, ?, ?, ?)"""
        if item.get('book_name'):

            if item.get('interpreter'):
                self.cursor.executemany(interpreter_insert,
                                        zip(item.get('interpreter')))  # insert "interpreter" into db

            if item.get('genre'):
                self.cursor.executemany(genre_insert, zip(item.get('genre')))  # insert "genre" into db

            if item.get('in_language'):
                self.cursor.execute(language_insert, (item.get('in_language'),))  # insert "in_language" into db

            if item.get('original_language'):
                self.cursor.execute(language_insert,
                                    (item.get('original_language'),))  # insert "original_language" into db

            self.cursor.execute(book_insert,
                                (item.get('book_id'),
                                 item.get('book_name'),
                                 item.get('number_of_pages'),
                                 item.get('printed_name'),
                                 item.get('description'),
                                 item.get('year_publish'),
                                 item.get('city_publish'),
                                 item.get('publisher'),
                                 item.get('in_language'),
                                 item.get('original_language'),
                                 )
                                )

            if item.get('author_from_book_id'):
                self.cursor.executemany(tmp_insert,
                                        ((x, item.get('book_id'),) for x in item.get('author_from_book_id'))
                                        )

            self.cursor.executemany(book_genre_insert,
                                    ((item.get('book_name'), x,) for x in item.get('genre'))
                                    )

            if item.get('interpreter'):
                self.cursor.executemany(book_interpreter_insert,
                                        ((item.get('book_name'), x,) for x in item.get('interpreter'))
                                        )

            if item.get('isbn'):
                self.cursor.executemany(isbn_insert,
                                        ((x, item.get('book_name')) for x in item.get('isbn')))  # insert "isbn" into db

            if item.get('images'):
                self.cursor.execute(book_images_insert,
                                    (item.get('images')[0].get('checksum'),
                                     item.get('images')[0].get('path'))
                                    )

        if item.get('author_id'):
            self.cursor.execute(author_insert,
                                (item.get('author_id'),
                                 item.get('author_name'),
                                 item.get('gender'),
                                 item.get('birth_date'),
                                 item.get('birth_place'),
                                 item.get('death_date'),
                                 item.get('death_place'),
                                 item.get('author_bio'),
                                 )
                                )

        self.con.commit()
        return item

    def close_spider(self, spider):
        self.con.close()
