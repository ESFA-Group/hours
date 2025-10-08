let originalApiData = {};
let Debug = false;

const titleMapping = {
	balance_rials_official: 'موجودی حساب‌های رسمی (ریال)',
	balance_rials: 'موجودی حساب‌های غیر رسمی (ریال)',
	balance_dollars: 'موجودی دلاری',
	montly_checks_received: 'چک‌های دریافتی (ریال)',
	montly_checks_issued: 'چک‌های صادر شده (ریال)',
	montly_installment: 'اقساط وام های دریافتی (ریال)',
	montly_total_sales: 'فروش کل داخل (ریال)',
	montly_international_total_sales: 'فروش کل خارج (دلار)',
	individual_sales: 'فروش تفکیکی داخل (ریال)',
	individual_sales_quantities: 'فروش تفکیکی داخل (تعداد)',
	individual_sales_total_received: 'مجموع دریافتی تا این لحظه (ریال)',
	individual_sales_check_received: 'مقدار چک دریافت شده (ریال)',
	individual_sales_unknown: 'مقدار نامعلوم (ریال)',
	international_individual_sales: 'فروش تفکیکی خارج (ریال)',
	international_individual_sales_quantities: '(تعداد) فروش تفکیکی خارج',
	ready_products: 'موجودی تولیدشده آماده تحویل',
	ready_kavosh_products: 'موجودی کاوش تولیدشده آماده تحویل',
	ready_kia_products: 'موجودی کیا تولیدشده آماده تحویل',
	unproduced_workshop_inventory: 'موجودی کارگاه تولید نشده',
	unproduced_kavosh_workshop_inventory: 'موجودی کاوش کارگاه تولید نشده',
	unproduced_kia_workshop_inventory: 'موجودی کیا کارگاه تولید نشده',
	deliverd_1404: 'تحویل داده شده از ابتدای سال',
	deliverd_1403: 'کل تحویلی در سال 1403',
	deliverd_1402: 'کل تحویلی در سال 1402',
	deliverd_1401: 'کل تحویلی در سال 1401',
	deliverd_1400: 'کل تحویلی در سال 1400',
	deliverd_1399: 'کل تحویلی در سال 99',
	turkiye_inventory: 'موجودی ترکیه',
	china_production_orders: 'سفارشات چین درحال تولید',
	total_insured_staffs: 'تعداد کارکنان بیمه‌ای',
	total_uninsured_staffs: 'تعداد کارکنان غیر بیمه',
	total_salary_paid: 'مجموع کل حقوق (ریال)',
	total_insurance_paid: 'مجموع بیمه پرداختی (ریال)'
};

const keyToModelFieldMap = {
	// financial_info
	'balance_rials_official': 'financial_info',
	'balance_rials': 'financial_info',
	'montly_checks_received': 'financial_info',
	'montly_checks_issued': 'financial_info',
	'montly_installment': 'financial_info',
	'montly_total_sales': 'financial_info',
	'individual_sales': 'financial_info',
	'individual_sales_quantities': 'financial_info',
	'individual_sales_total_received': 'financial_info',
	'individual_sales_check_received': 'financial_info',
	'individual_sales_unknown': 'financial_info',
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
	'international_individual_sales_quantities': 'international_sales_info',
	'turkiye_inventory': 'international_sales_info',

	// products_info
	'unproduced_workshop_inventory': 'products_info',
	'ready_products': 'products_info',

	// kavosh products_info
	'unproduced_kavosh_workshop_inventory': 'kavosh_products_info',
	'ready_kavosh_products': 'kavosh_products_info',

	// kia products_info
	'ready_kia_products': 'kia_products_info',
	'unproduced_kia_workshop_inventory': 'kia_products_info',
	'deliverd_1404': 'kia_products_info',
	'deliverd_1403': 'kia_products_info',
	'deliverd_1402': 'kia_products_info',
	'deliverd_1401': 'kia_products_info',
	'deliverd_1400': 'kia_products_info',
	'deliverd_1399': 'kia_products_info',
};

// data backend connection ========================
async function getCurrencies() {
	if (Debug) {
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
				"unit": "ریال"
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
				"unit": "ریال"
			}
		};
	}

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

