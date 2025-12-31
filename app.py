from flask import Flask, render_template, request, redirect, session
import psycopg2
import uuid
import time

pengumuman_event = {
    "ts": 0,
    "data": []
}

app = Flask(__name__)
app.secret_key = "desk-secret-key"

# database pake postgres
def get_db():
    return psycopg2.connect(
        host="localhost",
        database="nama database anda",
        user="username db anda",
        password="password db anda"
    )

def get_all_petugas():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT nama, aktif FROM petugas ORDER BY nama")
    data = cur.fetchall()
    conn.close()
    return data
def get_petugas_aktif():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT nama FROM petugas WHERE aktif=true ORDER BY nama")
    data = [r[0] for r in cur.fetchall()]
    conn.close()
    return data

def get_instansi_aktif():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT nama FROM instansi WHERE aktif=true ORDER BY nama")
    data = [r[0] for r in cur.fetchall()]
    conn.close()
    return data
def get_instansi_all():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT nama, aktif FROM instansi ORDER BY nama")
    data = cur.fetchall()
    conn.close()
    return data

# umumkan antri
def get_pengumuman():
    pengumuman = []
    for meja in meja_list:
        antrian = [a for a in meja["antrian"] if not a["selesai"]]
        if len(antrian) > 1:
            pengumuman.append({
                "meja": meja["nama"],
                "instansi": antrian[1]["nama"]
            })
    return pengumuman
@app.route("/pengumuman")
def pengumuman():
    data = []
    if not meja_list:
        return {'ts':0, 'data':[]}
    for meja in meja_list:
        if not meja.get("pernah_selesai"):
            continue
        antrian = [a for a in meja["antrian"] if not a["selesai"]]
        if antrian:
            data.append({
                "meja": meja["nama"],
                "instansi": antrian[0]["nama"]
            })
    # return {"pengumuman": data}
    return pengumuman_event


# bwat login admin
def is_admin():
    return session.get("admin", False)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["admin"] = True
            return redirect("/admin")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

meja_list = []
instansi_selesai = set()
current_meja_index = 0

# nampilin layar best
@app.route("/")
def index():
    return render_template(
        "index.html",
        meja_list=meja_list,
        pengumuman=get_pengumuman(),
        is_admin=is_admin()
    )

# ajax
@app.route("/api/meja")
def api_meja():
    data = []
    for meja in meja_list:
        data.append({
            "nama": meja["nama"],
            "petugas": meja["petugas"],
            "antrian": [
                {
                    "nama": a["nama"],
                    "selesai": a["selesai"]
                } for a in meja["antrian"]
            ]
        })
    return {"meja": data}

# mindah instansi
@app.route("/admin/pindah_instansi", methods=["POST"])
def pindah_instansi():
    if not is_admin():
        return redirect("/login")

    from_meja = int(request.form["from_meja"])
    to_meja = int(request.form["to_meja"])
    nama_instansi = request.form["instansi"].strip()

    antrian = meja_list[from_meja]["antrian"]

    for i, inst in enumerate(antrian):
        if inst["nama"] == nama_instansi and not inst["selesai"]:
            meja_list[to_meja]["antrian"].append(antrian.pop(i))
            return redirect("/admin")

    session["error"] = f"Instansi '{nama_instansi}' belum ada di antrian meja tersebut"
    return redirect("/admin")



# admin
@app.route("/admin")
def admin():
    if not is_admin():
        return redirect("/login")

    error = session.pop("error", None)
    return render_template(
        "admin.html",
        meja_list=meja_list,
        error=error,
        petugas_all=get_all_petugas(), 
        petugas_aktif=get_petugas_aktif(), 
        instansi_dropdown=[i for i in get_instansi_aktif() if i not in instansi_selesai],
        instansi_all=get_instansi_all() 
    )


# ini buat nambah meja
@app.route("/admin/tambah_meja", methods=["POST"])
def tambah_meja():
    if not is_admin():
        return redirect("/login")

    meja_list.append({
        "nama": f"Meja {len(meja_list)+1}",
        "petugas": [],
        "antrian": [],
        "pernah_selesai": False
    })
    return redirect("/admin")

