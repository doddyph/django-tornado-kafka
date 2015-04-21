from django.shortcuts import render_to_response
from django.template import RequestContext
from .forms import RegistrationForm


def register(request):
    context = RequestContext(request)
    registered = False

    if request.method == 'POST':
        reg_form = RegistrationForm(data=request.POST)

        if reg_form.is_valid():
            reg = reg_form.save()
            reg.set_password(reg.password)
            reg.save()

            registered = True
        else:
            print reg_form.errors
    else:
        reg_form = RegistrationForm()

    return render_to_response(
        'accounts/reg.html',
        {'reg_form': reg_form, 'registered': registered},
        context)


# def user_login(request):
#     context = RequestContext(request)
#
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#
#         user = authenticate(username=username, password=password)
#         if user:
#             if user.is_active:
#                 login(request, user)
#                 return HttpResponseRedirect('/demo/')
#             else:
#                 return HttpResponse("Your account is disabled.")
#         else:
#             print 'Invalid login, details: {0}, {1}'.format(username, password)
#             return HttpResponse("invalid login details supplied.")
#     else:
#         return render_to_response('accounts/login.html', {}, context)