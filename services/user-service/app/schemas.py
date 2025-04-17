from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2))
    last_name = fields.Str(required=True, validate=validate.Length(min=2))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    phone = fields.Str(required=False)
    address = fields.Str(required=False)

class UserUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=2))
    last_name = fields.Str(validate=validate.Length(min=2))
    email = fields.Email()
    phone = fields.Str()
    address = fields.Str()

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))