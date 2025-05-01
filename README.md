# Vulnerable E-commerce Application

⚠️ **DISCLAIMER: This project is intended for educational and ethical hacking purposes ONLY. Do NOT use in production or deploy on public networks.** ⚠️

This application is intentionally built with security vulnerabilities to demonstrate common web security issues. It simulates a basic e-commerce platform with significant security flaws that should NEVER be implemented in real-world applications.

## Security Vulnerabilities

This application contains the following vulnerabilities:

1. **SQL Injection** - In login and product search
2. **Cross-Site Scripting (XSS)**
   - Stored XSS in product reviews
   - Reflected XSS in search functionality
3. **Cross-Site Request Forgery (CSRF)** - No CSRF tokens on any forms
4. **Insecure Direct Object Reference (IDOR)** - Access to users' data via URL parameters
5. **Insecure Authentication** - Passwords stored in plaintext; poor session management
6. **Command Injection** - Via profile update functionality

## Setup Instructions

### Prerequisites
- Python 3.x

### Windows Setup
1. Clone the repository
2. Open command prompt in the project directory
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment: `venv\Scripts\activate`
5. Install dependencies: `pip install flask`
6. Initialize the database: `python db_setup.py`
7. Run the application: `python main.py`
8. Access the application in your browser at: `http://localhost:5000`

### Linux Setup
1. Clone the repository
2. Open terminal in the project directory
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment: `source venv/bin/activate`
5. Install dependencies: `pip install flask`
6. Initialize the database: `python db_setup.py`
7. Run the application: `python main.py`
8. Access the application in your browser at: `http://localhost:5000`

## Educational Purposes

This application is designed to help security professionals, developers, and cybersecurity students understand how common vulnerabilities work and how to protect against them in real-world applications.

## WARNING

DO NOT:
- Use this code in production
- Host this on a public server
- Use real personal information when testing
- Deploy this in an environment connected to sensitive systems

## Ethical Use

This tool should only be used for:
- Education and learning
- Controlled security training
- Authorized penetration testing practice
