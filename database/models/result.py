from tortoise import fields, models

class Result(models.Model):
    id = fields.IntField(primary_key=True, unique=True)
    user = fields.ForeignKeyField('models.User', related_name='user_results')
    contest = fields.ForeignKeyField('models.Contest', related_name='contest_results')
    right_answers = fields.IntField()
    all_answers = fields.IntField()
    dop_text = fields.TextField()

    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'results'
