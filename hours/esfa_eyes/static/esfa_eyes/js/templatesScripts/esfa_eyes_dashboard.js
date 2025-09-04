let originalApiData = {};

const titleMapping = {
	balance_rials_official: 'موجودی حساب‌های رسمی',
	balance_rials: 'موجودی حساب‌های غیر رسمی',
	balance_dollars: 'موجودی دلاری',
	montly_checks_recieved: 'چک‌های دریافتی',
	montly_checks_issued: 'چک‌های صادر شده',
	montly_installment: 'اقساط وام های دریافتی',
	montly_total_sales: 'فروش کل داخل',
	montly_international_total_sales: 'فروش کل خارج',
	individual_sales: 'فروش تفکیکی داخل',
	international_individual_sales: 'فروش تفکیکی خارج',
	ready_products: 'موجودی تولیدشده آماده تحویل',
	unproduced_workshop_inventory: 'موجودی کارگاه تولید نشده',
	turkiye_inventory: 'موجودی ترکیه',
	china_production_orders: 'سفارشات چین درحال تولید',
	total_insured_staffs: 'تعداد کارکنان بیمه‌ای',
	total_uninsured_staffs: 'تعداد کارکنان غیر بیمه',
	total_salary_paid: 'مجموع کل حقوق',
	total_insurance_paid: 'مجموع بیمه پرداختی'
};

const keyToModelFieldMap = {
	// financial_info
	'balance_rials_official': 'financial_info',
	'balance_rials': 'financial_info',
	'montly_checks_recieved': 'financial_info',
	'montly_checks_issued': 'financial_info',
	'montly_installment': 'financial_info',
	'montly_total_sales': 'financial_info',
	'individual_sales': 'financial_info',
	'total_insured_staffs': 'financial_info',
	'total_uninsured_staffs': 'financial_info',
	'total_salary_paid': 'financial_info',
	'total_insurance_paid': 'financial_info',

	// international_finance_info
	'balance_dollars': 'international_finance_info',
	'china_production_orders': 'international_finance_info',

	// international_sales_info
	'montly_international_total_sales': 'international_sales_info',
	'international_individual_sales': 'international_sales_info',
	'turkiye_inventory': 'international_sales_info',

	// products_info
	'unproduced_workshop_inventory': 'products_info',
	'ready_products': 'products_info'
};

// data backend connection ========================
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
		.then(data => {
			return { "USD": data.currency[1], "CNY": data.currency[9] };
		});
}

async function getEyesData(year) {
	return apiService.get(`/eyes/${year}`, {}, {}, "Failed to get eyes data");
}

async function postEyesData(year, payload) {
	return apiService.post(`/eyes/${year}`, payload, {}, "Failed to post eyes data");
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

	const jdate = new JDate([year, month, day]);

	const gregorianDate = jdate._d;
	gregorianDate.setHours(hour, minute, second, 0);

	return gregorianDate;
}

function createNumericTable(data, title, itemKeys) {
	const availableItems = itemKeys.filter(key => data[key]);
	if (availableItems.length === 0) return;
	const card = document.createElement('div');
	card.className = 'col-lg-12 mb-4';
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
		tableBody += `<tr class="${bgColor}"><td>${titleMapping[key] || key}</td><td contenteditable="true" data-key="${key}">${item._info.toLocaleString()}</td><td>${formattedDate}</td></tr>`;
	});
	card.innerHTML = `
        <div class="card h-100">
            <div class="card-header ${cardBgColor}">${title}</div>
            <div class="card-body p-0"><div class="table-responsive"><table class="table table-striped table-hover table-vertical-lines"><thead><tr class="${cardBgColor}"><th>عنوان</th><th>مقدار</th><th>آخرین بروزرسانی</th></tr></thead><tbody>${tableBody}</tbody></table></div></div>
            <div class="card-footer text-center"><button class="btn btn-primary btn-submit">ثبت تغییرات</button></div>
        </div>`;
	document.getElementById('dashboard-container').appendChild(card);
}

