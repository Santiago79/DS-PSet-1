Acción----Comando

Levantar todo----docker compose up --build
Bajar servicios----docker compose down
Correr Tests----docker compose exec api env PYTHONPATH=. pytest
Ver Logs----docker compose logs -f