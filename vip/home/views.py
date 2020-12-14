# from django.shortcuts import render
# from django.contrib.auth.forms import UserCreationForm
# from django.urls import reverse_lazy
# from django.views import generic



# def home(request):
#     return render(request, 'home/main.html')
from django.http import HttpResponseRedirect
from home.models import Poll, Comment, Fav, Choice, Profile, Follow, Issue, IssueComment
from home.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView

from django.views import View
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.humanize.templatetags.humanize import naturaltime
from home.forms import CreateForm, CommentForm, UserUpdateForm, ProfileUpdateForm, IssueCreateForm, IssueCommentForm
from home.utils import dump_queries
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q

class PollListView(OwnerListView):
    # model = Ad
    template_name = "home/poll_list.html"

    def get(self, request) :
        # ad_list = Ad.objects.all()
        # favorites = list()
        # if request.user.is_authenticated:
        #     # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
        #     rows = request.user.favorite_ads.values('id')
        #     # favorites = [2, 4, ...] using list comprehension
        #     favorites = [ row['id'] for row in rows ]
        # ctx = {'ad_list' : ad_list, 'favorites': favorites}
        # return render(request, self.template_name, ctx)

        strval =  request.GET.get("search", False)
        if strval :
            # Simple title-only search
            # objects = Post.objects.filter(title__contains=strval).select_related().order_by('-updated_at')[:10]

            # Multi-field search
            query = Q(question__contains=strval)
            query.add(Q(choice1__contains=strval), Q.OR)
            query.add(Q(choice2__contains=strval), Q.OR)
            query.add(Q(choice3__contains=strval), Q.OR)
            query.add(Q(choice4__contains=strval), Q.OR)
            # query.add(Q(owner__contains=strval), Q.OR)
            objects = Poll.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else :
            # try both versions with > 4 posts and watch the queries that happen
            objects = Poll.objects.all().order_by('-updated_at')[:10]
            # objects = Post.objects.select_related().all().order_by('-updated_at')[:10]

        # Augment the post_list
        issues = Issue.objects.all().order_by('-updated_at')[:10]
        for i in issues:
            i.natural_updated= naturaltime(i.updated_at)
        for obj in objects:
            obj.natural_updated = naturaltime(obj.updated_at)
        userobjects = User.objects.all()

        # userobjects.remove(self)
        folowings= Follow.objects.filter(user=request.user)
        followers= Follow.objects.filter(follow_user=request.user)
        # for fl in followers:
        #     userobjects.remove(fl.user)
        following_list=[]
        for fi in folowings:
            following_list.append(fi.follow_user)
        ctx = {'poll_list' : objects, 'search': strval, 'user_list': userobjects, 'issue_list': issues,'followers':followers.count(), 'followings':folowings.count(),'following_list':following_list}
        retval = render(request, self.template_name, ctx)

        dump_queries()
        return retval



class PollDetailView(OwnerDetailView):
    model = Poll
    template_name = "home/poll_detail.html"
    # permission=True
    def get(self, request, pk) :
        prof= Profile.objects.filter(user=request.user)
        print(prof)
        x = Poll.objects.get(id=pk)
        choiceset= Choice.objects.filter(poll=x)
        counttotal=0
        for choiceins in choiceset:
            counttotal+=choiceins.votes
        print(x)
        permission=False
        if(x.Required_Minimum_Age == 0 or int(prof[0].age) >= int(x.Required_Minimum_Age)):
            permission=True
        else:
            permission=False
        if((x.Required_City == '0' or str(prof[0].city) == str(x.Required_City)) and permission== True):
            permission=True
        else:
            permission=False
        if((x.Required_Sex == '0' or str(prof[0].sex) == str(x.Required_Sex)) and permission==True):
            permission=True
        else:
            permission=False
        print(permission)
        comments = Comment.objects.filter(poll=x).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'poll' : x, 'comments': comments, 'comment_form': comment_form, "profile":prof[0], "permission":permission,'ctotal':counttotal,'ccount':comments.count() }
        return render(request, self.template_name, context)

