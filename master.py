from flask import Flask, request, jsonify
import sqlite3, requests

app = Flask(__name__)
DB = "meta.db"

def setup():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS chunkloc (id TEXT, node TEXT)")
    con.commit()
setup()

NODES = [
    "http://127.0.0.1:5001",
    "http://127.0.0.1:5002",
    "http://127.0.0.1:5003"
]

@app.route("/upload_chunk", methods=["POST"])
def upload_chunk():
    cid = request.form["chunk_id"]
    file = request.files["file"]
    node = NODES[hash(cid) % len(NODES)]

    requests.post(f"{node}/write", data={"chunk_id": cid}, files={"file": file})

    con = sqlite3.connect(DB)
    con.execute("INSERT INTO chunkloc VALUES (?,?)", (cid, node))
    con.commit()

    return jsonify({"node": node})

@app.route("/loc/<cid>")
def loc(cid):
    con = sqlite3.connect(DB)
    cur = con.execute("SELECT node FROM chunkloc WHERE id=?", (cid,))
    row = cur.fetchone()
    if row:
        return jsonify({"node": row[0]})
    return jsonify({"error": "not found"})

if __name__ == "__main__":
    app.run(port=4000)
