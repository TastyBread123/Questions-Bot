from tortoise import fields, models


class User(models.Model):
    id = fields.BigIntField(primary_key=True, unique=True)
    access = fields.IntField(default=0)
    current_contest = fields.BigIntField(null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'users'


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

