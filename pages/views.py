from django.shortcuts import render, HttpResponse, redirect
from .models import *
import random
import json
import requests
from .creditionals import URL, BOT_API, QUESTION_URL
from django.views.decorators.csrf import csrf_exempt
from .telegramAPI import sendMessage, deleteMessage, forwardMessage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages


# Create your views here.
def index(request):
    print(request.user)
    return render(request, template_name="index.html")


def auth_admin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


@login_required
def tests(request):
    subjects = Subject.objects.all()
    return render(request, "for_admin/tests.html", {'subjects': subjects})


@login_required
def delete_subject(request):
    subject_id = request.GET['id']
    subject = Subject.objects.filter(id=subject_id)
    if subject:
        subject[0].delete()
    
    return redirect(tests)


@login_required
def get_test_info(request):
    pass


@login_required
def edit_question(request):
    subject = ""
    if request.method == "POST":
        question_data = {}
        name = request.POST['subject_id']
        branch = SubjectBranch.objects.filter(name=request.POST['branch'])
        
        if branch:
            branch = branch[0]
        else:
            branch = SubjectBranch.objects.create(name=request.POST['branch'])

        subject = Subject.objects.filter(id=name)
        subject = subject[0]
        
        for key, value in request.POST.items():
            if key.startswith('question'):
                question_id = key.replace('question', '')
                question_text = value
                options = []
                for option_key, option_value in request.POST.items():
                    if option_key.startswith(f'answer-{question_id}-'):
                        options.append(option_value)
                answer = request.POST.get(f'option{question_id}')
                question_data[question_id] = {
                    'text': question_text,
                    'options': options,
                    'answer': answer,
                }

        for key, value in request.FILES.items():
            if key.startswith('file'):
                question_id = key.replace('file', '')
                question_data[question_id]['file'] = value

        old_questions = Test.objects.filter(subject=subject)
        for old_question in old_questions:
            old_question.delete()

        for question_id, data in question_data.items():
            test = Test.objects.create(
                subject=subject,
                text=data['text'],
                answer=data['answer'],
                options={'options': data['options']}
            )
            if 'file' in data:
                Image.objects.create(question=test, image=data['file'])
        
        number_of_questions = Test.objects.filter(subject=subject)
        count = len(number_of_questions)
        subject.count = count
        subject.save()
        count = range(count + 1)
        
        return render(request, "for_admin/edit_question_score.html", {"subject": subject, 'count': count}) # Redirect to a success page or render the same page
    else:
        subject_id = request.GET['id']
        subject = Subject.objects.filter(id=subject_id)

    if subject:
        questions = Test.objects.filter(subject=subject[0])
        branches = SubjectBranch.objects.all()
        return render(request, "for_admin/editQuestion.html", {"subject": subject[0], "branches": branches, "questions": questions})
    else:
        return HttpResponse("Fan topilmadi.")


@login_required
def courses(request):
    return render(request, "for_admin/courses.html") 


@login_required
def available_courses(request):
    return render(request, "for_admin/available_courses.html") 


@login_required
def add_question(request):
    if request.method == 'POST':
        question_data = {}
        name = request.POST['name']
        branch = SubjectBranch.objects.filter(name=request.POST['branch'])
        
        if branch:
            branch = branch[0]
        else:
            branch = SubjectBranch.objects.create(name=request.POST['branch'])

        subject = Subject.objects.create(branch_name=branch,name=name)
        
        for key, value in request.POST.items():
            if key.startswith('question'):
                question_id = key.replace('question', '')
                question_text = value
                options = []
                for option_key, option_value in request.POST.items():
                    if option_key.startswith(f'answer-{question_id}-'):
                        options.append(option_value)
                answer = request.POST.get(f'option{question_id}')
                question_data[question_id] = {
                    'text': question_text,
                    'options': options,
                    'answer': answer,
                }

        for key, value in request.FILES.items():
            if key.startswith('file'):
                question_id = key.replace('file', '')
                question_data[question_id]['file'] = value

        for question_id, data in question_data.items():
            test = Test.objects.create(
                subject=subject,
                text=data['text'],
                answer=data['answer'],
                options={'options': data['options']}
            )
            if 'file' in data:
                Image.objects.create(question=test, image=data['file'])
        
        number_of_questions = Test.objects.filter(subject=subject)
        count = len(number_of_questions)
        subject.count = count
        subject.save()
        count = range(count + 1)
        
        return render(request, "add_question_score.html", {"subject": subject, 'count': count}) # Redirect to a success page or render the same page

    branches = SubjectBranch.objects.all()
    return render(request, 'add_question.html', {'branches': branches})


@login_required
def add_question_score(request):
    if request.method == 'POST':

        qolib = {
            "min": 0,
            "max": 100,
            "grade": "",
        }
        score = []

        for key, value in request.POST.items():
            if key.startswith("score"):
                qolib = {
                    "min": int(request.POST[f'from{key[5:]}']),
                    "max": int(request.POST[f'to{key[5:]}']),
                    "grade": value, 
                }
                score.append(qolib)
        
        subject = Subject.objects.filter(id=request.POST.get("subject_id"))

        if subject:
            subject = subject[0]
            subject.scores = {'score': score}
            subject.is_active = True
            subject.save()

            return render(request, 'add_question_success.html', {'subject': subject})
    return redirect(index)


