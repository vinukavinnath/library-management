from mesa import Agent, Model
from mesa.time import RandomActivation
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import RDFS, XSD
import datetime
import uuid

# Load RDF Ontology
g = Graph()
try:
    g.parse("library_ontology.rdf", format="xml")
except Exception as e:
    print(f"Warning: {e}. Creating new graph.")
LIB = Namespace("http://www.library-system.org/ontology#")

class LibraryModel(Model):
    def __init__(self):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.running = True
        self.graph = g
        self.init_agents()
    
    def save_graph(self):
        """Safely save the graph with proper XML formatting"""
        try:
            self.graph.serialize(
                destination="library_ontology.rdf",
                format="pretty-xml",
                encoding="utf-8"
            )
        except Exception as e:
            print(f"Error saving graph: {e}")
            return False
        return True

    def init_agents(self):
        for admin in self.graph.subjects(RDF.type, LIB.Admin):
            username = str(self.graph.value(admin, LIB.username))
            password = str(self.graph.value(admin, LIB.password))
            admin_agent = AdminAgent(self.next_id(), self, username, password)
            self.schedule.add(admin_agent)

        for member in self.graph.subjects(RDF.type, LIB.Member):
            username = str(self.graph.value(member, LIB.username))
            password = str(self.graph.value(member, LIB.password))
            member_id = str(self.graph.value(member, LIB.memberID))
            member_agent = MemberAgent(self.next_id(), self, username, password, member_id)
            self.schedule.add(member_agent)

    def authenticate_user(self, username, password):
        for admin in self.graph.subjects(RDF.type, LIB.Admin):
            if (str(self.graph.value(admin, LIB.username)) == username and 
                str(self.graph.value(admin, LIB.password)) == password):
                return "admin"
        
        for member in self.graph.subjects(RDF.type, LIB.Member):
            if (str(self.graph.value(member, LIB.username)) == username and 
                str(self.graph.value(member, LIB.password)) == password):
                return "member"
        return None

    def search_book(self, title):
        book_details = {}
        for book in self.graph.subjects(RDF.type, LIB.Book):
            if str(self.graph.value(book, LIB.title)).lower() == title.lower():
                book_details['title'] = str(self.graph.value(book, LIB.title))
                book_details['ISBN'] = str(self.graph.value(book, LIB.ISBN))
                book_details['author'] = str(self.graph.value(book, LIB.author))
                book_details['year'] = str(self.graph.value(book, LIB.year))
                book_details['isAvailable'] = str(self.graph.value(book, LIB.isAvailable))
                book_details['uri'] = str(book)
                return book_details
        return None

class UserAgent(Agent):
    def __init__(self, unique_id, model, username, password):
        super().__init__(unique_id, model)
        self.username = username
        self.password = password

    def authenticate(self):
        return self.model.authenticate_user(self.username, self.password)

