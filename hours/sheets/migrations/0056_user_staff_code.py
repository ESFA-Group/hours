from django.db import migrations, models

# Keyed by lowercase full name with spaces removed. Employees marked "غیر فعال" are omitted.
STAFF_CODES = {
	"mohammadmalekan": "10594",
	"moeinabedini": "10146",
	"hamidaslani": "10190",
	"alirezaabooei": "11082",
	"samiraforoughi": "10294",
	"erfanriyahi": "10460",
	"mohammadmahdirajabi": "10034",
	"sinamohamadi": "10324",
	"hosseinkasaei": "10966",
	"mohammadhassanzahedi": "10000",
	"soheilsafavi": "10001",
	"vahidhajihasani": "10003",
	"alirezaamiri": "10004",
	"mortezamansoori": "10081",
	"pooriaallahkarami": "10028",
	"hosseindadashiilkhechi": "10032",
	"ahmadrezadarabi": "10033",
	"mohammadhadiattarieh": "10037",
	"alirezamohammadi": "10039",
	"hamedmorsali": "10040",
	"mohsenghasemi": "10054",
	"mohammadhajzaman": "10082",
	"masoumehbayat": "10117",
	"gholamrezamoradi": "10191",
	"seyedjalalasefalhosseini": "10199",
	"mohammadaminsanei": "10245",
	"samanehmoslemi": "10341",
	"mehdizebarjadizirak": "10578",
	"miladtaherkhani": "10505",
	"mehrdadjahanbakhshi": "10732",
	"mohsenhasanpoor": "10784",
	"mohadesehkhandani": "10785",
	"aliasadzadeh": "10803",
	"mohammadsaeedghanbari": "10842",
	"amirhosseineslahchi": "10843",
	"rezafarzi": "10844",
	"mohammadaminzeinali": "10845",
	"mohammadmahdikarimi": "10846",
	"mahvoshabedinpour": "10859",
	"areftabatabaei": "10880",
	"farjadjafari": "10220",
	"saeedjallo": "10334",
	"mohamadhoseinpiran": "10924",
	"fatemehjanmshhadi": "10925",
	"mahsanorouzimehrabani": "10926",
	"omidsadeghzadeh": "10475",
	"hosseinmahmoodihashemi": "10888",
	"alibehjati": "10029",
	"abbastorkamani": "10030",
	"alisolouki": "10320",
	"mahshidkheyri": "10031",
	"negarkhosravi": "11044",
	"neginghiasvand": "11077",
	"doniasalehi": "11100",
	"aliebrahimi": "10027",
	"mahdidavarpanah": "10068",
	"mohammadmahdibanaei": "11033",
	"mortaredghafouri": "11051",
}


def fill_staff_codes(apps, schema_editor):
	User = apps.get_model("sheets", "User")
	for u in User.objects.all():
		key = "".join(f"{u.first_name}{u.last_name}".split()).lower()
		if key in STAFF_CODES:
			User.objects.filter(pk=u.pk).update(staff_code=STAFF_CODES[key])


class Migration(migrations.Migration):

	dependencies = [("sheets", "0055_manager_review_lock")]

	operations = [
		migrations.AddField(
			model_name="user",
			name="staff_code",
			field=models.CharField("staff_code", max_length=20, blank=True, default=""),
		),
		migrations.RunPython(fill_staff_codes, migrations.RunPython.noop),
	]
