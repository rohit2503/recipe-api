from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin


class UserManager(BaseUserManager):
    """
    custom UserManager that creates user with email
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        creates and saves a new user
        :param email: user email address
        :param password: user password
        :return: user object
        """
        if not email:
            raise ValueError("User must have an email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(self._db)

        return user

    def create_superuser(self, email, password):
        """
        create super user
        :param email: super user email address
        :param password: super user password
        :return: return user object
        """
        s_user = self.create_user(email=email, password=password)
        s_user.is_superuser = True
        s_user.is_staff = True
        s_user.save(self._db)

        return s_user


class User(AbstractBaseUser, PermissionsMixin):
    """
    custom user model that supports user creation
    using email instead of username
    """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