class AdminAgent(UserAgent):
    def add_book(self, title, isbn, author, year, category):
        try:
            book_id = str(uuid.uuid4())
            book_uri = URIRef(f"http://www.library-system.org/ontology#book_{book_id}")
            
            # Add book properties with proper datatypes
            self.model.graph.add((book_uri, RDF.type, LIB.Book))
            self.model.graph.add((book_uri, LIB.title, Literal(title)))
            self.model.graph.add((book_uri, LIB.ISBN, Literal(isbn)))
            self.model.graph.add((book_uri, LIB.author, Literal(author)))
            self.model.graph.add((book_uri, LIB.year, Literal(year, datatype=XSD.integer)))
            self.model.graph.add((book_uri, LIB.isAvailable, Literal('true', datatype=XSD.boolean)))
            
            category_uri = URIRef(f"http://www.library-system.org/ontology#category_{category.lower()}")
            self.model.graph.add((book_uri, LIB.hasCategory, category_uri))
            
            return self.model.save_graph()
            
        except Exception as e:
            print(f"Error adding book: {e}")
            return False

    def remove_book(self, book_uri):
        try:
            for s, p, o in self.model.graph.triples((URIRef(book_uri), None, None)):
                self.model.graph.remove((s, p, o))
            return self.model.save_graph()
        except Exception as e:
            print(f"Error removing book: {e}")
            return False

    def view_all_transactions(self):
        """View all transactions in the system with detailed information"""
        transactions = {}
        
        # Query all transactions
        for transaction in self.model.graph.subjects(RDF.type, LIB.Transaction):
            transaction_id = str(transaction).split('#')[-1]
            transactions[transaction_id] = {
                'borrow_date': str(self.model.graph.value(transaction, LIB.borrowDate)),
                'due_date': str(self.model.graph.value(transaction, LIB.dueDate)),
                'status': str(self.model.graph.value(transaction, LIB.transactionStatus) or 'Unknown'),
                'book': {},
                'member': {}
            }
            
            # Get book details
            book = self.model.graph.value(transaction, LIB.involvesBook)
            if book:
                transactions[transaction_id]['book'] = {
                    'title': str(self.model.graph.value(book, LIB.title)),
                    'ISBN': str(self.model.graph.value(book, LIB.ISBN)),
                    'author': str(self.model.graph.value(book, LIB.author))
                }
            
            # Get member details - Updated method
            member_uri = self.model.graph.value(transaction, LIB.hasTransaction)
            if member_uri:
                # Verify this is a member URI
                if (member_uri, RDF.type, LIB.Member) in self.model.graph:
                    username = self.model.graph.value(member_uri, LIB.username)
                    member_id = self.model.graph.value(member_uri, LIB.memberID)
                    email = self.model.graph.value(member_uri, LIB.email)
                    
                    transactions[transaction_id]['member'] = {
                        'username': str(username) if username else 'Unknown',
                        'member_id': str(member_id) if member_id else 'Unknown',
                        'email': str(email) if email else 'Unknown'
                    }
        
        return transactions

class MemberAgent(UserAgent):
    def __init__(self, unique_id, model, username, password, member_id):
        super().__init__(unique_id, model, username, password)
        self.member_id = member_id

    def borrow_book(self, book_uri):
        try:
            book = URIRef(book_uri)
            is_available = self.model.graph.value(book, LIB.isAvailable)
            
            if str(is_available).lower() != 'true':
                return False, "Book is not available"
    
            # Update book availability
            self.model.graph.remove((book, LIB.isAvailable, None))
            self.model.graph.add((book, LIB.isAvailable, Literal('false', datatype=XSD.boolean)))
            
            # Create new transaction
            transaction_id = str(uuid.uuid4())
            transaction_uri = URIRef(f"http://www.library-system.org/ontology#transaction_{transaction_id}")
            
            borrow_date = datetime.datetime.now()
            due_date = borrow_date + datetime.timedelta(days=30)
            
            # Format dates properly
            borrow_date_str = borrow_date.strftime("%Y-%m-%d")
            due_date_str = due_date.strftime("%Y-%m-%d")
            
            # Create member URI
            member_uri = URIRef(f"http://www.library-system.org/ontology#member_{self.member_id}")
            
            # Add transaction details
            self.model.graph.add((transaction_uri, RDF.type, LIB.Transaction))
            self.model.graph.add((transaction_uri, LIB.borrowDate, 
                                Literal(borrow_date_str, datatype=XSD.date)))
            self.model.graph.add((transaction_uri, LIB.dueDate, 
                                Literal(due_date_str, datatype=XSD.date)))
            self.model.graph.add((transaction_uri, LIB.involvesBook, book))
            self.model.graph.add((transaction_uri, LIB.transactionStatus, Literal("Active")))
            
            # Add proper member associations
            self.model.graph.add((transaction_uri, LIB.hasTransaction, member_uri))
            self.model.graph.add((member_uri, LIB.hasTransaction, transaction_uri))
            
            # Add book-member association
            self.model.graph.add((book, LIB.borrowedBy, member_uri))
            
            if self.model.save_graph():
                return True, "Book borrowed successfully"
            else:
                return False, "Error saving transaction"
                
        except Exception as e:
            print(f"Error in borrowing book: {e}")
            return False, f"Error borrowing book: {str(e)}"


