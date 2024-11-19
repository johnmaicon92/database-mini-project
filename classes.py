
class Book:
    def __init__(self, title, author_id, isbn, publication_date, genre, id=None, is_borrowed=False):
        self.id = id
        self.title = title
        self.author_id = author_id
        self.isbn = isbn
        self.publication_date = publication_date
        self.genre = genre
        self.is_borrowed = is_borrowed

    def __str__(self):
        return f"Title: {self.title}, Author: {self.author_id}, ISBN: {self.isbn}, Genre: {self.genre}, Published: {self.publication_date}, Available: {'Yes' if not self.is_borrowed else 'No'}"

class User:
    def __init__(self, name, library_id, email, borrowed_books=[]):
        self.name = name
        self.library_id = library_id
        self.email = email
        self.borrowed_books = borrowed_books

    def __str__(self):
        return f"Name: {self.name}, Library ID: {self.library_id}, Email: {self.email}, Borrowed Books: {self.borrowed_books}"

class Author:
    def __init__(self, name, id=None, biography=None):
        self.id = id
        self.name = name
        self.biography = biography 

    def __str__(self):
        return f"Author: {self.name}"
