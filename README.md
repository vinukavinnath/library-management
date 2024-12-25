
# A Multiagent based Library Management System


This project is a Multiagent-Based Library Management System implemented using the Python [Mesa](https://github.com/projectmesa/mesa) framework and an ontology designed with Protege. The system incorporates two main roles: Admin and Member. The ontology defines the structure and relationships of the library data, while Mesa enables agent-based interactions.

![Imgur](https://i.imgur.com/IDx8lqG.png)

## User Roles and Functionalities

### Admin Features
- Add Books: Add new books to the library catalog.
- Remove Books: Remove books from the catalog.
- View Transactions: View borrowing and returning transactions.
- Search Books: Search for books based on specific criteria.

### Member Features

- Search Books: Search for available books in the library catalog.
- Borrow Books: Borrow books if available.


## Main System Components

### Protege Ontology

Defines the library data structure, including entities like books, members, and transactions. Provides relationships and rules for data consistency and querying.

### Mesa Framework

Simulates the interactions between Admin and Member agents. Handles agent-based operations like searching, borrowing, and updating the library catalog.

## Installation

1. Clone the repository
```bash
git clone https://github.com/vinukavinnath/library-management.git
```
2. Go to project directory

```bash
cd library-management
```
3. Activate a new conda environment and run below commands to install necessary packages
```bash
conda install anaconda::flask
conda install conda-forge::mesa
conda install conda-forge::rdflib
```
4. Run Flask backend
```bash
python app.py
```
## User Credentials
### Admin
- Username: admin_john
- Password: Admin123!

### Member
- Username: sarah_smith
- Password: LibraryPass123!

<br>These details are stored in Ontology as data properties of User instances and fetched by agent system for successful authentication.

## Technologies Used

- Python: Core programming language for implementation
- Mesa: Python framework for agent-based modeling
- Protege: Ontology editor to design the library structure
- HTML/Tailwind CSS (Frontend): For creating the user interface
- Flask: For connecting the frontend with the agent system

## Screenshots
### Admin Dashboard
![Admin dashboard](https://i.imgur.com/jR3FZus.png)
### Member Dashboard
![Member Dashboard](https://i.imgur.com/8fU2I6x.png)
### Search for a book
![Search](https://i.imgur.com/b78rtyx.png)
### All Transactions
![Transactions](https://i.imgur.com/CHqpIM7.png)

## Contact
For any inquiries or feedback, please contact:
- Name: Vinuka Vinnath
- Email: hellovinuka@gmail.com
- GitHub: [github.com/vinukavinnath](https://github.com/vinukavinnath)