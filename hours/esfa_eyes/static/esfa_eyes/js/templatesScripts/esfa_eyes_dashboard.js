const titleMapping = {
	balance_rials_official: 'موجودی ریالی رسمی',
	balance_rials: 'موجودی ریالی',
	balance_dollars: 'موجودی دلاری',
	montly_checks_recieved: 'چک‌های دریافتی',
	montly_checks_issued: 'چک‌های صادر شده',
	montly_installment: 'اقساط',
	montly_total_sales: 'فروش کل',
	montly_international_total_sales: 'فروش کل بین‌المللی',
	individual_sales: 'فروش فردی',
	international_individual_sales: 'فروش فردی بین‌المللی',
	ready_products: 'محصولات آماده',
	unproduced_workshop_inventory: 'موجودی کارگاه',
	turkiye_inventory: 'موجودی ترکیه',
	china_production_orders: 'سفارشات تولید چین',
	total_insured_staffs: 'کارکنان بیمه شده',
	total_uninsured_staffs: 'کارکنان بیمه نشده',
	total_salary_paid: 'حقوق پرداخت شده',
	total_insurance_paid: 'بیمه پرداخت شده'
};

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

function parseJalaliDateTime(dateTimeString) {
	const [datePart, timePart] = dateTimeString.split(' ');
	const [year, month, day] = datePart.split('-').map(Number);
	const [hour, minute, second] = timePart.split(':').map(Number);

	// Create a JDate object from the date parts
	const jdate = new JDate([year, month, day]);

	// Get the underlying Gregorian Date object (_d) and set the time
	const gregorianDate = jdate._d;
	gregorianDate.setHours(hour, minute, second, 0);

	return gregorianDate;
}

function createNumericTable(data, title, itemKeys) {
	const availableItems = itemKeys.filter(key => data[key]);
	if (availableItems.length === 0) return;

	const card = document.createElement('div');
	// CHANGE: Updated grid class for responsive layout
	card.className = 'col-lg-12 mb-4';

	let tableBody = '';
	let cardBgColor = 'bg-success-subtle';

	availableItems.forEach(key => {
		const item = data[key];
		const bgColor = getBackgroundColor(item.last_modify_time, item.UPDATE_INTERVAL_DAYS);
		if (bgColor === 'bg-warning-subtle' && cardBgColor !== 'bg-danger-subtle') cardBgColor = bgColor;
		if (bgColor === 'bg-danger-subtle') cardBgColor = bgColor;
		const [datePart, timePart] = item.last_modify_time.split(' ');
		const [year, month, day] = datePart.split('-').map(Number);
		const jdate = new JDate([year, month, day]);
		const formattedDate = jdate.format('YYYY-MM-DD') + ' ' + timePart.substring(0, 5);

		tableBody += `
                    <tr class="${bgColor}">
                        <td>${titleMapping[key] || key}</td>
                        <td contenteditable="true">${item._info.toLocaleString()}</td>
                        <td>${formattedDate}</td>
                    </tr>
                `;
	});

	card.innerHTML = `<div class="card h-100"><div class="card-header ${cardBgColor}">${title}</div><div class="card-body p-0"><div class="table-responsive"><table class="table table-striped table-hover table-vertical-lines"><thead><tr><th>عنوان</th><th>مقدار</th><th>آخرین بروزرسانی</th></tr></thead><tbody>${tableBody}</tbody></table></div></div><div class="card-footer text-center"><button class="btn btn-primary">ثبت تغییرات</button></div></div>`;
	document.getElementById('dashboard-container').appendChild(card);
}


function createObjectTable(data, title, itemKeys) {
	const availableItems = itemKeys.filter(key => data[key] && typeof data[key]._info === 'object');
	if (availableItems.length === 0) return;

	const card = document.createElement('div');
	card.className = 'col-lg-12 mb-4';

	// Define headers dynamically from the first available item
	const firstItemInfo = data[availableItems[0]]._info;
	const subItemHeaders = Object.keys(firstItemInfo);
	let tableHeader = '<th>عنوان</th>';
	subItemHeaders.forEach(header => tableHeader += `<th>${header}</th>`);
	tableHeader += '<th>آخرین بروزرسانی</th>'; // Add last update header

	let tableBody = '';
	let cardBgColor = 'bg-success-subtle';

	availableItems.forEach(key => {
		const item = data[key];
		const bgColor = getBackgroundColor(item.last_modify_time, item.UPDATE_INTERVAL_DAYS);
		if (bgColor === 'bg-warning-subtle' && cardBgColor !== 'bg-danger-subtle') cardBgColor = bgColor;
		if (bgColor === 'bg-danger-subtle') cardBgColor = bgColor;

		const [datePart, timePart] = item.last_modify_time.split(' ');
		const jdate = new JDate(datePart.split('-').map(Number));
		const formattedDate = jdate.format('YYYY-MM-DD') + ' ' + timePart.substring(0, 5);

		let row = `<tr class="${bgColor}"><td>${titleMapping[key] || key}</td>`;
		subItemHeaders.forEach(header => {
			// Make each data cell editable
			row += `<td contenteditable="true">${(item._info[header] || 0).toLocaleString()}</td>`;
		});
		row += `<td>${formattedDate}</td></tr>`; // Add last update data cell
		tableBody += row;
	});

	card.innerHTML = `<div class="card h-100"><div class="card-header ${cardBgColor}">${title}</div><div class="card-body p-0"><div class="table-responsive"><table class="table table-striped table-hover table-vertical-lines"><thead><tr>${tableHeader}</tr></thead><tbody>${tableBody}</tbody></table></div></div><div class="card-footer text-center"><button class="btn btn-primary">ثبت تغییرات</button></div></div>`;
	document.getElementById('dashboard-container').appendChild(card);
}

function getBackgroundColor(lastModifyTime, updateIntervalDays) {
	const now = new Date();
	const lastUpdate = parseJalaliDateTime(lastModifyTime);

	const diffMilliseconds = now.getTime() - lastUpdate.getTime();
	const diffDays = diffMilliseconds / (1000 * 3600 * 24);

	if (diffDays <= updateIntervalDays) {
		return 'bg-success-subtle';
	} else if (diffDays <= updateIntervalDays * 2) {
		return 'bg-warning-subtle';
	} else {
		return 'bg-danger-subtle';
	}
}

async function initTables() {
	let data = await getEyesData($("#year").val());

	createNumericTable(data, 'موجودی‌ها', ['balance_dollars', 'balance_rials', 'balance_rials_official']);
	createObjectTable(data, 'چک‌ها', ['montly_checks_issued', 'montly_checks_recieved', 'montly_installment']);
	createObjectTable(data, 'فروش کل', ['montly_total_sales', 'montly_international_total_sales']);
	createObjectTable(data, 'فروش تفکیکی', ['individual_sales', 'international_individual_sales']);
	createObjectTable(data, 'موجودی دستگاه‌ها', ['ready_products', 'unproduced_workshop_inventory', 'turkiye_inventory', 'china_production_orders']);
	createNumericTable(data, 'حقوق کارکنان', ['total_insured_staffs', 'total_uninsured_staffs', 'total_salary_paid', 'total_insurance_paid']);
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

	initTables();
	$("#year, #month").change(function () {
		initTables();
	});
});
