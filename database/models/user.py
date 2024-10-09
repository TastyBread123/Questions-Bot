from tortoise import fields, models

class User(models.Model):
    id = fields.IntField(primary_key=True, unique=True)
    access = fields.IntField(default=0)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'users'
