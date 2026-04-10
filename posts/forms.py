from django import forms

class HandleComments(forms.Form):
    post_id = forms.UUIDField()
    comment = forms.CharField(max_length=2500)