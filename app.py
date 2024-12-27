from flask import Flask, request, jsonify, render_template
from models import db, Pokemon
from routes import index, add_pokemon, delete_pokemon, edit_pokemon
from flask_migrate import Migrate  # Importa Flask-Migrate
# Crear la aplicación Flask
app = Flask(__name__, static_url_path='/static', static_folder='static')

# Configuración de la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg"}

# Inicializar la base de datos
db.init_app(app)

# Inicializar Flask-Migrate
migrate = Migrate(app, db)

@app.route("/", methods=["GET"])
def index():
    search_query = request.args.get("search", "")
    page = int(request.args.get("page", 1))
    per_page = 10

    # Filtrar Pokémon por nombre o tipo
    query = Pokemon.query.filter(
        Pokemon.name.ilike(f"%{search_query}%")
        | Pokemon.type.ilike(f"%{search_query}%")
    )

    total_pokemons = query.count()
    pokemons = query.offset((page - 1) * per_page).limit(per_page).all()

    total_pages = (total_pokemons + per_page - 1) // per_page

    # Obtener la imagen del Pokémon desde la API de Pokémon
    for pokemon in pokemons:
        pokemon.image_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon.id}.png"
  # Imprimir la URL de la imagen en la consola para verificar
        print(pokemon.image_url)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(
            {
                "pokemons": [
                    {
                        "id": pokemon.id,
                        "name": pokemon.name,
                        "type": pokemon.type,
                        "height": pokemon.height,
                        "weight": pokemon.weight,
                        "image_url": pokemon.image_url,
                    }
                    for pokemon in pokemons
                ],
                "total_pages": total_pages,
            }
        )

    return render_template(
        "index.html",
        pokemons=pokemons,
        search_query=search_query,
        total_pages=total_pages,
        current_page=page,
    )


# Rutas
app.add_url_rule("/delete_pokemon/<int:id>", "delete_pokemon", delete_pokemon)
app.add_url_rule("/edit_pokemon/<int:id>", "edit_pokemon", edit_pokemon, methods=["GET", "POST"])
app.add_url_rule("/add_pokemon", "add_pokemon", add_pokemon, methods=["GET", "POST"])

# Iniciar la aplicación Flask
if __name__ == "__main__":
    app.run(debug=True)
