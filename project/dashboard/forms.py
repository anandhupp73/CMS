from django import forms
from accounts.models import User, Role

class AdminUserCreateForm(forms.ModelForm):
    # Styling the password field
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all outline-none',
            'placeholder': '••••••••'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'is_active']
        # Styling the other fields
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all outline-none',
                'placeholder': 'Enter username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all outline-none',
                'placeholder': 'email@example.com'
            }),
            'role': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all outline-none'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 rounded text-blue-600 focus:ring-blue-500 border-slate-300'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #never allow admin role in custom ui
        self.fields['role'].queryset = Role.objects.exclude(name='Admin')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user