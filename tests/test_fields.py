'''tests for the fields module'''

import datetime as dt

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
    fields.DateTime
]

LINKED_OBJECT_FIELDS = [
    fields._LinkedObjectField,
    fields.Embed,
    fields.Nested,  # to be deprecated in 0.5
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
    '''Test error on supplying more than one of get, val and attr.'''
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
    assert not hasattr(field, 'attr')
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


class TestLinkedObjectFields:

    class LinkedSchema(schema.Schema):
        foo = fields.Integer()
        bar = fields.String()

    @pytest.mark.parametrize('cls', LINKED_OBJECT_FIELDS)
    def test_linked_object_by_schema_inst(self, cls):
        schema_inst = self.LinkedSchema(many=True)
        field = cls(schema=schema_inst)
        assert field._schema_arg is schema_inst
        assert field._schema_inst is schema_inst
        assert field._schema_inst.many == True

    @pytest.mark.parametrize('cls', LINKED_OBJECT_FIELDS)
    def test_linked_object_by_schema_class(self, cls):
        schema_cls = self.LinkedSchema
        field = cls(schema=schema_cls, many=True)
        assert field._schema_arg is schema_cls
        assert isinstance(field._schema_inst, schema_cls)
        assert field._schema_inst.many == True

    @pytest.mark.parametrize('cls', LINKED_OBJECT_FIELDS)
    def test_linked_object_by_schema_name(self, cls):
        schema_name = self.__class__.__qualname__ + '.LinkedSchema'
        field = cls(schema=schema_name, many=True)
        assert field._schema_arg is schema_name
        assert isinstance(field._schema_inst, self.LinkedSchema)
        assert field._schema_inst.many == True

    @pytest.mark.parametrize('cls', LINKED_OBJECT_FIELDS)
    def test_linked_object_fail_on_unnecessary_kwargs(self, cls):
        schema_inst = self.LinkedSchema()
        # here we supply a kwarg, even though schema is already instantiated
        field = cls(schema=schema_inst, many=True)
        with pytest.raises(ValueError):
            field._schema_inst  # this will complain about our earlier error

    @pytest.mark.parametrize('cls', LINKED_OBJECT_FIELDS)
    def test_linked_object_fail_on_nonexistent_class(self, cls):
        # here we supply a nonexistent schema name
        field = cls(schema='NonExistentSchemaName')
        with pytest.raises(exc.ClassNotFoundError):
            field._schema_inst  # this will complain about our earlier error

    @pytest.mark.parametrize('cls', LINKED_OBJECT_FIELDS)
    def test_linked_object_fail_on_illegal_schema_arg(self, cls):
        # here we supply a wrong schema arg
        field = cls(schema=0xbad1dea)
        with pytest.raises(TypeError):
            field._schema_inst  # this will complain about our earlier error

    def test_linked_object_field_pack_not_implemented(self):
        field = fields._LinkedObjectField(schema='ThisDoesntEvenHaveToExist')
        with pytest.raises(NotImplementedError):
            field.pack('foo')
