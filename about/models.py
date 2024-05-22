from django.db import models


class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()


class Feedback(models.Model):
    info = models.TextField()
