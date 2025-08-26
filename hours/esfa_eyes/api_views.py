from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from esfa_eyes import customPermissions

from esfa_eyes.models import EsfaEyes


class EsfaEyesApiView(APIView):
	permission_classes = [customPermissions.hasEsfaEyesAccess]
	
	def get(self, request, year: str):
		user = self.request.user
		
		esfa_eyes_object ,created  = EsfaEyes.objects.get_or_create(year=year)
		data = esfa_eyes_object.get(user)
		
		return Response(data, status=status.HTTP_200_OK)