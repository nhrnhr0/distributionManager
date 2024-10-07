# from .models import BizMessages,MessageCategory,MessageLink
# from django import forms


# from django import forms
# from django.forms import inlineformset_factory
# from .models import BizMessages, MessageCategory

# # Create a form for the MessageCategory model
# class MessageCategoryForm(forms.ModelForm):
#     class Meta:
#         model = MessageCategory
#         fields = ['category', 'send_at', 'is_sent']

# # Create the formset for MessageCategory related to BizMessages
# MessageCategoryFormSet = inlineformset_factory(
#     BizMessages,  # parent model
#     MessageCategory,  # related model
#     form=MessageCategoryForm,  # the form to use
#     extra=1  # number of empty forms to display
# )

# class BizMessagesForm(forms.ModelForm):
#     class Meta:
#         model = BizMessages
#         fields = ['business', 'messageTxt']
