//get data========================
async function getCurrencies() {
	return {
		"USD": {
			"date": "1404/06/06",
			"time": "12:16",
			"time_unix": 1756370760,
			"symbol": "USD",
			"name_en": "US Dollar",
			"name": "دلار",
			"price": 100150,
			"change_value": -300,
			"change_percent": -0.3,
			"unit": "تومان"
		},
		"CNY": {
			"date": "1404/06/06",
			"time": "12:17",
			"time_unix": 1756370820,
			"symbol": "CNY",
			"name_en": "Chinese Yuan",
			"name": "یوآن چین",
			"price": 14170,
			"change_value": 130,
			"change_percent": 0.93,
			"unit": "تومان"
		}
	};

	return apiService.get('https://BrsApi.ir/Api/Market/Gold_Currency.php?key=BfTErgVQ4YHlDZ33IcmWap9FhgiWU17H', {}, {}, "failed to get currencies")
		.then(result => {
			if (result.success) {
				return { "USD": result.data.currency[1], "CNY": result.data.currency[9] };
			}
			else {
				throw new Error()
			}
		});
}

async function getEyesData(year) {
	return apiService.get(`/eyes/${year}`, {}, {}, "Failed to get eyes data")
		.then(result => {
			if (result.success) {
				return result.data;
			}
			else {
				throw new Error()
			}
		});
}

//handle data ========================
async function updateCurrencies() {
	result = await getCurrencies();

	$('#dollar-holder').text(result.USD.price.toLocaleString() + ' T');
	$('#yuan-holder').text(result.CNY.price.toLocaleString() + ' T');
}

async function initTable() {
	let data = await getEyesData($("#year").val());
	console.log(data);
	//let sheet = await getEsfaEyesInfo(year);

	//constructTable(sheet.data, sheet.submitted);
	//onChangeHandler();
}

async function getEsfaEyesInfo(year) {
	const url = `{% url "esfa_eyes:api_eyes" year='yearHolder' %}`
		.replace("yearHolder", year)
	try {
		let res = await fetch(url);
		return await res.json();
	}
	catch (err) {
		jSuites.notification({
			error: 1,
			name: 'Error',
			title: "Fetching This month's Sheet",
			message: err,
		});
	}
}

async function constructTable(data, readOnlyAll = false) {

}

function saveSheet(data) {
	const year = $("#year").val();
	const month = $("#month").val();
	const url = `{% url "sheets:api_sheets" year='yearHolder' month='monthHolder' %}`
		.replace("yearHolder", year)
		.replace("monthHolder", month);
	fetch(url, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': '{{csrf_token}}',
		},
		body: JSON.stringify({ "data": data, "saveSheet": true }),
	})
		.then(res => res.json())
		.then(() => updatePaymentsValue())
		.catch(err => {
			jSuites.notification({
				error: 1,
				name: 'Error',
				title: "Updating Sheet",
				message: err,
			});
		});
}

function fillYears(year) {
	for (let i = window.START_YEAR; i <= year; i++) {
		$("#year").append($("<option>").text(i));
	}
}


// =================== document ready ============================
$("document").ready(async function () {
	const today = new JDate();
	const currentYear = today.getFullYear();
	const currentMonth = today.getMonth();
	updateCurrencies();

	fillYears(currentYear);
	$("#year").val(currentYear);

	initTable();
	$("#year, #month").change(function () {
		initTable();
	});
});
