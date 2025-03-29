from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Questions, Answers, UserProfile
from openpyxl import Workbook
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User


def is_admin(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.is_admin

@user_passes_test(is_admin)
def admin_panel(request):
    # Get all participants created by the current admin
    participants = User.objects.filter(userprofile__created_by=request.user)
    return render(request, 'main/admin_panel.html', {'participants': participants})

@user_passes_test(is_admin)
def export_user_answers(request, user_id):
    # Get the user and their answers
    user = User.objects.get(id=user_id)
    answers = Answers.objects.filter(user=user).select_related('question')

    # Create a new workbook and select the active worksheet
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Answers"

    # Add headers to the worksheet
    headers = ["Question", "Answer", "Answer Value"]
    worksheet.append(headers)

    # Add data rows to the worksheet
    for answer in answers:
        row = [
            answer.question.quest,  # Question text
            "Yes" if answer.answer else "No",  # Answer (Yes/No)
            answer.answer_value,  # Answer value
        ]
        worksheet.append(row)

    # Create an HTTP response with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=answers_{user.username}.xlsx'

    # Save the workbook to the response
    workbook.save(response)

    return response


def export_answers_to_excel(request):
    # Create a new workbook and select the active worksheet
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Answers"

    # Add headers to the worksheet
    headers = ["User", "Question", "Answer", "Answer Value"]
    worksheet.append(headers)

    # Fetch all answers from the database
    answers = Answers.objects.select_related('user', 'question').all()

    # Add data rows to the worksheet
    for answer in answers:
        row = [
            answer.user.username,  # User's username
            answer.question.quest,  # Question text
            "Yes" if answer.answer else "No",  # Answer (Yes/No)
            answer.answer_value,  # Answer value
        ]
        worksheet.append(row)

    # Create an HTTP response with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=answers.xlsx'

    # Save the workbook to the response
    workbook.save(response)

    return response


@login_required
def questions_list(request):
    # Get all questions
    questions_list = Questions.objects.all()

    # Paginate the questions (10 questions per page)
    paginator = Paginator(questions_list, 10)
    page_number = request.GET.get('page')  # Get the current page number from the URL
    page_obj = paginator.get_page(page_number)  # Get the Page object for the current page

    return render(request, 'main/questions_list.html', {'page_obj': page_obj})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Check if the user is an admin
            if hasattr(user, 'userprofile') and user.userprofile.is_admin:
                return redirect('admin_panel')  # Redirect admins to the admin panel
            else:
                return redirect('home')  # Redirect non-admin users to the questions list
        else:
            return render(request, 'main/login.html', {'error': 'Invalid username or password'})
    
    return render(request, 'main/login.html')

@login_required
def submit_answer(request):
    if request.method == 'POST':
        question_id = request.POST.get('question_id')
        answer = request.POST.get('answer') == 'true'  # Convert string to boolean

        try:
            question = Questions.objects.get(num=question_id)
            
            # Calculate answer_value based on the user's answer and the question's y/n values
            if answer:  # User answered "Yes"
                answer_value = question.y  # Use the value from the 'y' column
            else:  # User answered "No"
                answer_value = question.n  # Use the value from the 'n' column

            # Check if the user has already answered this question
            answer_obj, created = Answers.objects.get_or_create(
                question=question,
                user=request.user,
                defaults={
                    'answer': answer,
                    'answer_value': answer_value,  # Set the calculated answer_value
                }
            )
            if not created:
                # Update the existing answer
                answer_obj.answer = answer
                answer_obj.answer_value = answer_value
                answer_obj.save()
        except Questions.DoesNotExist:
            # Handle the case where the question does not exist
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return redirect('questions_list')



def user_logout(request):
    logout(request)
    return redirect('login')

