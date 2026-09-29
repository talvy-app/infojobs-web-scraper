# infojobs-web-scraper

Demo público de cómo hacer scraping del buscador web de InfoJobs.

## Endpoint

```
GET https://www.infojobs.net/webapp/offers/search?keyword={kw}&page={n}
```

| Parámetro | Valor |
|---|---|
| `keyword` | Término de búsqueda, p. ej. `developer`, `data engineer`. Vacío = todas las ofertas |
| `page` | Número de página, 22 ofertas por página. El rango lo da `navigation.totalPages` de la respuesta |

Cabeceras:

| Header | Obligatorio |
|---|---|
| `User-Agent` de navegador | Sí — con UA de script responde `456` |
| `Accept: application/json` | Sí |
| `X-Schibsted-Tenant: infojobs`, `X-Adevinta-Channel: web`, `Portalid: 0` | No (los manda la web; los incluimos por fidelidad) |

Sin autenticación. Ojo: el parámetro es `keyword`, **no** `q` (con `q=` el endpoint responde 200 pero ignora el término y devuelve el listado completo).

### Respuesta (200)

Raíz con varias claves; las relevantes:

```json
{
  "offers": [
    {
      "code": "875a42e51f4c10ba58b91b6d60e06a",
      "title": "Técnico/a de Gestión de Personal",
      "description": "En DomusVi, cuidar es ...",
      "link": "https://www.infojobs.net/oferta/...",
      "companyLink": "https://www.infojobs.net/empresa/...",
      "companyName": "DomusVi",
      "companyLogo": "https://...png",
      "city": "Madrid",
      "contractType": "Contrato indefinido",
      "workday": "Jornada completa",
      "teleworking": "Presencial",
      "publishedAt": "2026-09-30T10:00:00+02:00",
      "executive": false,
      "states": []
    }
  ],
  "navigation": { "self": 1, "next": 2, "totalPages": 3186, "totalElements": 63716, "sortedBy": "PUBLICATION_DATE" },
  "aggregation": { "province": [...], "category": [...], "contractType": [...] },
  "search": { "keyword": { "value": "developer" }, "...": "..." }
}
```

Notas:

- Todo viene en el listado: el `code` de la oferta es su ID; no hay llamada de detalle adicional (el contenido completo de la descripción ya viene en `description`).
- Fin de paginación: `page > navigation.totalPages` devuelve `offers: []` (sin 404).
- `aggregation` trae facets con conteos (provincia, categoría, tipo de contrato...) útiles para filtrar.
- El scraper original usa timeout de 30s y 3 reintentos.

## Uso

```bash
# printear a stdout
python3 scraper.py developer

# varias keywords, página concreta
python3 scraper.py developer "data engineer" --page 2

# escribir a JSON
python3 scraper.py developer --output jobs.json
```

Salida: objeto JSON `{ "<keyword>": [offers...] }`. Progreso y avisos van a stderr.

---

## English

Public demo of how to scrape the InfoJobs web search endpoint.

## Endpoint

```
GET https://www.infojobs.net/webapp/offers/search?keyword={kw}&page={n}
```

| Param | Value |
|---|---|
| `keyword` | Search term, e.g. `developer`, `data engineer`. Empty = all offers |
| `page` | Page number, 22 offers per page. Range given by `navigation.totalPages` in the response |

Headers:

| Header | Required |
|---|---|
| Browser `User-Agent` | Yes — script UAs get `456` |
| `Accept: application/json` | Yes |
| `X-Schibsted-Tenant: infojobs`, `X-Adevinta-Channel: web`, `Portalid: 0` | No (sent by the web app; included for fidelity) |

No auth. Note: the param is `keyword`, **not** `q` (with `q=` the endpoint answers 200 but ignores the term and returns the full listing).

### Response (200)

Root has several keys; the relevant ones:

See the JSON example above (same shape). Key points:

- Everything comes in the listing: the offer's `code` is its ID; no extra detail call needed (the full description is already in `description`).
- End of pagination: `page > navigation.totalPages` returns `offers: []` (no 404).
- `aggregation` carries facets with counts (province, category, contract type...) useful for filtering.
- The original scraper uses a 30s timeout and 3 retries.

## Usage

```bash
# print to stdout
python3 scraper.py developer

# multiple keywords, specific page
python3 scraper.py developer "data engineer" --page 2

# write to JSON
python3 scraper.py developer --output jobs.json
```

Output: JSON object `{ "<keyword>": [offers...] }`. Progress and warnings go to stderr.
