# from flask import Flask, render_template, redirect, url_for, request
from flask import Flask, render_template, redirect, url_for, request, session
from datetime import datetime
import re
from zoneinfo import ZoneInfo
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "secretkey" 
app.config.setdefault("APP_TIMEZONE", "UTC")

users = []


items = []
week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
          'September', 'October', 'November', 'December']

def application_now():
    return datetime.now(ZoneInfo(app.config["APP_TIMEZONE"]))


def dashboard_context(errors=None, submitted_values=None):
    now = application_now()
    today = now.date()

    for item in items:
        due_date = item['due_date']
        item['overdue'] = datetime(
            due_date['year'], due_date['month'], due_date['day']
        ).date() < today

    return {
        'errors': errors or {},
        'leng': len(items),
        'list_items': items,
        'submitted_values': submitted_values or {},
        'today': f'{now.day} {months[now.month - 1]} {now.year}, {week_days[now.weekday()]}'
    }

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users.append({
            "username": username,
            "password": generate_password_hash(password)
        })

        return redirect("/login")

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        for user in users:
            if user["username"] == username and check_password_hash(user["password"], password):
                session["user"] = username
                return redirect("/")

        return "Login failed"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route('/', methods=['GET', 'POST'])
def home():
    if "user" not in session:
        return redirect("/login")

    if request.method == 'POST':
        new_item_content = request.form.get('newItem', '')
        new_item_duedate = request.form.get('duedate', '')
        errors = {}
        parsed_due_date = None

        if not new_item_content.strip():
            errors['newItem'] = 'Enter a task name.'

        if not new_item_duedate:
            errors['duedate'] = 'Enter a due date.'
        elif not re.fullmatch(r'\d{4}-\d{2}-\d{2}', new_item_duedate):
            errors['duedate'] = 'Enter a valid calendar date.'
        else:
            try:
                parsed_due_date = datetime.strptime(new_item_duedate, '%Y-%m-%d').date()
            except ValueError:
                errors['duedate'] = 'Enter a valid calendar date.'
            else:
                if parsed_due_date <= application_now().date():
                    errors['duedate'] = 'Choose a due date later than today.'

        if errors:
            return render_template(
                'index.html',
                **dashboard_context(
                    errors=errors,
                    submitted_values={
                        'newItem': new_item_content,
                        'duedate': new_item_duedate
                    }
                )
            )

        new_item_id = len(items) + 1
        new_item = {
            'id': int(new_item_id),
            'content': new_item_content,
            'due_date': {
                'year': parsed_due_date.year,
                'month': parsed_due_date.month,
                'day': parsed_due_date.day
            }
        }

        items.append(new_item)

        return redirect(url_for('home'))
    return render_template('index.html', **dashboard_context())


@app.route('/delete-item', methods=['POST'])
def delete_item():
    if request.method == 'POST':
        form = request.form
        id = int(form['checkbox'])
        for item in items:
            if item['id'] == id:
                del items[items.index(item)]
                break
        return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
