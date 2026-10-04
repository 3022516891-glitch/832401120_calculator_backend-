import pytest


@pytest.fixture(autouse=True)
def isolate_local_database(monkeypatch):
    # 单元测试不能连接线上数据库，尤其是包含全部删除操作的测试。
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("VERCEL", raising=False)
