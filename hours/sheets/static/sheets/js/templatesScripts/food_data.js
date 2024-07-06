"use strict";
//CONSTANTS************************************************
const TODAY = new JDate();
TODAY._d.setHours(0, 0, 0, 0)


const CURRENT_YEAR = TODAY.getFullYear();
var ACTIVE_YEAR = CURRENT_YEAR;

const CURRENT_MONTH = TODAY.getMonth();
var ACTIVE_MONTH = CURRENT_MONTH

const CURRENT_MONTH_WEEKS = getWeeksOfMonth()
var ACTIVE_MONTH_WEEKS = CURRENT_MONTH_WEEKS

const [CURRENT_WEEK, CURRENT_WEEK_INDEX] = getCurrentWeek()
var ACTIVE_WEEK = CURRENT_WEEK
var ACTIVE_WEEK_INDEX = CURRENT_WEEK_INDEX
// ********************************************************

function fillYears(yearId, year = ACTIVE_YEAR) {
	for (let i = window.START_YEAR; i <= year; i++) {
		$(yearId).append($("<option>").text(i));
	}
}

function fillWeeks() {
	let weeks = getWeeksOfMonth()
	$("#modal_week").empty();
	for (let i = 0; i < weeks.length; i++) {
		$("#modal_week").append($("<option>")
			.text(`week${i + 1} (${weeks[i]['0'].format('MM/DD')} --> ${weeks[i]['6'].format('MM/DD')})`)
			.val(i));
	}
}

function getWeeksOfMonth() {
	let year = ACTIVE_YEAR
	let month = ACTIVE_MONTH
	const totalDaysInMonth = JDate.daysInMonth(year, month);

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
					month += 1;
					if (month > 12) {
						year += 1
						month = 1
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

function getCurrentWeek() {
	for (const [index, week] of Object.entries(CURRENT_MONTH_WEEKS)) {
		let startweekday = week[0]
		let dayDiff = getDayDiff(TODAY, startweekday)
		if (dayDiff <= 0 && dayDiff >= -6) {
			return [week, index];
		}
	};
}

function getDayDiff(JDate1, JDate2) {
	let diff = JDate2._d.getTime() - JDate1._d.getTime()
	return Math.round(diff / (1000 * 60 * 60 * 24));
}

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

async function postRequest(url, data) {
	try {
		const response = await fetch(url, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': window.CSRF_TOKEN,
			},
			body: JSON.stringify(data)
		});
		return await response.json()
	} catch (err) {
		jSuites.notification({
			error: 1,
			name: 'Error',
			title: "Updating Sheet",
			message: err,
		});
	}
}

async function putRequest(url, data) {
	try {
		const response = await fetch(url, {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': window.CSRF_TOKEN,
			},
			body: JSON.stringify(data)
		});
		return await response.json()
	} catch (err) {
		jSuites.notification({
			error: 1,
			name: 'Error',
			title: "Updating Sheet",
			message: err,
		});
	}
}

async function getSheetDBT(year, month) {
	const url = `/hours/api/sheets/${year}/${month}`;
	return await getRequest(url)
}


async function getFoodDataDBT(year = ACTIVE_YEAR, month = ACTIVE_MONTH) {
	const url = `/hours/api/FoodData/${year}/${month}`;
	return await getRequest(url)
}

async function saveFoodDataDBT(fooddata) {
	const url = `/hours/api/FoodManagement/${ACTIVE_YEAR}/${ACTIVE_MONTH}`;

	let res = await putRequest(url, fooddata);
}

async function getFoodOrderSummaryDBT(day = TODAY.getDate(), weekIndex = CURRENT_WEEK_INDEX, month = CURRENT_MONTH, year = CURRENT_YEAR) {
	const url = `/hours/api/daily_foods_order/${year}/${month}/${weekIndex}/${day}`;
	const data = await getRequest(url);
	return data;
}

async function getFoodOrderSummaryExcelDBT(weekIndex = CURRENT_WEEK_INDEX, month = CURRENT_MONTH, year = CURRENT_YEAR) {
	const url = `/hours/api/daily_foods_order/${year}/${month}/${weekIndex}/0`;

	const $form = $("<form>", { action: url, method: "POST" });
	$form.append($("<input type='hidden' name='csrfmiddlewaretoken'>").val( window.CSRF_TOKEN));
	$("body").append($form);
	$form.submit();

}

