'''tests for the fields module'''

import datetime as dt
import decimal

import pytest

from lima import abc, exc, fields, schema


PASSTHROUGH_FIELDS = [
    fields.Boolean,
    fields.Float,
    fields.Integer,
    fields.String,
]

SIMPLE_FIELDS = PASSTHROUGH_FIELDS + [
    fields.Date,
    fields.DateTime,
    fields.Decimal,
]


@pytest.mark.parametrize('cls', SIMPLE_FIELDS)
def test_simple_fields(cls):
    '''Test creation of simple fields.'''
    field = cls()
    assert isinstance(field, abc.FieldABC)


@pytest.mark.parametrize('cls', SIMPLE_FIELDS)
def test_simple_fields_attr(cls):
    '''Test creation of simple fields with attr.'''
    attr = 'foo'
    field = cls(attr=attr)
    assert isinstance(field, abc.FieldABC)
    assert field.attr == attr


@pytest.mark.parametrize('cls', SIMPLE_FIELDS)
def test_simple_fields_key(cls):
    '''Test creation of simple fields with key.'''
    key = 'foo'
    field = cls(key=key)
    assert isinstance(field, abc.FieldABC)
    assert field.key == key


@pytest.mark.parametrize('cls', SIMPLE_FIELDS)
def test_simple_fields_getter(cls):
    '''Test creation of simple fields with get.'''
    getter = lambda obj: obj.foo
    field = cls(get=getter)
    assert isinstance(field, abc.FieldABC)
    assert field.get == getter


@pytest.mark.parametrize('cls', SIMPLE_FIELDS)
def test_simple_fields_val(cls):
    '''Test creation of simple fields with val.'''
    val = object()  # some arbitrary value
    field = cls(val=val)
    assert isinstance(field, abc.FieldABC)
    assert field.val is val


@pytest.mark.parametrize('cls', SIMPLE_FIELDS)
def test_illegal_attr_fails(cls):
    '''Test if supplying a non-identifier attr raises an error.'''
    with pytest.raises(ValueError):
        field = cls(attr='0not;an,identifier')


@pytest.mark.parametrize('cls', SIMPLE_FIELDS)
def test_illegal_getter_fails(cls):
    '''Test if supplying a non-callable getter raises an error.'''
    with pytest.raises(ValueError):
        field = cls(get='this is not callable')


@pytest.mark.parametrize('cls', SIMPLE_FIELDS)
def test_attr_and_getter_fails(cls):
    '''Test error on supplying more than one of get, val, key and attr.'''
    with pytest.raises(ValueError):
        field = cls(attr='foo', key='bar')
    with pytest.raises(ValueError):
        field = cls(key='foo', val='bar')
    with pytest.raises(ValueError):
        field = cls(attr='foo', get=lambda obj: 'bar')
    with pytest.raises(ValueError):
        field = cls(attr='foo', val='bar')
    with pytest.raises(ValueError):
        field = cls(attr='foo', get=lambda obj: 'bar', val='baz')


@pytest.mark.parametrize('cls', PASSTHROUGH_FIELDS)
def test_passthrough_field_no_attrs(cls):
    '''Test simple fields having neither get nor pack attrs ...

    ... which would slow down serialization of trivial stuff

    '''
    field = cls()
    assert not hasattr(field, 'get')
    assert not hasattr(field, 'pack')


def test_date_pack():
    '''Test date field pack static method'''
    date = dt.date(1952, 9, 1)
    assert fields.Date.pack(date) == '1952-09-01'


def test_datetime_pack():
    '''Test date field pack static method'''
    tz = dt.timezone(dt.timedelta(hours=2))
    datetime = dt.datetime(1952, 9, 1, 23, 11, 59, 123456, tz)
    expected = '1952-09-01T23:11:59.123456+02:00'
    assert fields.DateTime.pack(datetime) == expected


def test_decimal_pack():
    '''Test decimal field pack static method'''
    val = decimal.Decimal('1.2345')
    assert fields.Decimal.pack(val) == '1.2345'


class SomeClass:
    '''Arbitrary class (to test linked object fields).'''
    def __init__(self, name, number):
        self.name = name
        self.number = number


class SomeSchema(schema.Schema):
    '''Schema for SomeClass (to test linked object fields).'''
    name = fields.String()
    number = fields.Integer()