function createNumericTable(data, title, itemKeys, editable = false) {
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

		tableBody += `
        <tr class="${bgColor}">
            <td>
                ${titleMapping[key] || key}
                ${createInfoIcon(item)}
            </td>
            <td contenteditable="${editable}" data-key="${key}">${item._info.toLocaleString()}</td>
            <td>${formattedDate}</td>
        </tr>`;
	});
	const cardBorderColor = cardBgColor.replace('bg-', 'border-').replace('-subtle', '');
	const cardFooter = editable ? `
        <div class="card-footer text-center">
            <button class="btn btn-primary btn-submit">
                ثبت تغییرات
            </button>
        </div>` : '';
	card.innerHTML = `
		<div class="card h-100 ${cardBorderColor} border-2">
            <div class="card-header ${cardBgColor} ${cardBorderColor}">
				${title}
			</div>
			<div class="card-body p-0">
				<div class="table-responsive">
					<table class="table table-striped table-hover table-vertical-lines">
						<thead>
							<tr class="${cardBgColor}">
								<th>عنوان</th>
								<th>مقدار</th>
								<th>آخرین بروزرسانی</th>
							</tr>
						</thead>
						<tbody>${tableBody}</tbody>
					</table>
				</div>
			</div>
			${cardFooter}
		</div>`;
	document.getElementById('dashboard-container').appendChild(card);
}

