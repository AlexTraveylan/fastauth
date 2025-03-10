from typing import Optional

import factory
import pytest
from factory.alchemy import SQLAlchemyModelFactory
from sqlmodel import Field, Session, SQLModel

from fastauth.common.exceptions import NotFoundException
from fastauth.db.repository import Repository


class SampleModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    age: int


class SampleModelFactory(SQLAlchemyModelFactory):
    class Meta:
        model = SampleModel
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    age = factory.Faker("random_int", min=18, max=90)


def get_sample_model_factory(session: Session, **kwargs):
    SampleModelFactory._meta.sqlalchemy_session = session

    return SampleModelFactory(**kwargs)


@pytest.fixture
def repositorytest():
    """Create a repository for testing."""

    class RepositoryTest(Repository[SampleModel]):
        __model__ = SampleModel

    return RepositoryTest()


def test_create(repositorytest: Repository[SampleModel], session: Session):
    item = SampleModel(name="test", age=18)

    created_item = repositorytest.create(session, item)

    assert created_item.id is not None
    assert created_item.name == "test"
    assert created_item.age == 18


def test_get_or_raise(repositorytest: Repository[SampleModel], session: Session):
    get_sample_model_factory(session, name="test")

    item = repositorytest.get_or_raise(session, name="test")

    assert item.name == "test"


def test_get_or_raise_not_found(
    repositorytest: Repository[SampleModel],
    session: Session,
):
    with pytest.raises(NotFoundException):
        repositorytest.get_or_raise(session, name="test")


def test_get_all(repositorytest: Repository[SampleModel], session: Session):
    get_sample_model_factory(session, name="test1")
    get_sample_model_factory(session, name="test2")
    get_sample_model_factory(session, name="test3")

    items = repositorytest.get_all(session)

    assert len(items) == 3


def test_delete(repositorytest: Repository[SampleModel], session: Session):
    item = get_sample_model_factory(session)

    repositorytest.delete(session, item.id)


def test_delete_not_found(repositorytest: Repository[SampleModel], session: Session):
    assert repositorytest.delete(session, 999) is False


def test_update(repositorytest: Repository[SampleModel], session: Session):
    item = get_sample_model_factory(session, name="old_name")
    updated = repositorytest.update(session, item.id, name="new_name")
    assert updated.name == "new_name"


def test_get_or_none(repositorytest: Repository[SampleModel], session: Session):
    item = get_sample_model_factory(session, name="test")

    assert repositorytest.get_or_none(session, name="test") == item


def test_get_or_none_not_found(
    repositorytest: Repository[SampleModel],
    session: Session,
):
    assert repositorytest.get_or_none(session, name="test") is None


class Sample2Model(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    other_field: str


class Sample2ModelFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Sample2Model
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    other_field = factory.Faker("name")


def get_sample_model2_factory(session: Session, **kwargs):
    Sample2ModelFactory._meta.sqlalchemy_session = session

    return Sample2ModelFactory(**kwargs)


@pytest.fixture
def repositorytest2():
    """Create a repository for testing."""

    class RepositoryTest(Repository[Sample2Model]):
        __model__ = Sample2Model

    return RepositoryTest()


def test_get_or_raise_with_different_model(
    repositorytest: Repository[SampleModel],
    repositorytest2: Repository[Sample2Model],
    session: Session,
):
    get_sample_model_factory(session, name="test")
    get_sample_model2_factory(session, other_field="test")

    item = repositorytest.get_or_raise(session, name="test")
    item2 = repositorytest2.get_or_raise(session, other_field="test")

    assert item.name == "test"
    assert item2.other_field == "test"
