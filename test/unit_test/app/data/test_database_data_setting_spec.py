import asyncio
from typing import Any, Dict, List, Sequence, Tuple

import os
import sys
import pytest

# We assume pytest-asyncio is available in the project.
pytestmark = pytest.mark.asyncio


class AsyncResultMock:
    def __init__(self, columns: Sequence[str], rows: List[Tuple[Any, ...]]):
        self._columns = list(columns)
        self._rows = list(rows)

    def keys(self):
        # SQLAlchemy Result.keys() returns a list-like of column names
        return self._columns

    def fetchall(self):
        # Returns a list of Row-like tuples; for our usage, tuples suffice
        return list(self._rows)


class ExecCall:
    def __init__(self, sql: str, params: Any = None):
        self.sql = sql
        self.params = params

    def __repr__(self):
        return f"ExecCall(sql={self.sql!r}, params={self.params!r})"


class AsyncSessionMock:
    def __init__(self, name: str, select_results: Dict[str, AsyncResultMock]):
        self.name = name  # "source" or "target"
        self._select_results = select_results
        self.exec_calls: List[ExecCall] = []
        self.commit_calls = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def execute(self, sql_obj, params=None):
        # The code under test passes sqlalchemy.text("..."), which str(sql_obj) contains SQL text.
        sql = str(sql_obj)
        self.exec_calls.append(ExecCall(sql, params))
        # If SELECT, return configured result
        normalized = sql.strip().lower()
        if normalized.startswith("select "):
            # Expect format like: select * from {table}
            # We'll resolve by checking any configured SELECT SQL substring keys
            for key, result in self._select_results.items():
                if key in normalized:
                    return result
            # Default empty if not matched
            return AsyncResultMock(columns=[], rows=[])
        # Non-SELECT returns no result
        class _NoResult:
            def keys(self):
                return []

            def fetchall(self):
                return []

        return _NoResult()

    async def commit(self):
        self.commit_calls += 1


class SessionmakerFactoryMock:
    def __init__(self, engine_name: str, select_results: Dict[str, AsyncResultMock]):
        self.engine_name = engine_name
        self.select_results = select_results

    def __call__(self):
        # Create an AsyncSessionMock for this invocation
        return AsyncSessionMock(name=self.engine_name, select_results=self.select_results)


class AsyncEngineMock:
    def __init__(self, name: str):
        self.name = name
        self.disposed = False

    async def dispose(self):
        self.disposed = True


