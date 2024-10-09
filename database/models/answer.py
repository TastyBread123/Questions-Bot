from tortoise import fields, models

class Answer(models.Model):
    id = fields.IntField(primary_key=True, unique=True)
    question = fields.ForeignKeyField('models.Question', related_name='question_answers')
    creator = fields.ForeignKeyField('models.User', related_name='user_answer')
    variant = fields.IntField()
    is_right = fields.BooleanField()

    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'answers'
