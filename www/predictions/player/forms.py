from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from predictions.player.models import Profile
 
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label = "Email")
    first_name = forms.CharField(label = "First name")
    last_name = forms.CharField(label = "Last name")
    free_game = forms.BooleanField(label = 'Free game (no gambling)?', required=False)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username",)

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        
        if commit:
            user.save()
            new_profile = Profile(user=user, nickname=user.username, free_game=self.cleaned_data['free_game'])
            new_profile.save()
        return user