def build_module_with_mocks(monkeypatch, env_source_url="dummy_source", env_target_url="dummy_target",
                            select_results_source: Dict[str, AsyncResultMock] = None):
    """
    Import the module under test with patched env and sqlalchemy constructs,
    returning (module, mocks)
    """
    if select_results_source is None:
        select_results_source = {}

    # Ensure module path root exists in sys.path for import
    repo_root = os.getcwd()
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    # Set environment variables BEFORE import so globals are initialized correctly
    monkeypatch.setenv("DEV_MYSQL_URL", env_source_url)
    monkeypatch.setenv("PROD_MYSQL_URL", env_target_url)

    # Prepare engine mocks to track disposal
    source_engine = AsyncEngineMock("source")
    target_engine = AsyncEngineMock("target")

    # Patch create_async_engine to return our engine mocks in the correct order
    create_order = []
    def fake_create_async_engine(url):
        # The SUT calls create_async_engine twice, first for source, then for target
        if len(create_order) == 0:
            create_order.append("source")
            return source_engine
        else:
            create_order.append("target")
            return target_engine

    # Patch sessionmaker to create context-managed AsyncSessionMock
    def fake_sessionmaker(engine, class_=None, expire_on_commit=False):
        if engine is source_engine:
            return SessionmakerFactoryMock("source", select_results_source)
        elif engine is target_engine:
            # target side doesn't need SELECT results; only receives TRUNCATE/INSERT statements
            return SessionmakerFactoryMock("target", {})
        else:
            # Fallback to a predictable mock
            return SessionmakerFactoryMock("unknown", {})

    # Minimal passthrough for sqlalchemy.text: in SUT they just pass it to execute; we only need string form
    class TextWrapper(str):
        pass

    def fake_text(sql: str):
        return TextWrapper(sql)

    # Apply patches in the module namespace path
    module_path = "test.unit_test.app.data.test_database_data_setting"
    # Clear previously imported module to ensure patches apply to fresh import
    if module_path in sys.modules:
        del sys.modules[module_path]

    # Monkeypatch targets inside the module's import path (i.e., names as imported by the SUT)
    import importlib.util
    # Import the module but before import, we need to temporarily inject a sentinel sqlalchemy env
    # However, since the SUT does 'from sqlalchemy import text' and 'from sqlalchemy.ext.asyncio import create_async_engine'
    # and 'from sqlalchemy.orm import sessionmaker', we patch these in the module after import or via import hooks.
    # Easiest: import the module, then monkeypatch attributes on the module object.

    # Temporarily import to get a handle, then patch, then reload to wire the function references.
    mod = importlib.import_module(module_path)

    # Patch in the module's namespace
    monkeypatch.setattr(mod, "create_async_engine", fake_create_async_engine, raising=True)
    monkeypatch.setattr(mod, "sessionmaker", fake_sessionmaker, raising=True)
    monkeypatch.setattr(mod, "text", fake_text, raising=True)

    # Reload to ensure any cached references are consistent
    mod = importlib.reload(mod)

    # Re-assert patches after reload (some imports might have been re-bound)
    monkeypatch.setattr(mod, "create_async_engine", fake_create_async_engine, raising=True)
    monkeypatch.setattr(mod, "sessionmaker", fake_sessionmaker, raising=True)
    monkeypatch.setattr(mod, "text", fake_text, raising=True)

    return mod, {
        "source_engine": source_engine,
        "target_engine": target_engine,
    }


def assert_contains_exec(exec_calls: List[ExecCall], expected_sql_substring: str, count: int = 1):
    matching = [c for c in exec_calls if expected_sql_substring.lower() in c.sql.lower()]
    assert len(matching) == count, f"Expected {count} execs containing {expected_sql_substring!r}, got {len(matching)}: {matching}"
    return matching


async def run_copy_tables(mod):
    # Drive the async function under test
    await mod.copy_tables()


def test_happy_path_copies_all_tables_with_correct_flow_and_disposal(monkeypatch, capsys):
    # Simulate three tables each with some rows and columns
    # We key SELECT results by a substring of the SQL (table name)
    select_results = {
        "from job": AsyncResultMock(columns=["id", "title"], rows=[(1, "a"), (2, "b")]),
        "from job_group": AsyncResultMock(columns=["id", "name"], rows=[(10, "g1")]),
        "from salary_stat": AsyncResultMock(columns=["id", "amount", "currency"], rows=[(100, 1234.56, "USD"), (101, 0, "KRW")]),
    }

    mod, mocks = build_module_with_mocks(monkeypatch, select_results_source=select_results)

    # Invoke
    asyncio.get_event_loop().run_until_complete(run_copy_tables(mod))

    # After completion, engines disposed
    assert mocks["source_engine"].disposed is True
    assert mocks["target_engine"].disposed is True

    # We cannot access sessions directly, but we can infer through stdout and commit/exec logs embedded in mocks.
    # Capture stdout for simple behavioral signals
    out = capsys.readouterr().out
    # Copy start logs
    assert "Copying table: job" in out
    assert "Copying table: job_group" in out
    assert "Copying table: salary_stat" in out
    # Rows copied logs present
    assert "2개의 행을 복사합니다. table_name='job'" in out or "2개의 행을 복사합니다. table_name=job" in out
    assert "1개의 행을 복사합니다. table_name='job_group'" in out or "1개의 행을 복사합니다. table_name=job_group" in out
    assert "2개의 행을 복사합니다. table_name='salary_stat'" in out or "2개의 행을 복사합니다. table_name=salary_stat" in out
    # Final completion log
    assert "복사 완료 되었습니다!" in out

    # To verify SQL sequence, we reconstruct from mocks by re-running to capture sessions.
    # Since sessions are created inside, we can't access them directly here; however, we can reconfigure a probe mock
    # by subclassing the factory to store last session instances. Do that in a separate test for fine-grained assertions.


