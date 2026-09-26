from datetime import date, datetime, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.database import Base
from app.models import (
    Category,
    Customer,
    Document,
    Employee,
    OperatingExpense,
    Organization,
    Product,
    Query,
    Report,
    SalesItem,
    SalesTransaction,
    Store,
    User,
    Workspace,
    WorkspaceMember,
)
from app.repositories.base import BaseRepository


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
async def test_database_table_creation(test_engine):
    """Verify that all ORM tables are registered in Base metadata."""
    tables = Base.metadata.tables.keys()
    assert "organizations" in tables
    assert "workspaces" in tables
    assert "users" in tables
    assert "stores" in tables
    assert "products" in tables
    assert "sales_transactions" in tables
    assert "sales_items" in tables
    assert "operating_expenses" in tables
    assert "documents" in tables
    assert "queries" in tables
    assert "reports" in tables


@pytest.mark.asyncio
async def test_multi_tenancy_hierarchy(test_session):
    """Test creating Organization -> Workspace -> Member hierarchy."""
    org_repo = BaseRepository(Organization, test_session)
    ws_repo = BaseRepository(Workspace, test_session)

    # 1. Create Organization
    org = Organization(name="NovaMart Retail Corp")
    saved_org = await org_repo.create(org)
    assert saved_org.id is not None
    assert saved_org.name == "NovaMart Retail Corp"

    # 2. Create Workspace under Organization
    ws = Workspace(org_id=saved_org.id, name="Main Production Workspace")
    saved_ws = await ws_repo.create(ws)
    assert saved_ws.id is not None
    assert saved_ws.org_id == saved_org.id


@pytest.mark.asyncio
async def test_novamart_business_domain_models(test_session):
    """Test inserting and querying NovaMart domain entity records."""
    org = Organization(name="NovaMart Enterprise")
    test_session.add(org)
    await test_session.flush()

    ws = Workspace(org_id=org.id, name="NovaMart HQ Workspace")
    test_session.add(ws)
    await test_session.flush()

    # Create Store
    store = Store(
        workspace_id=ws.id,
        store_code="STR-001",
        name="NovaMart Downtown Store",
        city="New York",
        state="NY",
        square_feet=25000,
        opened_date=date(2021, 5, 15),
    )
    test_session.add(store)

    # Create Category & Product
    category = Category(
        workspace_id=ws.id,
        name="Electronics",
        description="Consumer tech & gadgets",
    )
    test_session.add(category)
    await test_session.flush()

    product = Product(
        workspace_id=ws.id,
        category_id=category.id,
        sku="SKU-ELEC-001",
        name="Wireless Noise-Canceling Headphones",
        unit_cost=75.00,
        unit_price=149.99,
        reorder_level=15,
    )
    test_session.add(product)
    await test_session.flush()

    # Create Customer & Employee
    customer = Customer(
        workspace_id=ws.id,
        customer_code="CUST-1001",
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.com",
        city="New York",
        state="NY",
        signup_date=date(2023, 1, 10),
    )
    employee = Employee(
        workspace_id=ws.id,
        store_id=store.id,
        first_name="John",
        last_name="Smith",
        role="Store Manager",
        salary=65000.00,
        hired_date=date(2021, 6, 1),
    )
    test_session.add_all([customer, employee])
    await test_session.flush()

    # Create Sales Transaction & Item
    now_utc = datetime.now(timezone.utc)
    tx = SalesTransaction(
        workspace_id=ws.id,
        store_id=store.id,
        customer_id=customer.id,
        employee_id=employee.id,
        transaction_date=now_utc,
        subtotal=149.99,
        tax_amount=12.00,
        discount_amount=0.00,
        total_amount=161.99,
        payment_method="Credit Card",
    )
    test_session.add(tx)
    await test_session.flush()

    item = SalesItem(
        workspace_id=ws.id,
        transaction_id=tx.id,
        product_id=product.id,
        quantity=1,
        unit_price=149.99,
        cost_price=75.00,
        total_price=149.99,
    )
    test_session.add(item)

    # Create Operating Expense
    expense = OperatingExpense(
        workspace_id=ws.id,
        store_id=store.id,
        expense_date=date(2023, 6, 1),
        category="Utilities",
        amount=1250.00,
        description="Electricity bill Q2",
    )
    test_session.add(expense)
    await test_session.commit()

    # Query & Verify
    store_repo = BaseRepository(Store, test_session)
    fetched_store = await store_repo.get_by_id(store.id)
    assert fetched_store is not None
    assert fetched_store.name == "NovaMart Downtown Store"
    assert fetched_store.store_code == "STR-001"

    prod_repo = BaseRepository(Product, test_session)
    fetched_prod = await prod_repo.get_by_id(product.id)
    assert fetched_prod is not None
    assert fetched_prod.unit_price == 149.99


