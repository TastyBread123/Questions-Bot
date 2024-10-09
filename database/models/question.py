from tortoise import fields, models

class Question(models.Model):
    id = fields.IntField(primary_key=True, unique=True)
    contest = fields.ForeignKeyField('models.Contest', related_name='questions')
    title = fields.TextField()
    description = fields.TextField()
    right_variant = fields.IntField(null=True)
    variants = fields.JSONField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'questions'
