from test._async_compat import mark_sync_test

from pytest import mark

from neomodel.sync_.core import db
from neomodel.util import version_tag_to_integer


# TODO : This calling database_version should be async
@mark.skipif(
    db.database_version != "5.7.0", reason="Testing a specific database version"
)
def test_version_awareness():
    assert db.database_version == "5.7.0"
    assert db.version_is_higher_than("5.7")
    assert db.version_is_higher_than("5.6.0")
    assert db.version_is_higher_than("5")
    assert db.version_is_higher_than("4")

    assert not db.version_is_higher_than("5.8")


@mark_sync_test
def test_edition_awareness():
    if db.database_edition == "enterprise":
        assert db.edition_is_enterprise()
    else:
        assert not db.edition_is_enterprise()


def test_version_tag_to_integer():
    assert version_tag_to_integer("5.7.1") == 50701
    assert version_tag_to_integer("5.1") == 50100
    assert version_tag_to_integer("5") == 50000
    assert version_tag_to_integer("5.14.1") == 51401
    assert version_tag_to_integer("5.14-aura") == 51400
