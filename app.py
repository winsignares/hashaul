from flask import Flask, request, redirect, render_template
from config.db import app

#en esta parte se importan los modulos de flask y el app de la configuracion

# registramos las rutas con blueprint


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=true, port=5000,host="0.0.0.0")
