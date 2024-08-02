from django.urls import path
from .views import index, add_question, add_question_score, get_test, check_answers, get_post, setwebhook


urlpatterns = [
    path('', index, name="Home"),
    path('addQuestion', add_question, name="addQuestion"),
    path('addQuestionScore', add_question_score, name="addQuestionScore"),
    path('test', get_test, name='test'),
    path('checkAnswers', check_answers, name='checkAnswers'),
    path('getpost/', get_post, name='getpost'),
    path('setwebhook', setwebhook, name='setwebhook'),
]
