from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

Usuario = get_user_model()

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        help_text="Deja en blanco para no cambiar la contraseña."
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'rol', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Excluir el usuario actual al editar
        qs = Usuario.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Este correo ya está en uso.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)  # encripta la contraseña
        if commit:
            user.save()
        return user
