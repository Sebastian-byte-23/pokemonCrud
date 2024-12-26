import requests
from flask import render_template, request, redirect, url_for, jsonify
from models import db, Pokemon


# Función para obtener los detalles de un Pokémon
def fetch_pokemon_details(pokemon_url):
    response = requests.get(pokemon_url)
    data = response.json()
    return {
        "name": data["name"],
        "type": data["types"][0]["type"]["name"],
        "height": data["height"],
        "weight": data["weight"],
    }


# Función para obtener todos los Pokémon
def fetch_all_pokemons():
    url = "https://pokeapi.co/api/v2/pokemon?limit=100"  # Limitamos a los primeros 100 Pokémon
    response = requests.get(url)
    pokemons_data = response.json()["results"]

    for pokemon in pokemons_data:
        details = fetch_pokemon_details(pokemon["url"])

        # Verificar si ya existe en la base de datos antes de agregarlo
        existing_pokemon = Pokemon.query.filter_by(name=details["name"]).first()
        if not existing_pokemon:
            new_pokemon = Pokemon(
                name=details["name"],
                type=details["type"],
                height=details["height"],
                weight=details["weight"],
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


# Ruta para agregar un Pokémon
def add_pokemon():
    if request.method == "POST":
        name = request.form["name"]
        type = request.form["type"]
        height = request.form["height"]
        weight = request.form["weight"]

        # Crear un nuevo Pokémon en la base de datos
        new_pokemon = Pokemon(name=name, type=type, height=height, weight=weight)

        db.session.add(new_pokemon)
        db.session.commit()

        return redirect(url_for("index"))  # Redirigir a la lista de Pokémon

    return render_template("add_pokemon.html")


# Ruta para eliminar un Pokémon
def delete_pokemon(id):
    pokemon_to_delete = Pokemon.query.get(id)
    if pokemon_to_delete:
        db.session.delete(pokemon_to_delete)
        db.session.commit()
    return redirect(url_for("index"))


# Ruta para editar un Pokémon
def edit_pokemon(id):
    pokemon = Pokemon.query.get(id)
    if request.method == "POST":
        pokemon.name = request.form["name"]
        pokemon.type = request.form["type"]
        pokemon.height = request.form["height"]
        pokemon.weight = request.form["weight"]

        db.session.commit()
        return redirect(url_for("index"))

    return render_template("edit_pokemon.html", pokemon=pokemon)