function createObjectTable(data, title, itemKeys) {
	const availableItems = itemKeys.filter(key => data[key] && typeof data[key]._info === 'object');
	if (availableItems.length === 0) return;
	const card = document.createElement('div');
	card.className = 'col-lg-12 mb-4';
	const firstItemInfo = data[availableItems[0]]._info;
	const subItemHeaders = Object.keys(firstItemInfo);
	let tableHeader = '<th>عنوان</th>';
	subItemHeaders.forEach(header => tableHeader += `<th>${header}</th>`);
	tableHeader += '<th>آخرین بروزرسانی</th>';
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
			row += `<td contenteditable="true" data-key="${key}" data-subkey="${header}">${(item._info[header] || 0).toLocaleString()}</td>`;
		});
		row += `<td>${formattedDate}</td></tr>`;
		tableBody += row;
	});
	card.innerHTML = `
        <div class="card h-100">
            <div class="card-header ${cardBgColor}">${title}</div>
            <div class="card-body p-0"><div class="table-responsive"><table class="table table-striped table-hover table-vertical-lines"><thead><tr class="${cardBgColor}">${tableHeader}</tr></thead><tbody>${tableBody}</tbody></table></div></div>
            <div class="card-footer text-center"><button class="btn btn-primary btn-submit">ثبت تغییرات</button></div>
        </div>`;
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

async function initTables(data = null) {
	if (data == null)
		data = await getEyesData($("#year").val());	

	document.getElementById('dashboard-container').innerHTML = '';

	createNumericTable(data, 'موجودی‌ها', ['balance_dollars', 'balance_rials', 'balance_rials_official']);
	createObjectTable(data, 'چک‌ها', ['montly_checks_issued', 'montly_checks_recieved', 'montly_installment']);
	createObjectTable(data, 'فروش کل', ['montly_total_sales', 'montly_international_total_sales']);
	createObjectTable(data, 'فروش تفکیکی', ['individual_sales', 'international_individual_sales']);
	createObjectTable(data, 'موجودی دستگاه‌ها', ['ready_products', 'unproduced_workshop_inventory', 'turkiye_inventory', 'china_production_orders']);
	createNumericTable(data, 'حقوق کارکنان', ['total_insured_staffs', 'total_uninsured_staffs', 'total_salary_paid', 'total_insurance_paid']);
}

function fillYears(year) {
	for (let i = window.START_YEAR; i <= year; i++) {
		$("#year").append($("<option>").text(i));
	}
}

// =================== interactions ============================
async function handleSubmit(button) {	
	const card = button.closest('.card');
	const editableCells = card.querySelectorAll('[contenteditable="true"]');

	// This object will group the updates by their target model field
	const groupedUpdates = {};

	editableCells.forEach(cell => {
		const key = cell.dataset.key;
		const subkey = cell.dataset.subkey;
		const value = parseInt(cell.innerText.replace(/,/g, ''), 10) || 0;

		// Find the correct model field for this piece of data using the map
		const modelField = keyToModelFieldMap[key];
		if (!modelField) {
			console.warn(`No model field mapping found for key: ${key}`);
			return; // Skip this cell if we don't know where it belongs
		}

		// Initialize objects if they don't exist
		if (!groupedUpdates[modelField]) groupedUpdates[modelField] = {};

		// **CHANGE HERE**: Create a new, clean object for each key that will only hold the _info property.
		if (!groupedUpdates[modelField][key]) {
			groupedUpdates[modelField][key] = {
				_info: subkey ? {} : 0
			};
		}

		// Update the value
		if (subkey) { // Object type (e.g., monthly sales)
			groupedUpdates[modelField][key]._info[subkey] = value;
		} else { // Numeric type (e.g., balances)
			groupedUpdates[modelField][key]._info = value;
		}
	});

	const year = $("#year").val();
	button.disabled = true;
	button.innerText = 'درحال ذخیره...';
	
	try {
		// Loop through the grouped updates and send one API request for each model field
		for (const fieldName in groupedUpdates) {
			const dataForField = groupedUpdates[fieldName];
			const payload = { [fieldName]: dataForField };
			let result = await postEyesData(year, payload);
			await initTables(result.data);
		}
		alert('تغییرات با موفقیت ذخیره شد!');
	} catch (error) {
		console.error('Failed to save data:', error);
		alert('خطا در ذخیره تغییرات.');
	} finally {
		button.disabled = false;
		button.innerText = 'ثبت تغییرات';
	}
}
// =================== document ready ============================
$("document").ready(async function () {
	const today = new JDate();
	const currentYear = today.getFullYear();
	updateCurrencies();

	fillYears(currentYear);
	$("#year").val(currentYear);

	initTables();

	//events
	$("#year, #month").change(function () {
		initTables();
	});

	$('#dashboard-container').on('click', '.btn-submit', function () {
		handleSubmit(this);
	});
});
