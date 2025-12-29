from app import create_app
from app.models import Movie, Review

app = create_app()

with app.app_context():
    movies = Movie.query.all()
    print(f"Total movies: {len(movies)}")
    for m in movies:
        print(
            f"Movie: {m.title}, ID: {m.id}, Reviews: "
            f"{m.reviews.count()}, Rating: {m.average_rating}"
        )

    reviews = Review.query.all()
    print(f"Total reviews: {len(reviews)}")
