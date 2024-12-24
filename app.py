# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from library_system import LibraryModel, AdminAgent, MemberAgent
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session management

# Initialize library model
library = LibraryModel()

def get_user_dict(user, user_type):
    """Convert user object to serializable dictionary"""
    base_dict = {
        'username': user.username,
        'type': user_type
    }
    
    if user_type == 'member':
        base_dict['member_id'] = user.member_id
        
    return base_dict

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:  # Changed from 'username' to 'user'
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'admin':
            flash('Admin access required')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_object(session_user):
    """Get actual user object from session data"""
    if session_user['type'] == 'admin':
        return next((agent for agent in library.schedule.agents 
                    if isinstance(agent, AdminAgent) and agent.username == session_user['username']), None)
    else:
        return next((agent for agent in library.schedule.agents 
                    if isinstance(agent, MemberAgent) and agent.username == session_user['username']), None)


@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Login attempt for user: {username}")  # Debug log
        
        user_type = library.authenticate_user(username, password)
        print(f"Authentication result: {user_type}")  # Debug log
        
        if user_type == 'admin':
            user = next((agent for agent in library.schedule.agents 
                        if isinstance(agent, AdminAgent) and agent.username == username), None)
            if user:
                session['user'] = get_user_dict(user, 'admin')
                session['user_type'] = 'admin'
                print(f"Admin login successful: {session['user']}")  # Debug log
                return redirect(url_for('dashboard'))
                
        elif user_type == 'member':
            user = next((agent for agent in library.schedule.agents 
                        if isinstance(agent, MemberAgent) and agent.username == username), None)
            if user:
                session['user'] = get_user_dict(user, 'member')
                session['user_type'] = 'member'
                print(f"Member login successful: {session['user']}")  # Debug log
                return redirect(url_for('dashboard'))
                
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = get_user_object(session['user'])
    if not user:
        return redirect(url_for('logout'))
        
    if session['user_type'] == 'admin':
        return render_template('admin_dashboard.html', user=user)
    else:
        return render_template('member_dashboard.html', user=user)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        title = request.form['title']
        book = library.search_book(title)
        return render_template('search.html', book=book)
    return render_template('search.html')

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
@admin_required
def add_book():
    if request.method == 'POST':

        user = get_user_object(session['user'])
        if not user:
            return redirect(url_for('logout'))

        title = request.form['title']
        isbn = request.form['isbn']
        author = request.form['author']
        year = request.form['year']
        category = request.form['category']
        
        # success = session['user'].add_book(title, isbn, author, year, category)
        
        success = user.add_book(title, isbn, author, year, category)

        if success:
            flash('Book added successfully!')
        else:
            flash('Failed to add book')
            
    return render_template('add_book.html')

@app.route('/remove_book', methods=['GET', 'POST'])
@login_required
@admin_required
def remove_book():
    if request.method == 'POST':
        user = get_user_object(session['user'])
        if not user:
            return redirect(url_for('logout'))
            
        title = request.form['title']
        book = library.search_book(title)
        
        if book:
            if user.remove_book(book['uri']):
                flash('Book removed successfully!')
            else:
                flash('Failed to remove book')
        else:
            flash('Book not found')
            
    return render_template('remove_book.html')

@app.route('/transactions')
@login_required
@admin_required
def transactions():
    user = get_user_object(session['user'])
    if not user:
        return redirect(url_for('logout'))
        
    transactions = user.view_all_transactions()
    return render_template('transactions.html', transactions=transactions)

@app.route('/borrow', methods=['GET', 'POST'])
@login_required
def borrow():
    if session['user_type'] != 'member':
        flash('Only members can borrow books')
        return redirect(url_for('dashboard'))
    
    user = get_user_object(session['user'])
    if not user:
        return redirect(url_for('logout'))
        
    if request.method == 'POST':
        title = request.form['title']
        book = library.search_book(title)
        
        if book:
            success, message = user.borrow_book(book['uri'])
            flash(message)
        else:
            flash('Book not found')
            
    return render_template('borrow.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)