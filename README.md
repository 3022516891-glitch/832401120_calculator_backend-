# Calculator Backend

Scientific calculations support `sqrt`, `log` (base 10), `ln`, `sin`, `cos`, and `tan`; constants `pi` (or π) and `e`; powers; and reciprocals. Requests may specify `angle_mode` as `DEG` or `RAD`, with DEG as the default. History stores the angle mode. For example, `{"expression":"sin(30)","angle_mode":"DEG"}` returns approximately 0.5. Negative square roots, logarithms of nonpositive values, undefined tangents, and division by zero produce explicit errors.

## Project Information

- Assignment: First Individual Assignment — Calculator with Separate Frontend and Backend
- Student name: Qiu Yuqi
- Student ID: 832401120
- Backend repository: https://github.com/3022516891-glitch/832401120_calculator_backend-
- Frontend repository: https://github.com/3022516891-glitch/832401120_calculator_frontend
- Frontend URL: https://832401120calculatorfrontend.vercel.app/
- Backend URL: https://832401120-calculator-backend-vlaf.vercel.app/

## Introduction

The frontend sends the user's original expression to this backend, which validates, parses, and calculates it, then saves successful calculations to a database. Local development uses SQLite by default; setting `DATABASE_URL` enables external PostgreSQL. User input is not executed with `eval()` or `exec()`. Additional features include history search, favorites displayed first, notes, and batch deletion.

## Production Deployment

The frontend and backend are separate Vercel projects. Production history persists in external PostgreSQL. See [DEPLOYMENT.md](DEPLOYMENT.md) for configuration, connection, and verification instructions.

## Technology Stack

- Python 3.13
- FastAPI
- SQLite (local) / PostgreSQL (production)
- Pytest

Local SQLite requires no separate database service. Production uses PostgreSQL for history storage. FastAPI handles request validation and responses. `/docs` provides a custom backend interaction page.

## Project Structure

```text
back_project/
├── app/
│   ├── calculator.py  # Expression parsing and calculation
│   ├── database.py    # Database connections and initialization
│   ├── history.py     # History creation, retrieval, and deletion
│   ├── main.py        # FastAPI application and endpoints
│   ├── schemas.py     # Request and response models
│   └── api_guide.html # Backend interaction page
├── tests/            # Calculation, history, and deployment tests
├── index.py          # Vercel application entry point
├── .python-version   # Python version
├── .env.example      # Example variables without real passwords
├── .gitignore
├── .vercelignore
├── requirements.txt
├── DEPLOYMENT.md
├── README.md
└── codestyle.md
```

## Installation and Startup

For local Windows development, install Python 3.13 and enter the backend directory containing `requirements.txt`. Replace the example path with your actual location after cloning.

```powershell
cd "D:\Download_D\软工_个人作业1\back_project"
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

These commands use the virtual environment's Python directly, without activation, and work in PowerShell and CMD. In CMD, use `cd /d "D:\Download_D\软工_个人作业1\back_project"` when switching drives. Skip creation if a working `.venv` exists. The server runs continuously and does not open a browser automatically. Press Ctrl+C to stop it.

After startup, visit:

- Health check: `http://127.0.0.1:8000/api/health`
- Backend interaction page: `http://127.0.0.1:8000/docs`

`/docs` provides calculation, history retrieval, search, favorites, and deletion. It calls backend APIs over HTTP; the backend performs calculations and saves data.

Without `DATABASE_URL`, the first local startup creates `data/calculator.db`. With `DATABASE_URL`, the application connects to PostgreSQL and initializes the history table. Local and production records are separate and are not migrated automatically. `.env.example` demonstrates the format only; the application does not automatically load `.env` files. Set production credentials in Vercel environment variables, not in the repository.

## API Reference

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Check the service and database connection |
| POST | `/api/calculate` | Calculate and save a record |
| GET | `/api/history` | Retrieve history |
| GET | `/api/history?page=1&page_size=10` | Retrieve paginated history |
| GET | `/api/history?keyword=1%2B2` | Search expressions, results, or notes |
| GET | `/api/history?favorite_only=true` | Retrieve favorites only |
| PATCH | `/api/history/{id}/favorite` | Add or remove a favorite |
| PATCH | `/api/history/{id}/metadata` | Update a note |
| DELETE | `/api/history/batch` | Delete specified records in a batch |
| DELETE | `/api/history/{id}` | Delete one record |
| DELETE | `/api/history` | Delete all history |

Example request: `{"expression": "(1+2)*3"}`

Successful response: `{"success": true, "expression": "(1+2)*3", "result": 9}`

Example error response (original API message preserved): `{"success": false, "message": "除数不能为零"}`. The message means that the divisor cannot be zero.

## Connecting the Frontend and Backend

The backend runs locally at `http://127.0.0.1:8000` by default. Configure the frontend API URL in `js/config.js`. Live Server usually serves the frontend at `http://127.0.0.1:5500`, which is included in the backend's CORS allowed origins.

For local integration, set the frontend API URL to `http://127.0.0.1:8000/api`, start the backend, and open the frontend with Live Server. Production uses the backend's HTTPS URL and the frontend origin configured in `FRONTEND_ORIGINS`. Redeploy after changing environment variables. Origins must not contain `/api` or other paths.

## Scientific Calculations and History Pagination

The API supports `3^2` (square), `2^3` (power), and `sqrt(9)` (square root), combined with basic arithmetic. Exponentiation is right-associative. `-2^2` is -4; `(-2)^2` is 4. Only `sqrt`, `log`, `ln`, `sin`, `cos`, and `tan` are allowed as functions; arbitrary code is not executed. Negative square roots, zero raised to a negative power, exponents with an absolute value greater than 1000, and excessively large results produce errors.

`GET /api/history?page=1&page_size=10` returns `items`, `total`, `page`, and `page_size`. Combine it with `keyword` and `favorite_only` as needed. Omitting `page` returns an array of records.

`DELETE /api/history` deletes all records, including favorites, and returns `success` and `deleted_count`. The frontend requests confirmation. Deletion cannot be undone through the application.

Favorites appear before ordinary records, with the newest records first within each group. Notes support up to 200 characters. Keyword searches match expressions, results, and notes. `DELETE /api/history/batch` accepts `{"ids":[1,2,3]}` and supports up to 100 records per request.

## Tests

After installing dependencies, run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Tests cover precedence, parentheses, decimals, negative numbers, division by zero, invalid expressions, scientific calculations, pagination, favorites, notes, batch deletion, and deployment configuration.

Unit tests use temporary SQLite databases or mocked PostgreSQL connections. They do not access production data and do not replace real production persistence checks.

For production verification, calculate `(1+2)*3`, confirm the result is 9, and check history. Refresh the page and redeploy the backend to verify persistence. Use `1/0` for error handling. Test deletion only with records created for testing.

## Limitations

There is no login or user isolation; history is shared by all visitors. Clearing history includes favorites and cannot be undone through the application. This project is an assignment demonstration and should not store sensitive information. Do not publish database passwords or two-factor authentication secrets to GitHub or a blog.
