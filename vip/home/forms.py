from django import forms
from django.contrib.auth.models import User
from home.models import Poll, Choice, Profile, Issue
from django.core.files.uploadedfile import InMemoryUploadedFile
from home.humanize import naturalsize
from django.contrib.auth.forms import UserCreationForm


# Create the form class.
class CreateForm(forms.ModelForm):
    max_upload_limit = 2 * 1024 * 1024
    max_upload_limit_text = naturalsize(max_upload_limit)

    # Call this 'picture' so it gets copied from the form to the in-memory model
    # It will not be the "bytes", it will be the "InMemoryUploadedFile"
    # because we need to pull out things like content_type
    picture = forms.FileField(required=False, label='File to Upload <= '+max_upload_limit_text)
    upload_field_name = 'picture'
    # choice1 = 

    # Hint: this will need to be changed for use in the ads application :)
    class Meta:
        model = Poll
        fields = ['question','choice1','choice2','choice3','choice4', 'picture', 'Required_Minimum_Age', 'Required_City', 'Required_Sex']  # Picture is manual

    # Validate the size of the picture
    def clean(self):
        cleaned_data = super().clean()
        pic = cleaned_data.get('picture')
        if pic is None:
            return
        if len(pic) > self.max_upload_limit:
            self.add_error('picture', "File must be < "+self.max_upload_limit_text+" bytes")

    # Convert uploaded File object to a picture
    def save(self, commit=True):
        instance = super(CreateForm, self).save(commit=False)
        

        # We only need to adjust picture if it is a freshly uploaded file
        f = instance.picture   # Make a copy
        if isinstance(f, InMemoryUploadedFile):  # Extract data from the form to the model
            bytearr = f.read()
            instance.content_type = f.content_type
            instance.picture = bytearr  # Overwrite with the actual image data

        if commit:
            instance.save()
            
        return instance

class CommentForm(forms.Form):
    Views = forms.CharField(required=True, max_length=500, min_length=3, strip=True)
    Anonymous = forms.BooleanField(required=False)

class IssueCreateForm(forms.ModelForm):
    max_upload_limit = 2 * 1024 * 1024
    max_upload_limit_text = naturalsize(max_upload_limit)

    # Call this 'picture' so it gets copied from the form to the in-memory model
    # It will not be the "bytes", it will be the "InMemoryUploadedFile"
    # because we need to pull out things like content_type
    picture = forms.FileField(required=False, label='File to Upload <= '+max_upload_limit_text)
    upload_field_name = 'picture'
    # choice1 = 
    anonymous= forms.BooleanField(required=False)
    # Hint: this will need to be changed for use in the ads application :)
    class Meta:
        model = Issue
        fields = ['title','text','anonymous', 'picture']  # Picture is manual

    # Validate the size of the picture
    def clean(self):
        cleaned_data = super().clean()
        pic = cleaned_data.get('picture')
        if pic is None:
            return
        if len(pic) > self.max_upload_limit:
            self.add_error('picture', "File must be < "+self.max_upload_limit_text+" bytes")

    # Convert uploaded File object to a picture
    def save(self, commit=True):
        instance = super(IssueCreateForm, self).save(commit=False)
        

        # We only need to adjust picture if it is a freshly uploaded file
        f = instance.picture   # Make a copy
        if isinstance(f, InMemoryUploadedFile):  # Extract data from the form to the model
            bytearr = f.read()
            instance.content_type = f.content_type
            instance.picture = bytearr  # Overwrite with the actual image data

        if commit:
            instance.save()
            
        return instance

class IssueCommentForm(forms.Form):
    Views = forms.CharField(required=True, max_length=500, min_length=3, strip=True)
    Anonymous = forms.BooleanField(required=False)

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'country', 'city', 'age', 'sex']