# FreshMart Inventory (Flask + SQLite)

A Python Flask conversion of the supplied FreshMart inventory UI. It uses HTML templates, CSS and JavaScript for the interface and interactions, Flask routes for application logic, and SQLite for persistent product and stock movement records.

## Run in VS Code

1. Install Python 3.10 or newer.
2. Open this folder in VS Code.
3. Open Terminal and run:
   ```bash
   python -m venv .venv
   ```
4. Activate the environment:
   - Windows PowerShell: ` .venv\Scripts\Activate.ps1 `
   - macOS/Linux: `source .venv/bin/activate`
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Start the app:
   ```bash
   python app.py
   ```
7. Open http://127.0.0.1:5000 in your browser.

The SQLite database `freshmart.db` is created automatically on first run and seeded with sample products and movement history based on the supplied code. Keep the database file to preserve your changes. To reset sample data, stop the app and delete `freshmart.db`; it will be recreated on next launch.

## Features
- Dashboard with inventory totals, stock value, low-stock list, expiry watch and recent movements
- Add, edit, search, filter and delete products
- Record stock in/out with validation and movement history
- Low-stock and expiry alerts, restock and write-off shortcuts
- Category summaries
- Printable inventory report with 7-day / 30-day / all-time movement filters
- Responsive layout for desktop and mobile

This is a local development app; `debug=True` is enabled for convenient development. Do not expose it directly to the public internet without production hardening.
