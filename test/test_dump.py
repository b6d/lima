from collections import OrderedDict
from datetime import date, datetime

import pytest

from lima import fields, schema


# model -----------------------------------------------------------------------

class Knight:
    '''A knight.'''
    def __init__(self, title, name, number, born):
        self.title = title
        self.name = name
        self.number = number
        self.born = born


class King(Knight):
    '''A king is a knight with subjects.'''
    def __init__(self, title, name, number, born, subjects=None):
        super().__init__(title, name, number, born)
        self.subjects = subjects if subjects is not None else []


# schemas ---------------------------------------------------------------------

class KnightSchema(schema.Schema):
    title = fields.String()
    name = fields.String()
    number = fields.Integer()
    born = fields.Date()


class KnightDictSchema(schema.Schema):
    title = fields.String(key='title')
    name = fields.String(key='name')
    number = fields.Integer(key='number')
    born = fields.Date(key='born')


class KnightListSchema(schema.Schema):
    title = fields.String(key=0)
    name = fields.String(key=1)
    number = fields.Integer(key=2)
    born = fields.Date(key=3)


class FieldWithAttrArgSchema(schema.Schema):
    date_of_birth = fields.Date(attr='born')


class FieldWithGetterArgSchema(schema.Schema):
    full_name = fields.String(
        get=lambda obj: '{} {}'.format(obj.title, obj.name)
    )


class FieldWithValArgSchema(schema.Schema):
    constant_date = fields.Date(val=date(2014, 10, 20))


class KingWithEmbeddedSubjectsObjSchema(KnightSchema):
    subjects = fields.Embed(schema=KnightSchema(many=True))


class KingWithEmbeddedSubjectsClassSchema(KnightSchema):
    subjects = fields.Embed(schema=KnightSchema, many=True)


class KingWithEmbeddedSubjectsStrSchema(KnightSchema):
    subjects = fields.Embed(schema=__name__ + '.KnightSchema', many=True)


class KingWithReferencedSubjectsObjSchema(KnightSchema):
    subjects = fields.Reference(schema=KnightSchema(many=True), field='name')


class KingWithReferencedSubjectsClassSchema(KnightSchema):
    subjects = fields.Reference(schema=KnightSchema, field='name', many=True)


class KingWithReferencedSubjectsStrSchema(KnightSchema):
    subjects = fields.Reference(schema=__name__ + '.KnightSchema',
                                field='name', many=True)


class KingSchemaEmbedSelf(KnightSchema):
    boss = fields.Embed(schema=__name__ + '.KingSchemaEmbedSelf',
                        exclude='boss')


class KingSchemaReferenceSelf(KnightSchema):
    boss = fields.Reference(schema=__name__ + '.KingSchemaEmbedSelf',
                            field='name')


# fixtures --------------------------------------------------------------------

@pytest.fixture
def bedevere():
    return Knight('Sir', 'Bedevere', 2, date(502, 2, 2))


@pytest.fixture
def lancelot():
    return Knight('Sir', 'Lancelot', 3, date(503, 3, 3))


@pytest.fixture
def galahad():
    return Knight('Sir', 'Galahad', 4, date(504, 4, 4))


@pytest.fixture
def knights(bedevere, lancelot, galahad):
    return [bedevere, lancelot, galahad]


@pytest.fixture
def arthur(knights):
    return King('King', 'Arthur', 1, date(501, 1, 1), knights)


@pytest.fixture
def lancelot_dict():
    return {
        'title': 'Sir',
        'name': 'Lancelot',
        'number': 3,
        'born': date(503, 3, 3),
    }


@pytest.fixture
def lancelot_list():
    return [
        'Sir',
        'Lancelot',
        3,
        date(503, 3, 3),
    ]


# tests -----------------------------------------------------------------------

def test_dump_single_dict_unordered(lancelot_dict):
    knight_dict_schema = KnightDictSchema(many=False, ordered=False)
    result = knight_dict_schema.dump(lancelot_dict)
    expected = {
        'title': 'Sir',
        'name': 'Lancelot',
        'number': 3,
        'born': '0503-03-03'
    }
    assert type(result) == dict
    assert result == expected


def test_dump_single_list_unordered(lancelot_list):
    knight_list_schema = KnightListSchema(many=False, ordered=False)
    result = knight_list_schema.dump(lancelot_list)
    expected = {
        'title': 'Sir',
        'name': 'Lancelot',
        'number': 3,
        'born': '0503-03-03'
    }
    assert type(result) == dict
    assert result == expected


def test_dump_single_unordered(lancelot):
    knight_schema = KnightSchema(many=False, ordered=False)
    result = knight_schema.dump(lancelot)
    expected = {
        'title': 'Sir',
        'name': 'Lancelot',
        'number': 3,
        'born': '0503-03-03'
    }
    assert type(result) == dict
    assert result == expected


def test_dump_single_ordered(lancelot):
    knight_schema = KnightSchema(many=False, ordered=True)
    result = knight_schema.dump(lancelot)
    expected = OrderedDict([
        ('title', 'Sir'),
        ('name', 'Lancelot'),
        ('number', 3),
        ('born', '0503-03-03'),
    ])
    assert type(result) == OrderedDict
    assert result == expected


def test_dump_many_unordered(knights):
    knight_schema = KnightSchema(many=True, ordered=False)
    result = knight_schema.dump(knights)
    expected = [
        dict(title='Sir', name='Bedevere', number=2, born='0502-02-02'),
        dict(title='Sir', name='Lancelot', number=3, born='0503-03-03'),
        dict(title='Sir', name='Galahad', number=4, born='0504-04-04'),
    ]
    assert all(type(x) == dict for x in result)
    assert result == expected


