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
