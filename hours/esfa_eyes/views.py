from django.utils.decorators import method_decorator
from esfa_eyes.customDecorators import *
from sheets.views import BaseView

@method_decorator([esfa_eyes_access_required], name="dispatch")
class EyesView(BaseView):
    template_name = "esfa_eyes_dashbord.html"