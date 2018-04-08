from django.shortcuts import render

import json

from django.forms import Form, fields, widgets, ValidationError
from django.shortcuts import render, reverse, redirect, HttpResponse
from django.http import JsonResponse
from django.db.transaction import atomic
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core import  validators
from django.contrib.auth.models import User
from django import forms
from event import models
from event.my_forms import CreateEventForm, QuestionnaireForm, QuestionForm, OptionForm, MaxValueForm, AnswerForm,ChoiceForm


# Create your views here.
def profile(request):
    args = {'user': request.user}
    return render(request, 'profile.html', args)


def index(request):
    '''
    问卷列表
    '''

    userid = request.user.id
    username = request.user.username
    user_event_list = models.Event.objects.filter(user_id = userid)

    event_list_owner = user_event_list.filter(role="owner")
    event_list_vendor = user_event_list.filter(role="vendor")
    event_list_guest = user_event_list.filter(role="guest")


    create_event_form = CreateEventForm()

    args = {
        "user_event_list": user_event_list,
        "username": username,
        "create_event_form": create_event_form,
        "event_list_owner": event_list_owner,
        "event_list_vendor": event_list_vendor,
        "event_list_guest": event_list_guest,
    }

    return render(request, 'index.html',args)


def addevent(request):
    '''
    添加问卷
    '''

    if request.is_ajax():
        req_dict = json.loads(request.body.decode('utf8'))

        res_dict = {'status': True, 'error_msg': None, 'event_id': None}

        name = req_dict.get('title')
        date = req_dict.get('classroom_id')
        try:
            new_questionnaire = models.Questionnaire.objects.create(title= name)

            new_obj = models.Event.objects.create(event_name=name, event_time=date, user_id = request.user, role = 'owner', questionnaire= new_questionnaire)

            res_dict['event_id'] = new_obj.id
            res_dict['questionnaire_id'] = new_obj.questionnaire_id

        except Exception as e:
            res_dict['status'] = False
            res_dict['error_msg'] = str(e)

        return JsonResponse(res_dict)


def invite(request, event_id):
    if request.is_ajax():
        req_dict = json.loads(request.body.decode('utf8'))
        res_dict = {'status': True, 'error_msg': None}

        email_address = req_dict.get('email')
        select_role = req_dict.get('role')

        try:
            finduser = User.objects.filter(email= email_address)
            if finduser.exists():
                event = models.Event.objects.filter(id=event_id)[0]
                user_list = models.Event.objects.filter(questionnaire=event.questionnaire)
                findinlist = user_list.filter(user_id= finduser[0])
                if findinlist.exists():
                    res_dict['status'] = False
                    res_dict['error_msg'] = "Already in the list!"
                else:
                    new_obj = models.Event.objects.create(event_name=event.event_name, event_time=event.event_time, user_id=finduser[0],
                                                          role=select_role, questionnaire=event.questionnaire)
                    res_dict['userid'] = new_obj.user_id.id
                    res_dict['username'] = new_obj.user_id.username
                    res_dict['role'] = new_obj.role

            else:
                res_dict['status'] = False
                res_dict['error_msg'] = "This user hasn't been register!"

        except Exception as e:
            res_dict['status'] = False
            res_dict['error_msg'] = str(e)

        return JsonResponse(res_dict)

    else:
        event = models.Event.objects.filter(id= event_id)[0]
        user_list = models.Event.objects.filter(questionnaire= event.questionnaire).order_by('role')
        args = {'user_list':user_list}
        return render(request, 'invite.html', args)


