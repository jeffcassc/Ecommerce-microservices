from marshmallow import Schema, fields, validate, validates_schema, ValidationError

class NotificationSchema(Schema):
    recipient = fields.Email(required=True)
    subject = fields.Str(required=True, validate=validate.Length(min=5))
    content = fields.Str(required=True, validate=validate.Length(min=10))
    notification_type = fields.Str(required=True, 
                                 validate=validate.OneOf(['WELCOME', 'CART_REMOVAL', 'ORDER_CONFIRMATION']))
    status = fields.Str(required=False, 
                       validate=validate.OneOf(['PENDING', 'SENT', 'FAILED']))

class NotificationQuerySchema(Schema):
    recipient = fields.Email(required=False)
    notification_type = fields.Str(required=False)
    status = fields.Str(required=False)
    start_date = fields.DateTime(required=False)
    end_date = fields.DateTime(required=False)

    @validates_schema
    def validate_dates(self, data, **kwargs):
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] > data['end_date']:
                raise ValidationError("End date must be after start date")