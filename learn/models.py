import re
import json

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator

from model_utils.managers import InheritanceManager


# Create your models here.

class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)

    # The additional attributes we wish to include.
    picture = models.ImageField(upload_to='profile_images', blank=True)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username  
		
class CourseManager(models.Manager):

    def new_course(self, course):
        new_course = self.create(course=re.sub('\s+', '-', course)
                                   .lower())

        new_course.save()
        return new_course

class Course(models.Model):

    course = models.CharField(max_length=250,
                                blank=True,
                                unique=True,
                                null=True)

    objects = CourseManager()

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __unicode__(self):
        return unicode(self.course)

class Quiz(models.Model):

    title = models.CharField(max_length=60,
                             blank=False)

    description = models.TextField(blank=True,
                                   help_text="a description of the quiz")

    url = models.SlugField(max_length=60,
                           blank=False,
                           help_text="a user friendly url",
                           verbose_name="user friendly url")

    course = models.ForeignKey(Course)

    random_order = models.BooleanField(blank=False,
                                       default=False,
                                       help_text="Display the questions in "
                                                 "a random order or as they "
                                                 "are set?")

    answers_at_end = models.BooleanField(blank=False,
                                         default=False,
                                         help_text="Correct answer is NOT"
                                                   " shown after question."
                                                   " Answers displayed at"
                                                   " the end.")

    exam_paper = models.BooleanField(blank=False,
                                     default=False,
                                     help_text="If yes, the result of each"
                                               " attempt by a user will be"
                                               " stored. Necessary for"
                                               " marking.")

    single_attempt = models.BooleanField(blank=False,
                                         default=False,
                                         help_text="If yes, only one attempt"
                                                   " by a user will be"
                                                   " permitted. Non users"
                                                   " cannot sit this exam.")

    pass_mark = models.SmallIntegerField(blank=True,
                                         default=0,
                                         help_text="Percentage required to"
                                                   " pass exam.",
                                         validators=[
                                             MaxValueValidator(100)])

    success_text = models.TextField(blank=True,
                                    help_text="Displayed if user passes.")

    fail_text = models.TextField(blank=True,
                                 help_text="Displayed if user fails.")

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.url = re.sub('\s+', '-', self.url).lower()

        self.url = ''.join(letter for letter in self.url if
                           letter.isalnum() or letter == '-')

        if self.single_attempt is True:
            self.exam_paper = True

        if self.pass_mark > 100:
            raise ValidationError(u'%s is above 100' % self.pass_mark)

        super(Quiz, self).save(force_insert, force_update, *args, **kwargs)

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"

    def __unicode__(self):
        return unicode(self.title)

    def get_questions(self):
        return self.question_set.all().select_subclasses()

    @property
    def get_max_score(self):
        return self.get_questions().count()

    def anon_score_id(self):
        return str(self.id) + "_score"

    def anon_q_list(self):
        return str(self.id) + "_q_list"


class ProgressManager(models.Manager):

    def new_progress(self, user):
        new_progress = self.create(user=user,
                                   score="")
        new_progress.save()
        return new_progress


