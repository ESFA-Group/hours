"use strict";
//CONSTANTS************************************************
const TODAY = new JDate();
TODAY._d.setHours(0, 0, 0, 0)
let is_manager_commenter = false;
let ActiveUser = "";

const CURRENT_YEAR = TODAY.getFullYear();
var ACTIVE_YEAR = CURRENT_YEAR;

const CURRENT_MONTH = TODAY.getMonth();
var ACTIVE_MONTH = CURRENT_MONTH

var ACTIVE_DAY = TODAY.getDate();
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

async function postRequest(url, data, errTitle = "Updating Sheet") {
	try {
		const response = await fetch(url, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': window.CSRF_TOKEN,
			},
			body: JSON.stringify(data)
		});
		if (response.ok) {
			return await response.json()
		}
		else {
			jSuites.notification({
				error: 1,
				name: 'Error',
				title: errTitle + " | " + response.status,
				message: response.statusText + " at " + url.replace("/hours/api/", ""),
			});
		}
	} catch (err) {
		jSuites.notification({
			error: 1,
			name: 'Error',
			title: errTitle,
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

async function get_reports_by_users() {
	const url = `/hours/api/daily_report_management/${ACTIVE_YEAR}/${ACTIVE_MONTH}`;
	return await getRequest(url);
}

async function get_reporting_limit() {
	const url = `/hours/api/daily_report_setting_management`;
	let res = await getRequest(url);
	return res;
}

function updateTitle() {
	$("#reportTitle").text("Submit Report " + $("#month").val() + "/" + $("#day").val());
}

async function get_active_day_report() {
	let res = await get_reports_by_users();
	let reports_by_users = res['data']
	is_manager_commenter = res['user']['is_MainReportManager']
	pre_load_user_reports();

	const $userList = $('#userList');
	$.each(reports_by_users, function (userName, reports) {
		const listItem = $('<li></li>')
			.addClass('list-group-item user-item')
			.text(`${userName} (${reports.length} reports)`)
			.attr('data-user-id', userName);

		// Append the list item to the user list
		$userList.append(listItem);

		// Add a click event to each list item
		listItem.on('click', function () {
			$('.user-item').removeClass('active');
			$(this).addClass('active');
			pre_load_user_reports()
			ActiveUser = userName;
			load_user_reports(userName, reports);
		});

		if (Object.keys(reports_by_users).indexOf(userName) === 0) {
			ActiveUser = userName;
			listItem.addClass('active');
		}
	});

	if (Object.keys(reports_by_users).length > 0) {
		const firstUser = Object.keys(reports_by_users)[0];
		const firstReports = reports_by_users[firstUser];
		load_user_reports(firstUser, firstReports);
	}
}

async function initialize_reporting_limit() {
	let res = await get_reporting_limit();
	if (res['no_limit_submission']) {
		$("#noLimitSubmissionRadioBtn").prop('checked', true).change();
	}
	else {
		$("#allowes5t10RadioBtn").prop('checked', true).change();
	}
}

async function saveReportingLimitModeDBT(valueNumber) {
	let limitation = false
	if (valueNumber == 0) {
		limitation = false
	}
	else if (valueNumber == 1) {
		limitation = true
	}

	const url = `/hours/api/daily_report_setting_management`;
	await postRequest(url, { "no_limit_submission": limitation });
}

function pre_load_user_reports() {
	const $reportsContainer = $('#reports_container');
	$reportsContainer.empty()
	for (let day = TODAY.getDate(); day >= 1; day--) {
		let reportHtml = `
			<div id="report_${day}" class="border p-2 mb-1 missed-report" style="border-radius: 8px;">
				<div class="card shadow mb-4">
					<div class="card-body">
						<h4 class="card-title fw-bold">Report #${day}</h4>
						<textarea id="report_content_${day}" class="form-control" name="content" disabled placeholder="گزارشی ارسال نشده" dir="rtl"></textarea>
					</div>
				</div>
		`;

		if (is_manager_commenter) {
			reportHtml += `
				<div class="card shadow mb-4">
					<div class="card-body">
						<h5 class="card-title fw-semibold">Manager's Comment:</h5>
						<div class="mb-3">
							<textarea id="manager_comment_${day}" name="content" class="form-control" placeholder="کامنت خود را وارد کنید" rows="4" required dir="rtl"></textarea>
						</div>
						
						<div class="form-check mb-2">
							<input class="form-check-input" type="checkbox" id="manager_hide_user_checkbox_${day}">
							<label class="form-check-label">
								Hide for User
							</label>
						</div>
						<div class="form-check">
							<input class="form-check-input" type="checkbox" id="hide_supervisor_checkbox_${day}">
							<label class="form-check-label">
								Hide for Supervisor
							</label>
						</div>

					</div>
				</div>

				<div class="card shadow mb-4">
					<div class="card-body">
						<h5 class="card-title fw-semibold">Supervisor's Comment:</h5>
						<textarea id="supervisor_comment_${day}" class="form-control" placeholder="کامنتی داده نشده" disabled dir="rtl"></textarea>
					</div>
				</div>
			`;
		} else {
			reportHtml += `
				<div class="card shadow mb-4">
					<div class="card-body">
						<h5 class="card-title fw-semibold">Manager's Comment:</h5>
						<textarea id="manager_comment_${day}" class="form-control" placeholder="کامنتی داده نشده" disabled dir="rtl"></textarea>
					</div>
				</div>

				<div class="card shadow mb-4">
					<div class="card-body">
						<h5 class="card-title fw-semibold">Supervisor's Comment:</h5>
						<div class="mb-3">
							<textarea id="supervisor_comment_${day}" name="content" class="form-control" placeholder="کامنت خود را وارد کنید" rows="4" required dir="rtl"></textarea>
						</div>

						<div class="form-check mb-2">
							<input class="form-check-input" type="checkbox" id="supervisor_hide_user_checkbox_${day}">
							<label class="form-check-label">
								Hide for User
							</label>
						</div>
					</div>
				</div>
			`;
		}

		reportHtml += `
			</div>
			<button id="submitReportBtn_${day}" class="submit_comment_btn btn btn-primary d-flex mb-3 justify-content-center align-items-center position-relative" type="submit" onclick="handleReportSubmit(${day})">
				<span id="submit-report-spinner_${day}" class="spinner-border spinner-border-sm d-none me-1" role="status"></span>
				<span>Submit Report</span>
				<div id="submit-report-check_${day}" class="bg-primary d-none" desabled>
					✅
				</div>
			</button>
			
			<br/>
		`;

		$reportsContainer.append(reportHtml);
	}
}

async function handleReportSubmit(day) {

	disable_btns(day)

	const data = {
		userName: ActiveUser,
		is_manager_submitted: is_manager_commenter,
		day: day
	};

	if (is_manager_commenter) {
		data.manager_comment = $(`#manager_comment_${day}`).val();
		data.manager_comment_hide_for_user = $(`#manager_hide_user_checkbox_${day}`).prop('checked');
		data.manager_comment_hide_for_supervisor = $(`#hide_supervisor_checkbox_${day}`).prop('checked');
	} else {
		data.supervisor_comment = $(`#supervisor_comment_${day}`).val();
		data.supervisor_comment_hide_for_user = $(`#supervisor_hide_user_checkbox_${day}`).prop('checked');
	}

	const url = `/hours/api/daily_report_management/${ACTIVE_YEAR}/${ACTIVE_MONTH}`;

	await postRequest(url, data)
	enable_btns(day)
}

function disable_btns(day) {
	$('.submit_comment_btn').prop('disabled', true);

	$(`#submit-report-spinner_${day}`).removeClass('d-none');
}

function enable_btns(day) {
	$('.submit_comment_btn').prop('disabled', false);
	$(`#submit-report-spinner_${day}`).addClass('d-none');
	$(`#submit-report-check_${day}`).removeClass('d-none').fadeIn(500, function () {
		// After fade in, fade out afttn_${daer a delay
		setTimeout(() => {
			$(`#submit-report-check_${day}`).fadeOut(500, function () {
				$(this).addClass('d-none').css('display', '');
			});
		}, 1000); // Delay before fading out
	});
}


function load_user_reports(userName, reports) {
	// Update the report title
	$('#reportTitle').text(`${userName}'s Reports`);

	reports.forEach(r => {
		let day = r.day
		if (r.content !== null && r.content.trim() !== "") {
			$(`#report_${day}`).removeClass("missed-report")
			$(`#report_${day}`).addClass("submitted-report")
			$(`#report_content_${day}`).val(r.content);
		}

		if (is_manager_commenter) {
			$(`#manager_comment_${day}`).text(r.manager_comment);
			$(`#supervisor_comment_${day}`).val(r.supervisor_comment);
			$(`#manager_hide_user_checkbox_${day}`).prop('checked', r.manager_comment_hide_for_user);
			$(`#hide_supervisor_checkbox_${day}`).prop('checked', r.manager_comment_hide_for_supervisor);
			$(`#supervisor_hide_user_checkbox_${day}`).prop('checked', r.supervisor_comment_hide_for_user);
		}
		else {
			if (!r.manager_comment_hide_for_supervisor) {
				$(`#manager_comment_${day}`).val(r.manager_comment);
			}
			$(`#supervisor_comment_${day}`).text(r.supervisor_comment);
			$(`#supervisor_hide_user_checkbox_${day}`).prop('checked', r.supervisor_comment_hide_for_user);
		}
	});
}

async function export_reports() {
	const exportUrl = `/hours/api/export_daily_report_management/${ACTIVE_YEAR}/${ACTIVE_MONTH}`;
	let response = await postRequest(exportUrl, {}, "Exporting Reports")
	console.log(response);
}

$("document").ready(async function () {
	fillYears("#year");
	initialize_date_dropdowns();
	get_active_day_report();
	initialize_reporting_limit();

	$("#year, #month").change(async function () {
		ACTIVE_YEAR = $("#year").val()
		ACTIVE_MONTH = $("#month").val()
		get_active_day_report();
	});

	$("#day").change(async function () {
		ACTIVE_DAY = $("#day").val();
		get_active_day_report();
	});

	$('input[name="btnradio"]').change(async function () {
		var selectedRadioId = $('input[name="btnradio"]:checked').attr('valueNumber');
		await saveReportingLimitModeDBT(parseInt(selectedRadioId))
	});

	$('#exportReportBtn').on("click", async function () {
		await export_reports()
	});
});		
