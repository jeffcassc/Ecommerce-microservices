from marshmallow import Schema, fields, validate, validates_schema, ValidationError

class CartItemSchema(Schema):
    productId = fields.Str(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))

class AddCartItemSchema(Schema):
    userId = fields.Str(required=True)
    productId = fields.Str(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))

class RemoveCartItemSchema(Schema):
    userId = fields.Str(required=True)