def get_test(request):
    id = request.GET.get('id')
    subject = Subject.objects.filter(id=id)
    if subject:
        subject = subject[0]
    else:
        return render(request, "error_test.html")
    
    tests = {
        "name": subject.name,
        "id": subject.id,
        "count": 0,
        "questions": [],
    }
    test = {
        "id": "",
        "text": "",
        "image": "",
        "options": [],
    }

    questions = Test.objects.filter(subject=subject)

    for question in questions:
        test = test.copy()
        test['id'] = question.id
        test["text"] = question.text
        options = []

        for option_key, option in enumerate(question.options['options']):
            options.append({
                "id": option_key + 1,
                "value": option
            }) 

        random.shuffle(options)    
        test['options'] = options
        image = Image.objects.filter(question=question)

        if image:
            test["image"] = image[0].image
        else:
            test['image'] = ""
        
        tests["questions"].append(test)
    
    random.shuffle(tests["questions"])

    tests["count"] = len(tests["questions"])

    return render(request, "test.html", {"questions": tests["questions"], 'subject': tests})


@csrf_exempt
def check_answers(request): 
    if request.method == "POST":
        answers = json.loads(request.POST['answers'])
        subject = Subject.objects.filter(id=answers['subject_id'])
        if subject:
            subject = subject[0]
            answers = answers['answers']
            correct_answers = 0

            for answer in answers:
                test = Test.objects.filter(id=answer['id'])
                
                if test:
                    if int(answer['answer']) == test[0].answer:
                        correct_answers += 1
            
            
            for score in subject.scores['score']:
                if correct_answers >= score['min'] and correct_answers <= score['max']:
                    score = score['grade']
                    break
            
            result = {
                "questions_count": len(answers),
                "correct_answers": correct_answers,
                "score": score
            }
        
        return render(request, "result.html", {"subject": subject, "result": result})

    return redirect(index)


# telegram bot start
@login_required
def setwebhook(request):
    response = requests.post(BOT_API + 'setWebhook?url=' + URL).json()
    return HttpResponse(f'{response}')


