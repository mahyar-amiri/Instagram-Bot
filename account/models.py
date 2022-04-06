from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=True, null=True, verbose_name='ایمیل')

    phone_regex = RegexValidator(regex=r'^09\d{9}$', message='')
    phone = models.CharField(validators=[phone_regex], max_length=11, blank=True, null=True, verbose_name='شماره تماس', help_text='شماره را بصورت *********09 وارد کنید')

    pass_word = models.CharField(max_length=100, verbose_name='رمزعبور')
    
    telegram_id = models.IntegerField(blank=True, null=True, verbose_name='شناسه تلگرام')
    instagram_id = models.IntegerField(blank=True, null=True, verbose_name='شناسه اینستاگرام')

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return self.name()

    def name(self):
        if self.get_full_name():
            return self.get_full_name()
        else:
            return self.username
    name.short_description = 'نام کاربر'

    def is_verified(self):
        if self.telegram_id and self.instagram_id:
            return True
        else:
            return False
    is_verified.boolean = True
    is_verified.short_description = 'تایید شده'
