from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Relationship
    songs = db.relationship('Song', backref='author',
                            lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Author {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'song_count': len(self.songs)
        }


class Song(db.Model):
    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey(
        'authors.id'), nullable=False)

    # Lyrics in different languages
    hindi_lyrics = db.Column(db.Text)
    urdu_lyrics = db.Column(db.Text)
    english_lyrics = db.Column(db.Text)

    # Themes in different languages
    hindi_theme = db.Column(db.Text)
    urdu_theme = db.Column(db.Text)
    english_theme = db.Column(db.Text)

    # Relationships
    analyses = db.relationship(
        'LineAnalysis', backref='song', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Song {self.title}>'

    def get_lyrics_by_language(self, language):
        """Get lyrics by language code"""
        language_map = {
            'en': self.english_lyrics,
            'hin': self.hindi_lyrics,
            'urd': self.urdu_lyrics
        }
        return language_map.get(language)

    def get_theme_by_language(self, language):
        """Get theme by language code"""
        language_map = {
            'en': self.english_theme,
            'hin': self.hindi_theme,
            'urd': self.urdu_theme,
            'hi': self.hindi_theme,
            'ur': self.urdu_theme
        }
        return language_map.get(language)

    def set_theme_by_language(self, language, theme):
        """Set theme by language code"""
        if language == 'en':
            self.english_theme = theme
        elif language == 'hin':
            self.hindi_theme = theme
        elif language == 'urd':
            self.urdu_theme = theme
        else:
            raise ValueError(f"Invalid language code: {language}")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author.to_dict() if self.author else None,
            'hindi_lyrics': self.hindi_lyrics,
            'urdu_lyrics': self.urdu_lyrics,
            'english_lyrics': self.english_lyrics,
            'hindi_theme': self.hindi_theme,
            'urdu_theme': self.urdu_theme,
            'english_theme': self.english_theme
        }


class LineAnalysis(db.Model):
    __tablename__ = 'line_analyses'

    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    line_number = db.Column(db.Integer, nullable=False)
    language = db.Column(db.String(10), nullable=False)
    analysis = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<LineAnalysis {self.song_id}:{self.line_number}:{self.language}>'

    def to_dict(self):
        return {
            'id': self.id,
            'song_id': self.song_id,
            'line_number': self.line_number,
            'language': self.language,
            'analysis': self.analysis,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
