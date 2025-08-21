# py-rag-chatbot

1) Copy .env.example to .env and set OPENAI_API_KEY.
2) Put your CSV at data/books.csv with headers: Title, Authors, Description, Category.
3) Start Chroma:
   docker compose up -d chroma

4) Ingest once:
   docker compose run --rm app python ingest.py --csv /app/data/books.csv --collection books

5) Verify count:
   docker compose run --rm app python -c "from db.chroma_client import get_or_create_collection; c=get_or_create_collection('books'); print('count=', c.count())"

Notes:
- Chroma server data persists in ./chroma-data volume.
- The app container has CHROMA_HOST=chroma and CHROMA_PORT=8000 for in-network access.
- For queries later, use the same HttpClient and collection name, and call .query() with either embeddings you compute for the incoming query text or let Chroma do server-side embedding once you add a server-side embedding function. Since we precomputed embeddings on add(), you can pass query_embeddings for exact control.
