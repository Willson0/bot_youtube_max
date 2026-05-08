from tortoise import fields, models

class User(models.Model):
    id = fields.BigIntField(primary_key=True, unique=True)
    blocked_us = fields.BooleanField(default=False)

    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'users'


class RefUser(models.Model):
    id = fields.BigIntField(primary_key=True, unique=True)
    link = fields.CharField(max_length=30)
    blocked_us = fields.BooleanField(default=False)

    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'referal_users'


class File(models.Model):
    id = fields.BigIntField(primary_key=True, unique=True)
    file_id = fields.CharField(max_length=300)
    file_name = fields.CharField(max_length=300)
    downloads = fields.IntField(default=0)

    button_link = fields.CharField(max_length=500, null=True)
    button_name = fields.CharField(max_length=50, null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'files'


class Download(models.Model):
    id = fields.BigIntField(primary_key=True, unique=True)
    file = fields.ForeignKeyField('models.File', related_name='download_file')
    user = fields.ForeignKeyField('models.User', related_name='download_user')

    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'downloads'


class Sponsor(models.Model):
    id = fields.BigIntField(primary_key=True, unique=True)
    need_check = fields.BooleanField(default=False)
    channel_id = fields.BigIntField(null=True)
    link = fields.CharField(max_length=500)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'sponsors'


class Shows(models.Model):
    id = fields.BigIntField(primary_key=True, unique=True)
    active = fields.BooleanField(default=True)

    need_count = fields.IntField()
    current_count = fields.IntField(default=0)

    text = fields.TextField(null=True)
    media_file = fields.TextField(null=True)
    markup = fields.TextField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'shows'


class Link(models.Model):
    id = fields.IntField(primary_key=True, unique=True)
    name = fields.CharField(max_length=30)
    file_id = fields.BigIntField(null=True)
    hide = fields.BooleanField(default=False)

    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'links'
