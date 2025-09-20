from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from esfa_eyes import customPermissions

from esfa_eyes.models import EsfaEyes
from .schemas.esfa_eyes_info import EsfaEyesInfo


class EsfaEyesApiView(APIView):
	permission_classes = [customPermissions.hasEsfaEyesAccess]
	
	def get(self, request, year: str):
		user = self.request.user
		
		esfa_eyes_object ,created  = EsfaEyes.objects.get_or_create(year=year)
		data = esfa_eyes_object.get(user)

		return Response(data, status=status.HTTP_200_OK)
		return Response({"message": f"eyes in {year} not found"}, status=status.HTTP_404_NOT_FOUND)

	def post(self, request, year: str):
		user = self.request.user
		esfa_eyes_obj, created = EsfaEyes.objects.get_or_create(year=year)
		
		if user.is_superuser and not (user.is_FinancialManager or user.is_InternationalFinanceManager or user.is_InternationalSalesManager or user.is_ProductionManager or user.is_R131ProductionManager or user.is_ProductionManagerReadonly):
			return Response({"title": "Access denied", "message": "Superuser cannot edit esfa eyes data"}, status=status.HTTP_403_FORBIDDEN)

		shared_keys_found = False
		access_data = esfa_eyes_obj.get(user, True)

		for field_name in request.data:
			new_field_data = request.data[field_name]
			shared_keys = list(set(access_data.keys()) & set(new_field_data.keys()))
			
			if len(shared_keys) > 0:
				shared_keys_found = True
				updated_esfa_eyes_obj = self._update_esfaEyes(esfa_eyes_obj, new_field_data, field_name)
				return Response(updated_esfa_eyes_obj.get(self.request.user), status=status.HTTP_200_OK)

		if not shared_keys_found:
			return Response({"title": "Access denied", "message": "You don't have permission to edit this data."}, status=status.HTTP_403_FORBIDDEN)

	def _update_esfaEyes(self, esfa_eyes_obj, new_field_data, field_name):
		current_field_data = getattr(esfa_eyes_obj, field_name)
		for innerfield in new_field_data:
			old = current_field_data[innerfield]
			new = new_field_data[innerfield]
			new_structed_data = EsfaEyesInfo(new['_info'], old['UPDATE_INTERVAL_DAYS']).__dict__
			current_field_data[innerfield] = new_structed_data
		setattr(esfa_eyes_obj, field_name, current_field_data)
		esfa_eyes_obj.save()
		return esfa_eyes_obj
