
from classes import Book, User, Author
from user_interaction import display_main_menu, display_book_operations, display_user_operations, display_author_operations
from db_operations import fetch_books, fetch_authors, save_book, save_user, save_author, fetch_users
from datetime import datetime
from file_handling import load_books_from_file, save_books_to_file, load_users_from_file, save_users_to_file, load_authors_from_file, save_authors_to_file
from error_handling import handle_invalid_input
from connect_mysql import connect_database
from error_handling import handle_mysql_error
import mysql.connector
import re


def main():
    conn = connect_database()
    if conn:
        books = fetch_books(conn)
        authors = fetch_authors(conn) 
        users = fetch_users(conn)
        
    else:
        print("Failed to connect to the database. Exiting.")
        exit() 
    books = load_books_from_file('books_backup.txt')
    users = load_users_from_file('users_backup.txt')
    authors = load_authors_from_file('authors_backup.txt')
    
    while True:
        display_main_menu()
        try:
            choice = input("Select an option (1-4): ")

            if choice == '1':
                handle_book_operations(books, conn, users)
            elif choice == '2':
                handle_user_operations(users, conn)
            elif choice == '3':
                handle_author_operations(authors, conn)
            elif choice == '4':
                conn = connect_database()
                if conn:
                    for book in books:
                        save_book(conn, book)
                    for user in users:
                        save_user(conn, user)
                    for author in authors:
                        save_author(conn, author)
                    conn.close()
                else:
                    print("Failed to connect to the database. Exiting.")
                    exit()

                save_books_to_file(books, 'books_backup.txt')
                save_users_to_file(users, 'users_backup.txt')
                save_authors_to_file(authors, 'authors_backup.txt')

                print("Exiting the Library Management System.")
                break
            else:
                handle_invalid_input()
        except ValueError:
            handle_invalid_input()

def handle_book_operations(books, conn, users):
    while True:
        display_book_operations()
        choice = input("Select an option (1-7): ")
        
        if choice == '1':
            add_book(conn, books)
        elif choice == '2':
            book_title = input("Enter the book title to borrow: ")
            book = find_book_by_title(books, book_title)
            if book:
                borrow_book(conn, users, books, book)
            else:
                print("Book not found.")
        elif choice == '3':
            return_book(conn, users, book)
        elif choice == '4':
            search_book(conn, books)
        elif choice == '5':
            list_books(conn, books)
        elif choice == '6':
            remove_book_from_db(book, conn)
        elif choice == '7':
            print("Returning to Main Menu.")
            return
        else:
            print("Invalid option. Please try again.")



def add_book(conn, books):
    try:
        
        title = input("Enter book title")
        author_name = input("Enter author name: ")
        cursor = conn.cursor(buffered=True)
        cursor.execute("INSERT INTO authors (name) VALUES (%s)", (author_name,))
        conn.commit()
        cursor.execute("SELECT LAST_INSERT_ID()") 
        author_id = cursor.fetchone()[0]

        genre = input("Enter genre: ")

        while True:
            pub_date_input = input("Enter publication date (YYYYMMDD or YYYY-MM-DD): ")
            
            if len(pub_date_input) == 8 and pub_date_input.isdigit():
                year = pub_date_input[:4]
                month = pub_date_input[4:6]
                day = pub_date_input[6:]
                publication_date = f"{year}-{month}-{day}"
                break
            elif len(pub_date_input) == 10 and '-' in pub_date_input:
                try:
                    publication_date = datetime.strptime(pub_date_input, "%Y-%m-%d").strftime("%Y-%m-%d")
                    break 
                except ValueError:
                    print("Invalid date format. Please enter the date as YYYYMMDD or YYYY-MM-DD.")
            else:
                print("Invalid date format. Please enter the date as YYYYMMDD or YYYY-MM-DD.")

        while True:
            isbn = input("Enter ISBN (International Standard Book Number): ")

            if isbn.isdigit():
                break
            print("Invalid ISBN format. Please enter only numbers.")
        
        cursor = conn.cursor()
        cursor.execute("INSERT INTO authors (name) VALUES (%s)", (author_name,))
        conn.commit()
        cursor = conn.cursor()
        cursor.execute("SELECT LAST_INSERT_ID()")
        author_id = cursor.fetchone()[0]
        new_book = Book(title=title, author_id=author_id, isbn=isbn, publication_date=publication_date, genre=genre)
        cursor.execute("INSERT INTO books (title, author_id, isbn, publication_date, genre, is_borrowed) VALUES (%s, %s, %s, %s, %s, %s)", (new_book.title, new_book.author_id, new_book.isbn, new_book.publication_date, new_book.genre, False))
        conn.commit()
        print(f"Book '{new_book.title}' added successfully.")

    except mysql.connector.Error as e:

        handle_mysql_error(e)

