# from django.shortcuts import render, HttpResponse, redirect
# from django.contrib.auth.models import User
# from django.contrib.auth import login, authenticate
# # Create your views here.
# def signup(request):
#     # HttpResponse("signup here.")
#     # fail=False
#     if request.method =="post":
#         name = request.POST["name"]
#         email = request.POST["email"]
#         username= request.POST["uname"]
#         password = request.POST["pass"]
#         if(User.objects.filter(username=username)):
#             fail=True
#             return render(request, "registration/signup.html", {'fail':True} )
#         user = authenticate(username=username, password=password, email=email, firstname=name)
#         login(request, user)
#         # return redirect('home')
#         return redirect("")
#     return render(request, "registration/signup.html", {'fail':False} )


from django.shortcuts import render, redirect
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        uform = UserUpdateForm(request.POST, instance=request.user)
        pform = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, f'Account has been updated.')
            return redirect('profile')
    else:
        uform = UserUpdateForm(instance=request.user)
        pform = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'registration/profile.html', {'uform': uform, 'pform': pform})



@login_required
def SearchView(request):
    if request.method == 'POST':
        kerko = request.POST.get('search')
        print(kerko)
        results = User.objects.filter(username__contains=kerko)
        context = {
            'results':results
        }
        return render(request, 'users/search_result.html', context)
