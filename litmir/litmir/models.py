from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class BookAuthor(Base):
    __tablename__ = 'book_author'

    book_id = Column(Integer, ForeignKey('books.id'), primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'), primary_key=True)
    book = relationship('Book', back_populates='authors')
    author = relationship('Author', back_populates='books')


class BookGenre(Base):
    __tablename__ = 'book_genre'

    book_id = Column(Integer, ForeignKey('books.id'), primary_key=True)
    genre_id = Column(Integer, ForeignKey('genres.id'), primary_key=True)
    book = relationship('Book', back_populates='genres')
    genre = relationship('Genre', back_populates='books')


class BookInterpreter(Base):
    __tablename__ = 'book_interpreter'

    book_id = Column(Integer, ForeignKey('books.id'), primary_key=True)
    interpreter_id = Column(Integer, ForeignKey('interpreters.id'), primary_key=True)
    book = relationship('Book', back_populates='interpreters')
    interpreter = relationship('Interpreter', back_populates='books')


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    number_of_pages = Column(Integer)
    printed_name = Column(String)
    description = Column(String)
    year_publish = Column(String)
    city_publish = Column(String)
    publisher = Column(String)
    in_language = Column(String)
    original_language = Column(String)
    image = relationship('Image', uselist=False, back_populates='book', cascade='all, delete, delete-orphan')
    isbn = relationship('Isbn', back_populates='book', lazy='dynamic', cascade='all, delete, delete-orphan')
    authors = relationship('BookAuthor', back_populates='book')
    genres = relationship('BookGenre', back_populates='book')
    interpreters = relationship('BookInterpreter', back_populates='book')

    def __repr__(self):
        return '<Book %r>' % self.title


class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    gender = Column(String)
    birth_date = Column(String)
    birth_place = Column(String)
    death_date = Column(String)
    death_place = Column(String)
    author_bio = Column(String)
    books = relationship('BookAuthor', back_populates='author')

    def __repr__(self):
        return '<Author %r' % self.name


class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, sqlite_on_conflict_unique='IGNORE')
    books = relationship('BookGenre', back_populates='genre')

    def __repr__(self):
        return '<Genre %r' % self.name


class Interpreter(Base):
    __tablename__ = 'interpreters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    books = relationship('BookInterpreter', back_populates='interpreter')

    def __repr__(self):
        return '<Interpreter %r' % self.name


class Isbn(Base):
    __tablename__ = 'isbn'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'))
    book = relationship('Book', back_populates='isbn')

    def __repr__(self):
        return '<ISBN %r' % self.name


class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, autoincrement=True)
    checksum = Column(String)
    path = Column(String, nullable=False, default='full/no_cover.jpg')
    book_id = Column(Integer, ForeignKey('books.id'))
    book = relationship('Book', back_populates='image')

    def __repr__(self):
        return '<Images %r' % self.checksum

