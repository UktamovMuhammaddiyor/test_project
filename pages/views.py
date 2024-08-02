from django.shortcuts import render, HttpResponse, redirect
from .models import *
import random
import json
import requests
from .creditionals import URL, BOT_API, QUESTION_URL
from django.views.decorators.csrf import csrf_exempt
from .telegramAPI import sendMessage
from django.contrib.auth.decorators import login_required


# Create your views here.
def index(request):
    return render(request, template_name="index.html")


@login_required
def add_question(request):
    if request.method == 'POST':
        question_data = {}
        name = request.POST['name']
        subject = Subject.objects.create(name=name)

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
        print(question_data)
        
        return render(request, "add_question_score.html", {"subject": subject}) # Redirect to a success page or render the same page

    return render(request, 'add_question.html')


@login_required
def add_question_score(request):
    if request.method == 'POST':
        score = {
            "5": request.POST.get("score5"),
            "4": request.POST.get("score4"),
            "3": request.POST.get("score3"),
            "2": request.POST.get("score2"),
            "1": request.POST.get("score1"),
            "0": request.POST.get("score0"),            
        }
        previous_score = request.POST.get("score5")

        if request.POST.get("score4"):
            previous_score = request.POST.get("score4")
        else:
            score["4"] = previous_score
        if request.POST.get("score3"):
            previous_score = request.POST.get("score3")
        else:
            score["3"] = previous_score
        if request.POST.get("score2"):
            previous_score = request.POST.get("score2")
        else:
            score["2"] = previous_score
        if request.POST.get("score1"):
            previous_score = request.POST.get("score1")
        else:
            score["1"] = previous_score
        if request.POST.get("score0") == "":
            score["0"] = previous_score

        subject = Subject.objects.filter(id=request.POST.get("subject_id"))
        
        if subject:
            subject[0].scores = score
            subject[0].save()

            return render(request, 'add_question_success.html', {"subject": subject[0]})
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
            
            score = correct_answers * 100 / len(answers)
            
            match score:
                case score if score >= 90:
                    score = subject.scores["5"]
                case score if score >= 70:
                    score = subject.scores["4"]
                case score if score >= 60:
                    score = subject.scores["3"]
                case score if score >= 40:
                    score = subject.scores["2"]
                case score if score >= 20:
                    score = subject.scores["1"]
                case score if score >= 0:
                    score = subject.scores["0"] 
            
            result = {
                "questions_count": len(answers),
                "correct_answers": correct_answers,
                "score": score
            }
        
        return render(request, "result.html", {"subject": subject, "result": result})

    return HttpResponse("Hello")


@login_required
def setwebhook(request):
    response = requests.post(BOT_API + 'setWebhook?url=' + URL).json()
    return HttpResponse(f'{response}')