async function renderSheet(food_data) {
	resetFoodSheet();

	let foodColumns = []
	if (typeof food_data[0] === 'object' && food_data[0].hasOwnProperty('data')) {
		foodColumns = food_data[0].data.map(foodItem => ({
			type: 'numeric',
			title: foodItem.name,
			width: 130,
			mask: '#,##0',
			readOnly: false
		}));
	}

	const columns = [
		{ type: 'text', title: 'Day', width: 80, readOnly: true },
		{ type: 'text', title: 'WeekDay', width: 130, readOnly: true },
		...foodColumns
	];


	let monthdata = await getSheetDBT(ACTIVE_YEAR, ACTIVE_MONTH)

	let foodSheetData = mergeMonthDataWithFoodData(monthdata.data, food_data)

	window.spreadTable = jspreadsheet(document.getElementById('spreadsheet'), {
		data: foodSheetData,
		columns: columns,
		allowInsertColumn: false,
		allowInsertRow: false,
		allowDeleteRow: false,
		allowRenameColumn: false,
		onundo: onChangeHandler,
		onredo: onChangeHandler,
		onchange: (worksheet, cell, x, y, value) => onChangeHandler(worksheet, cell, x, y, value, foodSheetData, food_data),
		ondeletecolumn: onChangeHandler,
		onselection: onselectionHandler,
		tableOverflow: true,
		tableHeight: "100%",
		updateTable: function (el, cell, x, y, source, value, id) {
			if (value == "Fri") {
				cell.style.color = 'red';
			}
		}
	});
	window.spreadTable.hideIndex();
}

function makePreviousDaysReadonly(y, cell) {
	const todayIndex = TODAY.getDate() - 1;
	if (y < todayIndex) {
		cell.classList.add('readonly');
		cell.setAttribute('readonly', 'readonly');
	}
}

function resetFoodSheet() {
	if (typeof window.spreadTable === 'object') {
		window.spreadTable.destroy();
	}
}

function onChangeHandler(worksheet, cell, x, y, value, foodSheetData, food_data) {
	const rawData = window.spreadTable.getJson();
	const tableData = convertTableData(rawData);
	const currentValue = foodSheetData[y][food_data[0].data[x - 2].name];
	value = removeCommasAndConvertToNumber(value)
	if (value === currentValue) {
		return;
	}
	const foodid = x - 2;
	const day = +y + 1;

	let index;
	let foodDataLastIndex = food_data.length - 1
	if ((index = food_data.findIndex(item => item.day === day)) !== -1) {
		updateFoodsPrice();
		removeDuplicates(food_data)
		saveFoodDataDBT(food_data);
		renderSheet(food_data);
	}
	else if (day < food_data.at(-1).day) {
		const [newIndex, newItem] = findAndCopyLastLessThan(food_data, day);
		newItem.day = day;
		newItem.data[foodid].price = value;
		food_data.splice(newIndex, 0, newItem);
		index = newIndex + 1;
		updateFoodsPrice()
		saveFoodDataDBT(food_data);
		renderSheet(food_data);
	}
	else {
		let new_data = JSON.parse(JSON.stringify(food_data.at(-1)));
		new_data.day = day;
		new_data.data[foodid].price = value;
		food_data.push(new_data);
		saveFoodDataDBT(food_data);
		renderSheet(food_data);
	}

	function updateFoodsPrice() {
		do {
			food_data.at(index).data[foodid].price = (+value);
			index += 1;
		} while (index <= foodDataLastIndex && food_data.at(index).data[foodid].price < +value);
	}
}

function removeCommasAndConvertToNumber(inputString) {
    let cleanedString = inputString.replace(/,/g, '');

    let numberValue = Number(cleanedString);

    return numberValue;
}

function removeDuplicates(data) {
	data.forEach((item, index) => {
		if (index === data.length - 1) return;

		const currentItemData = JSON.stringify(item.data);
		const nextItemData = JSON.stringify(data[index + 1].data);

		if (currentItemData === nextItemData) {
			// Remove the item with the greater day value
			if (item.day > data[index + 1].day) {
				data.splice(index, 1);
			} else {
				data.splice(index + 1, 1);
			}
		}
	});
	return data
}

function findAndCopyLastLessThan(array, newDay) {
	for (let i = array.length - 1; i >= 0; i--) {
		const item = array[i];

		if (item.day < newDay) {
			return [i + 1, JSON.parse(JSON.stringify(item))];
		}
	}
	return null;
}

function convertTableData(rawData) {
	/*  table's getJson method won't return table data correctly, some headers (mostly created ones in project adding) 
		are wrong in each rows data. this function iterates each row and correct wrong keys to real keys in header.
	*/
	const headers = window.spreadTable.getHeaders(true);
	rawData.map(row => {
		for (let [key, value] of Object.entries(row)) {
			if (!headers.includes(key)) {
				row[headers[key]] = value;
				delete row[key];
			}
		}
	})
	return rawData
}

