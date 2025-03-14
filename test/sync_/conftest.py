import os
import warnings
from test._async_compat import (
    mark_async_function_auto_fixture,
    mark_sync_session_auto_fixture,
)

from neomodel import config, db
from neomodel.util import DatabaseFlavour


@mark_sync_session_auto_fixture
def setup_neo4j_session(request):
    """
    Provides initial connection to the database and sets up the rest of the test suite

    :param request: The request object. Please see <https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_sessionstart>`_
    :type Request object: For more information please see <https://docs.pytest.org/en/latest/reference.html#request>`_
    """

    warnings.simplefilter("default")

    config.DATABASE_URL = os.environ.get(
        "NEO4J_BOLT_URL", "bolt://neo4j:foobarbaz@localhost:7687"
    )

    config.DATABASE_FLAVOUR = os.environ.get("DATABASE_FLAVOUR", DatabaseFlavour.NEO4J)

    # Clear the database if required
    database_is_populated, _ = db.cypher_query(
        "MATCH (a) return count(a)>0 as database_is_populated"
    )
    if database_is_populated[0][0] and not request.config.getoption("resetdb"):
        raise SystemError(
            "Please note: The database seems to be populated.\n\tEither delete all nodes and edges manually, or set the --resetdb parameter when calling pytest\n\n\tpytest --resetdb."
        )

    db.clear_neo4j_database(clear_constraints=True, clear_indexes=True)

    db.install_all_labels()

    if config.DATABASE_FLAVOUR == DatabaseFlavour.NEO4J:
        db.cypher_query(
            "CREATE OR REPLACE USER troygreene SET PASSWORD 'foobarbaz' CHANGE NOT REQUIRED"
        )
    elif config.DATABASE_FLAVOUR == DatabaseFlavour.MEMGRAPH:
        db.cypher_query(
            "CREATE USER IF NOT EXISTS troygreene IDENTIFIED BY 'foobarbaz'"
        )
    # db_edition = await adb.database_edition
    # if db_edition == "enterprise":
    #     await adb.cypher_query("GRANT ROLE publisher TO troygreene")
    #     await adb.cypher_query("GRANT IMPERSONATE (troygreene) ON DBMS TO admin")

    yield

    db.close_connection()


@mark_async_function_auto_fixture
def setUp():
    db.cypher_query("MATCH (n) DETACH DELETE n")
    yield