@csrf_exempt
def get_post(request):
    if request.method == "POST":
        response = json.loads(request.body)

        if "my_chat_member" not in response:
            response = list(response.values())[1]
            user = get_user(response)
        else:
            user = get_user(response['my_chat_member'])
        
        from_id = ""
        menu_markup = ['keyboard', [[["Testlar bo'limi.", "", ""]], [["Kurslar haqida ma'lumot", '', '']]]]

        if "from" in response:
            from_id = response['from']['id']
            
        if "my_chat_member" in response:
            response = response['my_chat_member']
            chat = response['chat']
            new_chat = response['new_chat_member']
            chat_id = chat['id']

            if new_chat['status'] == "member":
                sendMessage(chat_id, "Iltimos botni kanalga admin qiling.")
            elif new_chat['status'] == "administrator":
                try:
                    group = TgGroup.objects.get(group_id=chat_id)
                except:
                    if 'username' in chat:
                        group = TgGroup.objects.create(name=chat['title'], group_link=f"https://t.me/{chat['username']}", group_id=chat_id)
                    else:
                        group = TgGroup.objects.create(name=chat['title'], group_id=chat_id)
                sendMessage(chat_id, "Iltimos guruhni qo'shish uchun parolni tering.")
        elif 'data' in response:
            data = response['data']

            if data.startswith('course-'):
                deleteMessage(response['from']['id'], response['message']['message_id'])
                get_course(from_id, int(data[7:]))
            elif data.startswith('get-course-'):
                deleteMessage(response['from']['id'], response['message']['message_id'])
                get_course_for_user(from_id, int(data[11:]))
            elif data.startswith('question-from-course-'):
                user.status = data
                deleteMessage(response['from']['id'], response['message']['message_id'])

                sendMessage(from_id, "Iltimos savllingizni yozib qoldiring. Siz bilan tez orada adminlarimizdan biri bog'lanadi.")
            elif data == "back_to_courses_for_user":
                deleteMessage(response['from']['id'], response['message']['message_id'])
                markup = get_courses_for_user()
                sendMessage(from_id, "Kurslar ro'yhati.", reply_markup=markup)
            elif data.startswith("edit-course-name-"):
                deleteMessage(response['from']['id'], response['message']['message_id'])
                user.status = data
                
                sendMessage(from_id, "Aha, nima deb nomlamoqchisiz: --->")
            elif data.startswith("edit-course-description-"):
                deleteMessage(response['from']['id'], response['message']['message_id'])
                user.status = data
                
                sendMessage(from_id, "Aha, nimaga o'zgartirmoqchisiz: --->")
            elif data.startswith("edit-course-teachers-"):
                deleteMessage(response['from']['id'], response['message']['message_id'])
                user.status = data
                
                sendMessage(from_id, "Aha, o'zgartirilgan o'qituvchilarni jo'nating: --->")
            elif data.startswith("edit-course-media-"):
                deleteMessage(response['from']['id'], response['message']['message_id'])
                user.status = data
                
                sendMessage(from_id, "Aha, kurs uchun video yoki rasm jo'nating: --->\n\n <i>Agar rasm yoki video bo'lmasa 'n' ni jo'nating: ---></i>")
            elif data.startswith("delete-course-"):
                deleteMessage(response['from']['id'], response['message']['message_id'])
                user.status = data
                
                sendMessage(from_id, "Bu kursni rostan o'chirmoqchimisiz? Ha / Yo'q ")
            elif data == "back_to_courses":
                deleteMessage(response['from']['id'], response['message']['message_id'])
                markup = get_courses()
                sendMessage(from_id, "Kurslar ro'yhati.", reply_markup=markup)
            elif data.startswith("activate-course-"):
                course = Course.objects.get(id=int(data[16:]))
                course.is_active = True
                course.save()
                
                deleteMessage(response['from']['id'], response['message']['message_id'])
                get_course(from_id, int(data[16:]))
            elif data.startswith("deactivate-course-"):
                course = Course.objects.get(id=int(data[18:]))
                course.is_active = False
                course.save()
                
                deleteMessage(response['from']['id'], response['message']['message_id'])
                get_course(from_id, int(data[18:]))
            elif data == "addForQuestions":
                group = TgGroup.objects.filter(group_id=response['message']['chat']['id'])
                groups = TgGroup.objects.filter(group_for="Questions")

                for group2 in groups:
                    group2.is_active = False
                    group2.save()

                if group:
                    group = group[0]
                    group.is_active = True
                    group.group_for = "Questions"
                    group.save()
                    deleteMessage(group.group_id, response['message']['message_id'])
                    sendMessage(group.group_id, "Gruh qo'shildi")
                else:
                    sendMessage(response['meassage']['chat']['id'], "Gruh topilmadi. Iltimos botni admin qiling.")
            elif data.startswith("open-course-"):
                user.status = data
                deleteMessage(response['from']['id'], response['message']['message_id'])
                sendMessage(from_id, "Kursni ochilish sanasini kiriting.\nMisol uchun: <i>22.05.2024</i>")
        elif response['chat']['type'] == 'supergroup' or response['chat']['type'] == 'group':
            if 'reply_to_message' in response:
                if response['reply_to_message']['from']['is_bot'] and ('forward_origin' in response['reply_to_message']):
                    sender_id = ForwardMessage.objects.filter(forwarded_message_id=response['reply_to_message']['message_id'])
                        
                    if sender_id:
                        sender_id = sender_id[0]
                        requests.post(BOT_API + 'copyMessage', {
                            'chat_id': sender_id.user_id,
                            'from_chat_id': response['chat']['id'],
                            'message_id': response['message_id'],
                            'reply_parameters': json.dumps({
                                "message_id": sender_id.message_id
                            })
                        })
                elif 'text' in response['reply_to_message']:
                    if response['reply_to_message']['text'] == "Iltimos guruhni qo'shish uchun parolni tering.":
                        if response["text"] == '1':
                            deleteMessage(response['chat']['id'], response['reply_to_message']['message_id'])
                            reply_markup = ['inline_keyboard', [[["Bu kelgan savollar uchun", f'addForQuestions', '']], [["Bu ro'yhatdan o'tish uchun", "addForApplies", ""]]]]
                            sendMessage(response['chat']['id'], "Bu gruh nima uchun:", reply_markup=reply_markup)
                        else:
                            sendMessage(response['chat']['id'], "Parol nato'g'ri")
        elif "text" in response:
            text = response['text']

                                
            if text[:6] == "/start":
                main_post = MainPostForBot.objects.filter(why="MainPost")
                if main_post:
                    main_post = main_post[0]
                    entities = main_post.entities
                    entities = entities['entities']

                    sendMessage(from_id, main_post.text, message_type=main_post.file_type, reply_markup=menu_markup, file_id=main_post.file, entities=entities)
            elif text == "/getAdmin":
                user.status = "gettingAdmin"
                sendMessage(from_id, "Iltimos parolni kiriting: ")
            elif user.status == "gettingAdmin":
                user.status = ""

                if text == "1":
                    user.is_admin = True
                    reply_markup = ["keyboard", [[["/addMainPost", "", ""], ['/addCourse', '', '']], [['/courses', '', '']], [['/addAutoAnswerForTest', '', '']]]]
                    sendMessage(from_id, "✅ Endi siz adminsiz.", reply_markup=reply_markup)
                else:
                    sendMessage(from_id, "❌ Parol xato!!!")
            elif text == "Testlar bo'limi.":
                user.status = "test"
                markup = ['keyboard', []]
                subjects = SubjectBranch.objects.all()

                for subject in subjects:
                    markup[1].append([[f'{subject.name}', f'', '']])
                
                subjects = Subject.objects.all()
                
                for subject in subjects:
                    if not subject.branch_name:
                        markup[1].append([[f'{subject.name}', f'', '']])


                markup[1].append([["🔝 Asosiy menyuga qaytish", '', '']])
                auto_answer = MainPostForBot.objects.filter(why="autoAnswerForTest")
                entities = {"entities": ""}

                if auto_answer:
                    entities = auto_answer[0].entities
                    entities = entities['entities']
                    auto_answer = auto_answer[0].text
                else:
                    auto_answer = "O'quv markazning testlar to'plamiga xush kelibsiz!\nDarajangizga mos testni ishlang va menejerga murojaat qiling.\nTestda omad tilaymiz! 😉"

                sendMessage(from_id, auto_answer, reply_markup=markup, entities=entities)
            elif text == "🔙 Back":
                pass
            elif text == "🔝 Asosiy menyuga qaytish":
                user.status = ""
                sendMessage(from_id, "Iltimos menyulardan(pastdagi tugmalardan) birini tanlang: --->", reply_markup=menu_markup)
            elif text == "Kurslar haqida ma'lumot":
                user.status = ""
                markup = get_courses_for_user()

                sendMessage(from_id, "Kurslar ro'yhati.", reply_markup=markup)
            elif user.status == "test":
                subject = Subject.objects.filter(name=text)
                if subject:
                    subject = Subject.objects.filter(name=text)

                    if subject:
                        message = f"<a href='{QUESTION_URL}{subject[0].id}'>{text}</a>"
                        sendMessage(from_id, message)
                    else:
                        sendMessage(from_id, "Bunday test topilmadi iltimos menyudagi testlardan birini tanglang.")
                else:
                    user.status = "test2"
                    markup = ['keyboard', []]
                    branch = SubjectBranch.objects.filter(name=text)
                    
                    if branch:
                        branch = branch[0]
                        subjects = Subject.objects.filter(branch_name=branch, is_active=True)

                        for subject in subjects:
                            markup[1].append([[f'{subject.name}', f'', '']])

                    markup[1].append([["🔝 Asosiy menyuga qaytish", '', '']])
                    auto_answer = MainPostForBot.objects.filter(why="autoAnswerForTest")
                    entities = {"entities": ""}
                    sendMessage(from_id, "Iltimos menyudagi testlardan birini tanlang: ", reply_markup=markup, entities=entities)
            elif user.status == "test2":
                subject = Subject.objects.filter(name=text)

                if subject:
                    message = f"<a href='{QUESTION_URL}{subject[0].id}'>{text}</a>"
                    sendMessage(from_id, message)
                else:
                    sendMessage(from_id, "Bunday test topilmadi iltimos menyudagi testlardan birini tanglang.")
            elif user.status.startswith('question-from-course-'):
                group = TgGroup.objects.filter(group_for="Questions", is_active=True)

                sendMessage(from_id, "Savollingiz qabul qilindi tez orada adminlardan biri siz bilan bo'g'lanadi.")

                if group:
                    group = group[0]
                    course = Course.objects.filter(id=int(user.status[21:]))
                    if course:
                        course = course[0]
                        sendMessage(group.group_id, f"<a href='tg://user?id={user.user_id}'>{user.name}</a> foydalanuvchi \n<i>'{course.name}'</i> kursi haqida savolli bor ekan.")
                    result = forwardMessage(group.group_id, user.user_id, response['message_id'])
                    if result['ok']:
                        ForwardMessage.objects.create(message_id=response['message_id'], forwarded_message_id=result['result']['message_id'], user_id=user.user_id)
                else:
                    admin = BotUser.objects.filter(is_admin=True)
                    if admin:
                        admin = admin[0]
                        course = Course.objects.filter(id=int(user.status[21:]))
                        if course:
                            course = course[0]
                            sendMessage(group.group_id, f"<a href='tg://user?id={user.user_id}'>{user.name}</a> foydalanuvchi \n<i>'{course.name}'</i> kursi haqida savolli bor ekan.")

                        result = forwardMessage(admin.user_id, user.user_id, response['message_id'])
                        if result['ok']:
                            ForwardMessage.objects.create(message_id=response['message_id'], forwarded_message_id=result['result']['message_id'], user_id=user.user_id)
            elif not user.is_admin:
                sendMessage(from_id, "Iltimos pastdagi menyulardan birini tanglang", reply_markup=menu_markup)
            elif text == "/addMainPost":
                user.status = "addingMainPostMessage"
                sendMessage(from_id, "Iltimos postning matnini jo'nating: --->")
            elif user.status == "addingMainPostMessage":
                user.status = "addingMainPostFile"
                entities = {"entities": ""}
                if 'entities' in response:
                    entities = {'entities': response['entities']}

                MainPostForBot.objects.create(text=text, post_id=user.user_id, why="MainPost", entities=entities)

                sendMessage(from_id, "Iltimos postga video yoki rasm jo'nating: --->\n\n <i>Agar rasm yoki video bo'lmasa 'n' ni jo'nating: ---></i>")
            elif user.status == 'addingMainPostFile':
                user.status == ''
                post = MainPostForBot.objects.filter(post_id=user.user_id)

                if post and len(post) > 1:
                    main_posts = MainPostForBot.objects.filter(why="MainPost")
                    for main_post in main_posts:
                        if main_post.id == post[1].id:
                            post[1].file_type = "Photo"
                            post[1].file = file_id
                            post[1].save()
                        else:
                            main_post.delete()
                
                    sendMessage(from_id, "Post qo'shildi.")
                elif post:
                    post[0].file_type = "Photo"
                    post[0].file = file_id
                    post[0].save()
                else:
                    sendMessage(from_id, "Post o'chib ketgan boshqattan yarating.")
            elif text == "/addAutoAnswerForTest":
                user.status = "addingAutoAnswerForTest"
                sendMessage(from_id, "Iltiom javob matnini jo'nating: --->")
            elif user.status == "addingAutoAnswerForTest":
                user.status = ""
                auto_answers = MainPostForBot.objects.filter(why="autoAnswerForTest")

                if auto_answers:
                    for auto_answer in auto_answers:
                        auto_answer.delete()
                
                entities = {"entities": ""}
                if 'entities' in response:
                    entities = {'entities': response['entities']}

                MainPostForBot.objects.create(text=text, why="autoAnswerForTest", entities=entities)
                sendMessage(from_id, "Auto javob qo'shildi.")
            elif text == "/addCourse":
                user.status = "addingCourse"
                sendMessage(from_id, "Iltimos kurs nomini kiriting: ")
            elif user.status == "addingCourse":
                course = Course.objects.create(name=text)
                user.status = f"addingCourse-{course.id}"
                sendMessage(from_id, "Kurs haqida ma'lumot kiriting: --->")
            elif user.status.startswith("addingCourse-"):
                course = Course.objects.filter(id=user.status[13:])
                user.status = f"addingCourseTeachers-{user.status[13:]}"
                entities = {"entities": ""}
                if 'entities' in response:
                    entities = {'entities': response['entities']}
                if course:
                    course = course[0]
                    course.description = text
                    course.description_entities = entities
                    course.save()
                    sendMessage(from_id, "Kursning o'qtuvchilari haqida ma'lumot jo'nating: --->")
                else:
                    sendMessage(from_id, "Kurs topilmadi. Iltimos jarayyonni boshqattan boshlang.")
            elif user.status.startswith("addingCourseTeachers-"):
                course = Course.objects.filter(id=user.status[21:])
                user.status = f"addingCourseFile-{user.status[21:]}"
                entities = {"entities": ""}
                if 'entities' in response:
                    entities = {'entities': response['entities']}
                if course:
                    course = course[0]
                    course.teachers = text
                    course.teachers_entities = entities
                    course.save()
                    sendMessage(from_id, "Iltimos kurs uchun video yoki rasm jo'nating: --->\n\n <i>Agar rasm yoki video bo'lmasa 'n' ni jo'nating: ---></i>")
                else:
                    sendMessage(from_id, "Kurs topilmadi. Iltimos jarayyonni boshqattan boshlang.")
            elif user.status.startswith('addingCourseFile-'):
                course = Course.objects.filter(id=user.status[17:])
                course = course[0]
                course.is_active = True
                course.file_type = "Message"
                course.save()
                user.status = ""
                sendMessage(from_id, "Kurs qo'shildi.")
            elif text == "/courses":
                markup = get_courses()

                sendMessage(from_id, "Kurslar ro'yhati.", reply_markup=markup)
            elif user.status.startswith('edit-course-name-'):
                course = Course.objects.filter(id=user.status[17:])
                if course:
                    course = course[0]
                    course.name = text
                    course.save()
                    sendMessage(from_id, "Nomi o'zgartirildi.")
                    get_course(from_id, int(user.status[17:]))
                else:
                    sendMessage(from_id, "Kurs topilmadi. Iltimos jarayyonni boshqattan boshlang.")
                    markup = get_courses()

                    sendMessage(from_id, "Kurslar ro'yhati.", reply_markup=markup)
                user.status = ""
            elif user.status.startswith('edit-course-description-'):
                course = Course.objects.filter(id=user.status[24:])
                entities = {"entities": ""}
                if 'entities' in response:
                    entities = {'entities': response['entities']}
                if course:
                    course = course[0]
                    course.description = text
                    course.description_entities = entities
                    course.save()
                    sendMessage(from_id, "Ma'lumot o'zgartirildi.")
                    get_course(from_id, int(user.status[24:]))
                else:
                    sendMessage(from_id, "Kurs topilmadi. Iltimos jarayyonni boshqattan boshlang.")
                    markup = get_courses()

                    sendMessage(from_id, "Kurslar ro'yhati.", reply_markup=markup)
                user.status = ""  
            elif user.status.startswith('edit-course-teachers-'):
                course = Course.objects.filter(id=user.status[21:])
                entities = {"entities": ""}
                if 'entities' in response:
                    entities = {'entities': response['entities']}
                if course:
                    course = course[0]
                    course.teachers = text
                    course.teachers_entities = entities
                    course.save()
                    sendMessage(from_id, "Ma'lumot o'zgartirildi.")
                    get_course(from_id, int(user.status[21:]))
                else:
                    sendMessage(from_id, "Kurs topilmadi. Iltimos jarayyonni boshqattan boshlang.")
                    markup = get_courses()

                    sendMessage(from_id, "Kurslar ro'yhati.", reply_markup=markup)
                user.status = ""          
            elif user.status.startswith('edit-course-media-'):
                course = Course.objects.filter(id=user.status[18:])
                if course:
                    course = course[0]
                    course.file = ""
                    course.file_type = "Message"
                    course.save()
                    sendMessage(from_id, "Ma'lumot o'zgartirildi.")
                    get_course(from_id, int(user.status[18:]))
                else:
                    sendMessage(from_id, "Kurs topilmadi. Iltimos jarayyonni boshqattan boshlang.")
                    markup = get_courses()

                    sendMessage(from_id, "Kurslar ro'yhati.", reply_markup=markup)
                user.status = ""
            elif user.status.startswith('delete-course-'):
                course = Course.objects.filter(id=user.status[14:])
                if course:
                    course = course[0]

                    if text ==  "ha" or text == "Ha":
                        course.delete()
                        markup = get_courses()

                        sendMessage(from_id, "Kurs o'chirib tashlandi.")
                        sendMessage(from_id, "Kurslar ro'yhati.", reply_markup=markup)
                    else:
                        sendMessage(from_id, "Kurs o'chirilmadi.")
                else:
                    sendMessage(from_id, "Kurs topilmadi. Iltimos jarayyonni boshqattan boshlang.")
                    markup = get_courses()

                    sendMessage(from_id, "Kurslar ro'yhati.", reply_markup=markup)
                user.status = ""
            elif user.status.startswith("open-course-"):
                course_id = int(user.status[12:])
                course = Course.objects.get(id=course_id)
                available_course = AvailableCourse.objects.create(
                    name=course.name,
                    description=course.description,
                    description_entities=course.description_entities,
                    file=course.file,
                    file_type=course.file_type,
                    start_date=text
                )
                user.status = f"opening-course-teacher-{available_course.id}"
                sendMessage(from_id, "Kurs o'qituvchisi kim?")
            elif user.status.startswith("opening-course-teacher-"):
                course = AvailableCourse.objects.filter(id=user.status[23:])
                entities = {"entities": ""}
                if 'entities' in response:
                    entities = {'entities': response['entities']}
                if course:
                    user.status = f"opening-course-date-{user.status[23:]}"
                    course = course[0]
                    course.teacher = text
                    course.teacher_entitie = entities
                    course.save()
                    sendMessage(from_id, "Kurs qaysi kunlari soat nechida bo'ladi.")
                else:
                    sendMessage(from_id, "Kurs topilmadi. Iltimos jarayyonni boshqattan boshlang.")
            elif user.status.startswith("opening-course-date-"):
                course = AvailableCourse.objects.filter(id=user.status[20:])
                if course:
                    user.status = ""
                    course = course[0]
                    course.date = text
                    course.status = "Active"
                    course.save()
                    sendMessage(from_id, "Kurs qo'shildi.")
                else:
                    sendMessage(from_id, "Kurs topilmadi. Iltimos jarayyonni boshqattan boshlang.")
            
        elif "photo" in response:
            file_id = response['photo'][-1]['file_id']

            if user.status.startswith('question-from-course-'):
                group = TgGroup.objects.filter(group_for="Questions", is_active=True)

                sendMessage(from_id, "Savollingiz qabul qilindi tez orada adminlardan biri siz bilan bo'g'lanadi.")

                if group:
                    group = group[0]
                    course = Course.objects.filter(id=int(user.status[21:]))
                    if course:
                        course = course[0]
                        sendMessage(group.group_id, f"<a href='tg://user?id={user.user_id}'>{user.name}</a> foydalanuvchi \n<i>'{course.name}'</i> kursi haqida savolli bor ekan.")
                    result = forwardMessage(group.group_id, user.user_id, response['message_id'])
                    if result['ok']:
                        ForwardMessage.objects.create(message_id=response['message_id'], forwarded_message_id=result['result']['message_id'], user_id=user.user_id)
                else:
                    admin = BotUser.objects.filter(is_admin=True)
                    if admin:
                        admin = admin[0]
                        course = Course.objects.filter(id=int(user.status[21:]))
                        if course:
                            course = course[0]
                            sendMessage(group.group_id, f"<a href='tg://user?id={user.user_id}'>{user.name}</a> foydalanuvchi \n<i>'{course.name}'</i> kursi haqida savolli bor ekan.")

                        result = forwardMessage(admin.user_id, user.user_id, response['message_id'])
                        if result['ok']:
                            ForwardMessage.objects.create(message_id=response['message_id'], forwarded_message_id=result['result']['message_id'], user_id=user.user_id)
            elif user.status == "addingMainPostFile":
                user.status = ""
                post = MainPostForBot.objects.filter(post_id=user.user_id)

                if post and len(post) > 1:
                    main_posts = MainPostForBot.objects.filter(why="MainPost")
                    for main_post in main_posts:
                        if main_post.id == post[1].id:
                            post[1].file_type = "Photo"
                            post[1].file = file_id
                            post[1].save()
                        else:
                            main_post.delete()
                
                    sendMessage(from_id, "Post qo'shildi.")
                elif post:
                    post[0].file_type = "Photo"
                    post[0].file = file_id
                    post[0].save()
                else:
                    sendMessage(from_id, "Post o'chib ketgan boshqattan yarating.")      
            elif user.status.startswith('addingCourseFile-'):
                course = Course.objects.filter(id=user.status[17:])
                course = course[0]
                course.is_active = True
                course.file = file_id
                course.file_type = "Photo"
                course.save()
                user.status = ""
                sendMessage(from_id, "Kurs qo'shildi.")
            elif user.status.startswith('edit-course-media-'):
                course = Course.objects.filter(id=user.status[18:])
                if course:
                    course = course[0]
                    course.file = file_id
                    course.file_type = "Photo"
                    course.save()
                    sendMessage(from_id, "Ma'lumot o'zgartirildi.")
                    get_course(from_id, int(user.status[18:]))
                else:
                    sendMessage(from_id, "Kurs topilmadi. Iltimos jarayyonni boshqattan boshlang.")
                    markup = get_courses()

                    sendMessage(from_id, "Kurslar ro'yhati.", reply_markup=markup)
                user.status = ""
        elif "video" in response:
            file_id = response['video']['file_id']

            if user.status.startswith('question-from-course-'):
                group = TgGroup.objects.filter(group_for="Questions", is_active=True)

                sendMessage(from_id, "Savollingiz qabul qilindi tez orada adminlardan biri siz bilan bo'g'lanadi.")

                if group:
                    group = group[0]
                    course = Course.objects.filter(id=int(user.status[21:]))
                    if course:
                        course = course[0]
                        sendMessage(group.group_id, f"<a href='tg://user?id={user.user_id}'>{user.name}</a> foydalanuvchi \n<i>'{course.name}'</i> kursi haqida savolli bor ekan.")
                    result = forwardMessage(group.group_id, user.user_id, response['message_id'])
                    if result['ok']:
                        ForwardMessage.objects.create(message_id=response['message_id'], forwarded_message_id=result['result']['message_id'], user_id=user.user_id)
                else:
                    admin = BotUser.objects.filter(is_admin=True)
                    if admin:
                        admin = admin[0]
                        course = Course.objects.filter(id=int(user.status[21:]))
                        if course:
                            course = course[0]
                            sendMessage(group.group_id, f"<a href='tg://user?id={user.user_id}'>{user.name}</a> foydalanuvchi \n<i>'{course.name}'</i> kursi haqida savolli bor ekan.")

                        result = forwardMessage(admin.user_id, user.user_id, response['message_id'])
                        if result['ok']:
                            ForwardMessage.objects.create(message_id=response['message_id'], forwarded_message_id=result['result']['message_id'], user_id=user.user_id)
            elif user.status == "addingMainPostFile":
                user.status = ""
                post = MainPostForBot.objects.filter(post_id=user.user_id)

                if post and len(post) > 1:
                    main_posts = MainPostForBot.objects.filter(why="MainPost")
                    for main_post in main_posts:
                        if main_post.id == post[1].id:
                            post[1].file_type = "Video"
                            post[1].file = file_id
                            post[1].save()
                        else:
                            main_post.delete()
                
                    sendMessage(from_id, "Post qo'shildi.")
                elif post:
                    post[0].file_type = "Photo"
                    post[0].file = file_id
                    post[0].save()
                else:
                    sendMessage(from_id, "Post o'chib ketgan boshqattan yarating.")
            elif user.status.startswith('addingCourseFile-'):
                course = Course.objects.filter(id=user.status[17:])
                course = course[0]
                course.is_active = True
                course.file = file_id
                course.file_type = "Video"
                course.save()
                user.status = ""
                sendMessage(from_id, "Kurs qo'shildi.")
            elif user.status.startswith('edit-course-media-'):
                course = Course.objects.filter(id=user.status[18:])
                if course:
                    course = course[0]
                    course.file = file_id
                    course.file_type = "Video"
                    course.save()
                    sendMessage(from_id, "Ma'lumot o'zgartirildi.")
                    get_course(from_id, int(user.status[18:]))
                else:
                    sendMessage(from_id, "Kurs topilmadi. Iltimos jarayyonni boshqattan boshlang.")
                    markup = get_courses()

                    sendMessage(from_id, "Kurslar ro'yhati.", reply_markup=markup)
                user.status = ""
        else:
            if user.status == "addingMainPostFile":
                sendMessage(from_id, "Iltimos rasm yoki video jo'nating: --->")     
            elif user.status.startswith('addingCourseFile-'):
                sendMessage(from_id, "Iltimos rasm yoki video jo'nating: --->")
            elif user.status.startswith('question-from-course-'):
                group = TgGroup.objects.filter(group_for="Questions", is_active=True)

                sendMessage(from_id, "Savollingiz qabul qilindi tez orada adminlardan biri siz bilan bo'g'lanadi.")

                if group:
                    group = group[0]
                    course = Course.objects.filter(id=int(user.status[21:]))
                    if course:
                        course = course[0]
                        sendMessage(group.group_id, f"<a href='tg://user?id={user.user_id}'>{user.name}</a> foydalanuvchi \n<i>'{course.name}'</i> kursi haqida savolli bor ekan.")
                    result = forwardMessage(group.group_id, user.user_id, response['message_id'])
                    if result['ok']:
                        ForwardMessage.objects.create(message_id=response['message_id'], forwarded_message_id=result['result']['message_id'], user_id=user.user_id)
                else:
                    admin = BotUser.objects.filter(is_admin=True)
                    if admin:
                        admin = admin[0]
                        course = Course.objects.filter(id=int(user.status[21:]))
                        if course:
                            course = course[0]
                            sendMessage(group.group_id, f"<a href='tg://user?id={user.user_id}'>{user.name}</a> foydalanuvchi \n<i>'{course.name}'</i> kursi haqida savolli bor ekan.")

                        result = forwardMessage(admin.user_id, user.user_id, response['message_id'])
                        if result['ok']:
                            ForwardMessage.objects.create(message_id=response['message_id'], forwarded_message_id=result['result']['message_id'], user_id=user.user_id)
                 

        user.save()
        
        return HttpResponse("")
    return redirect(index)


