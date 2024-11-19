import os
from classes import Book, User, Author
from error_handling import handle_file_error


def load_books_from_file(filename):
    books = []
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:  # Skip empty lines
                        title, author, isbn, genre, pub_date, is_borrowed = line.split(',')
                        books.append(Book(title, author, isbn, genre, pub_date, is_borrowed == 'True'))
    except Exception as e:
        handle_file_error(e)
    return books

def save_books_to_file(books, filename):
    with open(filename, 'w') as file:
        for book in books:
            file.write(f"{book.title},{book.author},{book.isbn},{book.genre},{book.publication_date},{book.is_borrowed}\n")

def load_users_from_file(filename):
    users = []
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    name, library_id, email, borrowed_books = line.split(',')
                    user = User(name, library_id, email)
                    user.borrowed_books = borrowed_books.split(';') if borrowed_books else []
                    users.append(user)
    return users

def save_users_to_file(users, filename):
    with open(filename, 'w') as file:
        for user in users:
            borrowed_books = ';'.join(user.borrowed_books)
            file.write(f"{user.name},{user.library_id},{user.email},{borrowed_books}\n")

def load_authors_from_file(filename):
    authors = []
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    name, biography = line.split(',')
                    authors.append(Author(name, biography))
    return authors

def save_authors_to_file(authors, filename):
    with open(filename, 'w') as file:
        for author in authors:
            file.write(f"{author.name},{author.biography}\n")