def list_books(conn, books):
    if not books:
        print("No books available in the system.")
    else:
        print("Books in the system:")
        for book in books:
            print(book)

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                b.id, b.title, a.name AS author, b.isbn, b.genre, b.publication_date, b.is_borrowed
            FROM 
                books b
            JOIN 
                authors a ON b.author_id = a.id
        """)
        db_books = cursor.fetchall()
        if db_books:
            print("\nBooks in the database:")
            for row in db_books:
                db_book = Book(id=row[0], title=row[1], author_id=row[2], isbn=row[3], genre=row[4], publication_date=row[5], is_borrowed=row[6])
                print(db_book)
        cursor.close()
    except mysql.connector.Error as e:
        handle_mysql_error(e)

def borrow_book(conn, users, books, book):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT is_borrowed FROM books WHERE id = %s", (book.id,))
        book_data = cursor.fetchone()
        if book_data and not book_data[0]:
            cursor.execute("UPDATE books SET is_borrowed = %s WHERE id = %s", (True, book.id))
            current_user = users[0]
            current_user.borrowed_books.append(book)
            conn.commit()
            print(f"{current_user.name} has borrowed the book '{book.title}'.")

            books.remove(book)

            print(f"Book '{book.title}' removed from the system.")
        else:
            print("Book is already borrowed or does not exist.")
    except mysql.connector.Error as e:
        handle_mysql_error(e)

def find_book_by_title(books, book_title):
    for book in books:
        if book.title.lower() == book_title.lower():
            return book
    return None

def return_book(conn, users, book):
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE books SET is_borrowed = %s WHERE id = %s", (False, book.id))
        current_user = users[0]
        current_user.borrowed_books.remove(book)
        conn.commit()
        print(f"{current_user.name} has returned the book '{book.title}'.")
    except mysql.connector.Error as e:
        handle_mysql_error(e)

def fetch_books(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                b.id, b.title, a.name AS author, b.isbn, b.genre, b.publication_date
            FROM 
                books b
            JOIN 
                authors a ON b.author_id = a.id
        """)
        books = []
        for row in cursor.fetchall():
            books.append(Book(id=row[0], title=row[1], author_id=row[2], isbn=row[3], genre=row[5], publication_date=row[4]))
        return books
    except mysql.connector.Error as e:
        handle_mysql_error(e)
        return []


def search_book(conn, books):
    search_term = input("Enter the book title to search: ")
    matching_books = [book for book in books if book.title.lower() == search_term.lower()]
    if matching_books:
        print("Found the following matching books in the system:")
        for book in matching_books:
            print(book)

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                b.id, b.title, a.name AS author, b.isbn, b.genre, b.publication_date, b.is_borrowed
            FROM 
                books b
            JOIN 
                authors a ON b.author_id = a.id
            WHERE 
                b.title LIKE %s
            """,
            (f"%{search_term}%",), 
        )
        db_books = cursor.fetchall()
        if db_books:
            print("\nFound the following matching books in the database:")
            for row in db_books:
                db_book = Book(
                    id=row[0],
                    title=row[1],
                    author_id=row[2],
                    isbn=row[3],
                    genre=row[4],
                    publication_date=row[5],
                    is_borrowed=row[6],
                )
                print(db_book)
        cursor.close()
    except mysql.connector.Error as e:
        handle_mysql_error(e)


def remove_book_from_db(book, conn):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE id = %s", (book.id,))
        conn.commit()

        
        books = load_books_from_file('books_backup.txt')
        books.remove(book) 
        save_books_to_file(books, 'books_backup.txt') 
        print(f"Book '{book.title}' removed successfully.")
    except mysql.connector.Error as e:
        handle_mysql_error(e)

def handle_user_operations(users):
    while True:
        display_user_operations()
        choice = input("Select an option (1-5): ")
        
        if choice == '1':
            add_user(users)
        elif choice == '2':
            view_user_details(users)
        elif choice == '3':
            list_users(users)
        elif choice == '4':
            remove_user(users)
        elif choice == '5':
            return
        else:
            print("Invalid option. Please try again.")

def validate_email(email):
    
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(email_pattern, email):
        return True
    else:
        return False

def add_user(users):
    name = input("Enter user name: ")
    
    while True:
        email = input("Enter user email: ")
        if validate_email(email):
            break
        else:
            print("Invalid email format. Please enter a valid email.")

    user = User(name, email)
    users.append(user)
    print(f"User '{name}' added successfully.")

def view_user_details(users):
    library_id = input("Enter the library ID of the user: ")
    
    user_found = None
    for user in users:
        if user.library_id == library_id:
            user_found = user
            break
    
    if user_found:
        print(user_found)
    else:
        print(f"No user found with library ID: {library_id}")

def list_users(users):
    if not users:
        print("No users found.")
    else:
        for user in users:
            print(user)

def remove_user(users):
    library_id = input("Enter the library ID of the user to remove: ")
    
    user_to_remove = None
    for user in users:
        if user.library_id == library_id:
            user_to_remove = user
            break
    
    if user_to_remove:
        users.remove(user_to_remove)
        print(f"User '{user_to_remove.name}' removed successfully.")
    else:
        print(f"No user found with library ID: {library_id}")

def handle_author_operations(authors):
    while True:
        display_author_operations()
        choice = input("Select an option (1-4): ")
        
        if choice == '1':
            add_author(authors)
        elif choice == '2':
            list_authors(authors)
        elif choice == '3':
            remove_author(authors)
        elif choice == '4':
            return

def add_author(authors):
    name = input("Enter author name: ")
    biography = input("Enter biography: ")
    author = Author(name=name, biography=biography)
    save_author(author)
    print(f"Author '{name}' added successfully.")

def list_authors(authors):
    if not authors:
        print("No authors available.")
    else:
        for author in authors:
            print(author)

def remove_author(authors):
    name = input("Enter the name of the author to remove: ")
    authors = [author for author in authors if author.name != name]
    print(f"Author '{name}' removed.")

if __name__ == "__main__":
    main()