from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app, title='Movies API', description='A simple REST API for movies')

movie_ns = api.namespace('movies', description='Movies Base')
directors_ns = api.namespace('directors', description='Directors List')
genres_ns = api.namespace('genres', description='Genres List')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movie_ns.route('/')
class MoviesView(Resource):

    def get(self):
        """ Get all movies or filter movies by director id and/or genre id. """
        director = request.args.get('director_id')
        genre = request.args.get('genre_id')
        if director and genre:
            all_movies = db.session.query(Movie).filter(Movie.director_id == director, Movie.genre_id == genre)
        elif director:
            all_movies = db.session.query(Movie).filter(Movie.director_id == director)
        elif genre:
            all_movies = db.session.query(Movie).filter(Movie.genre_id == genre)
        else:
            all_movies = db.session.query(Movie).all()
        return movies_schema.dump(all_movies), 200

    def post(self):
        """ Add a new movie """
        req_json = request.json
        new_movie = Movie(**req_json)

        db.session.add(new_movie)
        db.session.commit()
        return '', 201


@movie_ns.route('/<int:movie_id>')
class MovieView(Resource):

    def get(self, movie_id):
        """ Get movie by id """
        movie_by_id = db.session.query(Movie).get(movie_id)
        return movie_schema.dump(movie_by_id), 200

    def put(self, movie_id):
        """ Update movie data by id """
        movie = db.session.query(Movie).get_or_404(movie_id)
        req_json = request.json

        movie.title = req_json.get('title')
        movie.description = req_json.get('description')
        movie.trailer = req_json.get('trailer')
        movie.year = req_json.get('year')
        movie.rating = req_json.get('rating')
        movie.genre_id = req_json.get('genre_id')
        movie.director_id = req_json.get('director_id')

        db.session.add(movie)
        db.session.commit()
        return '', 204

    def delete(self, movie_id):
        """ Delete movie by id """
        movie = db.session.query(Movie).get_or_404(movie_id)

        db.session.delete(movie)
        db.session.commit()
        return '', 204


@directors_ns.route('/')
class DirectorsView(Resource):

    def get(self):
        """ Get all directors """
        directors = db.session.query(Director).all()
        return directors_schema.dump(directors), 200

    def post(self):
        """ Add a new director """
        req_json = request.json
        new_director = Director(**req_json)

        db.session.add(new_director)
        db.session.commit()
        return '', 201


@directors_ns.route('/<int:director_id>')
class DirectorView(Resource):

    def get(self, director_id):
        """ Get director by id """
        director_by_id = db.session.query(Director).get(director_id)
        return director_schema.dump(director_by_id), 200

    def put(self, director_id):
        """ Update director data by id """
        director = db.session.query(Director).get_or_404(director_id)
        req_json = request.json

        director.name = req_json.get('name')

        db.session.add(director)
        db.session.commit()
        return '', 204

    def delete(self, director_id):
        """ Delete director by id """
        director = db.session.query(Director).get_or_404(director_id)

        db.session.delete(director)
        db.session.commit()
        return '', 204


@genres_ns.route('/')
class GenresView(Resource):

    def get(self):
        """ Get all genres """
        genres = db.session.query(Genre).all()
        return genres_schema.dump(genres), 200

    def post(self):
        """ Add a new genre """
        req_json = request.json
        new_genre = Genre(**req_json)

        db.session.add(new_genre)
        db.session.commit()
        return '', 201


@genres_ns.route('/<int:genre_id>')
class GenreView(Resource):

    def get(self, genre_id):
        """ Get genre by id """
        genre_by_id = db.session.query(Genre).get(genre_id)
        return genre_schema.dump(genre_by_id), 200

    def put(self, genre_id):
        """ Update genre data by id """
        genre = db.session.query(Genre).get_or_404(genre_id)
        req_json = request.json

        genre.name = req_json.get('name')

        db.session.add(genre)
        db.session.commit()
        return '', 204

    def delete(self, genre_id):
        """ Delete genre by id """
        genre = db.session.query(Genre).get_or_404(genre_id)

        db.session.delete(genre)
        db.session.commit()
        return '', 204


api.add_resource(MovieView, '/movies/<int:movie_id>')
api.add_resource(DirectorView, '/directors/<int:director_id>')
api.add_resource(GenreView, '/genres/<int:genre_id>')

if __name__ == '__main__':
    app.run(debug=True)
