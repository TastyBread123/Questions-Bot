from tortoise import fields, models

class Contest(models.Model):
    id = fields.IntField(primary_key=True, unique=True)
    creator = fields.ForeignKeyField('models.User', related_name='contests')
    title = fields.TextField()
    description = fields.TextField()
    dop_texts = fields.JSONField(null=True)
    active = fields.BooleanField(default=False)

    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'contests'
