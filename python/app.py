from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Flask App!"

@app.route('/data')
def data():
    connection = mysql.connector.connect(
        host="db",
        user="jimmy",
        password="dzu7$2",
        database="db"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT DATABASE();")
    db_name = cursor.fetchone()
    return jsonify({"Connected to": db_name[0]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)