def get_user(response):
    try:
        user = BotUser.objects.get(user_id=response['from']['id'])
    except:
        username, first_name, last_name = "", "", ""
        if "username" in response['from']:
            username = response['from']['username']
        if "first_name" in response['from']:
            first_name = response['from']['first_name']
        if "last_name" in response['from']:
            last_name = response['from']['last_name']
        user = BotUser.objects.create(user_id=response['from']['id'], user_name=username, name=(first_name + last_name))

    return user


def get_courses():
    """ get course info """

    courses = Course.objects.all()

    reply_markup = ['inline_keyboard', []]
    reply_markup_inside = []
    increment = 0

    if len(courses) < 3:
        reply_markup[1].append([[course.name, f'course-{course.id}', ''] for course in courses])
    else:
        for course in courses:
            if increment < 2:
                increment += 1
                reply_markup_inside.append([course.name, f'course-{course.id}', ''])
            else:
                increment = 0
                reply_markup_inside.append([course.name, f'course-{course.id}', ''])
                reply_markup[1].append(reply_markup_inside)
                reply_markup_inside = []

    return reply_markup


def get_courses_for_user():
    """ get course info """

    courses = Course.objects.filter(is_active=True)

    reply_markup = ['inline_keyboard', []]
    reply_markup_inside = []
    increment = 0

    if len(courses) < 3:
        reply_markup[1].append([[course.name, f'get-course-{course.id}', ''] for course in courses])
    else:
        for course in courses:
            if increment < 2:
                increment += 1
                reply_markup_inside.append([course.name, f'get-course-{course.id}', ''])
            else:
                increment = 0
                reply_markup_inside.append([course.name, f'get-course-{course.id}', ''])
                reply_markup[1].append(reply_markup_inside)
                reply_markup_inside = []

    return reply_markup