@csrf_exempt
def get_post(request):
    if request.method == "POST":
        response = json.loads(request.body)
        if 'message' in response:
            response = response['message']
        
        user = get_user(response)
        chat_id = ""

        print(response)
        if "from" in response:
            chat_id = response['from']['id']
        
        if "text" in response:
            text = response['text']

            if text[:6] == "/start":
                main_post = MainPostForBot.objects.filter(why="MainPost")
                if main_post:
                    main_post = main_post[0]
                    markup = ['keyboard', [[["Testlar bo'limi.", "", ""]]]]
                    entities = main_post.entities
                    entities = entities['entities']

                    sendMessage(chat_id, main_post.text, message_type=main_post.file_type, reply_markup=markup, file_id=main_post.file, entities=entities)
            elif text == "/getAdmin":
                user.status = "gettingAdmin"
                sendMessage(chat_id, "Iltimos parolni kiriting: ")
            elif user.status == "gettingAdmin":
                user.status = ""

                if text == "1":
                    user.is_admin = True
                    reply_markup = ["keyboard", [[["/addMainPost", "", ""]], [['/addAutoAnswerForTest', '', '']]]]
                    sendMessage(chat_id, "✅ Endi siz adminsiz.", reply_markup=reply_markup)
                else:
                    sendMessage(chat_id, "❌ Parol xato!!!")
            elif text == "Testlar bo'limi.":
                user.status = "test"
                markup = ['keyboard', []]
                subjects = Subject.objects.all()

                for subject in subjects:
                    markup[1].append([[f'{subject.name}', f'{subject.id}', '']])

                markup[1].append([["🔝 Asosiy menyuga qaytish", '', '']])
                auto_answer = MainPostForBot.objects.filter(why="autoAnswerForTest")
                entities = {"entities": ""}

                if auto_answer:
                    entities = auto_answer[0].entities
                    entities = entities['entities']
                    auto_answer = auto_answer[0].text
                else:
                    auto_answer = "O'quv markazning testlar to'plamiga xush kelibsiz!\nDarajangizga mos testni ishlang va menejerga murojaat qiling.\nTestda omad tilaymiz! 😉"

                sendMessage(chat_id, auto_answer, reply_markup=markup, entities=entities)
            elif text == "🔙 Back":
                pass
            elif text == "🔝 Asosiy menyuga qaytish":
                user.status = ""
                markup = ['keyboard', [[["Testlar bo'limi.", "", ""]]]]
                sendMessage(chat_id, "Iltimos menyulardan(pastdagi tugmalardan) birini tanlang: --->", reply_markup=markup)
            elif user.status == "test":
                subject = Subject.objects.filter(name=text)

                if subject:
                    message = f"<a href='{QUESTION_URL}{subject[0].id}'>{text}</a>"
                    sendMessage(chat_id, message)
                else:
                    sendMessage(chat_id, "Bunday test topilmadi iltimos menyudagi testlardan birini tanglang.")
            elif not user.is_admin:
                pass
            elif text == "/addMainPost":
                user.status = "addingMainPostMessage"
                sendMessage(chat_id, "Iltimos postning matnini jo'nating: --->")
            elif user.status == "addingMainPostMessage":
                user.status = "addingMainPostFile"
                entities = {"entities": ""}
                if 'entities' in response:
                    entities = {'entities': response['entities']}

                MainPostForBot.objects.create(text=text, post_id=user.user_id, why="MainPost", entities=entities)

                sendMessage(chat_id, "Iltimos postga video yoki rasm jo'nating: --->\n\n <i>Agar rasm yoki video bo'lmasa 'n' ni jo'nating: ---></i>")
            elif user.status == 'addingMainPostFile':
                user.status == ''
                post = MainPostForBot.objects.filter(post_id=user.user_id)

                if post:
                    main_posts = MainPostForBot.objects.filter(why="MainPost")
                    for main_post in main_posts:
                        if main_post.id == post[1].id:
                            post[1].file_type = "Photo"
                            post[1].file = file_id
                            post[1].save()
                        else:
                            main_post.delete()
                
                    sendMessage(chat_id, "Post qo'shildi.")
                else:
                    sendMessage(chat_id, "Post o'chib ketgan boshqattan yarating.")
            elif text == "/addAutoAnswerForTest":
                user.status = "addingAutoAnswerForTest"
                sendMessage(chat_id, "Iltiom javob matnini jo'nating: --->")
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
                sendMessage(chat_id, "Auto javob qo'shildi.")
        elif "photo" in response:
            file_id = response['photo'][-1]['file_id']

            if user.status == "addingMainPostFile":
                user.status = ""
                post = MainPostForBot.objects.filter(post_id=user.user_id)

                if post:
                    main_posts = MainPostForBot.objects.filter(why="MainPost")
                    for main_post in main_posts:
                        if main_post.id == post[1].id:
                            post[1].file_type = "Photo"
                            post[1].file = file_id
                            post[1].save()
                        else:
                            main_post.delete()
                
                    sendMessage(chat_id, "Post qo'shildi.")
                else:
                    sendMessage(chat_id, "Post o'chib ketgan boshqattan yarating.")      
        elif "video" in response:
            file_id = response['video']['file_id']

            if user.status == "addingMainPostFile":
                user.status = ""
                post = MainPostForBot.objects.filter(post_id=user.user_id)

                if post:
                    main_posts = MainPostForBot.objects.filter(why="MainPost")
                    for main_post in main_posts:
                        if main_post.id == post[1].id:
                            post[1].file_type = "Video"
                            post[1].file = file_id
                            post[1].save()
                        else:
                            main_post.delete()
                
                    sendMessage(chat_id, "Post qo'shildi.")
                else:
                    sendMessage(chat_id, "Post o'chib ketgan boshqattan yarating.")
        else:
            if user.status == "addingMainPostFile":
                sendMessage(chat_id, "Iltimos rasm yoki video jo'nating: --->")     

        user.save()
    return HttpResponse("done")


def get_user(response):
    try:
        user = BotUser.objects.get(user_id=response['from']['id'])
    except:
        username, first_name, last_name = "", "", ""
        if "username" in response['from']:
            username = response['from']['username']
        if "first_name" in response['from']:
            first_name = response['from']['username']
        if "last_name" in response['from']:
            last_name = response['from']['username']
        user = BotUser.objects.create(user_id=response['from']['id'], user_name=username, name=(first_name + last_name))

    return user
