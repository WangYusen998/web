from collections import Counter
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from app.models import Movie, Genre


def get_recommendations(user, limit=6):
    """
    基于用户收藏的简单推荐系统
    """
    # 1. 获取用户收藏的所有电影（预加载genres以避免N+1）
    favorited_movies = user.favorited_movies.options(
        joinedload(Movie.genres)).all()

    # 如果用户没有收藏，返回评分最高的电影
    if not favorited_movies:
        return Movie.query.order_by(
            desc(Movie.average_rating)).limit(limit).all()

    # 2. 获取这些电影的所有类型并统计频率
    all_genres = []
    for movie in favorited_movies:
        for genre in movie.genres:
            all_genres.append(genre.id)

    if not all_genres:
        return Movie.query.order_by(
            desc(Movie.average_rating)).limit(limit).all()

    # 3. 找出用户最喜欢的类型 (Top 3)
    genre_counts = Counter(all_genres)
    most_common_genres = [g[0] for g in genre_counts.most_common(3)]

    # 4. 找出同样类型的其他电影（用户未收藏的）
    # 使用 joinedload 预加载 genres，方便后续可能的使用
    favorited_ids = [m.id for m in favorited_movies]

    recommendations = Movie.query.filter(
        Movie.genres.any(Genre.id.in_(most_common_genres)),  # 包含用户喜欢的任一类型
        ~Movie.id.in_(favorited_ids)                         # 排除已收藏的
    ).order_by(
        desc(Movie.average_rating)                           # 5. 按评分排序
    ).limit(limit).all()

    return recommendations


def get_similar_movies(movie, limit=4):
    """
    获取相似电影：基于共同类型数量
    """
    if not movie.genres:
        return []

    # 1. 获取当前电影的所有类型ID
    genre_ids = [g.id for g in movie.genres]

    # 2. 找出有相同类型的其他电影
    # 这里先获取候选集，稍大一点以便Python层排序
    candidates = Movie.query.filter(
        Movie.genres.any(Genre.id.in_(genre_ids)),
        Movie.id != movie.id
    ).options(joinedload(Movie.genres)).all()

    if not candidates:
        return []

    # 3. 按共同类型数量排序
    # Python层排序：(共同类型数量 DESC, 评分 DESC)
    movie_genre_ids = set(genre_ids)

    candidates.sort(key=lambda m: (
        len(set(g.id for g in m.genres) & movie_genre_ids),  # 共同类型数量
        m.average_rating                                    # 评分
    ), reverse=True)

    # 4. 返回前N部
    return candidates[:limit]