class IssueDetailView(OwnerDetailView):
    model = Issue
    template_name = "home/issue_detail.html"
    # permission=True
    def get(self, request, pk) :
        # prof= Profile.objects.filter(user=request.user)
        # print(prof)
        x = Issue.objects.get(id=pk)
        comments = IssueComment.objects.filter(issue=x).order_by('-updated_at')
        comment_form = IssueCommentForm()
        context = { 'issue' : x, 'comments': comments, 'comment_form': comment_form,'ccount':comments.count() }
        return render(request, self.template_name, context)

class PollResultView(OwnerDetailView):
    model = Poll
    template_name = "home/poll_result.html"
    def get(self, request, pk) :
        x = Poll.objects.get(id=pk)
        choiceset= Choice.objects.filter(poll=x)
        counttotal=0
        for choiceins in choiceset:
            counttotal+=choiceins.votes
        comments = Comment.objects.filter(poll=x).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'poll' : x, 'comments': comments, 'comment_form': comment_form,'ctotal':counttotal, 'ccount':comments.count()}
        return render(request, self.template_name, context)

class PollCreateView(LoginRequiredMixin, View):
    template_name = 'home/poll_form.html'
    success_url = reverse_lazy('home:all')

    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        poll = form.save(commit=False)
        poll.owner = self.request.user
        poll.save()
        ch1 = Choice(poll= poll, choice= str(poll.choice1))
        ch1.save()
        ch2 = Choice(poll= poll, choice= str(poll.choice2))
        ch2.save()
        ch3 = Choice(poll= poll, choice= str(poll.choice3))
        ch3.save()
        ch4 = Choice(poll= poll, choice= str(poll.choice4))
        ch4.save()
        return redirect(self.success_url)

class IssueCreateView(LoginRequiredMixin, View):
    template_name = 'home/issue_form.html'
    success_url = reverse_lazy('home:all')

    def get(self, request, pk=None):
        form = IssueCreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = IssueCreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        issue = form.save(commit=False)
        issue.owner = self.request.user
        issue.save()
        return redirect(self.success_url)

def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    k=request.POST['choice']
    print(k)
    if(k):
        selected_choice = poll.choice_set.get(pk=k)
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('home:poll_result', args=(poll.id,)))
    else:
        return render(request, 'home/detail.html', {
            'poll': poll,
            'error_message': "You didn't select a choice.",
        })
        

class PollUpdateView(LoginRequiredMixin, View):
    template_name = 'home/poll_form.html'
    success_url = reverse_lazy('home:all')

    def get(self, request, pk):
        poll = get_object_or_404(Poll, id=pk, owner=self.request.user)
        form = CreateForm(instance=poll)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        poll = get_object_or_404(Poll, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=poll)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        poll = form.save(commit=False)
        poll.save()

        return redirect(self.success_url)

class PollDeleteView(OwnerDeleteView):
    model = Poll


def stream_file(request, pk):
    poll = get_object_or_404(Poll, id=pk)
    response = HttpResponse()
    response['Content-Type'] = poll.content_type
    response['Content-Length'] = len(poll.picture)
    response.write(poll.picture)
    return response