def test_sequence_and_parameters_for_each_table(monkeypatch):
    # Enhanced mocks to capture per-session interactions
    created_sessions = {}

    class CapturingSessionmakerFactory(SessionmakerFactoryMock):
        def __call__(self):
            sess = AsyncSessionMock(name=self.engine_name, select_results=self.select_results)
            created_sessions.setdefault(self.engine_name, []).append(sess)
            return sess

    select_results = {
        "from job": AsyncResultMock(columns=["id", "title"], rows=[(1, "a")]),
        "from job_group": AsyncResultMock(columns=["gid", "name"], rows=[(10, "g1")]),
        "from salary_stat": AsyncResultMock(columns=["sid", "amount"], rows=[(100, 42.0)]),
    }

    def build_with_custom_sessionmaker(monkeypatch):
        mod, mocks = build_module_with_mocks(monkeypatch, select_results_source=select_results)
        # Override the sessionmaker in the module to use capturing factory
        def capturing_sessionmaker(engine, class_=None, expire_on_commit=False):
            if engine is mocks["source_engine"]:
                return CapturingSessionmakerFactory("source", select_results)
            elif engine is mocks["target_engine"]:
                return CapturingSessionmakerFactory("target", {})
            return CapturingSessionmakerFactory("unknown", {})
        monkeypatch.setattr(mod, "sessionmaker", capturing_sessionmaker, raising=True)
        return mod, mocks

    mod, mocks = build_with_custom_sessionmaker(monkeypatch)

    asyncio.get_event_loop().run_until_complete(run_copy_tables(mod))

    # We should have exactly one source session and one target session created
    assert len(created_sessions.get("source", [])) == 1
    assert len(created_sessions.get("target", [])) == 1
    source_sess = created_sessions["source"][0]
    target_sess = created_sessions["target"][0]

    # Target: first disable foreign key checks
    assert_contains_exec(target_sess.exec_calls, "SET FOREIGN_KEY_CHECKS = 0", count=1)

    # For each table: TRUNCATE then SELECT then INSERT (since rows exist)
    for table in ["job", "job_group", "salary_stat"]:
        # TRUNCATE issued to target
        assert_contains_exec(target_sess.exec_calls, f"TRUNCATE TABLE {table}", count=1)
        # SELECT issued to source
        assert_contains_exec(source_sess.exec_calls, f"SELECT * FROM {table}", count=1)

    # Validate INSERT statements and parameter construction for each table
    insert_calls = [c for c in target_sess.exec_calls if "insert into" in c.sql.lower()]
    # Expect one insert per table since we batch per table
    assert len(insert_calls) == 3

    # Check columns/params mapping by table
    def find_insert_for(table):
        for call in insert_calls:
            if f"into {table} " in call.sql.lower():
                return call
        return None

    job_insert = find_insert_for("job")
    assert job_insert is not None
    assert job_insert.sql == "INSERT INTO job (id, title) VALUES (:id, :title)"
    assert job_insert.params == [{"id": 1, "title": "a"}]

    job_group_insert = find_insert_for("job_group")
    assert job_group_insert is not None
    assert job_group_insert.sql == "INSERT INTO job_group (gid, name) VALUES (:gid, :name)"
    assert job_group_insert.params == [{"gid": 10, "name": "g1"}]

    salary_insert = find_insert_for("salary_stat")
    assert salary_insert is not None
    assert salary_insert.sql == "INSERT INTO salary_stat (sid, amount) VALUES (:sid, :amount)"
    assert salary_insert.params == [{"sid": 100, "amount": 42.0}]

    # Verify commits: after each TRUNCATE and after each INSERT batch plus final enable foreign keys
    # In SUT, commit after each TRUNCATE and after each INSERT, and after re-enabling foreign keys
    # That's: 3 (truncate) + 3 (insert) + 1 (final) = 7 commits on target
    assert target_sess.commit_calls == 7

    # Source session should not call commit (only reads)
    assert source_sess.commit_calls == 0

    # Finally re-enable foreign key checks
    assert_contains_exec(target_sess.exec_calls, "SET FOREIGN_KEY_CHECKS = 1", count=1)