function onselectionHandler(worksheet, px, py, ux, uy, origin) {
	// scroll to element while working with arrow keys or sth when selected element is out of viewport
	const td = $(worksheet).find('td.highlight-selected.highlight').get(0);
	if (td === undefined)
		return false
	const box = td.getBoundingClientRect();
	if (box.top > window.innerHeight || box.bottom <= 0)
		td.scrollIntoView();
}

function mergeMonthDataWithFoodData(monthData, foodData) {
	const foodMap = new Map(foodData.map(item => [item.day, item.data]));
	let lastFoodData = [];
	let lastFoodPairs = {};

	return monthData.map(({ Day, WeekDay }) => {
		if (foodMap.has(Day)) {
			lastFoodData = foodMap.get(Day);
			lastFoodPairs = lastFoodData.reduce((acc, { name, price }) => {
				acc[name] = price;
				return acc;
			}, {});
		}

		return { Day, WeekDay, ...lastFoodPairs };
	});
}


function editFoodsBtnClick() {
	fillEditFoodsFormFromDB()
	$("#foodNamesModal").modal('show')
}

function FoodsOrderBtnClick() {
	fillFoodOrderDates()
	fillFoodsOrderFromDB()
	$("#foodsOrderModal").modal('show')
}

async function fillEditFoodsFormFromDB() {
	let res = await getFoodDataDBT()
	if (typeof res[0] === 'object' && res[0].hasOwnProperty('data')) {
		$('#dynamicInputFields').empty();
		for (let food of res[0].data) {
			foodItemCount = food.id
			addEmptyFoodRow()
			fillFoodRow(food.id, food.name)
		}
	}
}

function fillFoodOrderDates() {
	fillYears("#modal_year")
	fillWeeks();
	$("#modal_year").val(CURRENT_YEAR);
	$("#modal_month").val(CURRENT_MONTH);
	$("#modal_week").val(CURRENT_WEEK_INDEX);

}

async function fillFoodsOrderFromDB() {
	$("#orderList tbody").empty();

	const data = await getFoodOrderSummaryDBT();


	for (let item of data) {
		var newRow = `
			<tr>
				<td>${item.name}</td>
				<td>${item.count}</td>
			</tr>
		`;
		$("#orderList tbody").append(newRow);
	}
}

async function export_excel_click() {
	const year = $("#modal_year").val();
	const month = $("#modal_month").val();
	const week_index = $("#modal_week").val();
	const week = CURRENT_MONTH_WEEKS[week_index]
	await getFoodOrderSummaryExcelDBT(ACTIVE_WEEK_INDEX)
}


var foodItemCount = 1;
function addEmptyFoodRow() {
	const newRow = `
	<div class="d-flex align-items-end mx-1" id="row${foodItemCount}">
		<div class="flex-grow-1">
			<label for="food${foodItemCount}">Food Item ${foodItemCount}:</label>
			<input type="text" class="form-control" id="food${foodItemCount}" placeholder="Enter food item">
		</div>
		<div class="ml-2">
			<button type="button" class="btn btn-danger" onclick="deleteFoodRow(${foodItemCount})">—</button>
		</div>
	</div>
	`;


	$('#dynamicInputFields').append(newRow);
	foodItemCount++;
}

function fillFoodRow(id, name) {
	$(`#food${id}`).val(name);
}

function deleteFoodRow(rowId) {
	$(`#row${rowId}`).remove();
}

async function updateFoodClick() {
	const url = `/hours/api/FoodManagement/${ACTIVE_YEAR}/${ACTIVE_MONTH}`;
	const data = getModalFormFoodData()

	let res = await postRequest(url, data);
	renderSheet(res)
}

function getModalFormFoodData() {
	let foodData = {};

	for (let i = 1; i <= foodItemCount; i++) {
		let foodInput = document.getElementById(`food${i}`);

		if (foodInput) {
			let foodValue = foodInput.value;

			foodData[i] = foodValue;
		}
	}

	return foodData;
}

function handleChangeModalWeek() {
	ACTIVE_WEEK_INDEX = $("#modal_week").val();
	ACTIVE_WEEK = ACTIVE_MONTH_WEEKS[ACTIVE_WEEK_INDEX];
}

$("document").ready(async function () {
	fillYears("#year");
	const food_data = await getFoodDataDBT()
	renderSheet(food_data)
	$("#year").val(ACTIVE_YEAR);
	$("#month").val(ACTIVE_MONTH);


	$("#year, #month").change(async function () {
		ACTIVE_YEAR = $("#year").val()
		ACTIVE_MONTH = $("#month").val()

		const food_data = await getFoodDataDBT()
		renderSheet(food_data)
	});
	$("#modal_year, #modal_month, #modal_week").change(async function () {
		handleChangeModalWeek()
	});
});
