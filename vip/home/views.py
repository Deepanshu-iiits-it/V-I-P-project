# from django.shortcuts import render
# from django.contrib.auth.forms import UserCreationForm
# from django.urls import reverse_lazy
# from django.views import generic



# def home(request):
#     return render(request, 'home/main.html')
from django.http import HttpResponseRedirect
from home.models import Poll, Comment, Fav, Choice
from home.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView

from django.views import View
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.humanize.templatetags.humanize import naturaltime
from home.forms import CreateForm, CommentForm
from home.utils import dump_queries

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
            objects = Poll.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else :
            # try both versions with > 4 posts and watch the queries that happen
            objects = Poll.objects.all().order_by('-updated_at')[:10]
            # objects = Post.objects.select_related().all().order_by('-updated_at')[:10]

        # Augment the post_list
        for obj in objects:
            obj.natural_updated = naturaltime(obj.updated_at)

        ctx = {'poll_list' : objects, 'search': strval}
        retval = render(request, self.template_name, ctx)

        dump_queries()
        return retval



class PollDetailView(OwnerDetailView):
    model = Poll
    template_name = "home/poll_detail.html"
    def get(self, request, pk) :
        x = Poll.objects.get(id=pk)
        comments = Comment.objects.filter(poll=x).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'poll' : x, 'comments': comments, 'comment_form': comment_form }
        return render(request, self.template_name, context)

class PollResultView(OwnerDetailView):
    model = Poll
    template_name = "home/poll_result.html"
    def get(self, request, pk) :
        x = Poll.objects.get(id=pk)
        comments = Comment.objects.filter(poll=x).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'poll' : x, 'comments': comments, 'comment_form': comment_form }
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

def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    k=request.POST['choice']
    print(k)
    if(k):
        selected_choice = poll.choice_set.get(pk=k)
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
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

# class AdCreateView(OwnerCreateView):
#     model = Ad
#     fields = ['title', 'price', 'text']


# class AdUpdateView(OwnerUpdateView):
#     model = Ad
#     fields = ['title', 'price', 'text']


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
        comment = Comment(text=request.POST['comment'], owner=request.user, poll=poll)
        comment.save()
        return redirect(reverse('home:poll_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "home/comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        poll = self.object.poll
        return reverse('home:poll_detail', args=[poll.id])

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