@pytest.mark.asyncio
async def test_system_metadata_and_reports(test_session):
    """Test System Metadata ORM models (Documents, Queries, Reports)."""
    org = Organization(name="Meta Org")
    test_session.add(org)
    await test_session.flush()

    ws = Workspace(org_id=org.id, name="Meta Workspace")
    test_session.add(ws)
    await test_session.flush()

    user = User(email="meta_user@example.com", full_name="Meta User")
    test_session.add(user)
    await test_session.flush()

    # Create Document
    doc = Document(
        workspace_id=ws.id,
        uploaded_by=user.id,
        storage_path="docs/q2_report.pdf",
        file_name="Q2_Financial_Report.pdf",
        original_filename="Q2_Financial_Report.pdf",
        file_type="pdf",
        mime_type="application/pdf",
        file_size=1048576,
        status="processed",
    )
    test_session.add(doc)

    # Create Query & Report
    query = Query(
        workspace_id=ws.id,
        natural_query="Why did Q2 profit drop?",
        status="completed",
        execution_time_ms=1250,
    )
    test_session.add(query)
    await test_session.flush()

    report = Report(
        workspace_id=ws.id,
        query_id=query.id,
        title="Q2 Financial Analysis Report",
        content_markdown="# Q2 Report\nOperating expenses increased...",
        viz_config_json={"chart_type": "bar"},
    )
    test_session.add(report)
    await test_session.commit()

    doc_repo = BaseRepository(Document, test_session)
    fetched_doc = await doc_repo.get_by_id(doc.id)
    assert fetched_doc is not None
    assert fetched_doc.filename == "Q2_Financial_Report.pdf"

    report_repo = BaseRepository(Report, test_session)
    fetched_report = await report_repo.get_by_id(report.id)
    assert fetched_report is not None
    assert fetched_report.title == "Q2 Financial Analysis Report"


@pytest.mark.asyncio
async def test_seed_record_datetime_parsing(test_session):
    """Verify that seed record string date/datetime fields are converted to native Python types."""
    import sys
    from pathlib import Path
    project_root = Path(__file__).resolve().parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from data.scripts.seed_database import parse_record_fields
    import pandas as pd
    from sqlalchemy import text

    raw_record = {
        "id": "00000000-0000-4000-a000-000000000001",
        "name": "Test Org",
        "created_at": "2023-01-01 00:00:00+00",
        "opened_date": "2021-03-15",
        "hired_date": "2022-06-01",
        "signup_date": "2023-11-20",
        "expense_date": "2023-10-01",
        "last_updated": "2023-10-01 10:00:00+00",
        "transaction_date": "2023-10-01 00:01:41+00",
        "null_val": float("nan"),
    }

    parsed = parse_record_fields(raw_record.copy())

    assert isinstance(parsed["created_at"], datetime)
    assert isinstance(parsed["transaction_date"], datetime)
    assert isinstance(parsed["last_updated"], datetime)

    assert isinstance(parsed["opened_date"], date)
    assert not isinstance(parsed["opened_date"], datetime)
    assert isinstance(parsed["hired_date"], date)
    assert isinstance(parsed["signup_date"], date)
    assert isinstance(parsed["expense_date"], date)

    assert parsed["null_val"] is None

    # Verify executing parameterized SQL insert with parsed record in DB session
    org_record = {
        "id": "11111111-1111-4000-a000-111111111111",
        "name": "Parsed Seed Org",
        "created_at": parsed["created_at"],
    }
    await test_session.execute(
        text("INSERT INTO organizations (id, name, created_at) VALUES (:id, :name, :created_at)"),
        [org_record],
    )
    await test_session.commit()

    res = await test_session.execute(
        text("SELECT id, name, created_at FROM organizations WHERE id = '11111111-1111-4000-a000-111111111111'")
    )
    row = res.fetchone()
    assert row is not None
    assert row[1] == "Parsed Seed Org"


@pytest.mark.asyncio
async def test_workspace_member_model_and_seed_mapping(test_session):
    """Verify WorkspaceMember model maps joined_at and seed record parsing handles joined_at."""
    import sys
    from pathlib import Path
    project_root = Path(__file__).resolve().parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from data.scripts.seed_database import parse_record_fields
    import pandas as pd
    from sqlalchemy import text

    # 1. Test model attributes
    assert hasattr(WorkspaceMember, "joined_at")
    assert not hasattr(WorkspaceMember, "created_at")

    # 2. Test seed record field parsing for workspace_members CSV format
    raw_member = {
        "id": "91efe263-c18e-4cb0-9feb-217f76a4fd27",
        "workspace_id": "00000000-0000-4000-a000-000000000002",
        "user_id": "00000000-0000-4000-a000-000000000003",
        "role": "ADMIN",
        "joined_at": "2023-01-01 00:00:00+00",
    }
    parsed = parse_record_fields(raw_member.copy())
    assert isinstance(parsed["joined_at"], datetime)

    # 3. Test ORM persistence
    org = Organization(id="00000000-0000-4000-a000-000000000001", name="Test Org")
    ws = Workspace(id="00000000-0000-4000-a000-000000000002", org_id=org.id, name="Test WS")
    user = User(id="00000000-0000-4000-a000-000000000003", email="test@example.com", full_name="Test User")
    test_session.add_all([org, ws, user])
    await test_session.flush()

    member = WorkspaceMember(
        id=parsed["id"],
        workspace_id=parsed["workspace_id"],
        user_id=parsed["user_id"],
        role=parsed["role"],
        joined_at=parsed["joined_at"],
    )
    test_session.add(member)
    await test_session.commit()

    fetched = await test_session.get(WorkspaceMember, parsed["id"])
    assert fetched is not None
    assert fetched.role == "ADMIN"
    assert isinstance(fetched.joined_at, datetime)