class Progress(models.Model):
    """
    Progress is used to track an individual signed in users score on different
    quiz's and categories

    Data stored in csv using the format:
        course, score, possible, course, score, possible, ...
    """
    user = models.OneToOneField("auth.User")

    score = models.CommaSeparatedIntegerField(max_length=1024)

    objects = ProgressManager()

    class Meta:
        verbose_name = "User Progress"
        verbose_name_plural = "User progress records"

    def list_all_course_scores(self):
        """
        Returns a dict in which the key is the course name and the item is
        a list of three integers.

        The first is the number of questions correct,
        the second is the possible best score,
        the third is the percentage correct.

        The dict will have one key for every course that you have defined
        """
        score_before = self.score
        output = {}

        for crs in Course.objects.all():
            to_find = re.escape(Course.course) + r",(\d+),(\d+),"
            #  group 1 is score, group 2 is highest possible

            match = re.search(to_find, self.score, re.IGNORECASE)

            if match:
                score = int(match.group(1))
                possible = int(match.group(2))

                try:
                    percent = int(round((float(score) / float(possible))
                                        * 100))
                except:
                    percent = 0

                output[cat.course] = [score, possible, percent]

            else:  # if course has not been added yet, add it.
                self.score += cat.course + ",0,0,"
                output[cat.course] = [0, 0]

        if len(self.score) > len(score_before):
            # If a new course has been added, save changes.
            self.save()

        return output

    def check_cat_score(self, course_queried):
        """
        Pass in a course, get the users score and possible maximum score
        as the integers x,y respectively
        """
        course_test = Course.objects.filter(course=course_queried) \
                                        .exists()

        if course_test is False:
            return "error", "course does not exist"

        to_find = re.escape(course_queried) +\
            r",(?P<score>\d+),(?P<possible>\d+),"
        match = re.search(to_find, self.score, re.IGNORECASE)

        if match:
            return int(match.group('score')), int(match.group('possible'))

        else:  # if not found but course exists, add course with 0 points
            self.score += course_queried + ",0,0,"
            self.save()

            return 0, 0

    def update_score(self, course, score_to_add=0, possible_to_add=0):
        """
        Pass in string of the course name, amount to increase score
        and max possible.

        Does not return anything.
        """
        course_test = Course.objects.filter(course=course) \
                                        .exists()

        if any([course_test is False, score_to_add is False,
                possible_to_add is False, str(score_to_add).isdigit() is False,
                str(possible_to_add).isdigit() is False]):
            return "error", "course does not exist or invalid score"

        to_find = re.escape(str(course)) +\
            r",(?P<score>\d+),(?P<possible>\d+),"

        match = re.search(to_find, self.score, re.IGNORECASE)

        if match:
            updated_score = int(match.group('score')) + abs(score_to_add)
            updated_possible = int(match.group('possible')) +\
                abs(possible_to_add)

            new_score = (str(course) + "," +
                         str(updated_score) + "," +
                         str(updated_possible) + ",")

            # swap old score for the new one
            self.score = self.score.replace(match.group(), new_score)
            self.save()

        else:
            #  if not present but existing, add with the points passed in
            self.score += (str(course) + "," +
                           str(score_to_add) + "," +
                           str(possible_to_add) + ",")
            self.save()

    def show_exams(self):
        """
        Finds the previous quizzes marked as 'exam papers'.
        Returns a queryset of complete exams.
        """
        return Sitting.objects.filter(user=self.user) \
                              .filter(complete=True)



class SittingManager(models.Manager):

    def new_sitting(self, user, quiz):
        if quiz.random_order is True:
            question_set = quiz.question_set.all() \
                                            .select_subclasses() \
                                            .order_by('?')
        else:
            question_set = quiz.question_set.all() \
                                            .select_subclasses()

        questions = ""
        for question in question_set:
            questions += str(question.id) + ","

        new_sitting = self.create(user=user,
                                  quiz=quiz,
                                  question_list=questions,
                                  incorrect_questions="",
                                  current_score=0,
                                  complete=False,
                                  user_answers='{}')
        new_sitting.save()
        return new_sitting

    def user_sitting(self, user, quiz):
        if quiz.single_attempt is True and self.filter(user=user,
                                                       quiz=quiz,
                                                       complete=True)\
                                               .count() > 0:
            return False

        try:
            sitting = self.get(user=user, quiz=quiz, complete=False)
        except Sitting.DoesNotExist:
            sitting = self.new_sitting(user, quiz)
        except Sitting.MultipleObjectsReturned:
            sitting = self.filter(user=user, quiz=quiz, complete=False)[0]
        finally:
            return sitting