class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        poll = get_object_or_404(Poll, id=pk)
        a=False
        if(request.POST.get('Anonymous',0)=="on"):
            a=True
        comment = Comment(text=request.POST['Views'],anonymous=a, owner=request.user, poll=poll)
        comment.save()
        return redirect(reverse('home:poll_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "home/comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        poll = self.object.poll
        return reverse('home:poll_detail', args=[poll.id])

class IssueUpdateView(LoginRequiredMixin, View):
    template_name = 'home/issue_form.html'
    success_url = reverse_lazy('home:all')

    def get(self, request, pk):
        issue = get_object_or_404(Issue, id=pk, owner=self.request.user)
        form = IssueCreateForm(instance=issue)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        issue = get_object_or_404(Issue, id=pk, owner=self.request.user)
        form = IssueCreateForm(request.POST, request.FILES or None, instance=issue)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        issue = form.save(commit=False)
        issue.save()

        return redirect(self.success_url)

class IssueDeleteView(OwnerDeleteView):
    model = Issue


def istream_file(request, pk):
    issue = get_object_or_404(Issue, id=pk)
    response = HttpResponse()
    response['Content-Type'] = issue.content_type
    response['Content-Length'] = len(issue.picture)
    response.write(issue.picture)
    return response

class IssueCommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        issue = get_object_or_404(Issue, id=pk)
        a=False
        if(request.POST.get('Anonymous',0)=="on"):
            a=True
        print(a)
        comment = IssueComment(text=request.POST['Views'],anonymous=a, owner=request.user, issue=issue)
        comment.save()
        return redirect(reverse('home:issue_detail', args=[pk]))

class IssueCommentDeleteView(OwnerDeleteView):
    model = IssueComment
    template_name = "home/issue_comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        issue = self.object.issue
        print(issue, issue.id)
        return reverse('home:issue_detail', args=[issue.id])

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        t = get_object_or_404(Poll, id=pk)
        fav = Fav(user=request.user, poll=t)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        t = get_object_or_404(Poll, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, poll=t).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()

@login_required
def profile(request):
    poll_list= Poll.objects.filter(owner=request.user).order_by('-updated_at')[:10]
    issue_list= Issue.objects.filter(owner= request.user).order_by('-updated_at')[:10]
    comment_list= Comment.objects.filter(owner= request.user).order_by('-updated_at')[:10]
    issue_comment_list= IssueComment.objects.filter(owner= request.user).order_by('-updated_at')[:10]
    if request.method == 'POST':
        uform = UserUpdateForm(request.POST, instance=request.user)
        pform = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, f'Account has been updated.')
            
    else:
        uform = UserUpdateForm(instance=request.user)
        pform = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'home/profile.html', {'uform': uform, 'pform': pform,'poll_list':poll_list, 'issue_list':issue_list, 'comment_list':comment_list, 'issue_comment_list':issue_comment_list,})

@login_required
def SearchView(request):
    if request.method == 'POST':
        kerko = request.POST.get('search')
        print(kerko)
        results = User.objects.filter(username__contains=kerko)
        # results+= User.
        context = {
            'results':results
        }
        return render(request, 'home/search_result.html', context)

# class UserPostListView(LoginRequiredMixin, ListView):
#     model = Poll
#     template_name = 'home/user_posts.html'
#     context_object_name = 'polls'

#     def visible_user(self):
#         return get_object_or_404(User, username=self.kwargs.get('username'))

#     def get_context_data(self, **kwargs):
#         visible_user = self.visible_user()
#         logged_user = self.request.user
#         print(logged_user.username == '')

#         if logged_user.username == '' or logged_user is None:
#             can_follow = False
#         else:
#             can_follow = (Follow.objects.filter(user=logged_user,
#                                                 follow_user=visible_user).count() == 0)
#         data = super().get_context_data(**kwargs)

#         data['user_profile'] = visible_user
#         data['can_follow'] = can_follow
#         return data

#     def get_queryset(self):
#         user = self.visible_user()
#         return Poll.objects.filter(owner=user).order_by('-updated_at')

#     def post(self, request, *args, **kwargs):
#         if request.user.id is not None:
#             follows_between = Follow.objects.filter(user=request.user,
#                                                     follow_user=self.visible_user())

#             if 'follow' in request.POST:
#                     new_relation = Follow(user=request.user, follow_user=self.visible_user())
#                     if follows_between.count() == 0:
#                         new_relation.save()
#             elif 'unfollow' in request.POST:
#                     if follows_between.count() > 0:
#                         follows_between.delete()

#         return self.get(self, request, *args, **kwargs)

