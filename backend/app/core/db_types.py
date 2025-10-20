"""
Custom database types that work across PostgreSQL and SQLite
"""
from sqlalchemy import Text, TypeDecorator, BigInteger, Integer
from sqlalchemy.dialects.postgresql import ARRAY, JSON as PostgresJSON
import json


class BigIntegerType(TypeDecorator):
    """
    Custom type that uses BigInteger for PostgreSQL and Integer for SQLite
    This ensures proper auto-increment behavior in both databases
    """
    impl = BigInteger
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'sqlite':
            return dialect.type_descriptor(Integer)
        else:
            return dialect.type_descriptor(BigInteger)


class ArrayType(TypeDecorator):
    """
    Custom type that uses ARRAY for PostgreSQL and JSON for SQLite
    """
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(ARRAY(Text))
        else:
            return dialect.type_descriptor(Text)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            # For SQLite, convert list to JSON string
            return json.dumps(value) if value is not None else None

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            # For SQLite, parse JSON string back to list
            return json.loads(value) if value else None


class JSONType(TypeDecorator):
    """
    Custom type that uses JSON for both PostgreSQL and SQLite
    """
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresJSON)
        else:
            return dialect.type_descriptor(Text)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            # For SQLite, convert to JSON string
            return json.dumps(value) if value is not None else None

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            # For SQLite, parse JSON string
            return json.loads(value) if value else None
