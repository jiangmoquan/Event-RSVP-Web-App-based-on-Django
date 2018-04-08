from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


# Create your models here.

class Questionnaire(models.Model):

    title = models.CharField(max_length=64, verbose_name='问卷标题')

    class Meta:
        verbose_name_plural = '问卷表'

    def __str__(self):
        return self.title


class Event(models.Model):

    event_name = models.CharField(max_length=100, default='')
    event_time = models.CharField(max_length=100, default='')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, default='')
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)


class Question(models.Model):

    title = models.CharField(max_length=64, verbose_name='问题标题')
    questionnaire = models.ForeignKey(Questionnaire, verbose_name='所属问卷', on_delete=models.CASCADE)
    question_types = [
        (1, '打分'),
        (2, '单选'),
        (3, '建议'),
    ]
    type = models.IntegerField(choices=question_types, verbose_name='问题类型')

    vendor_view = models.BooleanField(default=False)
    finalized = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = '问题表'

    def __str__(self):
        return self.title


class Option(models.Model):
    content = models.CharField(max_length=16, verbose_name='选项名称')
    question = models.ForeignKey(to='Question', verbose_name='所属问题', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '选项表'

    def __str__(self):
        return self.content

class MaxValue(models.Model):
    max_value = models.IntegerField(verbose_name='MaxValue')
    question = models.ForeignKey(to='Question', verbose_name='所属数量问题', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'maxvalue'




class Answer(models.Model):
    value = models.IntegerField(null=True, blank=True, verbose_name='后台分值')
    option = models.ForeignKey(null=True, blank=True, to='Option', verbose_name='对应选项', on_delete=models.CASCADE)
    content = models.CharField(max_length=64, null=True, blank=True, verbose_name='文本内容')

    guest = models.ForeignKey(User, on_delete= models.CASCADE)
    question = models.ForeignKey(to='Question', verbose_name='所属问题', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '问题答案表'

    def __str__(self):
        if self.content:
            return self.content
        else:
            return str(self.value)