function createObjectTable(data, title, itemKeys, editable = false, add_sum = false, percentageConfig = null) {
	const availableItems = itemKeys.filter(key => data[key] && typeof data[key]._info === 'object');
	if (availableItems.length === 0) return;

	const card = document.createElement('div');
	card.className = 'col-lg-12 mb-4';
	const firstItemInfo = data[availableItems[0]]._info;
	const subItemHeaders = Object.keys(firstItemInfo);

	let tableHeader = '<th>عنوان</th>';
	if (add_sum) {
		tableHeader += '<th class="table-info">مجموع</th>';
	}
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

		let rowSum = 0;
		let dataCells = '';
		subItemHeaders.forEach(header => {
			const value = item._info[header] || 0;
			if (add_sum) {
				rowSum += value;
			}
			dataCells += `<td class="data-cell" contenteditable="${editable}" data-key="${key}" data-subkey="${header}">${value.toLocaleString()}</td>`;
		});

		let row = `
        <tr class="${bgColor}" data-row-key="${key}">
            <td>
                ${titleMapping[key] || key}
                ${createInfoIcon(item)}
            </td>`;
		if (add_sum) {
			row += `<td class="row-sum-cell table-info" data-key="${key}" style="font-weight: bold;">${rowSum.toLocaleString()}</td>`;
		}
		row += dataCells;
		row += `<td>${formattedDate}</td></tr>`;
		tableBody += row;
	});

	if (percentageConfig) {
		const numData = data[percentageConfig.numeratorKey];
		const denKeysData = percentageConfig.denominatorKeys.map(key => data[key]);

		if (numData && denKeysData.every(d => d)) {
			let pRow = `<tr class="percentage-row table-info" style="font-weight: bold;"><td>${percentageConfig.title}</td>`;

			if (add_sum) {
				let totalNum = 0;
				let totalDen = 0;
				subItemHeaders.forEach(header => {
					totalNum += numData._info[header] || 0;
					denKeysData.forEach(denData => {
						totalDen += denData._info[header] || 0;
					});
				});
				const totalPercentage = totalDen === 0 ? 0 : (totalNum / totalDen) * 100;
				pRow += `<td class="percentage-cell-sum table-info">${totalPercentage.toFixed(1)}%</td>`;
			}

			subItemHeaders.forEach(header => {
				const numerator = numData._info[header] || 0;
				const denominator = denKeysData.reduce((sum, denData) => sum + (denData._info[header] || 0), 0);
				const percentage = denominator === 0 ? 0 : (numerator / denominator) * 100;
				pRow += `<td class="percentage-cell" data-subkey="${header}">${percentage.toFixed(1)}%</td>`;
			});

			pRow += '<td>-</td></tr>';
			tableBody += pRow;
		}
	}


	const cardBorderColor = cardBgColor.replace('bg-', 'border-').replace('-subtle', '');
	const cardFooter = editable ? `
        <div class="card-footer text-center">
            <button class="btn btn-primary btn-submit">
                ثبت تغییرات
            </button>
        </div>` : '';
	card.innerHTML = `
        <div class="card h-100 ${cardBorderColor} border-2">
            <div class="card-header ${cardBgColor} ${cardBorderColor}">${title}</div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-striped table-hover table-vertical-lines">
                        <thead><tr class="${cardBgColor}">${tableHeader}</tr></thead>
                        <tbody>${tableBody}</tbody>
                    </table>
                </div>
            </div>
            ${cardFooter}
        </div>`;
	document.getElementById('dashboard-container').appendChild(card);

	if (editable) {
		const table = card.querySelector('table');
		table.addEventListener('input', (event) => {
			const targetCell = event.target;
			if (targetCell.classList.contains('data-cell')) {
				const key = targetCell.dataset.key;
				if (!key) return;

				if (add_sum) {
					let newRowSum = 0;
					table.querySelectorAll(`.data-cell[data-key="${key}"]`).forEach(cell => {
						newRowSum += parseInt(cell.innerText.replace(/,/g, ''), 10) || 0;
					});
					const sumCell = table.querySelector(`.row-sum-cell[data-key="${key}"]`);
					if (sumCell) sumCell.innerText = newRowSum.toLocaleString();
				}

				if (percentageConfig) {
					const subkey = targetCell.dataset.subkey;
					const numVal = parseInt(table.querySelector(`.data-cell[data-key="${percentageConfig.numeratorKey}"][data-subkey="${subkey}"]`)?.innerText.replace(/,/g, '') || '0', 10);
					const denVal = percentageConfig.denominatorKeys.reduce((sum, dKey) => {
						const cellVal = table.querySelector(`.data-cell[data-key="${dKey}"][data-subkey="${subkey}"]`)?.innerText.replace(/,/g, '') || '0';
						return sum + parseInt(cellVal, 10);
					}, 0);
					const newPercentage = denVal === 0 ? 0 : (numVal / denVal) * 100;
					const pCell = table.querySelector(`.percentage-cell[data-subkey="${subkey}"]`);
					if (pCell) pCell.innerText = `${newPercentage.toFixed(1)}%`;

					if (add_sum) {
						const totalNum = parseInt(table.querySelector(`.row-sum-cell[data-key="${percentageConfig.numeratorKey}"]`)?.innerText.replace(/,/g, '') || '0', 10);
						const totalDen = percentageConfig.denominatorKeys.reduce((sum, dKey) => {
							const cellVal = table.querySelector(`.row-sum-cell[data-key="${dKey}"]`)?.innerText.replace(/,/g, '') || '0';
							return sum + parseInt(cellVal, 10);
						}, 0);
						const totalPercentage = totalDen === 0 ? 0 : (totalNum / totalDen) * 100;
						const pSumCell = table.querySelector('.percentage-cell-sum');
						if (pSumCell) pSumCell.innerText = `${totalPercentage.toFixed(1)}%`;
					}
				}
			}
		});
	}
}

function getRemainingDays(lastModifyTime, updateIntervalDays) {
	const [datePart, timePart] = lastModifyTime.split(' ');

	const jdate = new JDate(datePart.split('-').map(Number));
	const now = new JDate();

	const diffMs = now._d - jdate._d;
	const daysPassed = Math.floor(diffMs / (1000 * 60 * 60 * 24));

	return Math.max(0, updateIntervalDays - daysPassed);
}

function createInfoIcon(item) {
    const remainingDays = getRemainingDays(item.last_modify_time, item.UPDATE_INTERVAL_DAYS);
    const whoCanSee = item.who_can_see ? item.who_can_see.join(', ') : 'نامشخص';
    const tooltipContent = `${whoCanSee} :قابل مشاهده توسط<br>بازه به روزرسانی: ${item.UPDATE_INTERVAL_DAYS} روز<br>روزهای باقیمانده: ${remainingDays} روز`;
    
    return `<svg class="info-icon-svg" data-bs-toggle="tooltip" data-bs-html="true" title="${tooltipContent}" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
        <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/>
    </svg>`;
}

