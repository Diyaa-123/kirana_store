from flask import Flask, render_template, request
from src.database.db_json import category

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/category/<name>')
def category_details(name):
    category_name = category[name]
    return render_template('card.html', category=category_name)
 
if __name__ == "__main__":
    app.run(debug=True)