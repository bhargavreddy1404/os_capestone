from flask import Flask, request, jsonify
import os, sys

app = Flask(__name__)
os.makedirs("chunks", exist_ok=True)

@app.route("/write", methods=["POST"])
def write_chunk():
    chunk_id = request.form["chunk_id"]
    file = request.files["file"]
    file.save(f"chunks/{chunk_id}")
    return jsonify({"ok": True})

@app.route("/read/<cid>")
def read_chunk(cid):
    return open(f"chunks/{cid}", "rb").read()

if __name__ == "__main__":
    port = int(sys.argv[1])
    app.run(port=port)