# nambah petugas
@app.route("/admin/meja/<int:index>/tambah_petugas", methods=["POST"])
def tambah_petugas_meja(index):
    if not is_admin():
        return redirect("/login")

    petugas = request.form["petugas"]
    for m in meja_list:
        if petugas in m["petugas"]:
            session["error"] = "Petugas sudah bertugas di meja lain"
            return redirect("/admin")
    # if len(meja_list[index]["petugas"]) >= 2:
    #     session["error"] = "Maksimal 2 petugas per meja"
    #     return redirect("/admin")

    meja_list[index]["petugas"].append(petugas)
    return redirect("/admin")


# ini buat nambah ke antrian
current_meja_index = 0
@app.route("/admin/tambah_instansi", methods=["POST"])
def tambah_instansi():
    if not is_admin():
        return redirect("/login")

    instansi = request.form["instansi"]
    meja_index = int(request.form["meja"])

    for m in meja_list:
        for a in m["antrian"]:
            if a["nama"] == instansi and not a["selesai"]:
                session["error"] = "Instansi sudah ada di antrian"
                return redirect("/admin")

    meja_list[meja_index]["antrian"].append({
        "id": str(uuid.uuid4()),
        "nama": instansi,
        "selesai": False
    })
    return redirect("/admin")



@app.route("/admin/selesai/<int:meja_index>/<int:inst_index>/<instansi_nama>")
def selesai(meja_index, inst_index, instansi_nama):
    global pengumuman_event
    inst = meja_list[meja_index]["antrian"][inst_index]

    if inst["nama"] == instansi_nama:
        inst["selesai"] = True
        instansi_selesai.add(inst["nama"])
        meja_list[meja_index]["pernah_selesai"] = True

        antrian = [a for a in meja_list[meja_index]["antrian"] if not a["selesai"]]

        if antrian:
            pengumuman_event = {
                "ts": time.time(),
                "data": [{
                    "meja": meja_list[meja_index]["nama"],
                    "instansi": antrian[0]["nama"]
                }]
            }
    return redirect("/admin")


# buat reset kalau misal kegiatan sdh selesai
@app.route("/admin/reset")
def reset():
    global pengumuman_event
    if not is_admin():
        return redirect("/login")

    meja_list.clear()
    instansi_selesai.clear()
    pengumuman_event={'ts':0, 'data':[]}
    return redirect("/admin")

# nambah petugas ke db
@app.route("/admin/petugas/tambah", methods=["POST"])
def tambah_petugas_db():
    if not is_admin():
        return redirect("/login")

    nama = request.form["nama"].strip()
    if not nama:
        return redirect("/admin")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO petugas (nama) VALUES (%s) "
        "ON CONFLICT (nama) DO UPDATE SET aktif=true",
        (nama,)
    )
    conn.commit()
    conn.close()
    return redirect("/admin")

@app.route("/admin/petugas/nonaktif/<nama>")
def nonaktif_petugas(nama):
    if not is_admin():
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE petugas SET aktif=false WHERE nama=%s", (nama,))
    conn.commit()
    conn.close()
    return redirect("/admin")

# ubah status
@app.route("/admin/petugas/toggle/<nama>")
def toggle_petugas(nama):
    if not is_admin():
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE petugas
        SET aktif = NOT aktif
        WHERE nama = %s
    """, (nama,))
    conn.commit()
    conn.close()
    return redirect("/admin")

@app.route("/admin/instansi/toggle/<nama>")
def toggle_instansi(nama):
    if not is_admin():
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE instansi SET aktif = NOT aktif WHERE nama=%s", (nama,))
    conn.commit()
    conn.close()
    return redirect("/admin")



# # ini buat nambah instansi ke db
# @app.route("/admin/instansi/tambah", methods=["POST"])
# def tambah_instansi_db():
#     if not is_admin():
#         return redirect("/login")

#     nama = request.form["nama"].strip()
#     if not nama:
#         return redirect("/admin")

#     conn = get_db()
#     cur = conn.cursor()
#     cur.execute(
#         "INSERT INTO instansi (nama) VALUES (%s) "
#         "ON CONFLICT (nama) DO UPDATE SET aktif=true",
#         (nama,)
#     )
#     conn.commit()
#     conn.close()
#     return redirect("/admin")

# @app.route("/admin/instansi/nonaktif/<nama>")
# def nonaktif_instansi(nama):
#     if not is_admin():
#         return redirect("/login")

#     conn = get_db()
#     cur = conn.cursor()
#     cur.execute("UPDATE instansi SET aktif=false WHERE nama=%s", (nama,))
#     conn.commit()
#     conn.close()
#     return redirect("/admin")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)