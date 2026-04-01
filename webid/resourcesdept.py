from import_export import resources
from .models import DeptandDesignation

class DeptandDesignationResource(resources.ModelResource):
    class Meta:
        model = DeptandDesignation