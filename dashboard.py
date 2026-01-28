from flask import Flask, render_template, request, jsonify
import requests, math, os

app = Flask(__name__, template_folder="templates")

MASTER = "http://127.0.0.1:4000"
FILES = {}

def split_file(data, name):
    size = 50 * 1024
    chunks = []
    total = math.ceil(len(data)/size)
    for i in range(total):
        chunks.append((f"{name}_chunk_{i}", data[i*size:(i+1)*size]))
    return chunks, total

@app.route("/")
def home():
    print("Rendering dashboard.html")
    return render_template("dashboard.html", files=list(FILES.keys()))

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    name = file.filename
    data = file.read()

    chunks, total = split_file(data, name)
    FILES[name] = total

    for cid, cdata in chunks:
        requests.post(
            f"{MASTER}/upload_chunk",
            data={"chunk_id": cid},
            files={"file": cdata}
        )

    return jsonify({"msg": f"{name} uploaded successfully!"})

@app.route("/get_chunks", methods=["POST"])
def get_chunks():
    name = request.form["name"]
    return jsonify([f"{name}_chunk_{i}" for i in range(FILES[name])])

@app.route("/metadata", methods=["POST"])
def metadata():
    cid = request.form["chunk"]
    return jsonify(requests.get(f"{MASTER}/loc/{cid}").json())

@app.route("/download", methods=["POST"])
def download():
    name = request.form["name"]
    total = FILES[name]

    full_data = b""
    for i in range(total):
        cid = f"{name}_chunk_{i}"
        node = requests.get(f"{MASTER}/loc/{cid}").json()["node"]
        full_data += requests.get(f"{node}/read/{cid}").content

    open(f"restored_{name}", "wb").write(full_data)
    return jsonify({"msg": f"{name} downloaded successfully!"})

if __name__ == "__main__":
    app.run(port=8080)
