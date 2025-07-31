from marshmallow import Schema, fields, validate

class UserRegistrationSchema(Schema):
    username = fields.username(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    name = fields.Str(required=True, validate=validate.Length(min=2))

class UserUpdateSchema(Schema):
    username = fields.username(required=True)
    name = fields.Str(validate=validate.Length(min=2))
    empid = fields.Str(validate=validate.Length(min=4))