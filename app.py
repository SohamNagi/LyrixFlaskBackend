import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, Song, Author, LineAnalysis
from gpt_service import GPTService

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lyrix.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
CORS(app, origins=["https://www.lyrix.app/", "localhost:3000", "http://localhost:5173"])

# Initialize GPT service
gpt_service = GPTService()


@app.route('/api/songs/<int:song_id>/transcription')
def get_transcription(song_id):
    """Get or generate line transcription for a song"""
    language = request.args.get('language', 'en')
    line_num = request.args.get('linenum', type=int)

    if line_num is None:
        return jsonify({'error': 'linenum parameter is required'}), 400

    try:
        # Find the song
        song = Song.query.get_or_404(song_id)

        # Check if analysis already exists
        existing_analysis = LineAnalysis.query.filter_by(
            song_id=song_id,
            line_number=line_num,
            language=language
        ).first()

        if existing_analysis:
            # Try to parse existing analysis as JSON, fallback to plain text
            try:
                return jsonify(json.loads(existing_analysis.analysis))
            except (json.JSONDecodeError, TypeError):
                # Legacy format - return as interpretation only
                return jsonify({
                    "translation": "Not available",
                    "interpretation": existing_analysis.analysis,
                    "connectionsToContext": "Legacy analysis format"
                })

        # Generate new analysis
        lyrics = song.get_lyrics_by_language(language)
        if not lyrics:
            return jsonify({'error': f'No lyrics available for language: {language}'}), 404

        lines = lyrics.split('\n')
        if line_num >= len(lines):
            return jsonify({'error': 'Line number out of range'}), 400

        line = lines[line_num]
        generated_analysis = gpt_service.generate_analysis(
            lyrics, line, language)

        # Save the analysis as JSON string
        new_analysis = LineAnalysis(
            song_id=song_id,
            line_number=line_num,
            language=language,
            analysis=json.dumps(generated_analysis)
        )
        db.session.add(new_analysis)
        db.session.commit()

        return jsonify(generated_analysis)

    except (json.JSONDecodeError, TypeError) as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/songs/<int:song_id>/theme')
def get_theme(song_id):
    """Get or generate theme for a song"""
    language = request.args.get('language', 'en')

    try:
        # Find the song
        song = Song.query.get_or_404(song_id)

        # Check if theme already exists
        existing_theme = song.get_theme_by_language(language)
        if existing_theme:
            return existing_theme

        # Generate new theme
        lyrics = song.get_lyrics_by_language(language)
        if not lyrics:
            return jsonify({'error': f'No lyrics available for language: {language}'}), 404

        generated_theme = gpt_service.generate_theme(lyrics, language)

        # Save the theme
        song.set_theme_by_language(language, generated_theme)
        db.session.commit()

        return generated_theme

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/songs')
def get_songs():
    """Get all songs with pagination"""
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)  # Limit to 100 songs per page

    # Get songs with pagination, ordered alphabetically by title
    songs_paginated = Song.query.order_by(Song.title).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'songs': [song.to_dict() for song in songs_paginated.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': songs_paginated.total,
            'pages': songs_paginated.pages,
            'has_next': songs_paginated.has_next,
            'has_prev': songs_paginated.has_prev
        }
    })


@app.route('/api/songs/<int:song_id>')
def get_song(song_id):
    """Get a specific song"""
    song = Song.query.get_or_404(song_id)
    return jsonify(song.to_dict())


@app.route('/api/authors')
def get_authors():
    """Get all authors with pagination"""
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)  # Limit to 100 authors per page

    # Get authors with pagination, ordered alphabetically by name
    authors_paginated = Author.query.order_by(Author.name).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'authors': [author.to_dict() for author in authors_paginated.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': authors_paginated.total,
            'pages': authors_paginated.pages,
            'has_next': authors_paginated.has_next,
            'has_prev': authors_paginated.has_prev
        }
    })


@app.route('/api/authors/<int:author_id>')
def get_author(author_id):
    """Get a specific author"""
    author = Author.query.get_or_404(author_id)
    return jsonify(author.to_dict())


@app.route('/api/authors/<int:author_id>/songs')
def get_songs_by_author(author_id):
    """Get all songs by a specific author"""
    # Verify author exists
    author = Author.query.get_or_404(author_id)

    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)  # Limit to 100 songs per page

    # Get songs with pagination, ordered alphabetically by title
    songs_query = Song.query.filter_by(
        author_id=author_id).order_by(Song.title)
    songs_paginated = songs_query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'author': author.to_dict(),
        'songs': [song.to_dict() for song in songs_paginated.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': songs_paginated.total,
            'pages': songs_paginated.pages,
            'has_next': songs_paginated.has_next,
            'has_prev': songs_paginated.has_prev
        }
    })


@app.route('/api/search')
def search():
    """Search for songs and authors"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Search query is required'}), 400

    # Search in song titles
    songs = Song.query.filter(
        Song.title.ilike(f'%{query}%')
    ).limit(20).all()

    # Search in author names
    authors = Author.query.filter(
        Author.name.ilike(f'%{query}%')
    ).limit(10).all()

    return jsonify({
        'query': query,
        'songs': [song.to_dict() for song in songs],
        'authors': [author.to_dict() for author in authors]
    })


@app.route('/api/search/songs')
def search_songs():
    """Search specifically for songs"""
    query = request.args.get('q', '').strip()
    author_id = request.args.get('author_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)

    if not query:
        return jsonify({'error': 'Search query is required'}), 400

    # Build query
    songs_query = Song.query.filter(Song.title.ilike(f'%{query}%'))

    # Filter by author if specified
    if author_id:
        songs_query = songs_query.filter_by(author_id=author_id)

    # Paginate results
    songs_paginated = songs_query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'query': query,
        'songs': [song.to_dict() for song in songs_paginated.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': songs_paginated.total,
            'pages': songs_paginated.pages,
            'has_next': songs_paginated.has_next,
            'has_prev': songs_paginated.has_prev
        }
    })


@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    return jsonify({
        'total_authors': Author.query.count(),
        'total_songs': Song.query.count(),
        'total_analyses': LineAnalysis.query.count(),
        'authors_with_songs': db.session.query(Author.id).join(Song).distinct().count()
    })


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()


if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0', port=5000)
