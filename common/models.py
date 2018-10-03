from django.utils import timezone

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from common import choices


class Vote(models.Model):
    profile = models.ForeignKey("Profile",
                                related_name="profile_votes",
                                null=True, on_delete=models.SET_NULL)
    place = models.ForeignKey("Place",
                              related_name="place_votes",
                              null=True, on_delete=models.CASCADE)
    rate = models.PositiveSmallIntegerField()
    vote_datetime = models.DateTimeField(auto_now_add=timezone.now)

    class Meta:
        ordering = ['-rate']

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.profile.user.first_name + ": " + str(self.rate)


class Place(models.Model):
    """
    Model representing a place where people can lunch.
    """

    title = models.CharField(max_length=64,
                             help_text="Enter a place title (e.g. Orhan Aspava, Dolmacı etc.")
    description = models.TextField(blank=True, null=True)
    rate = models.FloatField()

    class Meta:
        ordering = ['-rate']

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.title

    def get_absolute_url(self):
        """
        Returns the url to access a particular book instance.
        """
        return reverse('common:place-detail', args=[str(self.id)])


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    location = models.CharField(max_length=30, blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.user.first_name

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class Condition(models.Model):
    pay = models.IntegerField(choices=choices.PAY_CHOICES)
    time = models.IntegerField(choices=choices.TIME_CHOICES)
    kitchen = models.IntegerField(choices=choices.KITCHEN_CHOICES)
    hunger = models.IntegerField(choices=choices.HUNGER_CHOICES)

    profile = models.ForeignKey("Profile",
                                related_name="profile_conds",
                                null=True, on_delete=models.SET_NULL)

    place = models.ForeignKey(Place, on_delete=models.CASCADE)

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """

        return '{} {} {} {} {}'.format(self.pay, self.time, self.kitchen, self.hunger, self.place.id)
