from flask import Flask, request, jsonify, render_template
from models import db, Pokemon
from routes import index, add_pokemon, delete_pokemon, edit_pokemon, fetch_all_pokemons

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db.init_app(app)

# Ruta principal para ver todos los Pokémon
@app.route('/', methods=['GET'])
def home():
    search_query = request.args.get('search', '')  # Obtener el término de búsqueda si está presente
    
    # Filtrar los Pokémon por nombre o tipo
    pokemons = Pokemon.query.filter(
        Pokemon.name.ilike(f"%{search_query}%") |
        Pokemon.type.ilike(f"%{search_query}%")
    ).all()

    # Verificar si la solicitud es AJAX comprobando el encabezado
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'pokemons': [{
                'id': pokemon.id,
                'name': pokemon.name,
                'type': pokemon.type,
                'height': pokemon.height,
                'weight': pokemon.weight
            } for pokemon in pokemons]
        })

    # Si no es una solicitud AJAX, renderizar la plantilla
    return render_template("index.html", pokemons=pokemons, search_query=search_query)

# Rutas
app.add_url_rule('/', 'index', lambda: render_template('index.html'))
app.add_url_rule('/delete_pokemon/<int:id>', 'delete_pokemon', delete_pokemon)
app.add_url_rule('/edit_pokemon/<int:id>', 'edit_pokemon', edit_pokemon, methods=['GET', 'POST'])
app.add_url_rule('/add_pokemon', 'add_pokemon', add_pokemon, methods=['GET', 'POST'])

# Iniciar la aplicación Flask
if __name__ == '__main__':
    app.run(debug=True)
