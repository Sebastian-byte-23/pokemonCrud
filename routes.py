from flask import render_template, request, redirect, url_for, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import requests
from models import db, Pokemon

# Configuración para cargar imágenes
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


# Función para verificar la extensión del archivo
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Ruta para agregar un Pokémon
def add_pokemon():
    if request.method == "POST":
        name = request.form["name"]
        type = request.form["type"]
        height = request.form["height"]
        weight = request.form["weight"]

        # Manejo de la imagen
        image_url = None
        image = request.files.get("image")

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            image_url = f"/static/uploads/{filename}"

        # Crear un nuevo Pokémon en la base de datos
        new_pokemon = Pokemon(
            name=name,
            type=type,
            height=height,
            weight=weight,
            image_url=image_url,  # Guardamos la URL de la imagen
        )

        db.session.add(new_pokemon)
        db.session.commit()
        print(
            f"Image URL for {name}: {image_url}"
        )  # Imprimir la URL de la imagen para verificar
        return redirect(url_for("index"))  # Redirigir a la lista de Pokémon

    return render_template("add_pokemon.html")


def fetch_pokemon_details(pokemon_url):
    response = requests.get(pokemon_url)
    data = response.json()
    image_url = data["sprites"]["front_default"]  # URL de la imagen frontal del Pokémon
    return {
        "name": data["name"],
        "type": data["types"][0]["type"]["name"],
        "height": data["height"],
        "weight": data["weight"],
        "image_url": image_url,  # Agregar la URL de la imagen
    }


# Función para obtener todos los Pokémon
def fetch_all_pokemons():
    url = "https://pokeapi.co/api/v2/pokemon?limit=100"  # Limitamos a los primeros 100 Pokémon
    response = requests.get(url)
    pokemons_data = response.json()["results"]

    for pokemon in pokemons_data:
        # Obtener detalles del Pokémon, incluyendo la imagen
        details = fetch_pokemon_details(pokemon["url"])

        # Verificar si ya existe en la base de datos antes de agregarlo
        existing_pokemon = Pokemon.query.filter_by(name=details["name"]).first()
        if not existing_pokemon:
            new_pokemon = Pokemon(
                name=details["name"],
                type=details["type"],
                height=details["height"],
                weight=details["weight"],
                image_url=details.get("image_url", None),  # Asignar la URL de la imagen
            )
            db.session.add(new_pokemon)

    db.session.commit()


# Función para la página principal (lista de Pokémon)
def index(pokemons=None, search_query=""):
    # Si no se pasan Pokémon, cargamos todos
    if pokemons is None:
        pokemons = Pokemon.query.all()

    return render_template("index.html", pokemons=pokemons, search_query=search_query)


# Ruta para la búsqueda de Pokémon
def search():
    search_query = request.args.get("search", "")
    pokemons = Pokemon.query.filter(
        Pokemon.name.ilike(f"%{search_query}%")
        | Pokemon.type.ilike(f"%{search_query}%")
    ).all()

    # Convertir los resultados a un formato de lista de diccionarios
    pokemon_data = [
        {
            "id": pokemon.id,
            "name": pokemon.name,
            "type": pokemon.type,
            "height": pokemon.height,
            "weight": pokemon.weight,
        }
        for pokemon in pokemons
    ]

    # Devolver los datos como un JSON
    return jsonify({"pokemons": pokemon_data})


# Ruta para eliminar un Pokémon
def delete_pokemon(id):
    pokemon_to_delete = Pokemon.query.get(id)
    if pokemon_to_delete:
        db.session.delete(pokemon_to_delete)
        db.session.commit()
    return redirect(url_for("index"))


# Ruta para editar un Pokémon
def edit_pokemon(id):
    # Buscar el Pokémon por ID
    pokemon = Pokemon.query.get(id)
    
    # Si no se encuentra el Pokémon, redirige al listado
    if not pokemon:
        return redirect(url_for('index'))  # Redirigir a la lista de Pokémon si no se encuentra
    
    if request.method == "POST":
        # Si es un formulario POST, actualizar los datos
        pokemon.name = request.form["name"]
        pokemon.type = request.form["type"]
        pokemon.height = request.form["height"]
        pokemon.weight = request.form["weight"]

        # Guardar cambios en la base de datos
        db.session.commit()
        return redirect(url_for("index"))  # Redirigir a la lista de Pokémon después de guardar cambios

    # Si es un formulario GET, renderizar la plantilla de edición
    return render_template("edit_pokemon.html", pokemon=pokemon)