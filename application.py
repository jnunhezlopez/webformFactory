from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
from datetime import date, datetime
from helpers import *
import os
#from application1 import *
#05/03/2017 **********SOLO ESTÁ FUNCIONANDO PARA ALUMNOS DEL CURSO 2. HAY QUE BUSCAR LA FORMA DE SELECCIONAR EL CURSO
# ANTES DE PONERSE A GRABAR REGISTROS
#06/03/2017 **********HE QUITADO ALGUNOS CONTROLES DE DATOS ANTES DE GUARDAR PORQUE LO HE HECHO A TRAVÉS
# DE LA FUNCIONALIDAD EN EL FORMULARIO, PERO PUEDE NO SER SEGURO EN CASO DE QUE JAVASCRIPT ESTÉ DESHABILITADO
# configure application
app = Flask(__name__)
app.config['SQLALCHEMY_ECHO']=True
os.chdir('/var/www/html/webforms/')
# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
#db = SQL("sqlite:///pedidosweb.db")
db=SQL("mysql://javier:javier@localhost/pedidosweb")
#variables globales clientes y artículos
global gclientes
gclientes = db.execute("SELECT * FROM clientes")
global garticulos
garticulos = db.execute("SELECT * FROM articulos")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        formato = "%d/%m/%Y"
        fechas = []
        for i in (1,2):
            fechas.append(date.today().strftime(formato))
        rows = db.execute("SELECT pedidos.id, clientes.nombrecomercial as idcliente, fchpedido, fchprevent, estado FROM pedidos, clientes\
        WHERE pedidos.idcliente = clientes.id and vendedor = :vendedor", vendedor=session["user_id"] )
        return render_template("index.html", registros = rows, resumen = [], periodo = fechas)
    if request.method == "POST":
        accion = request.form.get("action")[0]
        id = request.form.get("action")[1:]
        if accion == "e":
            sql = "DELETE FROM pedidos WHERE id= " +id
            db.execute (sql)
            sql = "DELETE FROM lineaspedido WHERE idpedido= "+ id
            db.execute (sql)
            return redirect(url_for("index"))
        if accion == "c":
            sql = "UPDATE pedidos SET estado = 2 WHERE id=" + id
            db.execute(sql)
            return redirect(url_for("index"))
        if accion == "m":
            rows=db.execute("SELECT * FROM pedidos WHERE id=" + id)
            lines=db.execute("SELECT * FROM lineaspedido WHERE idpedido=" + id)
            updlineas=False
            return render_template("editpedido.html", registros = rows, lineas=lines, articulos=garticulos, updlineas=updlineas)
            #return apology("accion:{}, id:{}".format(accion,id))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("Debe introducirse un usuario.")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("Debe introducirse una password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("Usuario y/o password incorrectos.")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/cambiarpwd", methods=["GET","POST"])
@login_required
def cambiarpwd():
    if request.method == "POST":
        if not request.form.get("password"):
            return apology("Hay que indicar una password.")
        if request.form.get("password")!=request.form.get("password_2"):
            return apology("Las contraseñas tienen que coincidir.")
        rows = db.execute("UPDATE users SET hash = :hash WHERE id = :id", hash=pwd_context.encrypt(request.form.get("password")), id = session["user_id"])
        return redirect(url_for("index"))
    else:
        rows = db.execute("SELECT * FROM users WHERE id = :id", id = session["user_id"])
        usuario = rows[0]
        return render_template("cambiarpwd.html", usuario=usuario)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")
        # ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password")
        if request.form.get("password")!=request.form.get("password_2"):
            return apology("passwords must match")
        # query database for username in order to see if he already exits
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        # ensure username exists and password is correct
        if len(rows) != 0:
            return apology("username already exits")
        # if everything is OK then the new user is inserted into de db
        rows = db.execute("INSERT INTO users (username, hash) VALUES(:username,:hash)",
            username = request.form.get("username"), hash = pwd_context.encrypt(request.form.get("password")))
        # remember which user has logged in
        # redirect user to home page
        return redirect(url_for("index"))
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/pedido", methods=["GET", "POST"])
@login_required
def pedido():
    """Register pedido."""

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST" and request.form.get("action")=='grabar':
        # la aplicación está implementada con un control de errores en el cliente
        # se está deshabilitado javascript, esto podría dar problemas
        # valorar si se duplica el control de errores en el servidor, o sea, aquí

        pedido1 = db.execute ("SELECT id FROM pedidos WHERE id=:id",id=request.form.get("id"))
       # if not pedido1 is None:
        if pedido1 != []:
        # ensure username exists and password is correct
        # if len(rows) != 0:
            return apology("el pedido already exits")
        # if everything is OK then the new user is inserted into de db
        formato = "%d/%m/%Y"
        fechapedido = datetime.strptime(request.form.get("fchpedido"),formato)
        fechprevent = datetime.strptime(request.form.get("fchprevent"),formato)

        sql = "INSERT INTO pedidos (idcliente, fchpedido, fchprevent, estado, vendedor) VALUES ( " \
             + request.form.get("idcliente") + ",'" + fechapedido.strftime(formato) + "','" \
            + fechprevent.strftime(formato) +"'," + request.form.get("estado")+"," + str(session["user_id"]) + ")"
        id = db.execute (sql)
