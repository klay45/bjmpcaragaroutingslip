from import_export import resources
from .models import Forclaim
from .models import ForclaimAdmin

class ForclaimResource(resources.ModelResource):
    class Meta:
        model = Forclaim

#for admin module
class ForclaimResourceAdmin(resources.ModelResource):
    class Meta:
        model = ForclaimAdmin