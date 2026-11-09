# Conversor de monedas

Conversor con front (HTML + CSS + JavaScript vanilla, servido por nginx) y back (Python + Flask + gunicorn) en contenedores Docker separados.

Pares soportados: **COP→USD, USD→EUR, EUR→COP, USD→COP**. Cualquier otro par devuelve error 400.

> Las tasas de [api/config.py](api/config.py) son valores de **ejemplo**, editables. No son tasas reales.

## Arquitectura

```
Navegador ──► frontend (nginx :80, publicado en 8080)
                 ├─ /        → archivos estáticos
                 └─ /api/*   → proxy_pass http://api:5000/
                                   │
                              api (gunicorn :5000, solo red interna)
```

El front llama siempre a rutas relativas `/api/...`; nunca a `localhost:5000`.

## Ejecución

```bash
docker compose up --build
```

Abre <http://localhost:8080> y prueba los 4 pares. Para detener: `docker compose down`.

## Pruebas (pytest)

Local, con entorno virtual:

```bash
cd api
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt pytest
pytest -v
```

O dentro del contenedor:

```bash
docker compose run --rm --user root api sh -c "pip install -q pytest && pytest -v"
```

## API

Todas las respuestas usan el mismo formato:

```json
{
  "type": "success|warning|error",
  "code": "CONVERSION_OK",
  "message": "texto legible",
  "data": {}
}
```

| Endpoint                               | Descripción                             |
| -------------------------------------- | --------------------------------------- |
| `GET /health`                          | `{"status":"ok"}`                       |
| `GET /rates`                           | Pares disponibles (`data.pairs`)        |
| `GET /convert?de=USD&a=COP&valor=10.5` | `data: {de, a, valor, tasa, resultado}` |

Códigos: `CONVERSION_OK`, `RATES_OK`, `ZERO_VALUE` (warning), `INVALID_NUMBER`, `NEGATIVE_VALUE`, `VALUE_TOO_LARGE`, `UNSUPPORTED_PAIR`, `MISSING_PARAMS` (errores 400) e `INTERNAL_ERROR` (500).

Todo el cálculo usa `decimal.Decimal` con `ROUND_HALF_UP`: COP sin decimales, USD y EUR con 2.

## Verificar la comunicación entre contenedores

```bash
# 1. Ambos servicios arriba y la API "healthy"
docker compose ps

# 2. La API NO está publicada al host (debe fallar la conexión)
curl -s --max-time 3 http://localhost:5000/health || echo "puerto 5000 no expuesto (correcto)"

# 3. El front llega a la API por el proxy de nginx (desde el host)
curl http://localhost:8080/api/health
curl http://localhost:8080/api/rates
curl "http://localhost:8080/api/convert?de=USD&a=COP&valor=10.5"

# 4. Desde dentro del contenedor frontend, resolviendo el nombre `api`
docker compose exec frontend getent hosts api
docker compose exec frontend wget -qO- http://api:5000/health

# 5. Casos de error y advertencia
curl "http://localhost:8080/api/convert?de=COP&a=EUR&valor=10"   # UNSUPPORTED_PAIR (400)
curl "http://localhost:8080/api/convert?de=USD&a=COP&valor=0"    # ZERO_VALUE (warning)

# 6. Red compartida y logs
docker network ls
docker network inspect "$(basename "$PWD")_default" --format '{{range .Containers}}{{.Name}} {{end}}'
docker compose logs frontend api
```
