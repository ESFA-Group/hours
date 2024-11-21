"use strict";
//CONSTANTS************************************************
const TODAY = new JDate();
TODAY._d.setHours(0, 0, 0, 0)


const CURRENT_YEAR = TODAY.getFullYear();
var ACTIVE_YEAR = CURRENT_YEAR;

const CURRENT_MONTH = TODAY.getMonth();
var ACTIVE_MONTH = CURRENT_MONTH

var ACTIVE_DAY = TODAY.getDate();

let _REPORT;

let submitTimer;
let inactivityTimer;
let isSubmitting = false;

// ********************************************************

function fillYears(yearId, year = CURRENT_YEAR) {
	$(yearId).empty();
	for (let i = window.START_YEAR; i <= year; i++) {
		$(yearId).append($("<option>").text(i));
	}
}

function initialize_date_dropdowns() {
	$("#year").val(ACTIVE_YEAR);
	$("#month").val(ACTIVE_MONTH);
	$("#day").val(ACTIVE_DAY);
}


//#region API-Request 
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
//#endregion

async function get_report() {
	const url = `/hours/api/daily_report_user/${ACTIVE_YEAR}/${ACTIVE_MONTH}/${ACTIVE_DAY}`;
	return await getRequest(url);
}

function updateTitle() {
	$("#reportTitle").text("ثبت گزارش تاریخ " + $("#year").val() + "/" + $("#month").val() + "/" + $("#day").val());
}

async function get_active_day_report() {
	updateTitle();

	if (!_REPORT) {
		_REPORT = await get_report();
	}

	$("#report_content").text(_REPORT['content']);
	$("#main_comment").val(_REPORT['main_comment'] ? _REPORT['main_comment'] : 'هنوز نظری ثبت نشده');
	$("#sub_comment").val(_REPORT['sub_comment'] ? _REPORT['sub_comment'] : 'هنوز نظری ثبت نشده');
}

async function handle_submit_button_activation() {
	if (!_REPORT) {
		_REPORT = await get_report();
	}

	if (is_submit_valid()) {
		toggle_submmit_button(true)
	} else {
		toggle_submmit_button(false)
	}

	function toggle_submmit_button(shouldShow) {
		if (shouldShow) {
			// Check if the button already exists to avoid duplicates
			if ($("#submitReportBtn").length === 0) {
				$("#report_from").append(
					`
                <button id="submitReportBtn" class="btn btn-primary d-flex justify-content-center align-items-center position-relative" type="submit">
                    <span id="submit-report-spinner" class="spinner-border spinner-border-sm d-none me-1" role="status"></span>
                    <span>ثبت گزارش</span>
                    <div id="submit-report-check" class="bg-primary d-none">
                        ✅
                    </div>
                </button>
                `
				);
			}
		} else {
			$("#submitReportBtn").remove();
		}
	}
}

function startSubmitting() {
	if (!isSubmitting) {
		isSubmitting = true;
		submitTimer = setInterval(submitForm, 5000);
	}
}

function stopSubmitting() {
	clearInterval(submitTimer);
	isSubmitting = false;
}

async function submitForm() {
	if (!is_submit_valid()) {
		return
	}
	const content = $('#report_content').val();
	const url = `/hours/api/daily_report_user/${ACTIVE_YEAR}/${ACTIVE_MONTH}/${ACTIVE_DAY}`;

	return await postRequest(url, { content });
}

function is_submit_valid() {
	const currentHour = new Date().getHours(); // Get the current hour (0-23)
	return _REPORT.no_limit_submit_btn || (currentHour >= _REPORT.start_report_hour && currentHour <= _REPORT.end_report_hour)
}

$("document").ready(async function () {
	_REPORT = await get_report();
	fillYears("#year");
	initialize_date_dropdowns();
	get_active_day_report();
	handle_submit_button_activation()

	$("#year, #month").change(async function () {
		ACTIVE_YEAR = $("#year").val()
		ACTIVE_MONTH = $("#month").val()
		get_active_day_report();
	});

	$("#day").change(async function () {
		ACTIVE_DAY = $("#day").val();
		get_active_day_report();
	});

	$("#report_content").on("input", async function () {
		if (!_REPORT) {
			_REPORT = await get_report();
		}

		if (is_submit_valid()) {
			startSubmitting(); // Start submitting on input
			clearTimeout(inactivityTimer);
			inactivityTimer = setTimeout(stopSubmitting, 5000);
		}
	});

	$('#report_from').on('submit', async function (e) {
		e.preventDefault();

		$("#submit-report-spinner").removeClass('d-none');
		$("#submitReportBtn").prop('disabled', true)

		await submitForm();

		$("#submitReportBtn").prop('disabled', false)
		$("#submit-report-spinner").addClass('d-none');
		$("#submit-report-check").removeClass('d-none').fadeIn(500, function () {
			// After fade in, fade out after a delay
			setTimeout(() => {
				$("#submit-report-check").fadeOut(500, function () {
					$(this).addClass('d-none').css('display', '');
				});
			}, 1000); // Delay before fading out
		});
		stopSubmitting();
	});
});