def edit(request, naire_id):
    '''
    添加、编辑问卷页面
    '''
    username = request.user.username
    if not request.is_ajax():
        def outer():
            '''第一层生成器，返回每一个问题被QuestionForm处理后的对象'''
            question_list = models.Question.objects.filter(questionnaire_id=naire_id)
            if not question_list:
                # 如果是新添加的问卷，自动在页面生成一个空的问题
                que_form = QuestionForm()
                yield {'que_form': que_form}
            else:
                for que_obj in question_list:
                    que_form = QuestionForm(instance=que_obj)

                    temp_dict = {"que_form": que_form, "que_obj": que_obj, "class": 'hidden', "options": None, "values":None, "class2":''}
                    if que_obj.type == 2:
                        # 处理单选类问题
                        temp_dict['class'] = ''

                        def inner(question_obj):
                            '''第二层生成器，返回单选类问题的每一个选项被OptionForm处理后的对象'''
                            option_list = models.Option.objects.filter(question=question_obj)
                            for opt_obj in option_list:
                                opt_form = OptionForm(instance=opt_obj)
                                yield {"opt_form": opt_form, 'opt_obj': opt_obj}

                        # 这里必须传参，确保生成器内的question_obj一定是本次循环的que_obj
                        temp_dict['options'] = inner(que_obj)

                    elif que_obj.type == 1:
                        temp_dict['class2'] = ''

                        def inner_maxvalue(question_obj):
                            '''第二层生成器，返回单选类问题的每一个选项被OptionForm处理后的对象'''
                            value_list = models.MaxValue.objects.filter(question=question_obj)
                            for value_obj in value_list:
                                value_form = MaxValueForm(instance=value_obj)
                                yield {"value_form": value_form, 'value_obj': value_obj}

                        # 这里必须传参，确保生成器内的question_obj一定是本次循环的que_obj
                        temp_dict['values'] = inner_maxvalue(que_obj)


                    yield temp_dict

        return render(request, 'edit.html', {"username": username, "que_form_yield": outer()})

    else:
        req_que_list = json.loads(request.body.decode())
        # print(req_que_list)

        db_que_list = models.Question.objects.filter(questionnaire_id=naire_id)
        db_qid_list = [i.id for i in db_que_list]  # 数据库中所有问题的id
        post_qid_list = [i['qid'] for i in req_que_list if i['qid']]  # post提交的所有问题的id
        del_qid_set = set(db_qid_list) - set(post_qid_list)  # 待删除的问题id集合

        res_dict = {"status": True, "error_msg": None}
        try:
            with atomic():
                for qid in del_qid_set:
                    # 删除问题
                    models.Question.objects.filter(id=qid).delete()

                for que_dict in req_que_list:
                    qid = que_dict['qid']
                    title = que_dict['title']
                    type = que_dict['type']
                    vendor_view = que_dict['vendor_view']
                    if not qid:
                        # 新建问题
                        new_que_obj = models.Question.objects.create(title=title, type=type, questionnaire_id=naire_id,vendor_view=vendor_view,finalized=False)
                        if que_dict['type'] == 2:
                            for opt_dict in que_dict['options']:
                                models.Option.objects.create(content=opt_dict['content'], question=new_que_obj)
                        elif que_dict['type'] == 1:
                            models.MaxValue.objects.create(max_value= que_dict['max_value'], question=new_que_obj)
                    elif qid in db_qid_list:
                        # 更新问题，有可能存在有人在前端手动修改"qid"的情况，所以要做筛选，只更新数据库中已经存在的问题

                        update_query_set = models.Question.objects.filter(id=qid)
                        former_que_type = update_query_set.first().type
                        now_que_type = que_dict['type']
                        update_query_set.update(title=title, type=type,vendor_view=vendor_view)

                        # 对问题类型可能出现的变化做处理
                        if former_que_type == 2:
                            # 对原单选类问题的修改
                            if now_que_type == 2:
                                req_opt_list = que_dict['options']  # 在前端限制不能提交空值，这里一定不为空

                                db_opt_list = models.Option.objects.filter(question_id=qid)
                                db_oid_list = [i.id for i in db_opt_list]
                                post_oid_list = [i['oid'] for i in req_opt_list]
                                del_oid_set = set(db_oid_list) - set(post_oid_list)
                                for oid in del_oid_set:
                                    # 删除选项
                                    models.Option.objects.filter(id=oid).delete()

                                for opt_dict in req_opt_list:
                                    oid = opt_dict['oid']
                                    content = opt_dict['content']
                                    if not oid:
                                        models.Option.objects.create(content=content, question_id=qid)
                                    elif oid in db_oid_list:
                                        models.Option.objects.filter(id=oid).update(content=content)
                                    else:
                                        # 前端"oid"被恶意修改，不做任何操作
                                        pass
                            else:
                                # 单选-->其他类型，清空选项
                                models.Option.objects.filter(question_id=qid).delete()
                                if now_que_type == 1:
                                    models.MaxValue.objects.create(max_value=que_dict['max_value'], question_id= qid)
                        elif now_que_type == 2:
                            if former_que_type == 1:
                                models.MaxValue.objects.filter(question_id=qid).delete()
                            # 其他类型-->单选，创建选项
                            for opt_dict in que_dict['options']:
                                models.Option.objects.create(content=opt_dict['content'], question_id=qid)

                        elif former_que_type== 1:
                            if now_que_type == 1:
                                models.MaxValue.objects.filter(question_id=qid).update(max_value=que_dict['max_value'])
                            else:
                                models.MaxValue.objects.filter(question_id=qid).delete()
                        elif now_que_type == 1:
                            models.MaxValue.objects.create(max_value=que_dict['max_value'], question_id=qid)

                    else:
                        # 前端"qid"被恶意修改，不做任何操作
                        pass

        except Exception as e:
            res_dict['status'] = False
            res_dict['error_msg'] = str(e)
        return JsonResponse(res_dict)


