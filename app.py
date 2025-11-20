from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import datetime

app = Flask(__name__)

# Configuración MySQL
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "gimnasio"

mysql = MySQL(app)

# =========================
# Página principal
# =========================
@app.route("/")
def index():
    return render_template("index.html")

# ============================================================
# SOCIOS (CRUD COMPLETO)
# ============================================================

@app.route("/socios")
def socios_lista():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Socio")
    socios = cursor.fetchall()
    #esta en lo que hicimos con el lice pero no es necesario
    #cursor.close()
    return render_template("socios/lista.html", socios=socios)

@app.route("/socios/agregar", methods=["GET", "POST"])
def socios_agregar():   
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        email = request.form["email"]
        telefono = request.form["telefono"] 
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO socio (nombre, apellido, email, telefono) VALUES (%s,%s,%s,%s)",
            (nombre, apellido, email, telefono),
        )
        mysql.connection.commit()
        return redirect(url_for("socios_lista"))
    return render_template("socios/agregar.html")

@app.route("/socios/editar/<int:id>", methods=["GET", "POST"])
def socios_editar(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        email = request.form["email"]
        telefono = request.form["telefono"]
        cursor.execute(
            """UPDATE Socio SET nombre=%s, apellido=%s, email=%s, telefono=%s
                WHERE id_socio=%s""",
            (nombre, apellido, email, telefono, id),
        )
        mysql.connection.commit()
        return redirect(url_for("socios_lista"))
    cursor.execute("SELECT * FROM Socio WHERE id_socio=%s", (id,))
    socio = cursor.fetchone()
    return render_template("socios/editar.html", socio=socio)

@app.route("/socios/eliminar/<int:id>")
def socios_eliminar(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Socio WHERE id_socio=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for("socios_lista"))

# ============================================================
# PLANES (CRUD COMPLETO)
# ============================================================

@app.route("/planes")
def planes_lista():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM PlanMembresia")
    planes = cursor.fetchall()
    return render_template("planes/lista.html", planes=planes)

@app.route("/planes/agregar", methods=["GET", "POST"])
def planes_agregar():
    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]
        duracion_dias = request.form["duracion_dias"]

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO PlanMembresia (nombre_plan, precio, duracion_dias) VALUES (%s,%s,%s)",
            (nombre, precio, duracion_dias),
        )
        mysql.connection.commit()
        return redirect(url_for("planes_lista"))

    return render_template("planes/agregar.html")

@app.route("/planes/editar/<int:id>", methods=["GET", "POST"])
def planes_editar(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]
        duracion = request.form["duracion"]

        cursor.execute(
            """UPDATE PlanMembresia
               SET nombre_plan=%s, precio=%s, duracion_dias=%s
               WHERE id_plan=%s""",
            (nombre, precio, duracion, id),
        )
        mysql.connection.commit()
        return redirect(url_for("planes_lista"))

    cursor.execute("SELECT * FROM PlanMembresia WHERE id_plan=%s", (id,))
    plan = cursor.fetchone()
    return render_template("planes/editar.html", plan=plan)

@app.route("/planes/eliminar/<int:id>")
def planes_eliminar(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM PlanMembresia WHERE id_plan=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for("planes_lista"))

# ============================================================
# PAGOS (CRUD BÁSICO)
# ============================================================

@app.route("/pagos")
def pagos_lista():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        """
        SELECT p.id_pago, s.nombre, s.apellido, pl.nombre_plan, p.fecha_inicio, p.fecha_fin, p.monto
        FROM Pago p
        JOIN Socio s ON p.id_socio = s.id_socio
        JOIN PlanMembresia pl ON p.id_plan = pl.id_plan
        """
    )
    pagos = cursor.fetchall()
    return render_template("pagos/lista.html", pagos=pagos)

@app.route("/pagos/agregar", methods=["GET", "POST"])
def pagos_agregar():
    if request.method == "POST":
        id_socio = request.form["id_socio"]
        id_plan = request.form["id_plan"]
        fecha_inicio = request.form["fecha_inicio"]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("SELECT duracion_dias, precio FROM PlanMembresia WHERE id_plan=%s", (id_plan,))
        plan = cursor.fetchone()

        fecha_inicio_dt = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fecha_fin = fecha_inicio_dt + datetime.timedelta(days=plan["duracion_dias"])

        cursor.execute(
            "INSERT INTO Pago (id_socio,id_plan,fecha_inicio,fecha_fin,monto) VALUES (%s,%s,%s,%s,%s)",
            (id_socio, id_plan, fecha_inicio, fecha_fin.strftime("%Y-%m-%d"), plan["precio"]),
        )
        mysql.connection.commit()
        return redirect(url_for("pagos_lista"))

    return render_template("pagos/agregar.html")

@app.route("/pagos/editar/<int:id>", methods=["GET", "POST"])
def pagos_editar(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST":
        id_socio = request.form["id_socio"]
        id_plan = request.form["id_plan"]
        fecha_inicio = request.form["fecha_inicio"]
        fecha_fin = request.form["fecha_fin"]
        monto = request.form["monto"]

        cursor.execute("""
            UPDATE Pago 
            SET id_socio=%s, id_plan=%s, fecha_inicio=%s, fecha_fin=%s, monto=%s
            WHERE id_pago=%s
        """, (id_socio, id_plan, fecha_inicio, fecha_fin, monto, id))
        
        mysql.connection.commit()
        return redirect(url_for("pagos_lista"))

    cursor.execute("SELECT * FROM Pago WHERE id_pago=%s", (id,))
    pago = cursor.fetchone()

    return render_template("pagos/editar.html", pago=pago)

@app.route("/pagos/eliminar/<int:id>")
def pagos_eliminar(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Pago WHERE id_pago=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for("pagos_lista"))


# ============================================================
# CLASES (CRUD SIMPLE)
# ============================================================

@app.route("/clases")
def clases_lista():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Clase")
    clases = cursor.fetchall()
    return render_template("clases/lista.html", clases=clases)


@app.route("/clases/agregar", methods=["GET", "POST"])
def clases_agregar():
    if request.method == "POST":
        nombre = request.form["nombre_clase"]
        descripcion = request.form["descripcion"]
        cupo = request.form["cupo"]

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO Clase (nombre_clase, descripcion, cupo) VALUES (%s, %s, %s)",
            (nombre, descripcion, cupo)
        )
        mysql.connection.commit()
        return redirect(url_for("clases_lista"))

    return render_template("clases/agregar.html")



@app.route("/clases/editar/<int:id>", methods=["GET", "POST"])
def clases_editar(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST":
        nombre = request.form["nombre_clase"]
        descripcion = request.form["descripcion"]
        cupo = request.form["cupo"]

        cursor.execute("""
            UPDATE Clase 
            SET nombre_clase=%s, descripcion=%s, cupo=%s 
            WHERE id_clase=%s
        """, (nombre, descripcion, cupo, id))

        mysql.connection.commit()
        return redirect(url_for("clases_lista"))

    cursor.execute("SELECT * FROM Clase WHERE id_clase=%s", (id,))
    clase = cursor.fetchone()
    return render_template("clases/editar.html", clase=clase)



@app.route("/clases/eliminar/<int:id>")
def clases_eliminar(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Clase WHERE id_clase=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for("clases_lista"))


# =========================
# Ejecutar
# =========================
if __name__ == "__main__":
    app.run(debug=True)
