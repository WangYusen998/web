from app import create_app, db
from app.models import User, Movie, Review, Genre
from datetime import datetime, timedelta
import random

app = create_app()


def seed_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create Genres
        genres = [
            Genre(name='Drama'),
            Genre(name='Crime'),
            Genre(name='Action'),
            Genre(name='Sci-Fi'),
            Genre(name='Romance'),
            Genre(name='Adventure'),
            Genre(name='Animation'),
            Genre(name='Thriller'),
            Genre(name='Fantasy'),
            Genre(name='Comedy')
        ]
        db.session.add_all(genres)
        db.session.commit()

        # Create Users
        users = []
        # Default Admin
        admin = User(username='admin', email='admin@admin.com', is_admin=True)
        admin.set_password('admin123')
        users.append(admin)

        user1 = User(username='moviebuff', email='buff@example.com')
        user1.set_password('password')
        users.append(user1)

        user2 = User(username='critic_alice', email='alice@example.com')
        user2.set_password('password')
        users.append(user2)

        db.session.add_all(users)
        db.session.commit()

        # Create Movies with local JPG posters
        movies_data = [
            {
                'title': 'The Shawshank Redemption',
                'year': 1994,
                'director': 'Frank Darabont',
                'description': (
                    'Two imprisoned men bond over a number of years, '
                    'finding solace and eventual redemption through '
                    'acts of common decency.'
                ),
                'poster_url': '/static/images/shawshank.jpg',
                'genres': [
                    'Drama',
                    'Crime',
                ],
            },
            {
                'title': 'The Godfather',
                'year': 1972,
                'director': 'Francis Ford Coppola',
                'description': (
                    'The aging patriarch of an organized crime dynasty '
                    'transfers control of his clandestine empire to his '
                    'reluctant son.'
                ),
                'poster_url': '/static/images/godfather.jpg',
                'genres': [
                    'Crime',
                    'Drama',
                ],
            },
            {
                'title': 'The Dark Knight',
                'year': 2008,
                'director': 'Christopher Nolan',
                'description': (
                    'When the menace known as the Joker wreaks havoc '
                    'and chaos on the people of Gotham, Batman must '
                    'accept one of the greatest psychological and '
                    'physical tests of his ability to fight injustice.'
                ),
                'poster_url': '/static/images/dark_knight.jpg',
                'genres': [
                    'Action',
                    'Crime',
                    'Drama',
                ],
            },
            {
                'title': 'Pulp Fiction',
                'year': 1994,
                'director': 'Quentin Tarantino',
                'description': (
                    'The lives of two mob hitmen, a boxer, a gangster '
                    'and his wife, and a pair of diner bandits '
                    'intertwine in four tales of violence and '
                    'redemption.'
                ),
                'poster_url': '/static/images/pulp_fiction.jpg',
                'genres': [
                    'Crime',
                    'Drama',
                ],
            },
            {
                'title': 'Forrest Gump',
                'year': 1994,
                'director': 'Robert Zemeckis',
                'description': (
                    'The presidencies of Kennedy and Johnson, the '
                    'events of Vietnam, Watergate and other historical '
                    'events unfold from the perspective of an Alabama '
                    'man with an IQ of 75, whose only desire is to be '
                    'reunited with his childhood sweetheart.'
                ),
                'poster_url': '/static/images/forrest_gump.jpg',
                'genres': [
                    'Drama',
                    'Romance',
                ],
            },
            {
                'title': 'Inception',
                'year': 2010,
                'director': 'Christopher Nolan',
                'description': (
                    'A thief who steals corporate secrets through the '
                    'use of dream-sharing technology is given the '
                    'inverse task of planting an idea into the mind of '
                    'a C.E.O.'
                ),
                'poster_url': '/static/images/inception.jpg',
                'genres': [
                    'Action',
                    'Sci-Fi',
                ],
            },
            {
                'title': 'The Matrix',
                'year': 1999,
                'director': 'Lana Wachowski, Lilly Wachowski',
                'description': (
                    'A computer hacker learns from mysterious rebels '
                    'about the true nature of his reality and his role '
                    'in the war against its controllers.'
                ),
                'poster_url': '/static/images/matrix.jpg',
                'genres': [
                    'Action',
                    'Sci-Fi',
                ],
            },
            {
                'title': 'Fight Club',
                'year': 1999,
                'director': 'David Fincher',
                'description': (
                    'An insomniac office worker and a devil-may-care '
                    'soap maker form an underground fight club that '
                    'evolves into much more.'
                ),
                'poster_url': '/static/images/fight_club.jpg',
                'genres': [
                    'Drama',
                ],
            },
            {
                'title': 'Interstellar',
                'year': 2014,
                'director': 'Christopher Nolan',
                'description': (
                    'A team of explorers travel through a wormhole in '
                    "space in an attempt to ensure humanity's survival."
                ),
                'poster_url': '/static/images/interstellar.jpg',
                'genres': [
                    'Sci-Fi',
                    'Drama',
                    'Adventure',
                ],
            },
            {
                'title': 'Spirited Away',
                'year': 2001,
                'director': 'Hayao Miyazaki',
                'description': (
                    "During her family's move to the suburbs, a sullen "
                    '10-year-old girl wanders into a world ruled by '
                    'gods, witches, and spirits, and where humans are '
                    'changed into beasts.'
                ),
                'poster_url': '/static/images/spirited_away.jpg',
                'genres': [
                    'Animation',
                    'Adventure',
                ],
            },
            {
                'title': 'Parasite',
                'year': 2019,
                'director': 'Bong Joon Ho',
                'description': (
                    'Greed and class discrimination threaten the newly '
                    'formed symbiotic relationship between the wealthy '
                    'Park family and the destitute Kim clan.'
                ),
                'poster_url': '/static/images/parasite.jpg',
                'genres': [
                    'Thriller',
                    'Drama',
                ],
            },
            {
                'title': 'The Lord of the Rings: The Fellowship of the Ring',
                'year': 2001,
                'director': 'Peter Jackson',
                'description': (
                    'A meek Hobbit from the Shire and eight companions '
                    'set out on a journey to destroy the powerful One '
                    'Ring and save Middle-earth from the Dark Lord '
                    'Sauron.'
                ),
                'poster_url': '/static/images/lotr_fellowship.jpg',
                'genres': [
                    'Adventure',
                    'Fantasy',
                    'Action',
                ],
            },
            {
                'title': 'The Avengers',
                'year': 2012,
                'director': 'Joss Whedon',
                'description': (
                    "Earth's mightiest heroes must come together and "
                    'learn to fight as a team if they are to stop the '
                    'mischievous Loki and his alien army from enslaving '
                    'humanity.'
                ),
                'poster_url': '/static/images/avengers.jpg',
                'genres': [
                    'Action',
                    'Sci-Fi',
                ],
            },
            {
                'title': 'Titanic',
                'year': 1997,
                'director': 'James Cameron',
                'description': (
                    'A seventeen-year-old aristocrat falls in love with '
                    'a kind but poor artist aboard the luxurious, '
                    'ill-fated R.M.S. Titanic.'
                ),
                'poster_url': '/static/images/titanic.jpg',
                'genres': [
                    'Romance',
                    'Drama',
                ],
            },
            {
                'title': 'The Silence of the Lambs',
                'year': 1991,
                'director': 'Jonathan Demme',
                'description': (
                    'A young F.B.I. cadet must receive the help of an '
                    'incarcerated and manipulative cannibal killer to '
                    'help catch another serial killer, a madman who '
                    'skins his victims.'
                ),
                'poster_url': '/static/images/silence_of_lambs.jpg',
                'genres': [
                    'Crime',
                    'Thriller',
                ],
            },
            {
                'title': 'The Lion King',
                'year': 1994,
                'director': 'Roger Allers, Rob Minkoff',
                'description': (
                    'Lion prince Simba and his father are targeted by '
                    'his bitter uncle, who wants to ascend the throne '
                    'himself.'
                ),
                'poster_url': '/static/images/lion_king.jpg',
                'genres': [
                    'Animation',
                    'Adventure',
                    'Drama',
                ],
            },
            {
                'title': 'Back to the Future',
                'year': 1985,
                'director': 'Robert Zemeckis',
                'description': (
                    'Marty McFly, a 17-year-old high school student, is '
                    'accidentally sent thirty years into the past in a '
                    'time-traveling DeLorean invented by his close '
                    'friend, the eccentric scientist Doc Brown.'
                ),
                'poster_url': '/static/images/back_to_future.jpg',
                'genres': [
                    'Adventure',
                    'Comedy',
                    'Sci-Fi',
                ],
            },
            {
                'title': 'Gladiator',
                'year': 2000,
                'director': 'Ridley Scott',
                'description': (
                    'A former Roman General sets out to exact vengeance '
                    'against the corrupt emperor who murdered his '
                    'family and sent him into slavery.'
                ),
                'poster_url': '/static/images/gladiator.jpg',
                'genres': [
                    'Action',
                    'Adventure',
                    'Drama',
                ],
            },
            {
                'title': 'Avatar',
                'year': 2009,
                'director': 'James Cameron',
                'description': (
                    'A paraplegic Marine dispatched to the moon Pandora '
                    'on a unique mission becomes torn between following '
                    'his orders and protecting the world he feels is '
                    'his home.'
                ),
                'poster_url': '/static/images/avatar.jpg',
                'genres': [
                    'Action',
                    'Adventure',
                    'Sci-Fi',
                ],
            },
            {
                'title': 'The Green Mile',
                'year': 1999,
                'director': 'Frank Darabont',
                'description': (
                    'The lives of guards on Death Row are affected by '
                    'one of their charges: a black man accused of child '
                    'murder and rape, yet who has a mysterious gift.'
                ),
                'poster_url': '/static/images/green_mile.jpg',
                'genres': [
                    'Crime',
                    'Drama',
                    'Fantasy',
                ],
            },
            {
                'title': "Schindler's List",
                'year': 1993,
                'director': 'Steven Spielberg',
                'description': (
                    'In German-occupied Poland during World War II, '
                    'industrialist Oskar Schindler gradually becomes '
                    'concerned for his Jewish workforce after '
                    'witnessing their persecution by the Nazis.'
                ),
                'poster_url': '/static/images/schindlers_list.jpg',
                'genres': [
                    'Drama',
                ],
            },
            {
                'title': '12 Angry Men',
                'year': 1957,
                'director': 'Sidney Lumet',
                'description': (
                    'The jury in a New York City murder trial is '
                    'frustrated by a single member whose skeptical '
                    'caution forces them to more carefully consider the '
                    'evidence before jumping to a hasty verdict.'
                ),
                'poster_url': '/static/images/12_angry_men.jpg',
                'genres': [
                    'Crime',
                    'Drama',
                ],
            },
            {
                'title': 'Goodfellas',
                'year': 1990,
                'director': 'Martin Scorsese',
                'description': (
                    'The story of Henry Hill and his life in the mob, '
                    'covering his relationship with his wife Karen Hill '
                    'and his mob partners Jimmy Conway and Tommy DeVito '
                    'in the Italian-American crime syndicate.'
                ),
                'poster_url': '/static/images/goodfellas.jpg',
                'genres': [
                    'Crime',
                    'Drama',
                ],
            },
            {
                'title': 'Star Wars: Episode IV - A New Hope',
                'year': 1977,
                'director': 'George Lucas',
                'description': (
                    'Luke Skywalker joins forces with a Jedi Knight, a '
                    'cocky pilot, a Wookiee and two droids to save the '
                    "galaxy from the Empire's world-destroying battle "
                    'station, while also attempting to rescue Princess '
                    'Leia from the mysterious Darth Vader.'
                ),
                'poster_url': '/static/images/star_wars_new_hope.jpg',
                'genres': [
                    'Action',
                    'Adventure',
                    'Fantasy',
                ],
            },
            {
                'title': 'Seven Samurai',
                'year': 1954,
                'director': 'Akira Kurosawa',
                'description': (
                    'A poor village under attack by bandits recruits '
                    'seven unemployed samurai to help them defend '
                    'themselves.'
                ),
                'poster_url': '/static/images/seven_samurai.jpg',
                'genres': [
                    'Action',
                    'Drama',
                ],
            },
            {
                'title': 'City of God',
                'year': 2002,
                'director': 'Fernando Meirelles, Kátia Lund',
                'description': (
                    "In the slums of Rio, two kids' paths diverge as "
                    'one struggles to become a photographer and the '
                    'other a kingpin.'
                ),
                'poster_url': '/static/images/city_of_god.jpg',
                'genres': [
                    'Crime',
                    'Drama',
                ],
            },
            {
                'title': 'Life Is Beautiful',
                'year': 1997,
                'director': 'Roberto Benigni',
                'description': (
                    'When an open-minded Jewish librarian and his son '
                    'become victims of the Holocaust, he uses a perfect '
                    'mixture of will, humor, and imagination to protect '
                    'his son from the dangers around their camp.'
                ),
                'poster_url': '/static/images/life_is_beautiful.jpg',
                'genres': [
                    'Comedy',
                    'Drama',
                    'Romance',
                ],
            },
            {
                'title': 'Se7en',
                'year': 1995,
                'director': 'David Fincher',
                'description': (
                    'Two detectives, a rookie and a veteran, hunt a '
                    'serial killer who uses the seven deadly sins as '
                    'his motives.'
                ),
                'poster_url': '/static/images/seven.jpg',
                'genres': [
                    'Crime',
                    'Drama',
                    'Thriller',
                ],
            },
            {
                'title': 'Saving Private Ryan',
                'year': 1998,
                'director': 'Steven Spielberg',
                'description': (
                    'Following the Normandy Landings, a group of U.S. '
                    'soldiers go behind enemy lines to retrieve a '
                    'paratrooper whose brothers have been killed in '
                    'action.'
                ),
                'poster_url': '/static/images/saving_private_ryan.jpg',
                'genres': [
                    'Action',
                    'Drama',
                ],
            },
            {
                'title': 'The Usual Suspects',
                'year': 1995,
                'director': 'Bryan Singer',
                'description': (
                    'A sole survivor tells of the twisty events leading '
                    'up to a horrific gun battle on a boat, which began '
                    'when five criminals met at a seemingly random '
                    'police lineup.'
                ),
                'poster_url': '/static/images/usual_suspects.jpg',
                'genres': [
                    'Crime',
                    'Thriller',
                ],
            },
        ]

        movies = []
        for m_data in movies_data:
            movie = Movie(
                title=m_data['title'],
                year=m_data['year'],
                director=m_data['director'],
                description=m_data['description'],
                poster_url=m_data['poster_url']
            )
            for g_name in m_data['genres']:
                genre = Genre.query.filter_by(name=g_name).first()
                if genre:
                    movie.genres.append(genre)
            movies.append(movie)
            db.session.add(movie)

        db.session.commit()

        # Add Reviews
        reviews = []
        for movie in movies:
            # Add 1-3 reviews per movie
            for _ in range(random.randint(1, 3)):
                user = random.choice(users)
                rating = random.randint(3, 5)
                review_content = (
                    f"This is a sample review for {movie.title}. "
                    "I really enjoyed the directing and the plot was engaging."
                )
                review = Review(
                    content=review_content,
                    rating=rating,
                    author=user,
                    movie=movie,
                    created_at=datetime.utcnow()
                    - timedelta(days=random.randint(0, 30)),
                )
                reviews.append(review)
                db.session.add(review)

                # Update movie average rating (simple logic for seeding)
                current_reviews = [
                    r.rating for r in reviews if r.movie_id == movie.id]
                if current_reviews:
                    # This logic is slightly off because we haven't committed
                    # reviews yet, but for seeding we can just calc manually.
                    pass

        db.session.commit()

        # Re-calculate average ratings
        for movie in movies:
            all_reviews = movie.reviews.all()
            if all_reviews:
                avg = sum([r.rating for r in all_reviews]) / len(all_reviews)
                movie.average_rating = avg
        db.session.commit()

        print(
            "Database seeded successfully with movies, genres, users, and "
            "reviews."
        )


if __name__ == '__main__':
    seed_data()
