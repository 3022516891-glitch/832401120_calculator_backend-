import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response

from app.calculator import CalculationError, calculate
from app.database import get_connection, initialize_database
from app.history import add_record, clear_history, get_all_records, remove_record, set_favorite
from app.schemas import (
    CalculationRequest,
    CalculationResponse,
    FavoriteRequest,
    HistoryRecord,
    HistoryPage,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Calculator Backend API",
    description="前后端分离计算器的后端接口",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip().rstrip("/") for origin in os.environ.get(
        "FRONTEND_ORIGINS",
        "http://localhost:5500,http://127.0.0.1:5500,http://localhost:5173,http://127.0.0.1:5173",
    ).split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(HTTPException)
async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": str(exc.detail)},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, __: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"success": False, "message": "请求数据格式不正确"},
    )


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
def api_guide() -> HTMLResponse:
    page = Path(__file__).with_name("api_guide.html")
    return HTMLResponse(page.read_text(encoding="utf-8"))


@app.get("/api/health", summary="Health", tags=["System"])
def health_check() -> dict[str, str]:
    with get_connection() as connection:
        connection.execute("SELECT 1 FROM calculation_history LIMIT 1")
    return {"status": "ok", "database": "ok"}


@app.post(
    "/api/calculate",
    response_model=CalculationResponse,
    summary="Calculate",
    tags=["Calculator"],
)
def calculate_expression(payload: CalculationRequest) -> CalculationResponse:
    try:
        result = calculate(payload.expression, payload.angle_mode)
    except CalculationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    add_record(payload.expression, result, payload.angle_mode)
    return CalculationResponse(expression=payload.expression, result=result)


@app.get(
    "/api/history",
    response_model=HistoryPage | list[HistoryRecord],
    summary="History",
    tags=["History"],
)
def list_calculation_history(
    keyword: str | None = None, favorite_only: bool = False,
    page: int | None = Query(default=None, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
) -> list[dict] | dict:
    return get_all_records(keyword, favorite_only, page, page_size)


@app.delete("/api/history", summary="Clear All", tags=["History"])
def delete_all_history() -> dict:
    return {"success": True, "deleted_count": clear_history()}


@app.patch(
    "/api/history/{record_id}/favorite",
    response_model=HistoryRecord,
    summary="Favorite",
    tags=["History"],
)
def update_favorite(record_id: int, payload: FavoriteRequest) -> dict:
    record = set_favorite(record_id, payload.is_favorite)
    if record is None:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    return record


@app.delete(
    "/api/history/{record_id}",
    status_code=204,
    summary="Delete",
    tags=["History"],
)
def delete_calculation_history(record_id: int) -> Response:
    if not remove_record(record_id):
        raise HTTPException(status_code=404, detail="历史记录不存在")
    return Response(status_code=204)
