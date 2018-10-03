from import_export import resources
from .models import Profile, Vote, Place, Condition


class ConditionResource(resources.ModelResource):
    class Meta:
        model = Condition