from django.urls import path
from .views import index, edit_question, delete_subject, get_test_info, tests, courses, available_courses, auth_admin, add_question, add_question_score, get_test, check_answers, get_post, setwebhook


urlpatterns = [
    path('', index, name="home"),
    path('addQuestion', add_question, name="addQuestion"),
    path('editQuestion', edit_question, name="editQuestion"),
    path('addQuestionScore', add_question_score, name="addQuestionScore"),
    path('test', get_test, name='test'),
    path('checkAnswers', check_answers, name='checkAnswers'),
    path('getpost/', get_post, name='getpost'),
    path('setwebhook', setwebhook, name='setwebhook'),
    path('authAdmin', auth_admin, name='authAdmin'),
    path('tests', tests, name='tests'),
    path('courses', courses, name='courses'),
    path('availableCourses', available_courses, name='availableCourses'),
    path('getTest', get_test_info, name='getTest'),
    path('deleteSubject', delete_subject, name='deleteSubject'),
]
