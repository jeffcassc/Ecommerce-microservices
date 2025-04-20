from marshmallow import Schema, fields, validate, validates_schema, ValidationError

class UserSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2))
    last_name = fields.Str(required=True, validate=validate.Length(min=2))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    phone = fields.Str(required=False)
    

    @validates_schema
    def validate_unknown_fields(self, data, **kwargs):
        # Permite campos adicionales pero valida los requeridos
        unknown = set(self.fields) - set(data)
        if unknown:
            raise ValidationError(f"Unknown field: {list(unknown)[0]}")

class UserUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=2))
    last_name = fields.Str(validate=validate.Length(min=2))
    email = fields.Email()
    phone = fields.Str()
    address = fields.Str()

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

