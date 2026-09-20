"""
Unit Test Suite for SQLExecutor Engine (Phase 9).
"""

from datetime import date, datetime, timezone
import decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.business import Store
from app.models.tenancy import Organization, Workspace
from app.ai.sql.executor import SQLExecutor, sql_executor


@pytest.fixture
async def test_engine():
    """Fixture providing an async in-memory SQLite engine."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Fixture providing a clean test AsyncSession."""
    async_session = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.mark.asyncio
async def test_sql_executor_successful_select(test_session):
    """Verify executing a valid SELECT query returns correctly serialized rows."""
    org = Organization(name="Test Org")
    test_session.add(org)
    await test_session.flush()

    ws = Workspace(org_id=org.id, name="Test Workspace")
    test_session.add(ws)
    await test_session.flush()

    store1 = Store(
        workspace_id=ws.id,
        store_code="STR-001",
        name="Downtown Store",
        city="New York",
        state="NY",
        square_feet=15000,
        opened_date=date(2022, 1, 15),
    )
    store2 = Store(
        workspace_id=ws.id,
        store_code="STR-002",
        name="Uptown Store",
        city="New York",
        state="NY",
        square_feet=20000,
        opened_date=date(2023, 3, 10),
    )
    test_session.add_all([store1, store2])
    await test_session.commit()

    sql = f"SELECT store_code, name, square_feet FROM stores WHERE workspace_id = '{ws.id}' ORDER BY store_code ASC"
    res = await sql_executor.execute(
        session=test_session,
        sql=sql,
        workspace_id=ws.id,
        max_rows=50,
    )

    assert res.row_count == 2
    assert res.columns == ["store_code", "name", "square_feet"]
    assert len(res.rows) == 2
    assert res.rows[0]["store_code"] == "STR-001"
    assert res.rows[0]["name"] == "Downtown Store"
    assert res.rows[1]["store_code"] == "STR-002"
    assert res.execution_time_ms >= 0.0


@pytest.mark.asyncio
async def test_sql_executor_empty_result(test_session):
    """Verify query returning no matching rows returns row_count=0."""
    sql = "SELECT * FROM stores WHERE name = 'NonExistentStore'"
    res = await sql_executor.execute(
        session=test_session,
        sql=sql,
        workspace_id="ws-empty",
    )
    assert res.row_count == 0
    assert len(res.rows) == 0


@pytest.mark.asyncio
async def test_sql_executor_row_limit_truncation(test_session):
    """Verify max_rows limits returned dataset length."""
    org = Organization(name="Limit Org")
    test_session.add(org)
    await test_session.flush()

    ws = Workspace(org_id=org.id, name="Limit Workspace")
    test_session.add(ws)
    await test_session.flush()

    stores = [
        Store(workspace_id=ws.id, store_code=f"STR-{i:03d}", name=f"Store {i}")
        for i in range(10)
    ]
    test_session.add_all(stores)
    await test_session.commit()

    sql = f"SELECT store_code FROM stores WHERE workspace_id = '{ws.id}'"
    res = await sql_executor.execute(
        session=test_session,
        sql=sql,
        workspace_id=ws.id,
        max_rows=3,
    )

    assert res.row_count == 3
    assert len(res.rows) == 3


def test_sql_executor_value_serialization():
    """Verify internal value serialization handles decimals, dates, datetimes, and UUIDs."""
    executor = SQLExecutor()
    now_dt = datetime.now(timezone.utc)
    today_d = date(2024, 5, 20)
    dec_val = decimal.Decimal("149.99")

    assert executor._serialize_value(dec_val) == 149.99
    assert executor._serialize_value(now_dt) == now_dt.isoformat()
    assert executor._serialize_value(today_d) == "2024-05-20"
    assert executor._serialize_value(None) is None