class Sitting(models.Model):
    """
    Used to store the progress of logged in users sitting a quiz.
    Replaces the session system used by anon users.

    Question_list is a list of integers which represent id's of
    the unanswered questions in csv format.

    Incorrect_questions is a list in the same format.

    Sitting deleted when quiz finished unless quiz.exam_paper is true.

    User_answers is a json object in which the question PK is stored
    with the answer the user gave.
    """

    user = models.ForeignKey('auth.User')

    quiz = models.ForeignKey(Quiz)

    question_list = models.CommaSeparatedIntegerField(max_length=1024)

    incorrect_questions = models.CommaSeparatedIntegerField(max_length=1024,
                                                            blank=True)

    current_score = models.IntegerField()

    complete = models.BooleanField(default=False, blank=False)

    user_answers = models.TextField(blank=True, default='{}')

    objects = SittingManager()

    class Meta:
        permissions = (("view_sittings", "Can see completed exams."),)

    def get_first_question(self):
        """
        Returns the next question.
        If no question is found, returns False
        Does NOT remove the question from the front of the list.
        """
        first_comma = self.question_list.find(',')
        if first_comma == -1 or first_comma == 0:
            return False
        question_id = int(self.question_list[:first_comma])
        return Question.objects.get_subclass(id=question_id)

    def remove_first_question(self):
        first_comma = self.question_list.find(',')
        if first_comma != -1 or first_comma != 0:
            self.question_list = self.question_list[first_comma + 1:]
            self.save()

    def add_to_score(self, points):
        self.current_score += int(points)
        self.save()

    @property
    def get_current_score(self):
        return self.current_score

    @property
    def get_percent_correct(self):
        dividend = float(self.current_score)
        divisor = self.quiz.question_set.all().select_subclasses().count()
        if divisor < 1:
            return 0            # prevent divide by zero error

        if dividend > divisor:
            return 100

        correct = int(round((dividend / divisor) * 100))

        if correct >= 1:
            return correct
        else:
            return 0

    def mark_quiz_complete(self):
        self.complete = True
        self.save()

    def add_incorrect_question(self, question):
        """
        Adds uid of incorrect question to the list.
        The question object must be passed in.
        """
        if len(self.incorrect_questions) > 0:
            self.incorrect_questions += ','
        self.incorrect_questions += str(question.id) + ","
        if self.complete:
            self.add_to_score(-1)
        self.save()

    @property
    def get_incorrect_questions(self):
        """
        Returns a list of non empty integers, representing the pk of
        questions
        """
        return [int(q) for q in self.incorrect_questions.split(',') if q]

    def remove_incorrect_question(self, question):
        current = self.get_incorrect_questions
        current.remove(question.id)
        self.incorrect_questions = ','.join(map(str, current))
        self.add_to_score(1)
        self.save()

    @property
    def check_if_passed(self):
        if self.get_percent_correct >= self.quiz.pass_mark:
            return True
        else:
            return False

    @property
    def result_message(self):
        if self.check_if_passed:
            return self.quiz.success_text
        else:
            return self.quiz.fail_text

    def add_user_answer(self, question, guess):
        current = json.loads(self.user_answers)
        current[question.id] = guess
        self.user_answers = json.dumps(current)
        self.save()

    @property
    def questions_with_user_answers(self):
        output = {}
        user_answers = json.loads(self.user_answers)
        for question in self.quiz.question_set.all().select_subclasses():
            output[question] = user_answers[unicode(question.id)]
        return output


class Question(models.Model):
    """
    Base class for all question types.
    Shared properties placed here.
    """

    quiz = models.ManyToManyField(Quiz,
                                  blank=True)

    course = models.ForeignKey(Course,
                                 blank=True,
                                 null=True)

    content = models.CharField(max_length=1000,
                               blank=False,
                               help_text="Enter the question text that "
                                         "you want displayed",
                               verbose_name='Question')

    explanation = models.TextField(max_length=2000,
                                   blank=True,
                                   help_text="Explanation to be shown "
                                             "after the question has "
                                             "been answered.",
                                   verbose_name='Explanation')

    objects = InheritanceManager()

    class Meta:
        ordering = ['course']

    def __unicode__(self):
        return unicode(self.content)

		
class TF_Question(Question):
    correct = models.BooleanField(blank=False,
                                  default=False,
                                  help_text="Tick this if the question "
                                            "is true. Leave it blank for"
                                            " false.")

    def check_if_correct(self, guess):
        if guess == "True":
            guess_bool = True
        elif guess == "False":
            guess_bool = False
        else:
            return False

        if guess_bool == self.correct:
            return True
        else:
            return False

    def get_answers(self):
        return [{'correct': self.check_if_correct("True"),
                 'content': 'True'},
                {'correct': self.check_if_correct("False"),
                 'content': 'False'}]

    def get_answers_list(self):
        return [(True, True), (False, False)]

    def answer_choice_to_string(self, guess):
        return str(guess)

    class Meta:
        verbose_name = "True/False Question"
        verbose_name_plural = "True/False Questions"
        ordering = ['course']

class MCQuestion(Question):

    def check_if_correct(self, guess):
        answer = Answer.objects.get(id=guess)

        if answer.correct is True:
            return True
        else:
            return False

    def get_answers(self):
        return Answer.objects.filter(question=self)

    def get_answers_list(self):
        return [(answer.id, answer.content) for answer in
                Answer.objects.filter(question=self)]

    def answer_choice_to_string(self, guess):
        return Answer.objects.get(id=guess).content

    class Meta:
        verbose_name = "Multiple Choice Question"
        verbose_name_plural = "Multiple Choice Questions"


class Answer(models.Model):
    question = models.ForeignKey(MCQuestion)

    content = models.CharField(max_length=1000,
                               blank=False,
                               help_text="Enter the answer text that "
                                         "you want displayed")

    correct = models.BooleanField(blank=False,
                                  default=False,
                                  help_text="Is this a correct answer?")

    def __unicode__(self):
        return unicode(self.content)

		
class Essay_Question(Question):

    def check_if_correct(self, guess):
        return False

    def get_answers(self):
        return False

    def get_answers_list(self):
        return False

    def answer_choice_to_string(self, guess):
        return str(guess)

    def __unicode__(self):
        return unicode(self.content)

    class Meta:
        verbose_name = "Essay style question"
		