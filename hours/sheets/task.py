# tasks.py
from celery import shared_task
import pandas as pd
from sheets.models import Sheet, User
from django.http import HttpResponse, JsonResponse

@shared_task(bind=True)
def import_hours_task(self, file_path, year, month):
    df = pd.read_excel(file_path)
    df.fillna(0, inplace=True)
    not_founds = []

    for index, row in df.iterrows():
        try:
            user_id = self.USER_ID_MAP[row["کد پرسنلي"]]
        except:
            if row["نام خانوادگي"] not in not_founds:
                not_founds.append(row["نام خانوادگي"])
            continue
        date = row["تاريخ"]
        hours = row["مدت کارکرد"]
        current_sheet = None
        y = date.split('/')[0]
        m = date.split('/')[1]
        if int(month) != int(m) or year != y:            
            response_data = {
                "status": "error",
                "message": "year or month is not match",
                "users_not_found": not_founds,
            }
            return JsonResponse(response_data)
        
        d = int(date.split('/')[2])

        if current_sheet==None or current_sheet.user_id != user_id:
            if user_id == -1:
                continue
            current_sheet = Sheet.objects.get(
                user_id=user_id, year=year, month=month
            )
            current_sheet.normalize_sheet()
        
        currentDayData = current_sheet.data[d-1]
            
        currentDayData["Auto Hours"] = f"{hours.hour}:{hours.minute}" 
        current_sheet.save()
    

    return {"status": "success", "users_not_found": not_founds}
