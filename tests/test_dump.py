from collections import OrderedDict
from datetime import date, datetime

import pytest

from lima import fields, schema


class Person:
    def __init__(self, title, name, number, born):
        self.title = title
        self.name = name
        self.number = number
        self.born = born


class PersonSchema(schema.Schema):
    title = fields.String()
    name = fields.String()
    number = fields.Integer()
    born = fields.Date()


class DifferentAttrSchema(schema.Schema):
    date_of_birth = fields.Date(attr='born')


class GetterSchema(schema.Schema):
    some_getter = lambda obj: '{} {}'.format(obj.title, obj.name)

    full_name = fields.String(get=some_getter)


class ConstantValueSchema(schema.Schema):
    constant = fields.Date(val=date(2014, 10, 20))


class KnightSchema(schema.Schema):
    name = fields.String()


class KingSchemaEmbedStr(KnightSchema):
    title = fields.String()
    subjects = fields.Embed(schema=__name__ + '.KnightSchema', many=True)


class KingSchemaEmbedClass(KnightSchema):
    title = fields.String()
    subjects = fields.Embed(schema=KnightSchema, many=True)


class KingSchemaEmbedObject(KnightSchema):
    some_schema_object = KnightSchema(many=True)
    title = fields.String()
    subjects = fields.Embed(schema=some_schema_object)


class KingSchemaEmbedSelf(schema.Schema):
    name = fields.String()
    boss = fields.Embed(schema=__name__ + '.KingSchemaEmbedSelf',
                        exclude='boss')


@pytest.fixture
def king():
    return Person('King', 'Arthur', 1, date(501, 1, 1))


@pytest.fixture
def knights():
    return [
        Person('Sir', 'Bedevere', 2, date(502, 2, 2)),
        Person('Sir', 'Lancelot', 3, date(503, 3, 3)),
        Person('Sir', 'Galahad', 4, date(504, 4, 4)),
    ]


def test_dump_single_unordered(king):
    person_schema = PersonSchema(many=False, ordered=False)
    result = person_schema.dump(king)
    expected = {
        'title': 'King',
        'name': 'Arthur',
        'number': 1,
        'born': '0501-01-01'
    }
    assert type(result) == dict
    assert result == expected


def test_dump_single_ordered(king):
    person_schema = PersonSchema(many=False, ordered=True)
    result = person_schema.dump(king)
    expected = OrderedDict(
        [
            ('title', 'King'),
            ('name', 'Arthur'),
            ('number', 1),
            ('born', '0501-01-01'),
        ]
    )
    assert type(result) == OrderedDict
    assert result == expected


def test_dump_many_unordered(knights):
    person_schema = PersonSchema(many=True, ordered=False)
    result = person_schema.dump(knights)
    expected = [
        dict(title='Sir', name='Bedevere', number=2, born='0502-02-02'),
        dict(title='Sir', name='Lancelot', number=3, born='0503-03-03'),
        dict(title='Sir', name='Galahad', number=4, born='0504-04-04'),
    ]
    assert all(type(x) == dict for x in result)
    assert result == expected


def test_dump_many_ordered(knights):
    person_schema = PersonSchema(many=True, ordered=True)
    result = person_schema.dump(knights)
    expected = [
        OrderedDict([('title', 'Sir'), ('name', 'Bedevere'),
                     ('number', 2), ('born', '0502-02-02')]),
        OrderedDict([('title', 'Sir'), ('name', 'Lancelot'),
                     ('number', 3), ('born', '0503-03-03')]),
        OrderedDict([('title', 'Sir'), ('name', 'Galahad'),
                     ('number', 4), ('born', '0504-04-04')]),
    ]
    assert all(type(x) == OrderedDict for x in result)
    assert result == expected


def test_field_exclude_dump(king):
    person_schema = PersonSchema(exclude=['born'])
    result = person_schema.dump(king)
    expected = {
        'title': 'King',
        'name': 'Arthur',
        'number': 1,
    }
    assert result == expected


def test_field_only_dump(king):
    person_schema = PersonSchema(only=['name'])
    result = person_schema.dump(king)
    expected = {
        'name': 'Arthur',
    }
    assert result == expected


def test_attr_field_dump(king):
    attr_schema = DifferentAttrSchema()
    result = attr_schema.dump(king)
    expected = {
        'date_of_birth': '0501-01-01'
    }
    assert result == expected


def test_getter_field_dump(king):
    getter_schema = GetterSchema()
    result = getter_schema.dump(king)
    expected = {
        'full_name': 'King Arthur'
    }
    assert result == expected


def test_constant_value_field_dump(king):
    constant_value_schema = ConstantValueSchema()
    result = constant_value_schema.dump(king)
    expected = {
        'constant': '2014-10-20'
    }
    assert result == expected


def test_dump_fail_on_unexpected_collection(knights):
    person_schema = PersonSchema(many=False)
    with pytest.raises(Exception):
        person_schema.dump(knights)


@pytest.mark.parametrize('schema_cls',
                         [KingSchemaEmbedStr,
                          KingSchemaEmbedClass,
                          KingSchemaEmbedObject])
def test_dump_embed_schema(schema_cls, king, knights):
    king_schema = schema_cls()
    king.subjects = knights
    expected = {
        'title': 'King',
        'name': 'Arthur',
        'subjects': [
            {'name': 'Bedevere'},
            {'name': 'Lancelot'},
            {'name': 'Galahad'},
        ]
    }
    assert king_schema.dump(king) == expected


def test_dump_embed_schema_instance_double_kwargs_error():

    class EmbedSchema(schema.Schema):
        some_field = fields.String()

    embed_schema = KnightSchema(many=True)

    class EmbeddingSchema(schema.Schema):
        another_field = fields.String()
        # here we provide a schema instance. the kwarg "many" is unnecessary
        incorrect_embed_field = fields.Embed(schema=embed_schema, many=True)

    # the incorrect field is constructed lazily. we'll have to access it
    with pytest.raises(ValueError):
        EmbeddingSchema.__fields__['incorrect_embed_field']._schema_inst


def test_dump_embed_schema_self(king):
    king_schema = KingSchemaEmbedSelf()
    king.boss = king
    expected = {
        'name': 'Arthur',
        'boss': {'name': 'Arthur'},
    }
    assert king_schema.dump(king) == expected