#modificado lo siguiente, al principio enviaba de nuevo a crear otro pedido, pero 
#es más lógico enviar a modificar/agregar líneas
        #return render_template("pedido.html", registros=gclientes)
        rows=db.execute("SELECT * FROM pedidos WHERE id=:id", id=id)
        #aunque no debería tener líneas se mantiene la siguiente línea por compatibilidad
        #************TODO optimizar
        lines=db.execute("SELECT * FROM lineaspedido WHERE idpedido=:id", id=id)
        #seguramente sea más lógico seleccionar updlineas=True
        updlineas=False
        return render_template("editpedido.html", registros = rows, lineas=lines, articulos=garticulos, updlineas=updlineas)        
    # else if user reached route via GET (as by clicking a link or via redirect)
    if request.method == "POST" and request.form.get("action")=='modificar':
        return apology("hay que hacer modificar")
    if request.method == "GET":
        return render_template("pedido.html", registros=gclientes)

@app.route("/editpedido", methods=["GET", "POST"])
@login_required
def editpedido():
    if request.method == "POST" and request.form.get("action")== "modificar":
        db.execute( "UPDATE pedidos SET idcliente=:idcliente, fchpedido=:fchpedido \
            ,fchprevent=:fchprevent, estado=:estado, vendedor=:vendedor WHERE id =:id",idcliente=request.form.get("idcliente"),fchpedido=request.form.get("fchpedido") \
                    ,fchprevent=request.form.get("fchprevent"),estado=request.form.get("estado"),vendedor=session["user_id"], id=request.form.get("id"))
        return redirect(url_for("index"))
    if request.method == "POST" and request.form.get("action")== "linea":
        db.execute( "INSERT INTO lineaspedido (idpedido, idarticulo, descripcion, piezas, \
            fchprevent, fchent, estado) VALUES (:idpedido, :idarticulo, :descripcion, :piezas \
                , :fchprevent, :fchent, :estado)", idpedido= int(request.form.get("id"))\
                    ,idarticulo=request.form.get("idarticulo"), descripcion=request.form.get("descripcion"), piezas = request.form.get("piezas")\
                            , fchprevent=request.form.get("lfchprevent"), fchent="", estado=1)
        #modificar los importes de la cabecera del pedido eliminado porque he quitado los importes

        rows=db.execute("SELECT * FROM pedidos WHERE id=" + request.form.get("id"))
        lines=db.execute("SELECT * FROM lineaspedido WHERE idpedido=" + request.form.get("id"))
        return render_template("editpedido.html", registros = rows, lineas=lines)
    if request.method == "POST" and request.form.get("action") == "updlineas":
        id = request.form.get("id")
        rows=db.execute("SELECT * FROM pedidos WHERE id=" + id)
        lines=db.execute("SELECT * FROM lineaspedido WHERE idpedido=" + id)
        updlineas=True
        return render_template("editpedido.html", registros = rows, lineas=lines, articulos=garticulos, updlineas=updlineas)
        #return apology("Pendiente visualizar las líneas para poder añadir")
    if request.method == "POST" and request.form.get("action")[0]=="e":
        id=request.form.get("action")[1:]
        db.execute ("DELETE FROM lineaspedido WHERE id=:id",id=id)
	#eliminado todo lo relacionado con importes
        rows=db.execute("SELECT * FROM pedidos WHERE id=" + request.form.get("id"))
        lines=db.execute("SELECT * FROM lineaspedido WHERE idpedido=" + request.form.get("id"))
        return render_template("editpedido.html", registros = rows, lineas=lines)

    return apology(str(request.form.get("action")))
@app.route("/cargapedidos", methods=["GET", "POST"])
@login_required
def cargapedidos():
    if request.method == "GET":
        rows = db.execute("SELECT pedidos.id, clientes.nombrecomercial as idcliente,fchpedido, fchprevent, estado FROM pedidos, clientes\
        WHERE pedidos.idcliente = clientes.id and idcliente = :idcliente",idcliente=int(request.args.get("idcliente")))
    # alumnos=Alumno.query.filter_by(idcurso=request.args.get("idcurso"))
    # print("alumnos:",alumnos)
    # print("tipo alumnos:",type(alumnos))
    # for row in alumnos:
    #     print ("row:",row)
    # return jsonify(alumnos)
        return jsonify(rows)
    else:
        apology("No hay método POST")

