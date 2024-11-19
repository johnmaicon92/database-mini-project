import mysql.connector
from mysql.connector import Error

def handle_mysql_error(e):
    """ Handle MySQL connection errors """
    print(f"Database error occurred: {e}")
    with open("error_log.txt", "a") as file:
        file.write(f"Database Error: {e}\n")

def handle_file_error(e):
    """ Handle file I/O errors """
    print(f"File error occurred: {e}")
    with open("error_log.txt", "a") as file:
        file.write(f"File Error: {e}\n")

def handle_general_error(e):
    """ Handle general errors """
    print(f"An error occurred: {e}")
    with open("error_log.txt", "a") as file:
        file.write(f"General Error: {e}\n")

def handle_invalid_input():
    """ Handle invalid user inputs during menu selections """
    print("Invalid input. Please enter a number corresponding to the menu options.")
import os
from classes import Book, User, Author

files_to_check = ['books.txt', 'users.txt', 'authors.txt']

for filename in files_to_check:
    if not os.path.exists(filename):
        print(f"File {filename} does not exist.")

def load_books(filename):
    books = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if not line:  
                    continue
                try:
                    title, author, isbn, genre, publication_date, is_borrowed = line.split(',', 5)
                    book = Book(title, author, isbn, genre, publication_date)
                    book.is_borrowed = is_borrowed.lower() == 'true' 
                    books.append(book)
                except ValueError:
                    print(f"Skipping line due to incorrect format: {line}")
    except FileNotFoundError:
        print(f"{filename} not found. Starting with an empty book list.")
    return books

def save_books(books, filename):
    with open(filename, 'a') as file:
        for book in books:
            file.write(f"{book.get_title()},{book.get_author()},{book.isbn},{book.genre},{book.publication_date},{book.is_borrowed}\n")
    
def load_users(filename):
    users = []
    existing_emails = set()
    existing_library_ids = set()
    existing_usernames = set()
    
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                for line in file:
                    parts = line.strip().split(',')
                    
                    if len(parts) < 4:
                        print(f"Warning: Skipping line due to insufficient data: {line.strip()}")
                        continue
                    
                    try:
                        name, library_id, email, borrowed_books = parts
                        user = User(name, library_id, email)  
                        user.borrowed_books = borrowed_books.split(';') if borrowed_books else []
                        users.append(user)
                        existing_emails.add(email)
                        existing_library_ids.add(library_id)
                        existing_usernames.add(name)
                    except ValueError as ve:
                        print(f"Error processing line: {line.strip()}. Error: {ve}")
    except Exception as e:
        print(f"Error loading users: {e}")
    
    return users, existing_emails, existing_library_ids, existing_usernames

def save_users(users, filename):
    with open(filename, 'w') as file:
        for user in users:
            borrowed_books = ';'.join(user.get_borrowed_books())
            file.write(f"{user.get_name()},{user.get_library_id()},{user.get_email()},{borrowed_books}\n")

def load_authors(filename):
    authors = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                try:
                    name, biography = line.strip().split(',', 1) 
                    authors.append(Author(name, biography))
                except ValueError:
                    print(f"Warning: Skipping line due to missing biography: {line.strip()}")
    except FileNotFoundError:
        print(f"{filename} not found. Starting with an empty author list.")
    return authors

def save_authors(authors, filename):
    with open(filename, 'a') as file:
        for author in authors:
            file.write(f"{author.get_name()},{author.get_biography()}\n")
    print(f"Successfully saved {len(authors)} authors to {filename}.")