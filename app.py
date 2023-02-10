from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import qrcode
from PIL import Image

app = Flask(__name__)

# Configuramos la ruta a la base de datos
# Conexion a la db 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base_de_datos2.db' 
# Configuramos la clave secreta para el manejo de sesiones 
app.config['SECRET_KEY'] = 'clavesecreta'

# ------------- Definir la base de datos sobre app ------------------------------------
db = SQLAlchemy(app)

# -----------------------------------------CLASES--------------------------------------------------------

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    cedula = db.Column(db.Integer, nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    tipo_sangre = db.Column(db.String(50), nullable=False)
    enf_base = db.Column(db.String(50), nullable=False)
    alergia = db.Column(db.String(50), nullable=False)
    seguro_medico = db.Column(db.String(50), nullable=False)
    nom_cont = db.Column(db.String(50), nullable=False)
    tel_cont = db.Column(db.Integer, nullable=False)
    parentesco = db.Column(db.String(50), nullable=False)

    def __init__(self, nombre, cedula, edad, password, apellido, tipo_sangre, enf_base, alergia, seguro_medico, nom_cont, tel_cont, parentesco): 
        self.nombre = nombre
        self.cedula = cedula
        self.edad = edad
        self.password = password
        self.apellido = apellido
        self.tipo_sangre = tipo_sangre
        self.enf_base = enf_base
        self.alergia = alergia
        self.seguro_medico = seguro_medico
        self.nom_cont = nom_cont
        self.tel_cont = tel_cont
        self.parentesco = parentesco

# Con el conexto de la app, creamos la base de datos
with app.app_context():
    db.create_all()

# ----------------------------------RUTASSS ----------------------------------------------------------------------
@app.route('/register', methods= ['GET', 'POST'])
def register():

    if request.method == 'POST':
        diccionario = request.form

        nombre = diccionario['nombre']
        cedula = diccionario['cedula']
        edad = diccionario['edad']
        password = diccionario['password']
        apellido = diccionario['apellido']
        tipo_sangre = diccionario['tipo_sangre']
        enf_base = diccionario['enfermedad_base']
        alergia = diccionario['alergia']
        seguro_medico = diccionario['seguro_medico']
        nom_cont = diccionario['contacto']
        tel_cont = diccionario['telefono']
        parentesco = diccionario['parentesco']
        
        #print(nombre, cedula, password, apellido, tipo_sangre, enf_base, alergia, seguro_medico, nom_cont, tel_cont, parentesco)

        # crear un objeto con los datos del form y guardar 
        user = Usuario(nombre, cedula, edad, password, apellido, tipo_sangre, enf_base, alergia, seguro_medico, nom_cont, tel_cont, parentesco)
        
        # Agregar a la base de datos
        db.session.add(user)
        # Confirmar la operacion
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods= ['GET','POST'])
def login():
    if request.method == 'POST':
        cedula = request.form['cedula']
        password = request.form['password']

        # Verificar la cedula en la DB
        user = Usuario.query.filter_by(cedula=cedula).first()
        #Si existe el user...
        if user:
            # Comparar si cargo bien la contraseña
            if user.password == password:
                return redirect(url_for('ficha', cedula=user.cedula))
            else:
                print("Contraseña incorrecta")
        else:
            print("No existe un usuario con ese login")
    

    return render_template('login.html')

@app.route('/ficha')
def ficha():
    cedula = request.args['cedula']

    user = Usuario.query.filter_by(cedula=cedula).first()

    usuario_dict = user.__dict__

    print(usuario_dict)
    return render_template('ficha.html', usuario=usuario_dict)

def qr_generator(cedula, url): 
    # Pasamos el logo que vamos a utilizar en el qr code como una imagen
    logo_link = './static/lucas.jpeg'
    logo = Image.open(logo_link)

    # Pasamos los parametros de tamaño y color para nuestro codigo QR
    basewidth = 100
    wpercent = (basewidth / float(logo.size[0]))
    hsize = int((float(logo.size[1]) * float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)

    # Creamos una variable para almacenar el codigo de error en caso de que al generar el QR ocurra un errors
    Qrcode = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)

    # Generamos la ruta a la que nuestro codigo QR va a redireccionar
    Qrcode.add_data(url)
    # Generamos el codigo QR
    qrcode.make()

    # Pasamos los parametros de color y posicion de nuestro logo, tambien definimos el color que tendra nuestro QR
    qrcolor = 'Black'
    qrimg = Qrcode.make_image(fill_color=qrcolor, back_color="white").convert('RGB')
    pos = ((qrimg.size[0] - logo.size[0]) // 2, (qrimg.size[1] - logo.size[1]) // 2)
    qrimg.paste(logo, pos)
    # Guardamos nuestro codigo QR generado como una imagen
    qrimg.save(f'static/qr{cedula}.png')
    # Mostramos un texto una vez que el codigo QR haya sido generado con exito
    print('Codigo QR generado con exito') 

@app.route('/generar_qr')
def generar_qr(): 
    cedula = request.args['cedula']
    ip = '192.168.240.6:7000'
    url = 'http://'+ip+'/ficha?cedula='+cedula
    qr_generator (cedula, url)

    imagen = '/static/qr'+cedula+'.png'
    return render_template('visualizar_qr.html', imagen=imagen)

@app.route("/")
def index(): 
    return 'Hola'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000, debug=True)