def run_library_system():
    library = LibraryModel()
    current_user = None
    user_type = None

    while True:
        if not current_user:
            print("\n=== Library Management System ===")
            print("1. Login")
            print("2. Exit")
            choice = input("Enter your choice (1-2): ")

            if choice == "1":
                username = input("Enter username: ")
                password = input("Enter password: ")
                user_type = library.authenticate_user(username, password)
                
                if user_type == "admin":
                    current_user = next((agent for agent in library.schedule.agents 
                                     if isinstance(agent, AdminAgent) and agent.username == username), None)
                    if current_user:
                        print("Logged in as Administrator")
                    else:
                        print("Error finding admin user")
                elif user_type == "member":
                    current_user = next((agent for agent in library.schedule.agents 
                                     if isinstance(agent, MemberAgent) and agent.username == username), None)
                    if current_user:
                        print("Logged in as Member")
                    else:
                        print("Error finding member user")
                else:
                    print("Invalid credentials!")

            elif choice == "2":
                print("Goodbye!")
                break

        else:  # User is logged in
            if user_type == "admin":
                print("\n=== Administrator Menu ===")
                print("1. Add Book")
                print("2. Remove Book")
                print("3. Search Book")
                print("4. View All Transactions")
                print("5. Logout")
                
                admin_choice = input("Enter your choice (1-5): ")
                
                if admin_choice == "1":
                    title = input("Enter book title: ")
                    isbn = input("Enter ISBN: ")
                    author = input("Enter author: ")
                    year = input("Enter publication year: ")
                    category = input("Enter category: ")
                    if current_user.add_book(title, isbn, author, year, category):
                        print("Book added successfully!")
                    else:
                        print("Failed to add book!")
                
                elif admin_choice == "2":
                    title = input("Enter book title to remove: ")
                    book = library.search_book(title)
                    if book:
                        if current_user.remove_book(book['uri']):
                            print("Book removed successfully!")
                    else:
                        print("Book not found!")
                
                elif admin_choice == "3":
                    title = input("Enter book title to search: ")
                    book = library.search_book(title)
                    if book:
                        print("\nBook Details:")
                        for key, value in book.items():
                            if key != 'uri':
                                print(f"{key}: {value}")
                    else:
                        print("Book not found!")
                
                elif admin_choice == "4":
                    transactions = current_user.view_all_transactions()
                    if transactions:
                        print("\n=== All Transactions ===")
                        for transaction_id, details in transactions.items():
                            print(f"\nTransaction ID: {transaction_id}")
                            print(f"Borrow Date: {details['borrow_date']}")
                            print(f"Due Date: {details['due_date']}")
                            print(f"Status: {details['status']}")
                            
                            if details['book']:
                                print("\nBook Details:")
                                print(f"Title: {details['book']['title']}")
                                print(f"ISBN: {details['book']['ISBN']}")
                                print(f"Author: {details['book']['author']}")
                            
                            if details['member']:
                                print("\nMember Details:")
                                print(f"Username: {details['member']['username']}")
                                print(f"Member ID: {details['member']['member_id']}")
                                print(f"Email: {details['member']['email']}")
                            print("-" * 50)
                    else:
                        print("No transactions found in the system.")
                
                elif admin_choice == "5":
                    current_user = None
                    user_type = None
                    print("Logged out successfully!")

            elif user_type == "member":
                print("\n=== Member Menu ===")
                print("1. Search Book")
                print("2. Borrow Book")
                print("3. Logout")
                
                member_choice = input("Enter your choice (1-3): ")
                
                if member_choice == "1":
                    title = input("Enter book title to search: ")
                    book = library.search_book(title)
                    if book:
                        print("\nBook Details:")
                        for key, value in book.items():
                            if key != 'uri':
                                print(f"{key}: {value}")
                    else:
                        print("Book not found!")
                
                elif member_choice == "2":
                    title = input("Enter book title to borrow: ")
                    book = library.search_book(title)
                    if book:
                        success, message = current_user.borrow_book(book['uri'])
                        print(message)
                    else:
                        print("Book not found!")
                
                elif member_choice == "3":
                    current_user = None
                    user_type = None
                    print("Logged out successfully!")

if __name__ == "__main__":
    run_library_system()