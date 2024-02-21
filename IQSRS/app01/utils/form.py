from app01.models import *
from django import forms


class AddUserModelForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        # fields = '__all__'
        # exclude = ['username']
        fields = ['username', 'password', 'phone', 'investage', 'asset', 'risktolerance']
    def __init__(self, *args, **kwargs): #BootStrap
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control', 'placeholder': field.label, 'style': 'width: 167px;'}

class ModUserModelForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ['id', 'username', 'password', 'phone', 'investage', 'asset', 'risktolerance']
        # weights = {
        #     'investage': forms.TextInput(attrs={'style':'weights: 30px;'}),
        #     'risktolerance(': forms.TextInput(attrs={'style':'weights: 30px;'}),
        # }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'investage' or name == 'risktolerance':
                field.widget.attrs = {'class': 'form-control', 'placeholder': field.label, 'style': 'height:28px; width: 60px;'}
            else:
                field.widget.attrs = {'class': 'form-control', 'placeholder': field.label, 'style': 'height: 28px; width: 110px;'}


class BackTestModelForm(forms.ModelForm):
    class Meta:
        model = StrInfo
        fields = ['strid', 'starttime', 'endtime', 'stopgainratio', 'stoplossratio', 'startcash', 'parai1', 'parai2', 'parai3', 'parai4', 'parai5', 'paraf1', 'paraf2']

    def __init__(self, *args, **kwargs):  # BootStrap
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control', 'placeholder': field.label, 'style': 'width:100% ;'}
