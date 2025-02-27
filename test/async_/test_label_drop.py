from test._async_compat import mark_async_test

from neo4j.exceptions import ClientError

from neomodel import AsyncStructuredNode, StringProperty, adb, config
from neomodel.util import DatabaseFlavour


class ConstraintAndIndex(AsyncStructuredNode):
    name = StringProperty(unique_index=True)
    last_name = StringProperty(index=True)


@mark_async_test
async def test_drop_labels():
    await adb.install_labels(ConstraintAndIndex)
    constraints_before = await adb.list_constraints()
    indexes_before = await adb.list_indexes(exclude_token_lookup=True)

    assert len(constraints_before) > 0
    assert len(indexes_before) > 0

    await adb.remove_all_labels()

    constraints = await adb.list_constraints()
    indexes = await adb.list_indexes(exclude_token_lookup=True)

    assert len(constraints) == 0
    assert len(indexes) == 0

    # Recreating all old constraints and indexes
    for constraint in constraints_before:
        if config.DATABASE_FLAVOUR == DatabaseFlavour.NEO4J:
            constraint_type_clause = "UNIQUE"
            if constraint["type"] == "NODE_PROPERTY_EXISTENCE":
                constraint_type_clause = "NOT NULL"
            elif constraint["type"] == "NODE_KEY":
                constraint_type_clause = "NODE KEY"

            await adb.cypher_query(
                f'CREATE CONSTRAINT {constraint["name"]} FOR (n:{constraint["labelsOrTypes"][0]}) REQUIRE n.{constraint["properties"][0]} IS {constraint_type_clause}'
            )
        elif config.DATABASE_FLAVOUR == DatabaseFlavour.MEMGRAPH:
            constraint_type_clause = ""
            if constraint["constraint type"] == "exists":
                constraint_type_clause = f"EXISTS (n.{constraint['properties'][0]})"
            elif constraint["constraint type"] == "unique":
                constraint_type_clause = f"n.{constraint['properties'][0]} IS UNIQUE"
            await adb.cypher_query(
                f"CREATE CONSTRAINT ON (n:{constraint['label']}) ASSERT {constraint_type_clause}"
            )
    for index in indexes_before:
        try:
            if config.DATABASE_FLAVOUR == DatabaseFlavour.NEO4J:
                await adb.cypher_query(
                    f'CREATE INDEX {index["name"]} FOR (n:{index["labelsOrTypes"][0]}) ON (n.{index["properties"][0]})'
                )
            elif config.DATABASE_FLAVOUR == DatabaseFlavour.MEMGRAPH:
                await adb.cypher_query(
                    f"CREATE INDEX ON :{index['label']}({index['property']})"
                )
        except ClientError:
            pass
