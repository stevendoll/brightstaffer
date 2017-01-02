from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models.query_utils import Q
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template import loader
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from brightStaffer.settings import DEFAULT_FROM_EMAIL
from django.views.generic import *
from django.shortcuts import render
from brightStafferapp import util
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json



class ForgetPassword():
    def validate_email_address(email):

        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    def reset_password(user, request):
        c = {
            'email': user.email,
                                'domain': request.META['HTTP_HOST'],
                                'site_name': 'brightStaffer',
                                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                'user': user,
                                'token': default_token_generator.make_token(user),
                                'protocol': 'http',
        }
        subject_template_name ='registration/password_reset_subject.txt'
        # copied from
        # django/contrib/admin/templates/registration/password_reset_subject.txt
        # to templates directory
        email_template_name = 'registration/passwordresetemail.html'
        # copied from
        # django/contrib/admin/templates/registration/password_reset_email.html
        # to templates directory
        subject = loader.render_to_string(subject_template_name, c)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        email = loader.render_to_string(email_template_name, c)
        send_mail(subject, email, DEFAULT_FROM_EMAIL,
                  [user.email], fail_silently=False)
    @csrf_exempt
    def forget(request):
        param_dict = {}
        try:
            profile_data = json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(500,'Invalid Forrm Fields')
        data = profile_data["email"]
        # uses the method written above
        if ForgetPassword.validate_email_address(data) is True:
            '''
            If the input is an valid email address, then the following code will lookup for users associated with that email address. If found then an email will be sent to the address, else an error message will be printed on the screen.
            '''
            associated_users = User.objects.filter(
                Q(email=data) | Q(username=data))
            if associated_users.exists():
                for user in associated_users:
                    ForgetPassword.reset_password(user, request)

                param_dict['message'] = 'success'
                return util.returnSuccessShorcut(param_dict)
            return util.returnErrorShorcut(500,'UnAuthorized User')


class ResetPassword():
    @csrf_exempt
    def passwordresetconfirmView(request, uidb64=None, token=None):
        template_name = "views/resetpassword.html"
        return render(request,template_name=template_name)

    @csrf_exempt
    def resetpasswordApi(request):
        """
        View that checks the hash in a password reset link and presents a
        form for entering a new password.
        """
        param_dict = {}
        try:
            user_pasword = json.loads(request.body.decode("utf-8"))
            uidb64=user_pasword['token'].split('-')[0]
            token=user_pasword['token'].split('-')[1]+'-'+user_pasword['token'].split('-')[2]
        except ValueError:
            return util.returnErrorShorcut(500,'Invalid Forrm Fields')
        UserModel = get_user_model()
        assert uidb64 is not None and token is not None  # checked by URLconf
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            new_password = user_pasword['password']
            user.set_password(new_password)
            user.save()
            param_dict['message'] = 'success'
            return util.returnSuccessShorcut(param_dict)

        else:
            return util.returnErrorShorcut(500,'Link has been expired')



