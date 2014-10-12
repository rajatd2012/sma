# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.CharField(help_text=b'Enter the answer text that you want displayed', max_length=1000)),
                ('correct', models.BooleanField(default=False, help_text=b'Is this a correct answer?')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course', models.CharField(max_length=250, unique=True, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Course',
                'verbose_name_plural': 'Courses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.CommaSeparatedIntegerField(max_length=1024)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Progress',
                'verbose_name_plural': 'User progress records',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.CharField(help_text=b'Enter the question text that you want displayed', max_length=1000, verbose_name=b'Question')),
                ('explanation', models.TextField(help_text=b'Explanation to be shown after the question has been answered.', max_length=2000, verbose_name=b'Explanation', blank=True)),
            ],
            options={
                'ordering': ['course'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MCQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='learn.Question')),
            ],
            options={
                'verbose_name': 'Multiple Choice Question',
                'verbose_name_plural': 'Multiple Choice Questions',
            },
            bases=('learn.question',),
        ),
        migrations.CreateModel(
            name='Essay_Question',
            fields=[
                ('question_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='learn.Question')),
            ],
            options={
                'verbose_name': 'Essay style question',
            },
            bases=('learn.question',),
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=60)),
                ('description', models.TextField(help_text=b'a description of the quiz', blank=True)),
                ('url', models.SlugField(help_text=b'a user friendly url', max_length=60, verbose_name=b'user friendly url')),
                ('random_order', models.BooleanField(default=False, help_text=b'Display the questions in a random order or as they are set?')),
                ('answers_at_end', models.BooleanField(default=False, help_text=b'Correct answer is NOT shown after question. Answers displayed at the end.')),
                ('exam_paper', models.BooleanField(default=False, help_text=b'If yes, the result of each attempt by a user will be stored. Necessary for marking.')),
                ('single_attempt', models.BooleanField(default=False, help_text=b'If yes, only one attempt by a user will be permitted. Non users cannot sit this exam.')),
                ('pass_mark', models.SmallIntegerField(default=0, help_text=b'Percentage required to pass exam.', blank=True, validators=[django.core.validators.MaxValueValidator(100)])),
                ('success_text', models.TextField(help_text=b'Displayed if user passes.', blank=True)),
                ('fail_text', models.TextField(help_text=b'Displayed if user fails.', blank=True)),
                ('course', models.ForeignKey(to='learn.Course')),
            ],
            options={
                'verbose_name': 'Quiz',
                'verbose_name_plural': 'Quizzes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sitting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question_list', models.CommaSeparatedIntegerField(max_length=1024)),
                ('incorrect_questions', models.CommaSeparatedIntegerField(max_length=1024, blank=True)),
                ('current_score', models.IntegerField()),
                ('complete', models.BooleanField(default=False)),
                ('user_answers', models.TextField(default=b'{}', blank=True)),
                ('quiz', models.ForeignKey(to='learn.Quiz')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('view_sittings', 'Can see completed exams.'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TF_Question',
            fields=[
                ('question_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='learn.Question')),
                ('correct', models.BooleanField(default=False, help_text=b'Tick this if the question is true. Leave it blank for false.')),
            ],
            options={
                'ordering': ['course'],
                'verbose_name': 'True/False Question',
                'verbose_name_plural': 'True/False Questions',
            },
            bases=('learn.question',),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('picture', models.ImageField(upload_to=b'profile_images', blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='question',
            name='course',
            field=models.ForeignKey(blank=True, to='learn.Course', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='question',
            name='quiz',
            field=models.ManyToManyField(to='learn.Quiz', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(to='learn.MCQuestion'),
            preserve_default=True,
        ),
    ]
