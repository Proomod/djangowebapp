from django import forms
from .models import Postevent, Images, Members


class PostForm(forms.ModelForm):
    title = forms.CharField(max_length=128)
    description = forms.Textarea()

    class Meta:
        model = Postevent
        fields = ("title", "description")


class ImageForm(forms.ModelForm):
    image = forms.ImageField(label="Image")

    class Meta:
        model = Images
        fields = ("image",)


# class Membersform(forms.ModelForm):
#     firstname = forms.CharField(max_length=100)
#     lastname = forms.CharField(max_length=100)
#     position = forms.CharField(max_length=100)

#     class Meta:
#         model = Members
#         fields = ("first_name", "last_name", "position")