def test_dump_many_ordered(knights):
    knight_schema = KnightSchema(many=True, ordered=True)
    result = knight_schema.dump(knights)
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


def test_field_exclude_dump(lancelot):
    knight_schema = KnightSchema(exclude=['born', 'number'])
    result = knight_schema.dump(lancelot)
    expected = {
        'title': 'Sir',
        'name': 'Lancelot',
    }
    assert result == expected


def test_field_only_dump(lancelot):
    knight_schema = KnightSchema(only=['name', 'number'])
    result = knight_schema.dump(lancelot)
    expected = {
        'name': 'Lancelot',
        'number': 3,
    }
    assert result == expected


def test_dump_field_with_attr_arg(lancelot):
    attr_schema = FieldWithAttrArgSchema()
    result = attr_schema.dump(lancelot)
    expected = {
        'date_of_birth': '0503-03-03'
    }
    assert result == expected


def test_dump_field_with_getter_arg(lancelot):
    getter_schema = FieldWithGetterArgSchema()
    result = getter_schema.dump(lancelot)
    expected = {
        'full_name': 'Sir Lancelot'
    }
    assert result == expected


def test_dump_field_with_val_arg(lancelot):
    val_schema = FieldWithValArgSchema()
    result = val_schema.dump(lancelot)
    expected = {
        'constant_date': '2014-10-20'
    }
    assert result == expected


def test_fail_on_unexpected_collection(knights):
    knight_schema = KnightSchema(many=False)
    with pytest.raises(AttributeError):
        knight_schema.dump(knights)


@pytest.mark.parametrize(
    'king_schema_cls',
    [KingWithEmbeddedSubjectsObjSchema,
     KingWithEmbeddedSubjectsClassSchema,
     KingWithEmbeddedSubjectsStrSchema]
)
def test_dump_embedding_schema(king_schema_cls, arthur):
    king_schema = king_schema_cls()
    expected = {
        'title': 'King',
        'name': 'Arthur',
        'number': 1,
        'born': '0501-01-01',
        'subjects': [
            dict(title='Sir', name='Bedevere', number=2, born='0502-02-02'),
            dict(title='Sir', name='Lancelot', number=3, born='0503-03-03'),
            dict(title='Sir', name='Galahad', number=4, born='0504-04-04'),
        ]
    }
    assert king_schema.dump(arthur) == expected


@pytest.mark.parametrize(
    'king_schema_cls',
    [KingWithReferencedSubjectsObjSchema,
     KingWithReferencedSubjectsClassSchema,
     KingWithReferencedSubjectsStrSchema]
)
def test_dump_referencing_schema(king_schema_cls, arthur):
    king_schema = king_schema_cls()
    expected = {
        'title': 'King',
        'name': 'Arthur',
        'number': 1,
        'born': '0501-01-01',
        'subjects': ['Bedevere', 'Lancelot', 'Galahad']
    }
    assert king_schema.dump(arthur) == expected


def test_embed_self_schema(arthur):
    # a king is his own boss
    arthur.boss = arthur
    king_schema = KingSchemaEmbedSelf()
    result = king_schema.dump(arthur)
    expected = {
        'title': 'King',
        'name': 'Arthur',
        'number': 1,
        'born': '0501-01-01',
        'boss': {
            'title': 'King',
            'name': 'Arthur',
            'number': 1,
            'born': '0501-01-01',
        }
    }
    assert result == expected


def test_reference_self_schema(arthur):
    # a king is his own boss
    arthur.boss = arthur
    king_schema = KingSchemaReferenceSelf()
    result = king_schema.dump(arthur)
    expected = {
        'title': 'King',
        'name': 'Arthur',
        'number': 1,
        'born': '0501-01-01',
        'boss': 'Arthur',
    }
    assert result == expected


def test_fail_on_unnecessary_keywords():

    class EmbedSchema(schema.Schema):
        some_field = fields.String()

    embed_schema = EmbedSchema(many=True)

    class EmbeddingSchema(schema.Schema):
        another_field = fields.String()
        # here we provide a schema _instance_. the kwarg "many" is unnecessary
        incorrect_embed_field = fields.Embed(schema=embed_schema, many=True)

    # the incorrect field is constructed lazily. we'll have to access it
    with pytest.raises(ValueError):
        EmbeddingSchema.__fields__['incorrect_embed_field']._schema_inst


def test_fail_on_unnecessary_arg():

    class EmbedSchema(schema.Schema):
        some_field = fields.String()

    embed_schema = EmbedSchema(many=True)

    class EmbeddingSchema(schema.Schema):
        another_field = fields.String()
        # here we provide a schema _instance_. the kwarg "many" is unnecessary
        incorrect_embed_field = fields.Embed(schema=embed_schema, many=True)

    # the incorrect field is constructed lazily. we'll have to access it
    with pytest.raises(ValueError):
        EmbeddingSchema.__fields__['incorrect_embed_field']._schema_inst


def test_dump_exotic_field_names():
    exotic_names = [
        '',  # empty string
        '"',  # single quote
        "'",  # double quote
        '\u2665',  # unicode heart symbol
        'print(123)',  # valid python code
        'print("123\'',  # invalid python code
    ]

    class ExoticFieldNamesSchema(schema.Schema):
        __lima_args__ = {
            'include': {name: fields.String(attr='foo')
                        for name in exotic_names}
        }

    class Foo:
        def __init__(self):
            self.foo = 'foobar'

    obj = Foo()
    exotic_field_names_schema = ExoticFieldNamesSchema()
    result = exotic_field_names_schema.dump(obj)
    expected = {name: 'foobar' for name in exotic_names}
    assert result == expected

    for name in exotic_names:
        dump_field_func = exotic_field_names_schema._dump_field_func(name)
        result = dump_field_func(obj)
        expected = 'foobar'
        assert result == expected
