from pytest import raises

from neomodel import (
    IntegerProperty,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNodeAsync,
    UniqueIdProperty,
    config,
)
from neomodel.exceptions import DeflateError, UniqueProperty

config.AUTO_INSTALL_LABELS = True


class UniqueUser(StructuredNodeAsync):
    uid = UniqueIdProperty()
    name = StringProperty()
    age = IntegerProperty()


def test_unique_id_property_batch():
    users = UniqueUser.create_async(
        {"name": "bob", "age": 2}, {"name": "ben", "age": 3}
    )

    assert users[0].uid != users[1].uid

    users = UniqueUser.get_or_create_async(
        {"uid": users[0].uid}, {"name": "bill", "age": 4}
    )

    assert users[0].name == "bob"
    assert users[1].uid


class Customer(StructuredNodeAsync):
    email = StringProperty(unique_index=True, required=True)
    age = IntegerProperty(index=True)


def test_batch_create():
    users = Customer.create_async(
        {"email": "jim1@aol.com", "age": 11},
        {"email": "jim2@aol.com", "age": 7},
        {"email": "jim3@aol.com", "age": 9},
        {"email": "jim4@aol.com", "age": 7},
        {"email": "jim5@aol.com", "age": 99},
    )
    assert len(users) == 5
    assert users[0].age == 11
    assert users[1].age == 7
    assert users[1].email == "jim2@aol.com"
    assert Customer.nodes.get(email="jim1@aol.com")


def test_batch_create_or_update():
    users = Customer.create_or_update_async(
        {"email": "merge1@aol.com", "age": 11},
        {"email": "merge2@aol.com"},
        {"email": "merge3@aol.com", "age": 1},
        {"email": "merge2@aol.com", "age": 2},
    )
    assert len(users) == 4
    assert users[1] == users[3]
    assert Customer.nodes.get(email="merge1@aol.com").age == 11

    more_users = Customer.create_or_update_async(
        {"email": "merge1@aol.com", "age": 22},
        {"email": "merge4@aol.com", "age": None},
    )
    assert len(more_users) == 2
    assert users[0] == more_users[0]
    assert Customer.nodes.get(email="merge1@aol.com").age == 22


def test_batch_validation():
    # test validation in batch create
    with raises(DeflateError):
        Customer.create_async(
            {"email": "jim1@aol.com", "age": "x"},
        )


def test_batch_index_violation():
    for u in Customer.nodes.all():
        u.delete()

    users = Customer.create_async(
        {"email": "jim6@aol.com", "age": 3},
    )
    assert users
    with raises(UniqueProperty):
        Customer.create_async(
            {"email": "jim6@aol.com", "age": 3},
            {"email": "jim7@aol.com", "age": 5},
        )

    # not found
    assert not Customer.nodes.filter(email="jim7@aol.com")


class Dog(StructuredNodeAsync):
    name = StringProperty(required=True)
    owner = RelationshipTo("Person", "owner")


class Person(StructuredNodeAsync):
    name = StringProperty(unique_index=True)
    pets = RelationshipFrom("Dog", "owner")


def test_get_or_create_with_rel():
    bob = Person.get_or_create_async({"name": "Bob"})[0]
    bobs_gizmo = Dog.get_or_create_async({"name": "Gizmo"}, relationship=bob.pets)

    tim = Person.get_or_create_async({"name": "Tim"})[0]
    tims_gizmo = Dog.get_or_create_async({"name": "Gizmo"}, relationship=tim.pets)

    # not the same gizmo
    assert bobs_gizmo[0] != tims_gizmo[0]
