from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.

class Category(models.Model):
    name= models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name

class Poll(models.Model):
    question= models.CharField(
            max_length=500,
            validators=[MinLengthValidator(2, "Question must be greater than 2 characters")]
    )
    choice1 = models.CharField(max_length=500, null=True)
    choice2 = models.CharField(max_length=500, null=True)
    choice3 = models.CharField(max_length=500, null=True)
    choice4 = models.CharField(max_length=500, null=True)
    Required_Minimum_Age = models.IntegerField(null= True)
    Required_City = models.CharField(max_length=500, null=True)
    Required_Sex = models.CharField(max_length=500, null= True)
    n1 = models.IntegerField(default=0)
    n2 = models.IntegerField(default=0)
    n3 = models.IntegerField(default=0)
    n4 = models.IntegerField(default=0)
    is_issue = models.BooleanField(default="False")
    allow_views= models.BooleanField(default="True")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    no_user = models.IntegerField(default=0)
    category= models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL,through='Fav', related_name='favorite_polls')
    picture = models.BinaryField(null=True, editable=True)
    content_type = models.CharField(max_length=256, null=True, help_text='The MIMEType of the file')
    
    def __str__(self):
        return self.question
    
class Choice(models.Model):
    choice = models.CharField(
            max_length=200,
            validators=[MinLengthValidator(2, "Choice must be greater than 2 characters")]
    )
    poll = models.ForeignKey("Poll", on_delete=models.CASCADE)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice

class View(models.Model):
    text = models.TextField(
        validators=[MinLengthValidator(3, "View must be greater than 3 characters")]
    )
    # poll= models.ForeignKey(Poll, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    no_review= models.IntegerField(default=0)
    ups = models.IntegerField(default=0)
    downs = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    picture = models.BinaryField(null=True, editable=True)
    content_type = models.CharField(max_length=256, null=True, help_text='The MIMEType of the file')
    
    def __str__(self):
        return self.text

class Issue(models.Model):
    title = models.CharField(
            max_length=200,
            validators=[MinLengthValidator(2, "Title must be greater than 2 characters")]
    )
    text = models.TextField()
    anonymous = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    picture = models.BinaryField(null=True, editable=True)
    content_type = models.CharField(max_length=256, null=True, help_text='The MIMEType of the file')


    # Shows up in the admin list
    def __str__(self):
        return self.title

class IssueComment(models.Model) :
    text = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters")]
    )

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Shows up in the admin list
    def __str__(self):
        if len(self.text) < 15 : return self.text
        return str(self.text)[:11] + ' ...'

class Fav(models.Model) :
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # https://docs.djangoproject.com/en/3.0/ref/models/options/#unique-together
    class Meta:
        unique_together = ('poll', 'user')

    def __str__(self) :
        return '%s likes %s'%(self.user.username, self.poll.question[:10])

class Comment(models.Model) :
    text = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters")]
    )

    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Shows up in the admin list
    def __str__(self):
        if len(self.text) < 15 : return self.text
        return str(self.text)[:11] + ' ...'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name= models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, default='World', null=True)
    city = models.CharField(max_length=50, default='None', null=True)
    age = models.IntegerField(default=18, null=True)
    sex = models.CharField(max_length=10 ,default='None', null=True)
    # picture = models.BinaryField(null=True, editable=True)
    # content_type = models.CharField(max_length=256, null=True, help_text='The MIMEType of the file')

    def __str__(self):
        return f'{self.user.username} Profile'

    @property
    def followers(self):
        return Follow.objects.filter(follow_user=self.user).count()

    @property
    def following(self):
        return Follow.objects.filter(user=self.user).count()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save()


class Follow(models.Model):
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
    follow_user = models.ForeignKey(User, related_name='follow_user', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

# class Follow(models.Model):
#     follower= models.ForeignKey("", on_delete=models.CASCADE)
#     no_followers = models.IntegerField(default=0)
#     following = models.ManyToManyField("", through=,)
#     category = models.ManyToManyField("", through=, 
    

#     def __str__(self):
#         return self.name