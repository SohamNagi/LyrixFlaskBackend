# Lyrix API Documentation

## Base URL
```
http://localhost:5000/api
```

## Endpoints

### 🎵 Songs

#### Get All Songs
```http
GET /api/songs?page={page}&per_page={per_page}
```
**Description:** Retrieve all songs in the database with pagination.

**Parameters:**
- `page` (query, optional): Page number (default: 1)
- `per_page` (query, optional): Items per page (default: 20, max: 100)

**Response:**
```json
{
  "songs": [
    {
      "id": 1,
      "title": "Song Title",
      "author": {
        "id": 1,
        "name": "Author Name"
      },
      "hindi_lyrics": "...",
      "urdu_lyrics": "...",
      "english_lyrics": "...",
      "hindi_theme": "...",
      "urdu_theme": "...",
      "english_theme": "..."
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1314,
    "pages": 66,
    "has_next": true,
    "has_prev": false
  }
}
```

#### Get Specific Song
```http
GET /api/songs/{song_id}
```
**Description:** Retrieve a specific song by ID.

**Parameters:**
- `song_id` (path): Integer ID of the song

**Response:** Single song object (same structure as above)

#### Get Song Theme
```http
GET /api/songs/{song_id}/theme?language={language}
```
**Description:** Get or generate theme analysis for a song.

**Parameters:**
- `song_id` (path): Integer ID of the song
- `language` (query): Language code (`en`, `hi`, `ur`)

**Response:** String containing the theme analysis

#### Get Line Transcription
```http
GET /api/songs/{song_id}/transcription?language={language}&linenum={line_number}
```
**Description:** Get or generate line-by-line analysis for a specific line in a song.

**Parameters:**
- `song_id` (path): Integer ID of the song
- `language` (query): Language code (`en`, `hi`, `ur`)
- `linenum` (query): Integer line number (0-indexed)

**Response:** String containing the line analysis

---

### 👨‍🎨 Authors

#### Get All Authors
```http
GET /api/authors?page={page}&per_page={per_page}
```
**Description:** Retrieve all authors in the database with pagination.

**Parameters:**
- `page` (query, optional): Page number (default: 1)
- `per_page` (query, optional): Items per page (default: 20, max: 100)

**Response:**
```json
{
  "authors": [
    {
      "id": 1,
      "name": "Author Name"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 30,
    "pages": 2,
    "has_next": true,
    "has_prev": false
  }
}
```

#### Get Specific Author
```http
GET /api/authors/{author_id}
```
**Description:** Retrieve a specific author by ID.

**Parameters:**
- `author_id` (path): Integer ID of the author

**Response:** Single author object

#### Get Songs by Author
```http
GET /api/authors/{author_id}/songs?page={page}&per_page={per_page}
```
**Description:** Retrieve all songs by a specific author with pagination.

**Parameters:**
- `author_id` (path): Integer ID of the author
- `page` (query, optional): Page number (default: 1)
- `per_page` (query, optional): Items per page (default: 20, max: 100)

**Response:**
```json
{
  "author": {
    "id": 1,
    "name": "Author Name"
  },
  "songs": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 50,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

---

### 🔍 Search

#### General Search
```http
GET /api/search?q={query}
```
**Description:** Search across songs and authors.

**Parameters:**
- `q` (query): Search query string

**Response:**
```json
{
  "query": "search term",
  "songs": [...],
  "authors": [...]
}
```

#### Search Songs
```http
GET /api/search/songs?q={query}&author_id={author_id}&page={page}&per_page={per_page}
```
**Description:** Search specifically for songs with advanced filtering.

**Parameters:**
- `q` (query): Search query string
- `author_id` (query, optional): Filter by specific author ID
- `page` (query, optional): Page number (default: 1)
- `per_page` (query, optional): Items per page (default: 20, max: 100)

**Response:**
```json
{
  "query": "search term",
  "songs": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 15,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

---

### 📊 Statistics

#### Get Database Stats
```http
GET /api/stats
```
**Description:** Get overall database statistics.

**Response:**
```json
{
  "total_authors": 30,
  "total_songs": 1314,
  "total_analyses": 25,
  "authors_with_songs": 30
}
```

---

### 🏥 Health Check

#### Health Check
```http
GET /health
```
**Description:** Check if the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

---

## Language Codes

| Code | Language |
|------|----------|
| `en` | English (Romanized) |
| `hi` | Hindi (Devanagari) |
| `ur` | Urdu |

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message description"
}
```

Common HTTP status codes:
- `400` - Bad Request (missing or invalid parameters)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

---

## Notes

1. **Caching:** Themes and transcriptions are cached in the database after first generation
2. **Pagination:** Search and author song endpoints support pagination
3. **Languages:** All songs support three languages (English, Hindi, Urdu)
4. **GPT Integration:** Theme and transcription endpoints use GPT for analysis generation
5. **CORS:** API supports cross-origin requests from localhost and lyrix.app domains

---

## Example Usage

### Get first page of songs (20 per page)
```bash
curl "http://localhost:5000/api/songs"
```

### Get second page of songs with 10 per page
```bash
curl "http://localhost:5000/api/songs?page=2&per_page=10"
```

### Get all authors with pagination
```bash
curl "http://localhost:5000/api/authors?page=1&per_page=15"
```

### Get all songs by Mirza Ghalib
```bash
# First, find Ghalib's author ID
curl "http://localhost:5000/api/search?q=Mirza Ghalib"

# Then get his songs (assuming author_id = 3)
curl "http://localhost:5000/api/authors/3/songs"
```

### Get theme analysis for a song
```bash
curl "http://localhost:5000/api/songs/1/theme?language=en"
```

### Get line analysis for specific line
```bash
curl "http://localhost:5000/api/songs/1/transcription?language=hi&linenum=0"
```