def get_course(from_id, course_id):
    course = Course.objects.get(id=course_id)
    reply_markup = ['inline_keyboard', [[["Nomini O'zgartirish", f"edit-course-name-{course.id}", ""], ["Tavsifni O'zgartirish", f"edit-course-description-{course.id}", ""]], [["O'qituvchilarni o'zgartirish", f"edit-course-teachers-{course.id}", ""]], [["Faylni O'zgartirish", f"edit-course-media-{course.id}", ""], ["O'chirish", f"delete-course-{course.id}", ""]], [["Faollashtirish", f"activate-course-{course.id}", ""], ["Nofaollashtirish", f"deactivate-course-{course.id}", ""]], [["Kursni ochish.", f"open-course-{course.id}", ""]], [["Kurslar ro'yhatiga qaytish", "back_to_courses", ""]]]]

    if course.is_active:
        is_active = "Faol"
    else:
        is_active = "Faol emas"
    text = f"Kursning nomi: {course.name}\n\nO'qituvchilar:\n"
    entities = []
    for entity in course.teachers_entities['entities']:
        entity['offset'] = entity['offset'] + len(text)
        entities.append(entity)
    text = text + course.teachers + "\n\nKursning ma'lumoti:\n"
    for entity in course.description_entities['entities']:
        entity['offset'] = entity['offset'] + len(text)
        entities.append(entity)
    text = text + course.description + f"\n\nKurs: {is_active}"
         
    if course.file:
        sendMessage(from_id, text, course.file_type, entities=entities, reply_markup=reply_markup, file_id=course.file)
    else:
        sendMessage(from_id, text, entities=entities, reply_markup=reply_markup)


def get_course_for_user(from_id, course_id):
    course = Course.objects.get(id=course_id)
    reply_markup = ['inline_keyboard', [[["Kurs bo'yicha savvol yo'llash", f'question-from-course-{course.id}', '']], [["Kurslar ro'yhatiga qaytish", "back_to_courses_for_user", ""]]]]

    text = f"Kursning nomi: {course.name}\n\nO'qituvchilar:\n"
    entities = []
    for entity in course.teachers_entities['entities']:
        entity['offset'] = entity['offset'] + len(text)
        entities.append(entity)
    text = text + course.teachers + "\n\nKurs haqida qisqacha ma'lumot:\n"
    for entity in course.description_entities['entities']:
        entity['offset'] = entity['offset'] + len(text)
        entities.append(entity)
    text = text + course.description + f"\n"
         
    if course.file:
        sendMessage(from_id, text, course.file_type, entities=entities, reply_markup=reply_markup, file_id=course.file)
    else:
        sendMessage(from_id, text, entities=entities, reply_markup=reply_markup)