class TestLinkedObjectField:
    '''Tests for _LinkedObjectField, the base class for Embed and Reference'''

    @pytest.mark.parametrize(
        'schema_arg',
        [SomeSchema(), SomeSchema, __name__ + '.SomeSchema']
    )
    def test_linked_object_field(self, schema_arg):
        field = fields._LinkedObjectField(schema=schema_arg)
        assert field._schema_arg is schema_arg
        assert isinstance(field._schema_inst, SomeSchema)

    @pytest.mark.parametrize(
        'field',
        [
            fields._LinkedObjectField(
                schema=SomeSchema(many=True, only='number')
            ),
            fields._LinkedObjectField(
                schema=SomeSchema, many=True, only='number'
            ),
            fields._LinkedObjectField(
                schema=__name__ + '.SomeSchema', many=True, only='number'
            )
        ]
    )
    def test_linked_object_field_with_kwargs(self, field):
        assert isinstance(field._schema_inst, SomeSchema)
        assert field._schema_inst.many is True
        assert list(field._schema_inst._fields.keys()) == ['number']

    def test_linked_object_fail_on_unnecessary_kwargs(self):
        schema_inst = SomeSchema()
        # "many" is already defined for a schema instance. providing it again
        # when embedding will raise an error on lazy eval
        field = fields._LinkedObjectField(schema=schema_inst, many=True)
        with pytest.raises(ValueError):
            field._schema_inst  # this will complain about our earlier error

    def test_linked_object_fail_on_unnecessary_kwargs(self):
        schema_inst = SomeSchema()
        # "many" is already defined for a schema instance. providing it again
        # when embedding will raise an error on lazy eval
        field = fields._LinkedObjectField(schema=schema_inst, many=True)
        with pytest.raises(ValueError):
            field._schema_inst  # this will complain about our earlier error

    def test_linked_object_fail_on_nonexistent_class(self):
        # nonexistent schema name will raise an error on lazy eval
        field = fields._LinkedObjectField(schema='NonExistentSchemaName')
        with pytest.raises(exc.ClassNotFoundError):
            field._schema_inst  # this will complain about our earlier error

    def test_linked_object_fail_on_illegal_schema_arg(self):
        # wrong "schema" arg type will raise an error on lazy eval
        field = fields._LinkedObjectField(schema=123)
        with pytest.raises(TypeError):
            field._schema_inst  # this will complain about our earlier error

    def test_linked_object_field_pack_not_implemented(self):
        field = fields._LinkedObjectField(schema=SomeSchema)
        # pack method is not implemented
        with pytest.raises(NotImplementedError):
            field.pack('foo')


class TestEmbed:
    '''Tests for Embed, a class for embedding linked objects.'''

    @pytest.mark.parametrize(
        'schema_arg',
        [SomeSchema(), SomeSchema, __name__ + '.SomeSchema']
    )
    def test_pack(self, schema_arg):
        field = fields.Embed(schema=schema_arg)
        result = field.pack(SomeClass('one', 1))
        expected = {'name': 'one', 'number': 1}
        assert result == expected

    @pytest.mark.parametrize(
        'field',
        [
            fields.Embed(
                schema=SomeSchema(many=True, only='number')
            ),
            fields.Embed(
                schema=SomeSchema, many=True, only='number'
            ),
            fields.Embed(
                schema=__name__ + '.SomeSchema', many=True, only='number'
            )
        ]
    )
    def test_pack_with_kwargs(self, field):
        result = field.pack([SomeClass('one', 1), SomeClass('two', 2)])
        expected = [{'number': 1}, {'number': 2}]
        assert result == expected


class TestReference:
    '''Tests for Reference, a class for referencing linked objects.'''

    @pytest.mark.parametrize(
        'schema_arg',
        [SomeSchema(), SomeSchema, __name__ + '.SomeSchema']
    )
    def test_pack(self, schema_arg):
        field = fields.Reference(schema=schema_arg, field='number')
        result = field.pack(SomeClass('one', 1))
        expected = 1
        assert result == expected

    @pytest.mark.parametrize(
        'field',
        [
            fields.Reference(
                schema=SomeSchema(many=True, only='number'),
                field = 'number'
            ),
            fields.Reference(
                schema=SomeSchema, many=True, only='number',
                field = 'number'
            ),
            fields.Reference(
                schema=__name__ + '.SomeSchema', many=True, only='number',
                field = 'number'
            )
        ]
    )
    def test_pack_with_kwargs(self, field):
        result = field.pack([SomeClass('one', 1), SomeClass('two', 2)])
        expected = [1, 2]
        assert result == expected

    @pytest.mark.parametrize(
        'field',
        [
            fields.Reference(
                schema=SomeSchema(many=True, exclude='number'),
                field = 'number'
            ),
            fields.Reference(
                schema=SomeSchema, many=True, exclude='number',
                field = 'number'
            ),
            fields.Reference(
                schema=__name__ + '.SomeSchema', many=True, exclude='number',
                field = 'number'
            )
        ]
    )
    def test_fail_on_missing_field_arg(self, field):
        # field 'number' is no field of the field's associated schema instance since it
        # was excluded
        with pytest.raises(KeyError):
            result = field.pack([SomeClass('one', 1), SomeClass('two', 2)])