@app.route("/articulo", methods=["GET", "POST"])
@login_required
def articulo():
    """Register articulo."""

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST" and request.form.get("action") == "grabar":

        pedido1 = db.execute ("SELECT id FROM articulos WHERE id=:id",id=request.form.get("id"))
       # if not pedido1 is None:
        if pedido1 != []:
        # ensure username exists and password is correct
        # if len(rows) != 0:
            return apology("el articulo already exits, hay que corregir para modificaciones")
        # if everything is OK then the new user is inserted into de db
        sql = "INSERT INTO articulos (codigo, descripcion, estado) VALUES ( '" \
             + request.form.get("codigo") + "','" + request.form.get("descripcion") + "'," + request.form.get("estado")+")"
        db.execute (sql)
        global garticulos
        garticulos = db.execute("SELECT * FROM articulos")
        #pedido = Pedido(atributos)
        #db1.session.add(pedido)
        #db1.session.commit()
        # remember which user has logged in
        # redirect user to home page
        grabar = False
        return render_template("articulo.html", grabar=grabar)
    # else if user reached route via GET (as by clicking a link or via redirect)
    if request.method == "POST" and request.form.get("action") == "cargar":
        articulo=db.execute("SELECT * FROM articulos WHERE id=:id",id=request.form.get("id"))
        if not articulo==None:
            grabar=True
            nuevo = False
            #return apology ("Cargando {}".format(request.form.get("id")))
            return render_template("articulo.html", grabar=grabar, nuevo=nuevo, registros=articulo)
        else:
            return apology ("No se encuentra el artículo buscado")
    if request.method == "POST" and request.form.get("action") == "nuevo":
        grabar = True
        nuevo = True
        return render_template("articulo.html", grabar=grabar, nuevo=nuevo)
    if request.method == "GET":
        grabar = False
        nuevo = False
        return render_template("articulo.html", grabar=grabar, nuevo=nuevo)
@app.route("/cliente", methods=["GET", "POST"])
@login_required
def cliente():
    """Register cliente."""

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        pedido1 = db.execute ("SELECT id FROM clientes WHERE id=:id",id=request.form.get("id"))
       # if not pedido1 is None:
        if pedido1 != []:
        # ensure username exists and password is correct
        # if len(rows) != 0:
            return apology("el cliente already exits")
        # if everything is OK then the new user is inserted into de db
        sql = "INSERT INTO clientes (cif, nombrefiscal, nombrecomercial, direccion, cp, provincia, pais) VALUES ( '" \
             + request.form.get("cif") + "','" + request.form.get("nombrefiscal") + "','" +  request.form.get("nombrecomercial") + "','" + request.form.get("direccion") + "'," \
            + request.form.get("cp")+ ",'" + request.form.get("provincia") +"','" + request.form.get("pais")+"')"
        db.execute (sql)
        global gclientes
        gclientes = db.execute("SELECT * FROM clientes")
        #pedido = Pedido(atributos)
        #db1.session.add(pedido)
        #db1.session.commit()
        # remember which user has logged in
        # redirect user to home page
        return render_template("cliente.html")
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("cliente.html")

@app.route("/articulos", methods=["GET", "POST"])
@login_required
def articulos():
    articulos = db.execute("SELECT * FROM articulos")
    return render_template("articulos.html",registros=articulos)
@app.route("/cargapaquetes", methods=["GET", "POST"])
def cargapaquetes():
    if request.method == "GET":
        estado=request.args.get("estado")
        texto=request.args.get("texto")
        if texto != "":
            sql = "SELECT paquetes.id as id, paquetes.codigo as codigo, articulos.descripcion as descripcion," + \
                "paquetes.largo as largo, paquetes.ancho as ancho, paquetes.grueso as grueso," + \
                "paquetes.calculo as calculo, paquetes.UN as UN FROM paquetes, articulos " +\
                "WHERE paquetes.idarticulo = articulos.id and paquetes.estado = {} and articulos.descripcion like '%{}%'".format(estado, texto)
            rows = db.execute(sql)
        else:
            rows = db.execute("SELECT paquetes.id as id, paquetes.codigo as codigo, articulos.descripcion as descripcion, \
                paquetes.largo as largo, paquetes.ancho as ancho, paquetes.grueso as grueso, \
                paquetes.calculo as calculo, paquetes.UN as UN FROM paquetes, articulos\
                WHERE paquetes.idarticulo = articulos.id and paquetes.estado = :estado", estado=estado)

        return jsonify(rows)
    else:
        apology("No hay método POST")
@app.route("/consultapaquetes", methods=["GET", "POST"])
@login_required
def consultapaquetes():
    if request.method == "POST":
        return render_template("consultapaquetes.html")
    else:
        return render_template("consultapaquetes.html")
@app.route("/creapedido", methods=["GET", "POST"])
@login_required
def creapedido():
    if request.method == "POST":
        apology("En post creapedido")
    else:
        rows={"message": "caracoles", "severity": "danger"}
        return jsonify(rows)
if __name__ ==  '__main__':
    app.run()