def del_question(request, qid):
    '''
    删除问卷中的问题
    '''
    res_dict = {'status': None, 'error_msg': None}
    try:
        models.Question.objects.filter(id=qid).delete()
        res_dict['status'] = True
    except Exception as e:
        res_dict['error_msg'] = str(e)
    return JsonResponse(res_dict)


def delete(request):
    '''
    删除问卷
    '''
    if request.is_ajax():
        naire_id = request.GET.get('naire_id')
        res_dict = {'status': True, 'error_msg': None}
        try:
            models.Questionnaire.objects.filter(id=naire_id).delete()
        except Exception as e:
            res_dict['status'] = False
            res_dict['error_msg'] = str(e)

        return JsonResponse(res_dict)



def que_ans_form_generate(naire_id, guest):
    question_list = models.Question.objects.filter(questionnaire_id=naire_id)

    for que_obj in question_list:
        que_form = QuestionForm(instance=que_obj)



        ans_obj = models.Answer.objects.filter(question=que_obj).filter(guest= guest)
        if ans_obj.exists():
            ans_form = AnswerForm(instance=ans_obj[0])
        else:
            ans_form = AnswerForm()

        temp_dict = {"que_form": que_form, "que_obj": que_obj, "ans_form":ans_form, "ans_obj":ans_obj,
                     "options": None, "values": None, "choice_form":None ,"max_value":None}
        if que_obj.type == 2:
            def inner(question_obj):
                '''第二层生成器，返回单选类问题的每一个选项被OptionForm处理后的对象'''
                option_list = models.Option.objects.filter(question=question_obj)
                for opt_obj in option_list:
                    opt_form = OptionForm(instance=opt_obj)
                    yield {"opt_form": opt_form, 'opt_obj': opt_obj}

            # 这里必须传参，确保生成器内的question_obj一定是本次循环的que_obj
            temp_dict['options'] = inner(que_obj)


            choice_form = ChoiceForm(models.Option.objects.filter(question=que_obj).values_list("id","content"))

            temp_dict['choice_form'] = choice_form

        elif que_obj.type == 1:
            def inner_maxvalue(question_obj):
                '''第二层生成器，返回单选类问题的每一个选项被OptionForm处理后的对象'''
                value_list = models.MaxValue.objects.filter(question=question_obj)
                for value_obj in value_list:
                    value_form = MaxValueForm(instance=value_obj)
                    yield {"value_form": value_form, 'value_obj': value_obj}



            # 这里必须传参，确保生成器内的question_obj一定是本次循环的que_obj
            temp_dict['values'] = inner_maxvalue(que_obj)
            temp_dict['max_value'] = models.MaxValue.objects.get(question=que_obj).max_value

        yield temp_dict


