# Calculator Frontend

## Vercel Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions. Set the API base URL in `js/config.js`. Production must use the deployed backend's HTTPS URL rather than `127.0.0.1`. The backend stores production history in external PostgreSQL.

The expandable `Scientific` section is open by default. It supports squares, powers, square roots, reciprocals, log, ln, sin, cos, tan, π, and e. Functions can wrap an existing expression or be selected before entering a value. For example, select sin, enter 30, and press equals to obtain approximately 0.5. Trigonometric calculations use DEG (degrees).

## Project Information

- Assignment: First Individual Assignment — Calculator with Separate Frontend and Backend
- Student name: Qiu Yuqi
- Student ID: 832401120
- Project type: Web frontend
- Frontend repository: https://github.com/3022516891-glitch/832401120_calculator_frontend
- Backend repository: https://github.com/3022516891-glitch/832401120_calculator_backend-
- Backend URL: https://832401120-calculator-backend-vlaf.vercel.app/
- Live website: https://832401120calculatorfrontend.vercel.app/

## Introduction

This frontend uses plain HTML, CSS, and JavaScript to accept expressions, provide calculator buttons, send expressions to the backend, display results and errors, retrieve history, and request deletion of history records.

The backend handles validation, parsing, final calculation, and persistence. The frontend does not calculate final results independently.

## Technology Stack

- HTML5
- CSS3
- JavaScript
- Fetch API
- VS Code Live Server

No Vue, React, or npm dependencies are required.

## Project Structure

```text
front_project/
├── index.html
├── style.css
├── js/
│   ├── api.js
│   ├── config.js
│   └── app.js
├── DEPLOYMENT.md
├── README.md
└── codestyle.md
```

- `index.html`: Calculator and history page structure.
- `style.css`: Layout, colors, and interaction styles.
- `js/api.js`: Backend API requests.
- `js/config.js`: Backend API base URL.
- `js/app.js`: Button events, calculation requests, and page updates.
- `codestyle.md`: Coding conventions.

## Main Features

### 1. Basic Calculations

Supports addition, subtraction, multiplication, division, decimals, parentheses, unary plus and minus, compound expressions, squares, powers, and square roots. Exponents and results are subject to backend safety limits.

### 2. Calculation History

- Retrieve records from the backend database and display expressions, results, and timestamps.
- Search expressions, results, or notes.
- Add or remove favorites and filter favorites.
- Display favorites before other records.
- Copy results with one click.
- Add notes and display them directly in history.
- Select multiple records on the current page for batch deletion.
- Delete individual records or clear all history.
- Browse paginated history and reload it after deletion.

### 3. Error Messages

Displays errors for empty or invalid expressions, division by zero, backend connection failures, and failures to load or delete history.

## Frontend–Backend Communication

The backend's default local development address is `http://127.0.0.1:8000`.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/api/calculate` | Calculate an expression and save the record |
| GET | `/api/history` | Retrieve history |
| GET | `/api/history?page=1&page_size=10` | Retrieve paginated history |
| GET | `/api/history?keyword=...` | Search history |
| GET | `/api/history?favorite_only=true` | Retrieve favorites |
| PATCH | `/api/history/{id}/favorite` | Add or remove a favorite |
| PATCH | `/api/history/{id}/metadata` | Update a note |
| DELETE | `/api/history/batch` | Delete selected records |
| DELETE | `/api/history/{id}` | Delete one record |
| DELETE | `/api/history` | Clear all history |

Example request:

```json
{"expression": "(1+2)*3"}
```

Successful response:

```json
{"success": true, "expression": "(1+2)*3", "result": 9}
```

Update `js/config.js` if the backend deployment address changes.

## Runtime Environment

Recommended: Visual Studio Code, Chrome/Edge/Firefox, the VS Code Live Server extension, and a running backend service.

## Running Locally

### 1. Start the Backend

Follow the backend README to install dependencies and start the service. The default address is `http://127.0.0.1:8000`. Check its status at `http://127.0.0.1:8000/api/health`.

### 2. Start the Frontend

For a local backend, set the URL in `js/config.js` to `http://127.0.0.1:8000/api`. The current configuration points to production; starting a local backend does not switch the connection automatically. Production should use the backend's HTTPS URL with the trailing `/api`.

1. Open the project directory in Visual Studio Code.
2. Install Live Server.
3. Right-click `index.html`.
4. Select `Open with Live Server`.
5. Open the page in your browser.

Live Server usually serves the page at `http://127.0.0.1:5500`. No `npm install` is needed.

## Usage

1. Enter an expression using the calculator buttons.
2. Click equals.
3. The frontend sends the original expression to the backend.
4. The backend validates and calculates the expression.
5. The backend saves the successful calculation and returns the result.
6. The frontend displays the result and refreshes history.
7. Use the Delete button next to a record to delete it.

## Separation of Frontend and Backend

```text
User enters an expression
→ Frontend sends the original expression
→ Backend validates and parses it
→ Backend calculates the result
→ Backend saves the record
→ Backend returns the result
→ Frontend displays the result
```

When connected to a local backend, stopping that backend leaves the page and input buttons available but prevents new calculations. When connected to production, stopping the local service does not affect online calculations.

## Coding Conventions

See `codestyle.md` for coding conventions and reference sources.

## Notes

`x²` squares the current expression, `xʸ` inserts the power operator, and `√x` applies a square root. The backend performs all calculations.

History shows 10 records per page. Use `Previous` and `Next` to navigate. Searching or changing the favorites filter returns to page one. `Clear All` requires confirmation and deletes all records, including favorites.

- Use Live Server instead of opening `index.html` directly.
- Confirm that the backend is running.
- The frontend builds expressions and requests results; it does not use `eval()` to calculate them.
- History is shared by all visitors. Deletions affect others; do not store sensitive information.
- Verify the production API URL and backend CORS allowed origins after deployment.
