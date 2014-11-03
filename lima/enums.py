'''Enumerations used by lima.'''

__all__ = [
    'MarshalFormat',
]


class PoorEnumMeta(type):
    '''Meta class for PoorEnum, the poor man's enumeration.'''
    def __new__(metacls, name, bases, namespace):
        # pop member values (everything not starting with '_') from namespace.
        member_values = {}
        for key, val in list(namespace.items()):
            if not key.startswith('_'):
                member_values[key] = val
                del namespace[key]

        # create class
        cls = super().__new__(metacls, name, bases, namespace)

        # add members to class (members are instances of the class themselves).
        members = set()
        for key, val in member_values.items():
            member = cls(key, val)
            members.add(member)
            setattr(cls, key, member)
        cls._members = members

        return cls

    def __contains__(cls, item):
        '''Return True if item is a member of cls, else False.'''
        return item in cls._members


class PoorEnum(metaclass=PoorEnumMeta):
    '''Poor man's enumeration.

    Poorly mimicks part of the functionality of Python's own enumerations
    (available only in Python 3.4 and newer). If at some point in the future
    Python 3.3 support will be dropped, :class:`PoorEnum` will be dropped as
    well.

    Derive from this class to create poorly behaved enumerations.

    '''
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __eq__(self, other):
        '''Return True if self is equal to other, else False.

        PoorEnum instances are only considered equal if they have *the same*
        classes and their values match.

        '''
        return self.__class__ == other.__class__ and self.value == other.value

    def __repr__(self):
        return '<{}.{}: {!r}>'.format(self.__class__.__name__,
                                      self.name, self.value)

    def __hash__(self):
        return hash(self.__class__) ^ hash(self.name)


class MarshalFormat(PoorEnum):
    '''Object marshalling format.'''

    dict = 1
    '''Objects are marshalled as a dictionaries mapping field names to field
    values.'''

    ordered_dict = 2
    '''Objects are marshalled as ordered dictionaries
    (:class:`collections.OrderedDict`) mapping field names to field values.'''

    tuples = 3
    '''Objects are marshalled as lists of *(field name, field
    value)*-tuples.'''

    list = 4
    '''Objects are marshalled as lists of field values.'''
