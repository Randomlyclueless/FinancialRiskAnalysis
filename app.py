from flask import Flask, send_from_directory, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/')
def home():
    return send_from_directory('static','index.html')  # Looks inside templates/index.html

@app.route('/api/goals')
def get_goals():
    conn = sqlite3.connect('financial_goals.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM goals")
    rows = cursor.fetchall()
    conn.close()
    
    goals = [dict(zip(['id', 'goal_name', 'priority', 'progress'], row)) for row in rows]
    return jsonify(goals)

if __name__ == '__main__':
    app.run(debug=True)