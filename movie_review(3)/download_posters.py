import os
import requests


def join_url(*parts):
    return "".join(parts)


images = {
    '12_angry_men.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/9/91/12_Angry_Men_',
            '%281957_film_poster%29.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BMWU4N2FjNzYtNTVkNC00',
            'NzQ0LTg0MjAtYTJlMjFhNGUxZDFmXkEyXkFqcGdeQXVyNjc1NTYyMjg@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'avatar.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/d/d6/Avatar_%28200',
            '9_film%29_poster.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BZDA0OGQxNTItMDZkMC00',
            'N2UyLTg3MzMtYTJmNjg3Nzk5MzRiXkEyXkFqcGdeQXVyMjUzOTY1NTc@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'avengers.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/8/8a/The_Avengers_',
            '%282012_film%29_poster.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BNDYxNjQyMjAtNTdiOS00',
            'NGYwLWFmNTAtNThmYjU5ZGI2YTI1XkEyXkFqcGdeQXVyMTMxODk2OTU@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'back_to_future.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/d/d2/Back_to_the_F',
            'uture.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BZmU0M2Y1OGUtZjIxNi00',
            'ZjBkLTg1MjgtOWIyNThiZWIwYjRiXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'city_of_god.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/1/10/Cidade_de_Deu',
            's.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BMGU5Y2FkZDgtNzM2ZC00',
            'MTBkLTk4NzUtYTk3ODAyOWI2YjgzXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'dark_knight.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/1/1c/The_Dark_Knig',
            'ht_(2008_film_poster).jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5B',
            'anBnXkFtZTcwODAyMTk2Mw@@._V1_FMjpg_UX1000_.jpg',
        ),
    ],
    'fight_club.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/f/fc/Fight_Club_po',
            'ster.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BMmEzNTkxYjQtZTc0MC00',
            'YTVjLTg5ZTEtZWMwOWVlYzY0NWIwXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'forrest_gump.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/6/67/Forrest_Gump_',
            'poster.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BNWIwODRlZTUtY2U3ZS00',
            'Yzg1LWJhNzYtMmZiYmEyNmU1NjMzXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'gladiator.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/f/f6/Gladiator_ver',
            '1.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BMDliMmNhNDEtODUyOS00',
            'MjNlLTgxODEtN2U3NzIxMGVkZTA1XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'godfather.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/1/1c/Godfather_ver',
            '1.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00',
            'MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'goodfellas.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/7/7b/Goodfellas.jp',
            'g',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BY2NkZjEzMDgtN2RjYy00',
            'YzM1LWI4ZmQtMjIwYjFjNmI3ZGEwXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'green_mile.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/c/ce/Green_mile.jp',
            'g',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BMTUxMzQyNjA5MF5BMl5B',
            'anBnXkFtZTYwOTU2NTY3._V1_FMjpg_UX1000_.jpg',
        ),
    ],
    'inception.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/2/2e/Inception_(20',
            '10)_theatrical_poster.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5B',
            'anBnXkFtZTcwNTI5OTM0Mw@@._V1_FMjpg_UX1000_.jpg',
        ),
    ],
    'interstellar.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/b/bc/Interstellar_',
            'film_poster.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00',
            'OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'life_is_beautiful.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/7/7c/Vitaebella.jp',
            'g',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BYmJmM2Q4NmMtYThmNC00',
            'ZjRlLWEyZmItZTIwOTczZGQ1YTg0XkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'lion_king.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/3/3d/The_Lion_King',
            '_poster.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BYTYxNGMyZTYtMjE3MS00',
            'MzNjLWFjNmYtMDk3N2FmM2JiM2M1XkEyXkFqcGdeQXVyNjY5NDU4NzI@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'lotr_fellowship.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/8/8a/The_Lord_of_t',
            'he_Rings_The_Fellowship_of_the_Ring_%282001%29.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BN2EyZjM3NzUtNWUzMi00',
            'MTgxLWI0NTctMzY4M2VlOTdjZWRiXkEyXkFqcGdeQXVyNDUzOTQ5MjY@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'matrix.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/c/c1/The_Matrix_Po',
            'ster.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00',
            'ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0',
            'OTY@._V1_FMjpg_UX1000_.jpg',
        ),
    ],
    'parasite.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/5/53/Parasite_%282',
            '019_film%29.png',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BYWZjMjk3ZTItODQ2ZC00',
            'NTY5LWE0ZDYtZTI3MjcwN2Q5NTVkXkEyXkFqcGdeQXVyODk4OTc3MTY@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'pulp_fiction.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/3/3b/Pulp_Fiction_',
            '(1994)_poster.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BNGNhMDIzZTUtNTBlZi00',
            'MTRlLWFjM2ItYzViMjE3YzI5MjljXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'saving_private_ryan.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/a/ac/Saving_Privat',
            'e_Ryan_poster.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BZjhkMDM4MWItZTVjOC00',
            'ZDRhLThmYTAtM2I5NzBmNmNlMzI1XkEyXkFqcGdeQXVyNDYyMDk5MTU@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'schindlers_list.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/3/38/Schindler%27s',
            '_List_movie.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BNDE4OTMxMTctNmRhYy00',
            'NWE2LTg3YzItYTk3M2UwOTU5Njg4XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'seven.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/6/68/Seven_%28movi',
            'e%29_poster.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BOTUwODM5MTctZjczMi00',
            'OTk4LTg3NWUtNmVhMTAzNTNjYjcyXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'seven_samurai.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/commons/b/b5/Seven_Sa',
            'murai_poster.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BOWE4YWVjMDQtYTEzMS00',
            'YzE5LTg5N2ItZWE4ODM3M2Q0MjkwXkEyXkFqcGdeQXVyODk4OTc3MTY@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'shawshank.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/8/81/ShawshankRede',
            'mptionMoviePoster.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BNDE3ODUxMDQ4MV5BMl5B',
            'anBnXkFtZTcwMjY3MzXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_FMjpg_UX1',
            '000_.jpg',
        ),
    ],
    'silence_of_lambs.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/8/86/The_Silence_o',
            'f_the_Lambs_poster.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BNjNhZTk0ZmEtNjJhMi00',
            'YzFlLWE1MmEtYzM1M2ZmMGMwMTU4XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'spirited_away.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/d/db/Spirited_Away',
            '_Japanese_poster.png',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BMjlmZmI5MDctNDE2YS00',
            'YWE0LWE5ZWItZDBhYWQ0NTcxNWRhXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'star_wars_new_hope.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/8/87/StarWarsMovie',
            'Poster1977.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BNzVlY2MwMjktM2E4OS00',
            'Y2Y3LWE3ZjctYzhkZGM3YzA1ZWM2XkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'titanic.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/1/18/Titanic_%2819',
            '97_film%29_poster.png',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BMDdmZGU3NDQtY2E5My00',
            'ZTliLWIzOTUtMTY4ZGI1YjdiNjk3XkEyXkFqcGdeQXVyNTA4NzY1MzY@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
    'usual_suspects.jpg': [
        join_url(
            'https://upload.wikimedia.org/wikipedia/en/9/9c/Usual_suspect',
            's_ver1.jpg',
        ),
        join_url(
            'https://m.media-amazon.com/images/M/MV5BYTViNjMyNmUtNDFkNC00',
            'ZDRlLThmMDUtZDU2YWE4NGI2ZjVmXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1',
            '_FMjpg_UX1000_.jpg',
        ),
    ],
}

save_dir = '/Users/kbyte/Desktop/wys web/movie_review/static/images'

for filename, urls in images.items():
    success = False
    for url in urls:
        try:
            print(f"Attempting to download {filename} from {url}...")
            response = requests.get(
                url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10
            )
            if response.status_code == 200:
                with open(os.path.join(save_dir, filename), "wb") as f:
                    f.write(response.content)
                print(f"Successfully downloaded {filename}")
                success = True
                break
            else:
                print(f"Failed: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")

    if not success:
        print(f"Could not download {filename}")
