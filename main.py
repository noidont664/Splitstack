import os
import uuid
import csv
import io
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify, session, Response
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "splitstack-secret-key")

# In-memory data storage
users = []
expenses = []

# Add a default user and friends
default_user = {
    'id': str(uuid.uuid4()),
    'name': 'You',
    'is_current': True
}
users.append(default_user)

# Add some friends
friend1 = {
    'id': str(uuid.uuid4()),
    'name': 'Alex',
    'is_current': False
}
users.append(friend1)

friend2 = {
    'id': str(uuid.uuid4()),
    'name': 'Sam',
    'is_current': False
}
users.append(friend2)

# Define expense categories
expense_categories = [
    "Food", "Rent", "Transportation", "Entertainment", "Utilities", 
    "Shopping", "Health", "Education", "Travel", "Other"
]

# Add some sample expenses with more diverse categories
expenses.append({
    'id': str(uuid.uuid4()),
    'payer_id': friend1['id'],
    'payer_name': friend1['name'],
    'amount': 45.75,
    'description': 'Dinner at restaurant',
    'category': 'Food',
    'date': datetime.now().strftime('%Y-%m-%d %H:%M')
})

expenses.append({
    'id': str(uuid.uuid4()),
    'payer_id': default_user['id'],
    'payer_name': default_user['name'],
    'amount': 30.50,
    'description': 'Groceries',
    'category': 'Food',
    'date': datetime.now().strftime('%Y-%m-%d %H:%M')
})

expenses.append({
    'id': str(uuid.uuid4()),
    'payer_id': friend2['id'],
    'payer_name': friend2['name'],
    'amount': 22.99,
    'description': 'Movie tickets',
    'category': 'Entertainment',
    'date': datetime.now().strftime('%Y-%m-%d %H:%M')
})

expenses.append({
    'id': str(uuid.uuid4()),
    'payer_id': friend1['id'],
    'payer_name': friend1['name'],
    'amount': 800.00,
    'description': 'Apartment rent',
    'category': 'Rent',
    'date': datetime.now().strftime('%Y-%m-%d %H:%M')
})

expenses.append({
    'id': str(uuid.uuid4()),
    'payer_id': default_user['id'],
    'payer_name': default_user['name'],
    'amount': 35.50,
    'description': 'Uber ride',
    'category': 'Transportation',
    'date': datetime.now().strftime('%Y-%m-%d %H:%M')
})

expenses.append({
    'id': str(uuid.uuid4()),
    'payer_id': friend2['id'],
    'payer_name': friend2['name'],
    'amount': 95.20,
    'description': 'Electricity bill',
    'category': 'Utilities',
    'date': datetime.now().strftime('%Y-%m-%d %H:%M')
})

expenses.append({
    'id': str(uuid.uuid4()),
    'payer_id': friend1['id'],
    'payer_name': friend1['name'],
    'amount': 65.75,
    'description': 'New clothes',
    'category': 'Shopping',
    'date': datetime.now().strftime('%Y-%m-%d %H:%M')
})

expenses.append({
    'id': str(uuid.uuid4()),
    'payer_id': default_user['id'],
    'payer_name': default_user['name'],
    'amount': 40.00,
    'description': 'Pharmacy',
    'category': 'Health',
    'date': datetime.now().strftime('%Y-%m-%d %H:%M')
})

