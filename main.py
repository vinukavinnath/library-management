import tkinter as tk
from tkinter import ttk, messagebox
from library_system import LibraryModel, AdminAgent, MemberAgent

class LibraryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("800x600")
        
        # Initialize the library model
        self.library = LibraryModel()
        self.current_user = None
        
        # Create main containers
        self.login_frame = None
        self.admin_frame = None
        self.member_frame = None
        
        self.setup_login_screen()
    
    def setup_login_screen(self):
        if self.login_frame:
            self.login_frame.destroy()
            
        self.login_frame = ttk.Frame(self.root, padding="20")
        self.login_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        ttk.Label(self.login_frame, text="Library Management System", 
                 font=('Helvetica', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)
        
        # Username
        ttk.Label(self.login_frame, text="Username:").grid(row=1, column=0, pady=5)
        username_entry = ttk.Entry(self.login_frame)
        username_entry.grid(row=1, column=1, pady=5)
        
        # Password
        ttk.Label(self.login_frame, text="Password:").grid(row=2, column=0, pady=5)
        password_entry = ttk.Entry(self.login_frame, show="*")
        password_entry.grid(row=2, column=1, pady=5)
        
        # Login button
        ttk.Button(self.login_frame, text="Login", 
                  command=lambda: self.handle_login(username_entry.get(), password_entry.get())
                  ).grid(row=3, column=0, columnspan=2, pady=20)
    
    def setup_admin_screen(self):
        if self.admin_frame:
            self.admin_frame.destroy()
            
        self.admin_frame = ttk.Frame(self.root, padding="20")
        self.admin_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Admin menu buttons
        ttk.Label(self.admin_frame, text="Administrator Dashboard", 
                 font=('Helvetica', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)
        
        ttk.Button(self.admin_frame, text="Add Book", 
                  command=self.show_add_book_screen).grid(row=1, column=0, pady=10, padx=5)
        ttk.Button(self.admin_frame, text="Remove Book", 
                  command=self.show_remove_book_screen).grid(row=1, column=1, pady=10, padx=5)
        ttk.Button(self.admin_frame, text="Search Book", 
                  command=self.show_search_screen).grid(row=2, column=0, pady=10, padx=5)
        ttk.Button(self.admin_frame, text="View Transactions", 
                  command=self.show_transactions_screen).grid(row=2, column=1, pady=10, padx=5)
        ttk.Button(self.admin_frame, text="Logout", 
                  command=self.logout).grid(row=3, column=0, columnspan=2, pady=20)
    
    def setup_member_screen(self):
        if self.member_frame:
            self.member_frame.destroy()
            
        self.member_frame = ttk.Frame(self.root, padding="20")
        self.member_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Member menu buttons
        ttk.Label(self.member_frame, text="Member Dashboard", 
                 font=('Helvetica', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)
        
        ttk.Button(self.member_frame, text="Search Book", 
                  command=self.show_search_screen).grid(row=1, column=0, pady=10, padx=5)
        ttk.Button(self.member_frame, text="Borrow Book", 
                  command=self.show_borrow_screen).grid(row=1, column=1, pady=10, padx=5)
        ttk.Button(self.member_frame, text="Logout", 
                  command=self.logout).grid(row=2, column=0, columnspan=2, pady=20)

    def handle_login(self, username, password):
        user_type = self.library.authenticate_user(username, password)
        
        if user_type == "admin":
            self.current_user = next((agent for agent in self.library.schedule.agents 
                                    if isinstance(agent, AdminAgent) and agent.username == username), None)
            if self.current_user:
                self.login_frame.destroy()
                self.setup_admin_screen()
            else:
                messagebox.showerror("Error", "Error finding admin user")
                
        elif user_type == "member":
            self.current_user = next((agent for agent in self.library.schedule.agents 
                                    if isinstance(agent, MemberAgent) and agent.username == username), None)
            if self.current_user:
                self.login_frame.destroy()
                self.setup_member_screen()
            else:
                messagebox.showerror("Error", "Error finding member user")
        else:
            messagebox.showerror("Error", "Invalid credentials!")

    def show_add_book_screen(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Book")
        add_window.geometry("400x500")
        
        frame = ttk.Frame(add_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Book details entries
        ttk.Label(frame, text="Title:").grid(row=0, column=0, pady=5)
        title_entry = ttk.Entry(frame)
        title_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="ISBN:").grid(row=1, column=0, pady=5)
        isbn_entry = ttk.Entry(frame)
        isbn_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Author:").grid(row=2, column=0, pady=5)
        author_entry = ttk.Entry(frame)
        author_entry.grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text="Year:").grid(row=3, column=0, pady=5)
        year_entry = ttk.Entry(frame)
        year_entry.grid(row=3, column=1, pady=5)
        
        ttk.Label(frame, text="Category:").grid(row=4, column=0, pady=5)
        category_entry = ttk.Entry(frame)
        category_entry.grid(row=4, column=1, pady=5)
        
        def add_book():
            success = self.current_user.add_book(
                title_entry.get(),
                isbn_entry.get(),
                author_entry.get(),
                year_entry.get(),
                category_entry.get()
            )
            if success:
                messagebox.showinfo("Success", "Book added successfully!")
                add_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to add book!")
        
        ttk.Button(frame, text="Add Book", command=add_book).grid(row=5, column=0, columnspan=2, pady=20)

    def show_remove_book_screen(self):
        remove_window = tk.Toplevel(self.root)
        remove_window.title("Remove Book")
        remove_window.geometry("400x200")
        
        frame = ttk.Frame(remove_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="Enter book title:").grid(row=0, column=0, pady=5)
        title_entry = ttk.Entry(frame)
        title_entry.grid(row=0, column=1, pady=5)
        
        def remove_book():
            book = self.library.search_book(title_entry.get())
            if book:
                if self.current_user.remove_book(book['uri']):
                    messagebox.showinfo("Success", "Book removed successfully!")
                    remove_window.destroy()
                else:
                    messagebox.showerror("Error", "Failed to remove book!")
            else:
                messagebox.showerror("Error", "Book not found!")
        
        ttk.Button(frame, text="Remove Book", command=remove_book).grid(row=1, column=0, columnspan=2, pady=20)

    def show_search_screen(self):
        search_window = tk.Toplevel(self.root)
        search_window.title("Search Book")
        search_window.geometry("400x500")
        
        frame = ttk.Frame(search_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="Enter book title:").grid(row=0, column=0, pady=5)
        title_entry = ttk.Entry(frame)
        title_entry.grid(row=0, column=1, pady=5)
        
        result_text = tk.Text(frame, height=15, width=40)
        result_text.grid(row=2, column=0, columnspan=2, pady=20)
        
        def search_book():
            book = self.library.search_book(title_entry.get())
            result_text.delete(1.0, tk.END)
            if book:
                for key, value in book.items():
                    if key != 'uri':
                        result_text.insert(tk.END, f"{key}: {value}\n")
            else:
                result_text.insert(tk.END, "Book not found!")
        
        ttk.Button(frame, text="Search", command=search_book).grid(row=1, column=0, columnspan=2, pady=20)

    def show_transactions_screen(self):
        trans_window = tk.Toplevel(self.root)
        trans_window.title("Transaction History")
        trans_window.geometry("600x400")
        
        frame = ttk.Frame(trans_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create text widget with scrollbar
        text_widget = tk.Text(frame, height=20, width=70)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.grid(row=0, column=0, pady=5)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Display transactions
        transactions = self.current_user.view_all_transactions()
        for transaction_id, details in transactions.items():
            text_widget.insert(tk.END, f"\nTransaction ID: {transaction_id}\n")
            text_widget.insert(tk.END, f"Borrow Date: {details['borrow_date']}\n")
            text_widget.insert(tk.END, f"Due Date: {details['due_date']}\n")
            text_widget.insert(tk.END, f"Status: {details['status']}\n")
            
            if details['book']:
                text_widget.insert(tk.END, "\nBook Details:\n")
                text_widget.insert(tk.END, f"Title: {details['book']['title']}\n")
                text_widget.insert(tk.END, f"ISBN: {details['book']['ISBN']}\n")
                text_widget.insert(tk.END, f"Author: {details['book']['author']}\n")
            
            if details['member']:
                text_widget.insert(tk.END, "\nMember Details:\n")
                text_widget.insert(tk.END, f"Username: {details['member']['username']}\n")
                text_widget.insert(tk.END, f"Member ID: {details['member']['member_id']}\n")
                text_widget.insert(tk.END, f"Email: {details['member']['email']}\n")
            text_widget.insert(tk.END, "-" * 50 + "\n")

    def show_borrow_screen(self):
        borrow_window = tk.Toplevel(self.root)
        borrow_window.title("Borrow Book")
        borrow_window.geometry("400x200")
        
        frame = ttk.Frame(borrow_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="Enter book title:").grid(row=0, column=0, pady=5)
        title_entry = ttk.Entry(frame)
        title_entry.grid(row=0, column=1, pady=5)
        
        def borrow_book():
            book = self.library.search_book(title_entry.get())
            if book:
                success, message = self.current_user.borrow_book(book['uri'])
                if success:
                    messagebox.showinfo("Success", message)
                    borrow_window.destroy()
                else:
                    messagebox.showerror("Error", message)
            else:
                messagebox.showerror("Error", "Book not found!")
        
        ttk.Button(frame, text="Borrow Book", command=borrow_book).grid(row=1, column=0, columnspan=2, pady=20)

    def logout(self):
        self.current_user = None
        if self.admin_frame:
            self.admin_frame.destroy()
        if self.member_frame:
            self.member_frame.destroy()
        self.setup_login_screen()

def main():
    root = tk.Tk()
    app = LibraryGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()