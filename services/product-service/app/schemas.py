from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from decimal import Decimal

class ProductSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2))
    description = fields.Str(required=True, validate=validate.Length(min=10))
    price = fields.Decimal(required=True, places=2, validate=validate.Range(min=0.01))
    category = fields.Str(required=True)
    stock = fields.Int(required=True, validate=validate.Range(min=0))
    image_url = fields.Str(required=False)
    sku = fields.Str(required=False)

class ProductUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=2))
    description = fields.Str(validate=validate.Length(min=10))
    price = fields.Decimal(places=2, validate=validate.Range(min=0.01))
    category = fields.Str()
    stock = fields.Int(validate=validate.Range(min=0))
    image_url = fields.Str()
    sku = fields.Str()

class ProductSearchSchema(Schema):
    query = fields.Str(required=True)