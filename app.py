from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(10), nullable=False, default="Medium")
    is_completed = db.Column(db.Boolean, default=False)

# Routes
@app.route('/')
def index():
    todos = Todo.query.order_by(Todo.due_date).all()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add_todo():
    title = request.form['title']
    description = request.form['description']
    due_date = request.form['due_date']
    priority = request.form['priority']

    todo = Todo(
        title=title,
        description=description,
        due_date=datetime.strptime(due_date, '%Y-%m-%d') if due_date else None,
        priority=priority,
    )
    db.session.add(todo)
    db.session.commit()
    return redirect('/')

@app.route('/toggle/<int:id>')
def toggle_completion(id):
    todo = Todo.query.get_or_404(id)
    todo.is_completed = not todo.is_completed
    db.session.commit()
    return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    return redirect('/')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_todo(id):
    todo = Todo.query.get_or_404(id)
    if request.method == 'POST':
        todo.title = request.form['title']
        todo.description = request.form['description']

        # Convert due_date to a Python date object
        due_date_str = request.form['due_date']
        if due_date_str:
            todo.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        else:
            todo.due_date = None

        todo.priority = request.form['priority']
        todo.is_completed = 'is_completed' in request.form
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update.html', todo=todo)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