@pytest.mark.asyncio
async def test_cleanup_delete_query_predicate(test_session):
    """Verify that get_cleanup_delete_query uses 'id' predicate for workspaces and 'workspace_id' for child tables."""
    import sys
    from pathlib import Path
    project_root = Path(__file__).resolve().parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from data.scripts.seed_database import get_cleanup_delete_query
    from sqlalchemy import text

    ws_id = "00000000-0000-4000-a000-000000000002"

    # 1. Verify query strings generated
    ws_query = get_cleanup_delete_query("workspaces", ws_id)
    assert ws_query == f"DELETE FROM workspaces WHERE id = '{ws_id}'"

    store_query = get_cleanup_delete_query("stores", ws_id)
    assert store_query == f"DELETE FROM stores WHERE workspace_id = '{ws_id}'"

    sales_query = get_cleanup_delete_query("sales_transactions", ws_id)
    assert sales_query == f"DELETE FROM sales_transactions WHERE workspace_id = '{ws_id}'"

    # 2. Verify executing queries on DB session
    org = Organization(id="00000000-0000-4000-a000-000000000001", name="Cleanup Test Org")
    ws = Workspace(id=ws_id, org_id=org.id, name="Cleanup Test WS")
    store = Store(id="00000000-0000-4000-a000-000000000005", workspace_id=ws_id, store_code="STR-TEST", name="Test Store")
    test_session.add_all([org, ws, store])
    await test_session.commit()

    # Delete store child record first, then workspace
    await test_session.execute(text(get_cleanup_delete_query("stores", ws_id)))
    await test_session.execute(text(get_cleanup_delete_query("workspaces", ws_id)))
    await test_session.commit()

    # Confirm workspace and store are deleted in database
    ws_cnt = (await test_session.execute(text(f"SELECT COUNT(*) FROM workspaces WHERE id = '{ws_id}'"))).scalar()
    store_cnt = (await test_session.execute(text(f"SELECT COUNT(*) FROM stores WHERE workspace_id = '{ws_id}'"))).scalar()
    assert ws_cnt == 0
    assert store_cnt == 0


@pytest.mark.asyncio
async def test_store_zip_code_string_mapping(test_session):
    """Verify that store zip_code is parsed and stored as a string (VARCHAR)."""
    import sys
    from pathlib import Path
    project_root = Path(__file__).resolve().parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from data.scripts.seed_database import parse_record_fields
    import pandas as pd
    from sqlalchemy import text

    # 1. Test record parsing converts integer zip_code or preserves string zip_code
    raw_store_int_zip = {
        "id": "00000000-0000-4000-a000-000000000010",
        "workspace_id": "00000000-0000-4000-a000-000000000002",
        "store_code": "STR-MUM-01",
        "name": "NovaMart Bandra Flagship",
        "city": "Mumbai",
        "state": "Maharashtra",
        "zip_code": 400050,  # integer from pandas CSV inference
        "square_feet": 18500,
        "opened_date": "2021-03-15",
        "created_at": "2021-03-15 00:00:00+00",
    }
    parsed = parse_record_fields(raw_store_int_zip.copy())
    assert isinstance(parsed["zip_code"], str)
    assert parsed["zip_code"] == "400050"

    raw_store_leading_zero = {
        "zip_code": "01234",
    }
    parsed_zero = parse_record_fields(raw_store_leading_zero.copy())
    assert isinstance(parsed_zero["zip_code"], str)
    assert parsed_zero["zip_code"] == "01234"

    # 2. Test DB persistence with string zip_code
    org = Organization(id="00000000-0000-4000-a000-000000000001", name="Zip Test Org")
    ws = Workspace(id="00000000-0000-4000-a000-000000000002", org_id=org.id, name="Zip Test WS")
    test_session.add_all([org, ws])
    await test_session.commit()

    sql_str = """
        INSERT INTO stores (id, workspace_id, store_code, name, city, state, zip_code, square_feet, opened_date, created_at)
        VALUES (:id, :workspace_id, :store_code, :name, :city, :state, :zip_code, :square_feet, :opened_date, :created_at)
    """
    await test_session.execute(text(sql_str), [parsed])
    await test_session.commit()

    res = await test_session.execute(text("SELECT zip_code FROM stores WHERE id = '00000000-0000-4000-a000-000000000010'"))
    row = res.fetchone()
    assert row is not None
    assert isinstance(row[0], str)
    assert row[0] == "400050"
