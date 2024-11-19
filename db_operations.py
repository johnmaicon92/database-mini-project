
import mysql.connector
from mysql.connector import Error
from classes import Book, User, Author 
from connect_mysql import connect_database
from datetime import datetime
def handle_mysql_error(e):
    """ Handle MySQL connection errors """
    print(f"Database error occurred: {e}")
    with open("error_log.txt", "a") as file:
        file.write(f"Database Error: {e}\n")

def fetch_authors(conn):
    """Fetch all authors from the database."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM authors")
        authors = []
        for row in cursor.fetchall():
            authors.append(Author(id=row[0], name=row[1]))
        return authors
    except mysql.connector.Error as e:
        handle_mysql_error(e)
        return []
    
def save_book(conn, book):
    """ Save a book to the database """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM authors WHERE name = %s", (book.author,))
        author_data = cursor.fetchone()
        if author_data:
            author_id = author_data[0]
            cursor.execute("""
                INSERT INTO books (title, author_id, isbn, genre, publication_date) 
                VALUES (%s, %s, %s, %s, %s)
            """, (book.title, author_id, book.isbn, book.publication_date, book.genre))
            conn.commit()
            book.id = cursor.lastrowid
        else:
            print(f"Author '{book.author}' not found in the database. Book not saved.")
    except mysql.connector.Error as e:
        handle_mysql_error(e)

def fetch_books(conn):
    """Fetch all books from the database."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                b.id, b.title, b.author_id, b.isbn, b.genre, b.publication_date, b.is_borrowed
            FROM 
                books b
            JOIN 
                authors a ON b.author_id = a.id
        """)
        books = []
        for row in cursor.fetchall():
            books.append(Book(id=row[0], title=row[1], author_id=row[2], isbn=row[3], genre=row[4], publication_date=row[5], is_borrowed=row[6]))
        return books
    except mysql.connector.Error as e:
        handle_mysql_error(e)
        return []

def fetch_users(conn):
    """ Fetch all users from the database """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = [User(id=row[0], name=row[1], library_id=row[2 ], email=row[3]) for row in cursor.fetchall()]
        cursor.close()
        return users
    except mysql.connector.Error as e:
        handle_mysql_error(e)
        return []


def save_user(conn, user):
    """ Save a user to the database """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (name, library_id, email) 
            VALUES (%s, %s, %s)
        """, (user.name, user.library_id, user.email))
        conn.commit()
    except mysql.connector.Error as e:
        handle_mysql_error(e)

def save_author(author):
    """ Save an author to the database """
    try:
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO authors (name, biography) 
            VALUES (%s, %s)
        """, (author.name, author.biography))
        conn.commit()
        conn.close()
    except mysql.connector.Error as e:
        handle_mysql_error(e)