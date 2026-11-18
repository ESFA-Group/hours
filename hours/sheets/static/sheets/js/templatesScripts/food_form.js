"use strict";
//CONSTANTS************************************************
// const TODAY = new JDate(1403, 2, 22);
const TODAY = new JDate();
TODAY._d.setHours(0, 0, 0, 0)


const CURRENT_YEAR = TODAY.getFullYear();
var ACTIVE_YEAR = CURRENT_YEAR;

const CURRENT_MONTH = TODAY.getMonth();
var ACTIVE_MONTH = CURRENT_MONTH

const CURRENT_MONTH_WEEKS = getWeeksOfMonth()
var ACTIVE_MONTH_WEEKS = CURRENT_MONTH_WEEKS

const [CURRENT_WEEK, CURRENT_WEEK_INDEX] = getCurrentWeek(CURRENT_MONTH_WEEKS)
var ACTIVE_WEEK = CURRENT_WEEK
var ACTIVE_WEEK_INDEX = CURRENT_WEEK_INDEX


const weekdays = [
	'شنبه',
	'یک‌شنبه',
	'دوشنبه',
	'سه‌شنبه',
	'چهارشنبه',
	'پنج‌شنبه',
	'جمعه',
]
// ********************************************************

async function getRequest(url) {
	try {
		let response = await fetch(url);
		return await response.json();
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

async function getFoodDataDBT(year = ACTIVE_YEAR, month = ACTIVE_MONTH) {
	const url = `/api/FoodData/${year}/${month}`;
	return await getRequest(url)
}


function fillYears() {
	for (let i = window.START_YEAR; i <= ACTIVE_YEAR; i++) {
		$("#year").append($("<option>").text(i));
	}
}

function fillWeeks() {
	let weeks = getWeeksOfMonth()
	$("#week").empty();
	for (let i = 0; i < weeks.length; i++) {
		$("#week").append($("<option>")
			.text(`week${i + 1} (${weeks[i]['0'].format('MM/DD')} --> ${weeks[i]['6'].format('MM/DD')})`)
			.val(i));
	}
}

function getWeeksOfMonth() {
	let year = ACTIVE_YEAR
	let month = ACTIVE_MONTH
	let totalDaysInMonth = JDate.daysInMonth(year, month);
	if(year == 1403 && month == 6)
		totalDaysInMonth = 31
	
	let weeksDate = []
	let shouldbreak = false;
	for (let i = 1; i <= totalDaysInMonth; i++) {
		if (shouldbreak) {
			break;
		}
		let startDate = new JDate(year, month, i);
		if (startDate.getDay() === 6) {
			weeksDate.push({
				0: startDate
			})
			for (let j = 1; j < 7; j++) {
				i = i + 1
				if (i > totalDaysInMonth) {
					month = (parseInt(month) + 1).toString();
					if (month > 12) {
						year += (parseInt(year) + 1).toString();
						month = '1'
					}
					i = 1;
					startDate = new JDate(year, month, i);

					weeksDate[weeksDate.length - 1][j] = startDate;
					shouldbreak = true;
					continue;
				}
				startDate = new JDate(year, month, i);
				weeksDate[weeksDate.length - 1][j] = startDate;
			}
		}
	}
	return weeksDate;
}

function getCurrentWeek(current_week) {
	for (var [index, week] of Object.entries(current_week)) {
		let startweekday = week[0]
		let dayDiff = getDayDiff(TODAY, startweekday)
		if (dayDiff <= 0 && dayDiff >= -6) {
			return [week, index];
		}
	};
	// try searching the previous month
	ACTIVE_MONTH = CURRENT_MONTH - 1
	ACTIVE_MONTH_WEEKS = getWeeksOfMonth()
	return getCurrentWeek(ACTIVE_MONTH_WEEKS)
}

function getDayDiff(JDate1, JDate2) {
	let diff = JDate2._d.getTime() - JDate1._d.getTime()
	return Math.round(diff / (1000 * 60 * 60 * 24));
}

async function initializeFoodTable() {
	$("#foodTable tbody").empty();
	$("#foodTable thead tr").remove();
	let [foods, order_mode] = await getFoodDataDBT()

	let foodData = findLastFoodPriceDataOfTheWeek(foods)
	if (foodData === undefined) {
		fillFoodTableHeader([])
	}
	else {
		fillFoodTableHeader(foodData.data)
	}
	await fillFoodTablebody()
	desablePreviousDays(order_mode)
}

function findLastFoodPriceDataOfTheWeek(dailyFoodsData) {
	let currentWeekFirstDay = ACTIVE_WEEK[0].getDate();
	for (let i = dailyFoodsData.length - 1; i >= 0; i--) {
		const foodData = dailyFoodsData[i];
		if (foodData.day <= currentWeekFirstDay)
			return foodData;
	}
}

function fillFoodTableHeader(foods) {

	var headersRow = $("<tr>");
	headersRow.append($("<th>").text("غذا \\ روز"));


	foods.forEach(function (food) {
		headersRow.append(`
			<th data-id="${food.id}">
				<div class="d-flex flex-column">
					<span>${food.name}</span>
					<span>${food.price.toLocaleString('en-US')}</span>
				</div>
			</th>`
		);
	});
	$("#foodTable thead").append(headersRow);
}

async function GetHolidays(year, month1, month2) {
	let holidays = {}
	holidays[month1] = await EsfaPersianHolidays.getHolidays(year, month1)
	if (month1 != month2) {
		holidays[month2] = await EsfaPersianHolidays.getHolidays(year, month2)
	}

	return holidays;
}

async function fillFoodTablebody() {
	let week_days = Object.entries(ACTIVE_WEEK)
	let Holiday = await GetHolidays(ACTIVE_YEAR, week_days[0][1].date[1], week_days[6][1].date[1])

	for (const [index, day] of week_days) {
		var row = $("<tr>");
		// let IsHoliday = await EsfaPersianHolidays.IsHoliday(ACTIVE_YEAR, day.date[1], day.date[2])
		let isHoliday = Holiday[day.date[1]].includes(day.date[2])
		// Add day cell
		let cell = $(`<td>${day.format("dddd")}</td>`).val(day.date[2]).attr({
			'data-month': day.date[1]
		})
		if (isHoliday) {
			cell.addClass("holiday-row")
		}
		// row.append($(`<td>${day.format("dddd")}</td>`).val(day.date[2]));
		row.append(cell);

		const headerCount = $("#foodTable thead tr th").length
		for (let i = 1; i < headerCount; i++) {
			var cellContent = $("<span>");
			cellContent.append($("<input>", {
				type: "checkbox",
				class: "cell-checkbox",
			}));
			row.append($("<td>").append(cellContent));
		}

		$("#foodTable tbody").append(row);
	}
}

async function fillFoodTable() {
	const food_data = await getFoodData()
	if (food_data.length == 0) {
		return;
	}

	let activeWeek_food_data = food_data[ACTIVE_WEEK_INDEX]
	const [header, ...rows] = $('#foodTable tr')
	if (!Array.isArray(activeWeek_food_data)) 
		return
	activeWeek_food_data.forEach(dayfood => {
		const matchingRow = rows.filter(r => r.cells[0].value == dayfood.day)[0];
		if (matchingRow !== undefined) {
			const [day, ...checkboxes] = matchingRow.cells;
			for (const foodId of dayfood.foods) {
				var checkbox = checkboxes.find((c, i) => $(header.cells[i + 1]).attr('data-id') == foodId).querySelector('input[type="checkbox"]');
				checkbox['checked'] = true;
				continue;
			}
		}
	});
}

async function getFoodData() {
	const url = `/api/order_food/${ACTIVE_YEAR}/${ACTIVE_MONTH}`;
	try {
		let res = await fetch(url);
		return await res.json();
	}
	catch (err) {
		jSuites.notification({
			error: 1,
			name: 'Error',
			title: "Fetching Projects",
			message: err,
			timeout: 6000,
		});
	}
}

async function submitSelectedFoods() {
	$("#submit-food-spinner").removeClass('d-none');
	$("#submitFoodBtn").prop('disabled', true)
	const currentWeekSelectedFood = getSelectedFoodsFromTable();

	saveFoodData(currentWeekSelectedFood);
}


function saveFoodData(data) {
	const url = `/api/order_food/${ACTIVE_YEAR}/${ACTIVE_MONTH}`;

	fetch(url, {
		method: 'post',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': window.CSRF_TOKEN,
		},
		body: JSON.stringify({ "data": data, "index": ACTIVE_WEEK_INDEX }),
	})
		.then(res => res.json())
		.then(() => {
			return new Promise(resolve => setTimeout(resolve, 300)); // Wait for 1 second
		})
		.then(() => {
			$("#submit-food-spinner").addClass('d-none');
			$("#submit-food-check").removeClass('d-none').fadeIn(500, function () {
				// After fade in, fade out after a delay
				setTimeout(() => {
					$("#submit-food-check").fadeOut(500, function () {
						$(this).addClass('d-none').css('display', '');
					});
				}, 1000); // Delay before fading out
			});
		})
		.then(() => {
			$("#submitFoodBtn").prop('disabled', false);
		})
		.catch(err => {
			$("#submit-food-spinner").addClass('d-none');
			$("#submitFoodBtn").prop('disabled', false);

			jSuites.notification({
				error: 1,
				name: 'Error',
				title: "Updating Sheet",
				message: err,
			});
		});
}


function getSelectedFoodsFromTable() {
	let currentWeekSelectedFood = [];
	const [headerRow, ...bodyRows] = $('#foodTable tr');

	for (const row of bodyRows) {
		let selectedFoodsInRow = [];
		const [day, ...checkboxes] = row.cells;
		checkboxes.forEach((c, i) => {
			if (c.querySelector('input[type="checkbox"]').checked) {
				let headerCell = headerRow.cells[i + 1]; // Adjusted index to skip day column
				let foodId = $(headerCell).attr('data-id');
				selectedFoodsInRow.push(parseInt(foodId));
			}
		});
		currentWeekSelectedFood.push({ "month": day.getAttribute("data-month"), "day": day.value, "foods": [...selectedFoodsInRow] });
	}
	return currentWeekSelectedFood;
}

async function handleChangeModalWeekAsync() {
	ACTIVE_WEEK_INDEX = $("#week").val();
	ACTIVE_WEEK = ACTIVE_MONTH_WEEKS[ACTIVE_WEEK_INDEX];
	await initializeFoodTable();
	await fillFoodTable();
	return;
}

function desablePreviousDays(order_mode) {
	let tableRows = $("#foodTable tbody tr")
	// modes:
	//     0 -->  disablePastDays
	//     1 -->  free
	//     2 -->  disableWholeWeek

	if (order_mode == 1) {
		return;
	}

	let diff = ACTIVE_WEEK[0]._d - CURRENT_WEEK[0]._d;

	if (diff === 0) {//current week
		if (order_mode == 2) {
			disableWeekChechboxes(tableRows);
		}
		else if (order_mode == 0) {
			let today = new Date();
			let disableUntil = (today.getDay() + 1) % 7;  // Get the current day of the week (0 = Sunday, 1 = Monday, ..., 6 = Saturday)
			if (today.getHours() >= 10) {  // Check if the current hour is 10 PM or later
				disableUntil += 1;
			}


			for (let i = 0; i < disableUntil; i++) {
				let checkboxes = $(tableRows[i]).find("input[type='checkbox']");
				checkboxes.prop("disabled", true);
			}
		}
	}
	else if (diff < 0) {//past weeks
		disableWeekChechboxes(tableRows)
	}
}
function disableWeekChechboxes(tableRows) {
	for (const row of tableRows) {
		let checkboxes = $(row).find("input[type='checkbox']");
		checkboxes.prop("disabled", true);
	}
}

$("document").ready(async function () {

	fillYears(ACTIVE_YEAR);
	fillWeeks();
	$("#year").val(ACTIVE_YEAR);
	$("#month").val(ACTIVE_MONTH);
	$("#week").val(CURRENT_WEEK_INDEX);
	handleChangeModalWeekAsync()

	$("#current-sheet-date").text(`${ACTIVE_YEAR}/${ACTIVE_MONTH}`);

	$("#year, #month").change(function () {
		ACTIVE_YEAR = $("#year").val()
		ACTIVE_MONTH = $("#month").val()
		ACTIVE_MONTH_WEEKS = getWeeksOfMonth()
		fillWeeks();
		handleChangeModalWeekAsync()
	});

	$("#week").change(async function () {
		$("#week").prop("disabled", true);
		await handleChangeModalWeekAsync();
		$("#week").prop("disabled", false);
	});

	$("#foodTable tbody").on("click", "td", function (e) {
		if (!$(e.target).is('.cell-checkbox')) {
			var $checkbox = $(this).find('.cell-checkbox');
			if (!$checkbox.prop("disabled"))
				$checkbox.prop('checked', !$checkbox.prop('checked'));
		}
	});

	$("#submitFoodBtn").on("click", async function () {
		await submitSelectedFoods()
	});
});