def reply(request,naire_id):
    username = request.user.username
    if not request.is_ajax():
        que_ans_form = que_ans_form_generate(naire_id, request.user)
        return render(request, 'reply.html', {"username": username, "que_ans_form": que_ans_form})
    else:
        req_que_list = json.loads(request.body.decode())
        res_dict = {"status": True, "error_msg": None}
        try:
            for que_dict in req_que_list:

                ans_obj = models.Answer.objects.filter(question_id=que_dict['qid']).filter(guest=request.user)
                if ans_obj.count()>0:
                    if que_dict['type'] ==1:
                        ans_obj.update(value = que_dict['answer'])
                    elif que_dict['type'] ==2:
                        ans_obj.update(option_id= que_dict['answer'])
                    else:
                        ans_obj.update(content= que_dict['answer'])
                else:
                    if que_dict['type'] ==1:
                        models.Answer.objects.create(question_id=que_dict['qid'], guest=request.user, value=que_dict['answer'])
                    elif que_dict['type'] ==2:
                        models.Answer.objects.create(question_id=que_dict['qid'], guest=request.user, option_id=que_dict['answer'])
                    else:
                        models.Answer.objects.create(question_id=que_dict['qid'], guest=request.user, content=que_dict['answer'])

        except Exception as e:
            res_dict['status'] = False
            res_dict['error_msg'] = str(e)

        return JsonResponse(res_dict)


def person_form(naire_id, guest, viewer):
    question_list = models.Question.objects.filter(questionnaire_id=naire_id)
    this_event = models.Event.objects.filter(questionnaire_id = naire_id).get(user_id=viewer)
    guest_event = models.Event.objects.filter(questionnaire_id = naire_id).get(user_id=guest)

    for que_obj in question_list:

        if this_event.role != "vendor" or que_obj.vendor_view == True :
            que_form = QuestionForm(instance=que_obj)
            ans_obj = models.Answer.objects.filter(question=que_obj).filter(guest=guest)
            if ans_obj.exists():
                ans_form = AnswerForm(instance=ans_obj[0])
            else:
                ans_form = AnswerForm()

            temp_dict={"user": guest_event.user_id, "que_obj":que_obj, "que_form":que_form,"ans_form":ans_form}

            yield temp_dict



def view_form_generate(naire_id, viewer):
    this_event = models.Event.objects.filter(questionnaire_id=naire_id).get(user_id=viewer)
    if this_event.role == "guest":
        yield person_form(naire_id, viewer, viewer)
    else:
        guests = models.Event.objects.filter(questionnaire_id= naire_id).filter(role="guest")
        for guest in guests:
            yield person_form(naire_id, guest.user_id, viewer)



def view_response(request, naire_id):
    if request.method == 'GET':
        view_form = view_form_generate(naire_id, request.user)
        return render(request, 'view_response.html', {"view_form": view_form})




def finalize(request,naire_id):
    username = request.user.username
    if not request.is_ajax():


        def que_ans_gen(naire_id):
            question_list = models.Question.objects.filter(questionnaire_id=naire_id).filter(vendor_view=True)
            for que_obj in question_list:
                que_form = QuestionForm(instance=que_obj)
                temp_dict = {"que_form": que_form, "que_obj": que_obj}
                yield temp_dict

        que_ans_form = que_ans_gen(naire_id)
        return render(request, 'finalize.html', {"username": username, "que_ans_form": que_ans_form})
    else:
        req_que_list = json.loads(request.body.decode())
        res_dict = {"status": True, "error_msg": None}
        try:
            for que_dict in req_que_list:
                models.Question.objects.filter(id=que_dict['qid']).update(finalized=que_dict['finalized'])
        except Exception as e:
            res_dict['status'] = False
            res_dict['error_msg'] = str(e)

        return JsonResponse(res_dict)