# HTML template for the application
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-bs-theme="light" id="html-root">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="manifest" href="/static/manifest.json">
    <meta name="theme-color" content="#212529">
    <meta name="description" content="SplitStack - Split expenses with friends easily">
    <meta name="theme-color" content="#212529">
    <title>SplitStack - Expense Sharing</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
    <link rel="manifest" href="{{ url_for('static', filename='manifest.json') }}">
    <link rel="icon" type="image/png" href="{{ url_for('static', filename='icons/icon-192x192.png') }}">
    <link rel="apple-touch-icon" href="{{ url_for('static', filename='icons/icon-192x192.png') }}">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-receipt me-2"></i>SplitStack
            </a>
            <div class="d-flex align-items-center">
                <div class="form-check form-switch me-3">
                    <input class="form-check-input" type="checkbox" id="darkModeToggle" checked>
                    <label class="form-check-label text-light" for="darkModeToggle">
                        <i class="fas fa-moon"></i>
                    </label>
                </div>
                <div class="navbar-text text-light">
                    <i class="fas fa-user-circle me-1"></i> Logged in
                </div>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <div class="row">
            <div class="col-md-4">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-users me-2"></i>Users</h5>
                    </div>
                    <div class="card-body">
                        <form id="addUserForm" action="/users/add" method="post" class="mb-3">
                            <div class="input-group">
                                <input type="text" class="form-control" name="name" placeholder="User name" required>
                                <button type="submit" class="btn btn-primary">Add</button>
                            </div>
                        </form>

                        <ul class="list-group" id="usersList">
                            {% if users %}
                                {% for user in users %}
                                    <li class="list-group-item d-flex justify-content-between align-items-center {% if user.is_current %}bg-primary bg-opacity-25{% endif %}">
                                        {{ user.name }} {% if user.is_current %}<span class="badge bg-primary ms-2">You</span>{% endif %}
                                        <form action="/users/remove" method="post" class="d-inline">
                                            <input type="hidden" name="user_id" value="{{ user.id }}">
                                            <button type="submit" class="btn btn-sm btn-danger" {% if user.is_current %}disabled{% endif %}>
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </form>
                                    </li>
                                {% endfor %}
                            {% else %}
                                <li class="list-group-item text-center text-muted">No users added yet</li>
                            {% endif %}
                        </ul>
                    </div>
                </div>
            </div>

            <div class="col-md-8">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-file-invoice-dollar me-2"></i>Add Expense</h5>
                    </div>
                    <div class="card-body">
                        {% if users|length < 2 %}
                            <div class="alert alert-info">
                                Add at least 2 users to start tracking expenses
                            </div>
                        {% else %}
                             <form action="/expenses/add" method="post">
                                <div class="mb-3">
                                    <label for="payer" class="form-label">Who paid?</label>
                                    <select class="form-select" id="payer" name="payer_id" required>
                                        <option value="" selected disabled>Select a user</option>
                                        {% for user in users %}
                                            <option value="{{ user.id }}" {% if user.is_current %}selected{% endif %}>{{ user.name }} {% if user.is_current %}(You){% endif %}</option>
                                        {% endfor %}
                                    </select>
                                </div>

                                <div class="mb-3">
                                    <label for="amount" class="form-label">Amount</label>
                                    <div class="input-group">
                                        <span class="input-group-text">$</span>
                                        <input type="number" class="form-control" id="amount" name="amount" 
                                               min="0.01" step="0.01" placeholder="0.00" required>
                                    </div>
                                </div>
                                      <label for="description" class="form-label">Description</label>
                                      <input type="text" class="form-control" id="description" name="description" placeholder="What was this for?" required>
                                    </div>

                                    <div class="mb-3">
                                      <label for="category" class="form-label">Category</label>
                                      <select class="form-select" id="category" name="category" required>
                                        <option value="" selected disabled>Select category</option>
                                        {% for category in expense_categories %}
                                        <option value="{{ category }}">{{ category }}</option>
                                        {% endfor %}
                                      </select>
                                    </div>

                                <div class="d-grid">
                                    <button type="submit" class="btn btn-primary">Add Expense</button>
                                </div>
                            </form>
                        {% endif %}
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0 fs-4">
                            <i class="fas fa-list-alt me-2"></i>Expenses
                        </h5>
                        <div class="btn-group">
                            {% if expenses %}
                                <a href="{{ url_for('export_csv') }}" class="btn btn-sm btn-success">
                                    <i class="fas fa-file-csv me-1"></i> Export CSV
                                </a>
                                <form action="/expenses/clear" method="post" class="d-inline">
                                    <button type="submit" class="btn btn-sm btn-danger">
                                        <i class="fas fa-trash me-1"></i> Clear All
                                    </button>
                                </form>
                            {% endif %}
                        </div>
                    </div>
                    {% if expenses %}
                    <div class="card-body bg-light bg-opacity-10 p-3">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h4 class="mb-0 fs-5">Total Spent</h4>
                                <div class="fs-3 fw-bold text-primary">${{ "%.2f"|format(expenses|sum(attribute='amount')) }}</div>
                            </div>
                            <div class="text-end">
                                <p class="mb-0 text-muted">Total expenses</p>
                                <span class="badge bg-secondary fs-6 p-2">
                                    {{ expenses|length }} expense{% if expenses|length != 1 %}s{% endif %}
                                </span>
                            </div>
                        </div>
                    </div>
                    {% endif %}
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover mb-0">
                                <thead>
                                    <tr>
                                        <th>Paid by</th>
                                        <th>Description</th>
                                        <th>Category</th>
                                        <th>Amount</th>
                                        <th>Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% if expenses %}
                                        {# Group expenses by category #}
                                        {% set categories = {} %}
                                        {% for expense in expenses %}
                                            {% set cat = expense.category|default('Other') %}
                                            {% if cat not in categories %}
                                                {% set _ = categories.update({cat: []}) %}
                                            {% endif %}
                                            {% set _ = categories[cat].append(expense) %}
                                        {% endfor %}

                                        {% for category, cat_expenses in categories.items() %}
                                            <tr class="table-group-divider category-header">
                                                <td colspan="5" class="category-title bg-opacity-10 p-3 {% if category == 'Food' %}bg-success{% elif category == 'Entertainment' %}bg-info{% elif category == 'Transportation' %}bg-warning{% elif category == 'Shopping' %}bg-danger{% elif category == 'Travel' %}bg-primary{% elif category == 'Utilities' %}bg-info{% elif category == 'Rent' %}bg-dark{% elif category == 'Health' %}bg-danger{% elif category == 'Education' %}bg-warning text-dark{% else %}bg-secondary{% endif %}">
                                                    <strong class="fs-5">{{ category }}</strong>
                                                    <span class="badge rounded-pill bg-dark float-end p-2 px-3">
                                                        {{ cat_expenses|length }} expense{% if cat_expenses|length != 1 %}s{% endif %} - 
                                                        ${{ "%.2f"|format(cat_expenses|sum(attribute='amount')) }}
                                                    </span>
                                                </td>
                                            </tr>
                                            {% for expense in cat_expenses %}
                                                <tr>
                                                    <td class="fw-medium">{{ expense.payer_name }}</td>
                                                    <td>{{ expense.description }}</td>
                                                    <td><span class="badge py-2 px-3 fs-6 {% if expense.category == 'Food' %}bg-success{% elif expense.category == 'Entertainment' %}bg-info{% elif expense.category == 'Transportation' %}bg-warning{% elif expense.category == 'Shopping' %}bg-danger{% elif expense.category == 'Travel' %}bg-primary{% elif expense.category == 'Utilities' %}bg-info{% elif expense.category == 'Rent' %}bg-dark{% elif expense.category == 'Health' %}bg-danger{% elif expense.category == 'Education' %}bg-warning text-dark{% else %}bg-secondary{% endif %}">{{ expense.category }}</span></td>
                                                    <td class="fw-bold">${{ "%.2f"|format(expense.amount) }}</td>
                                                    <td>{{ expense.date }}</td>
                                                    <td>
                                                        <form action="/expenses/delete" method="post" class="d-inline">
                                                            <input type="hidden" name="expense_id" value="{{ expense.id }}">
                                                            <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Are you sure you want to delete this expense?')">
                                                                <i class="fas fa-trash"></i>
                                                            </button>
                                                        </form>
                                                    </td>
                                                </tr>
                                            {% endfor %}
                                        {% endfor %}
                                    {% else %}
                                        <tr>
                                            <td colspan="5" class="text-center text-muted py-3">No expenses recorded yet</td>
                                        </tr>
                                    {% endif %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-balance-scale me-2"></i>Balance Sheet</h5>
                    </div>
                    <div class="card-body">
                        {% if balances %}
                            <ul class="list-group" id="balanceList">
                                {% for balance in balances %}
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        <span>
                                            <strong>{{ balance.from_user }}</strong> owes 
                                            <strong>{{ balance.to_user }}</strong>
                                        </span>
                                        <span class="badge bg-primary rounded-pill">${{ "%.2f"|format(balance.amount) }}</span>
                                    </li>
                                {% endfor %}
                            </ul>
                        {% else %}
                            <p class="text-muted text-center mb-0">No balances to display</p>
                        {% endif %}
                    </div>
                </div>

                </div>
        </div>
    </div>

    <footer class="footer mt-5 py-3 bg-dark">
        <div class="container text-center">
            <div class="mb-3">
                <form action="/reset" method="post" class="d-inline">
                    <button type="submit" class="btn btn-outline-danger" onclick="return confirm('Are you sure you want to reset all data? This will remove all users except you and clear all expenses.')">
                        <i class="fas fa-redo me-1"></i> Reset All Data
                    </button>
                </form>
            </div>
            <span class="text-muted">SplitStack - Split expenses with friends</span><br>
            <small class="text-muted mt-2">SplitStack is not affiliated with Splitwise. Just inspired by the same problem.</small>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="{{ url_for('static', filename='js/analytics.js') }}"></script>
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
    <script src="{{ url_for('static', filename='js/pwa.js') }}"></script>
</body>
</html>
"""

@app.route('/')
def index():
    # Calculate balances
    balances = calculate_balances()

    return render_template_string(
        HTML_TEMPLATE,
        users=users,
        expenses=expenses,
        balances=balances,
        expense_categories=expense_categories
    )

@app.route('/users/add', methods=['POST'])
def add_user():
    name = request.form.get('name', '').strip()

    if not name:
        flash('Please enter a valid name', 'danger')
        return redirect(url_for('index'))

    # Check for user limit (10 users max)
    if len(users) >= 10:
        flash('Maximum number of users (10) reached. Please remove some users before adding more.', 'warning')
        return redirect(url_for('index'))

    # Check if user with this name already exists
    if any(user['name'].lower() == name.lower() for user in users):
        flash(f'User "{name}" already exists', 'warning')
        return redirect(url_for('index'))

    users.append({
        'id': str(uuid.uuid4()),
        'name': name,
        'is_current': False
    })

    flash(f'User "{name}" added successfully', 'success')
    return redirect(url_for('index'))

@app.route('/users/remove', methods=['POST'])
def remove_user():
    user_id = request.form.get('user_id')

    # Find user
    user = next((user for user in users if user['id'] == user_id), None)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('index'))

    # Check if user has expenses
    if any(expense['payer_id'] == user_id for expense in expenses):
        flash(f'Cannot remove {user["name"]} as they have recorded expenses', 'warning')
        return redirect(url_for('index'))

    # Remove user
    users.remove(user)
    flash(f'User "{user["name"]}" removed successfully', 'success')
    return redirect(url_for('index'))

@app.route('/expenses/add', methods=['POST'])
def add_expense():
    payer_id = request.form.get('payer_id')
    amount_str = request.form.get('amount', '0')
    description = request.form.get('description', '').strip()
    category = request.form.get('category', 'Other')

    # Find payer
    payer = next((user for user in users if user['id'] == payer_id), None)
    if not payer:
        flash('Selected user not found', 'danger')
        return redirect(url_for('index'))

    # Validate amount
    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except ValueError:
        flash('Please enter a valid positive amount', 'danger')
        return redirect(url_for('index'))

    # Validate description
    if not description:
        flash('Please enter a description', 'danger')
        return redirect(url_for('index'))

    # Add expense
    from datetime import datetime
    expenses.append({
        'id': str(uuid.uuid4()),
        'payer_id': payer_id,
        'payer_name': payer['name'],
        'amount': amount,
        'description': description,
        'category': category,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M')
    })

    flash('Expense added successfully', 'success')
    return redirect(url_for('index'))

@app.route('/expenses/delete', methods=['POST'])
def delete_expense():
    expense_id = request.form.get('expense_id')
    expense = next((exp for exp in expenses if exp['id'] == expense_id), None)
    
    if expense:
        expenses.remove(expense)
        flash('Expense deleted successfully', 'success')
    else:
        flash('Expense not found', 'danger')
    
    return redirect(url_for('index'))

@app.route('/expenses/clear', methods=['POST'])
def clear_expenses():
    global expenses
    expenses = []
    flash('All expenses have been cleared', 'success')
    return redirect(url_for('index'))

@app.route('/reset', methods=['POST'])
def reset_data():
    global users, expenses

    # Recreate default user
    users = []
    default_user = {
        'id': str(uuid.uuid4()),
        'name': 'You',
        'is_current': True
    }
    users.append(default_user)

    # Clear expenses
    expenses = []

    flash('All data has been reset', 'success')
    return redirect(url_for('index'))

@app.route('/export/csv')
def export_csv():
    # Create a CSV file in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['Date', 'Paid By', 'Description', 'Category', 'Amount'])

    # Write data
    for expense in expenses:
        writer.writerow([
            expense['date'],
            expense['payer_name'],
            expense['description'],
            expense.get('category', 'Other'),  # Using get in case some expenses don't have category
            f"${expense['amount']:.2f}"
        ])

    # Create response
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=splitstack_expenses.csv"}
    )

def calculate_balances():
    if not users or len(users) < 2 or not expenses:
        return []

    # Initialize dictionaries to track payments and debts
    total_paid = {user['id']: 0 for user in users}
    total_owed = {user['id']: 0 for user in users}

    # Calculate total payments and debts
    for expense in expenses:
        # Add what the payer paid
        total_paid[expense['payer_id']] += expense['amount']
        
        # Calculate each person's share of this expense
        share_per_person = expense['amount'] / len(users)
        
        # Add what each person owes for this expense
        for user in users:
            total_owed[user['id']] += share_per_person

    # Calculate net balance for each user
    net_balances = {}
    for user_id in total_paid:
        net_balances[user_id] = total_paid[user_id] - total_owed[user_id]

    # Separate into debtors and creditors
    debtors = [(user_id, -balance) for user_id, balance in net_balances.items() if balance < -0.01]
    creditors = [(user_id, balance) for user_id, balance in net_balances.items() if balance > 0.01]
    
    # Sort by amount (largest debts/credits first)
    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)

    # Generate settlements
    settlements = []
    for debtor_id, debt in debtors:
        remaining_debt = debt
        debtor_name = next(user['name'] for user in users if user['id'] == debtor_id)
        
        for creditor_id, credit in creditors:
            if remaining_debt <= 0.01:  # Done with this debtor
                break
                
            if credit <= 0.01:  # Skip creditors who are fully paid
                continue
                
            creditor_name = next(user['name'] for user in users if user['id'] == creditor_id)
            
            # Calculate the settlement amount
            settlement = min(remaining_debt, credit)
            
            if settlement > 0.01:  # Only add non-zero settlements
                settlements.append({
                    'from_user': debtor_name,
                    'to_user': creditor_name,
                    'amount': round(settlement, 2)  # Round to 2 decimal places
                })
            
            # Update remaining amounts
            remaining_debt -= settlement
            creditors[creditors.index((creditor_id, credit))] = (creditor_id, credit - settlement)

    return settlements
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
