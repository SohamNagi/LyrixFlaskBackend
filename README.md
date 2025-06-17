# Lyrix Flask Backend

A simple Flask backend that replaces the Spring Boot application for lyrics analysis.

## Features

- RESTful API for song lyrics analysis
- GPT-powered line-by-line transcription
- Theme generation for songs
- SQLite database for simplicity
- Support for multiple languages (English, Hindi, Urdu)

## Setup

1. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

2. Set up environment variables:

    ```bash
    export LYRIXOPENAIKEY="your-openai-api-key"
    ```

3. Run the application:

    ```bash
    python app.py
    ```

## API Endpoints

### Get Line Transcription

```sh
GET /api/songs/{id}/transcription?language=en&linenum=0
```

### Get Song Theme

```sh
GET /api/songs/{id}/theme?language=en
```

### Get All Songs

```sh
GET /api/songs
```

### Get Specific Song

```sh
GET /api/songs/{id}
```

### Get All Authors

```sh
GET /api/authors
```

### Health Check

```sh
GET /health
```

## Database

The application uses SQLite database (`lyrix.db`) with the following tables:

- `authors` - Song authors/artists
- `songs` - Song information with lyrics in multiple languages
- `line_analyses` - Cached GPT analyses for song lines

## Environment Variables

- `LYRIXOPENAIKEY` - OpenAI API key for GPT services

## Language Codes

- `en` - English
- `hin` - Hindi
- `urd` - Urdu