def test_empty_tables_skip_inserts_and_log_no_data(monkeypatch, capsys):
    # Configure source to return empty result for all tables
    empty_result = AsyncResultMock(columns=["id", "name"], rows=[])
    select_results = {
        "from job": empty_result,
        "from job_group": empty_result,
        "from salary_stat": empty_result,
    }
    mod, mocks = build_module_with_mocks(monkeypatch, select_results_source=select_results)

    asyncio.get_event_loop().run_until_complete(run_copy_tables(mod))

    out = capsys.readouterr().out
    # Logs saying no data exist for each table
    assert "데이터가 존재하지 않습니다. table_name='job'" in out or "데이터가 존재하지 않습니다. table_name=job" in out
    assert "데이터가 존재하지 않습니다. table_name='job_group'" in out or "데이터가 존재하지 않습니다. table_name=job_group" in out
    assert "데이터가 존재하지 않습니다. table_name='salary_stat'" in out or "데이터가 존재하지 않습니다. table_name=salary_stat" in out
    assert "복사 완료 되었습니다!" in out


def test_handles_env_variables_present_before_import(monkeypatch):
    # Ensure that if envs are set before importing, module picks them up and runs without None URLs.
    mod, mocks = build_module_with_mocks(monkeypatch, env_source_url="mysql+async://src", env_target_url="mysql+async://dst",
                                         select_results_source={"from job": AsyncResultMock(["id"], [(1,)]),
                                                                "from job_group": AsyncResultMock(["id"], []),
                                                                "from salary_stat": AsyncResultMock(["id"], [])})
    # Just ensure running does not raise and engines are disposed
    asyncio.get_event_loop().run_until_complete(run_copy_tables(mod))
    assert mocks["source_engine"].disposed
    assert mocks["target_engine"].disposed


def test_placeholder_order_matches_column_order(monkeypatch):
    # Columns in a different order than typical to ensure placeholders match order exactly
    select_results = {
        "from job": AsyncResultMock(columns=["title", "id"], rows=[("x", 5)]),
        "from job_group": AsyncResultMock(columns=[], rows=[]),
        "from salary_stat": AsyncResultMock(columns=[], rows=[]),
    }

    created_sessions = {}

    class CapturingSessionmakerFactory(SessionmakerFactoryMock):
        def __call__(self):
            sess = AsyncSessionMock(name=self.engine_name, select_results=self.select_results)
            created_sessions.setdefault(self.engine_name, []).append(sess)
            return sess

    mod, mocks = build_module_with_mocks(monkeypatch, select_results_source=select_results)
    def capturing_sessionmaker(engine, class_=None, expire_on_commit=False):
        if engine is mocks["source_engine"]:
            return CapturingSessionmakerFactory("source", select_results)
        elif engine is mocks["target_engine"]:
            return CapturingSessionmakerFactory("target", {})
        return CapturingSessionmakerFactory("unknown", {})
    monkeypatch.setattr(mod, "sessionmaker", capturing_sessionmaker, raising=True)

    asyncio.get_event_loop().run_until_complete(run_copy_tables(mod))

    target_sess = created_sessions["target"][0]
    inserts = [c for c in target_sess.exec_calls if "insert into job " in c.sql.lower()]
    assert len(inserts) == 1
    insert = inserts[0]
    # Columns should be in the same order as columns list: title, id
    assert insert.sql == "INSERT INTO job (title, id) VALUES (:title, :id)"
    assert insert.params == [{"title": "x", "id": 5}]