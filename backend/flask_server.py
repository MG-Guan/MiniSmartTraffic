from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
app = Flask(__name__)
CORS(app)  # 支持跨域

DB_FILE = os.path.join(os.path.dirname(__file__), "traffic_data.db")
print("--------------------------------------")
print("[DEBUG] Using DB file:", os.path.abspath(DB_FILE))

# === 从数据库分页读取数据 ===
def get_paginated_violations(page=1, limit=6):
    offset = (page - 1) * limit

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 总数
    cursor.execute("SELECT COUNT(*) FROM violations")
    total = cursor.fetchone()[0]

    # 当前页数据（按 ID 降序）
    cursor.execute('''
        SELECT id, timestamp, type, plate, location, image_base64
        FROM violations
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "timestamp": row[1],
            "type": row[2],
            "plate": row[3],
            "location": row[4],
            "image": row[5]
        })

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": result
    }


# === 接口：/api/violations?page=1&limit=6 ===
@app.route('/api/violations')
def api_violations():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 6))
    except ValueError:
        page = 1
        limit = 6

    data = get_paginated_violations(page, limit)
    return jsonify(data)

if __name__ == '__main__':
    print("[Flask] Running with pagination on http://localhost:5000/api/violations")
    app.run(debug=True)
