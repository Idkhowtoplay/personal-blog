from flask import Flask, render_template, request, redirect, session, url_for
from jinja2 import Environment 
import json
import os
import datetime

app = Flask(__name__)
app.secret_key = "secret"
data = "file.json"
environment = Environment()

def load_json():
    if not os.path.exists(data):
        return []
    with open(data, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []
        
def save_json(content):
    with open(data, "w") as file:
        json.dump(content, file, indent=4)

@app.template_filter("datetime_format")
def datetime_format(value, format="%Y-%m-%d"):
    if isinstance(value, str):
        try:
            value = datetime.datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return value
    return value.strftime(format)

@app.route("/")
def home():
    article = load_json()
    return render_template("home.html", article=article)

@app.route("/article/<int:id>")
def article(id):
    articles = load_json()
    index = id - 1
    article = articles[index]
    now = datetime.datetime.strptime(article["date"], "%Y-%m-%d")
    date = now.strftime("%B %d, %Y")
    return render_template("article.html", article=article, date=date)

@app.route("/login", methods =["GET", "POST"])
def login():
    result = None
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("pass")

        if name == "emanaon" and password == "321":
            session['user'] = True
            return redirect("/login/admin")
        else:
            result = "Username or password is inavalid"
    return render_template("login.html", result=result)

@app.route('/login/admin')
def index():
    if session.get("user") is not True:
        return redirect("/login")
    result = load_json()
    return render_template('admin.html', result=result)

@app.route('/new', methods=["GET", "POST"])
def new():
    if request.method == "POST":
        store = load_json()
        add = {
            "title": request.form.get("title"),
            "date": request.form.get("date"),
            "content": request.form.get("content")
        }
        store.append(add)
        save_json(store)
        return redirect("/login/admin")
    return render_template("add.html")

@app.route("/edit/<int:edit_id>", methods = ["GET", "POST"])
def edit(edit_id):
    articles = load_json()
    index = edit_id - 1
    article = articles[index]

    if request.method == "POST":
        for i in articles:
            if i["title"] == article["title"]:
                i["title"] = request.form.get("title")
                i["date"] = request.form.get("date")
                i["content"] = request.form.get("content")
        save_json(articles)
        return redirect(url_for("index"))
    return render_template("edit.html", article=article)

@app.route("/delete/<int:id>", methods = ["POST", "GET"])
def delete(id):
    articles = load_json()
    index = id - 1
    articles.pop(index)
    save_json(articles)
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)