@login_required
def UserDetail(request, viewusername):
    viewuser=User.objects.filter(username=viewusername)[0]
    poll_list= Poll.objects.filter(owner=viewuser).order_by('-updated_at')[:10]
    issue_list= Issue.objects.filter(owner= viewuser).order_by('-updated_at')[:10]
    comment_list= Comment.objects.filter(owner= viewuser).order_by('-updated_at')[:10]
    issue_comment_list= IssueComment.objects.filter(owner= viewuser).order_by('-updated_at')[:10]

    if(viewuser==request.user):
        if request.method == 'POST':
            uform = UserUpdateForm(request.POST, instance=request.user)
            pform = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
    
            if uform.is_valid() and pform.is_valid():
                uform.save()
                pform.save()
                messages.success(request, f'Account has been updated.')
                
        else:
            uform = UserUpdateForm(instance=request.user)
            pform = ProfileUpdateForm(instance=request.user.profile)
    
        return render(request, 'home/profile.html', {'uform': uform, 'pform': pform,'poll_list':poll_list, 'issue_list':issue_list, 'comment_list':comment_list, 'issue_comment_list':issue_comment_list,})
    elif(request.user.id is not None):
        follows_between = Follow.objects.filter(user=request.user,follow_user=viewuser)
        canfollow=True
        canunfollow=False
        if(follows_between.count()==0):
            canfollow=True
        else:
            canfollow=False
        if(follows_between.count()==1):
            canunfollow=True
        else:
            canunfollow=False
        prof=Profile.objects.filter(user=viewuser)[0]
        folowings= Follow.objects.filter(user=viewuser)
        followers= Follow.objects.filter(follow_user=viewuser)
        context={'viewuser':viewuser, 'prof':prof,'canfollow':canfollow, 'canunfollow':canunfollow, 'followers':followers.count(), 'followings':folowings.count(),'poll_list':poll_list, 'issue_list':issue_list, 'comment_list':comment_list, 'issue_comment_list':issue_comment_list,}
        return render(request, 'home/user_detail.html', context)

@login_required
def FollowView(request, viewusername):
    viewuser=User.objects.filter(username=viewusername)[0]
    poll_list= Poll.objects.filter(owner=viewuser).order_by('-updated_at')[:10]
    issue_list= Issue.objects.filter(owner= viewuser).order_by('-updated_at')[:10]
    comment_list= Comment.objects.filter(owner= viewuser).order_by('-updated_at')[:10]
    issue_comment_list= IssueComment.objects.filter(owner= viewuser).order_by('-updated_at')[:10]
    prof=Profile.objects.filter(user=viewuser)[0]
    new_relation = Follow(user=request.user, follow_user=viewuser)
    new_relation.save()
    folowings= Follow.objects.filter(user=viewuser)
    followers= Follow.objects.filter(follow_user=viewuser)
    context={'viewuser':viewuser, 'prof':prof, 'canfollow':False, 'canunfollow':True ,'followers':followers.count(), 'followings':folowings.count(),'poll_list':poll_list, 'issue_list':issue_list, 'comment_list':comment_list, 'issue_comment_list':issue_comment_list,}
    return render(request, 'home/user_detail.html', context)

@login_required
def UnfollowView(request, viewusername):
    viewuser=User.objects.filter(username=viewusername)[0]
    poll_list= Poll.objects.filter(owner=viewuser).order_by('-updated_at')[:10]
    issue_list= Issue.objects.filter(owner= viewuser).order_by('-updated_at')[:10]
    comment_list= Comment.objects.filter(owner= viewuser).order_by('-updated_at')[:10]
    issue_comment_list= IssueComment.objects.filter(owner= viewuser).order_by('-updated_at')[:10]
    prof=Profile.objects.filter(user=viewuser)[0]
    follows_between = Follow.objects.filter(user=request.user,follow_user=viewuser)
    follows_between.delete()
    folowings= Follow.objects.filter(user=viewuser)
    followers= Follow.objects.filter(follow_user=viewuser)
    context={'viewuser':viewuser, 'prof':prof, 'canfollow':True, 'canunfollow':False,  'followers':followers.count(), 'followings':folowings.count(),'poll_list':poll_list, 'issue_list':issue_list, 'comment_list':comment_list, 'issue_comment_list':issue_comment_list,}
    return render(request, 'home/user_detail.html', context)

@login_required
def FollowersView(request, username):
    user= User.objects.filter(username=username)[0]
    follower_list= Follow.objects.filter(follow_user=user)
    return render(request, 'home/follower.html',{'follower_list':follower_list, 'user':user})

@login_required
def FollowingsView(request, username):
    user= User.objects.filter(username=username)[0]
    following_list= Follow.objects.filter(user=user)
    return render(request, 'home/following.html',{'following_list':following_list, 'user':user})