function getBackgroundColor(lastModifyTime, updateIntervalDays) {
	const now = new Date();
	const lastUpdate = parseJalaliDateTime(lastModifyTime);
	const diffMilliseconds = now.getTime() - lastUpdate.getTime();
	const diffDays = diffMilliseconds / (1000 * 3600 * 24);

	if (diffDays * 2 <= updateIntervalDays) {
		return 'bg-success-subtle';
	} else if (diffDays <= updateIntervalDays) {
		return 'bg-warning-subtle';
	} else {
		return 'bg-danger-subtle';
	}
}

async function initTables(data = null) {
	if (data == null)
		data = await getEyesData($("#year").val());

	document.getElementById('dashboard-container').innerHTML = '';

	createNumericTable(data, 'موجودی‌ها', ['balance_rials', 'balance_rials_official'], window.USER.is_FinancialManager);
	createObjectTable(data, 'موجودی‌ دلاری', ['balance_dollars'], window.USER.is_InternationalFinanceManager, true);
	createObjectTable(data, 'چک‌ها', ['montly_checks_issued', 'montly_checks_received', 'montly_installment'], window.USER.is_FinancialManager);
	createObjectTable(data, 'فروش کل', ['montly_total_sales', 'montly_international_total_sales'], window.USER.is_FinancialManager || window.USER.is_InternationalSalesManager, true);

	const receivedPercentageConfig = {
		title: 'درصد دریافت شده',
		numeratorKey: 'individual_sales_total_received',
		denominatorKeys: ['individual_sales_total_received', 'individual_sales_check_received', 'individual_sales_unknown']
	};
	createObjectTable(data, 'فروش تفکیکی (بدون ارزش افزوده)', ['individual_sales', 'individual_sales_quantities', 'individual_sales_total_received', 'individual_sales_check_received', 'individual_sales_unknown',], window.USER.is_FinancialManager, true, receivedPercentageConfig);
	createObjectTable(data, 'موجودی دستگاه‌ها', ['turkiye_inventory', 'china_production_orders'], window.USER.is_InternationalFinanceManager || window.USER.is_InternationalSalesManager);
	createObjectTable(data, 'موجودی دستگاه‌های اسفا', ['ready_products', 'unproduced_workshop_inventory'], window.USER.is_ProductionManager);
	createObjectTable(data, 'موجودی دستگاه‌های کاوش', ['ready_kavosh_products', 'unproduced_kavosh_workshop_inventory',], window.USER.is_KavoshProductionManager); // dont add || window.USER.is_KavoshProductionManager
	createObjectTable(data, 'موجودی دستگاه‌های کیا الکترونیک', ['ready_kia_products', 'unproduced_kia_workshop_inventory', 'deliverd_1404', 'deliverd_1403', 'deliverd_1402', 'deliverd_1401', 'deliverd_1400', 'deliverd_1399'], window.USER.is_KiaProductionManager);
	createNumericTable(data, 'بیمه کارکنان', ['total_insured_staffs', 'total_uninsured_staffs'], window.USER.is_FinancialManager);
	createObjectTable(data, 'پرداختی کارکنان', ['total_salary_paid', 'total_insurance_paid'], window.USER.is_FinancialManager, true);

	setTimeout(() => {
		const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
		const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
			return new bootstrap.Tooltip(tooltipTriggerEl);
		});
	}, 100);
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
		const value = parseInt(cell.innerText.replace(/,/g, ''), 10) || cell.innerText;

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
		const payload = {}
		// Loop through the grouped updates and send one API request for each model field
		for (const fieldName in groupedUpdates) {
			payload[fieldName] = groupedUpdates[fieldName];
		}
		let result = await postEyesData(year, payload);
		if (result.success) {
			await initTables(result.data);
		}
	} catch (error) {
		console.error('Failed to save data:', error);
		jSuites.notification({
			error: 1,
			name: 'Error',
			title: "خطا در ثبت تغییرات",
			message: error,
		});
	} finally {
		button.disabled = false;
		button.innerText = 'ثبت تغییرات';
	}
}
// =================== document ready ============================
$("document").ready(async function () {
	console.log("is_superuser: " + window.USER.is_superuser);

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
