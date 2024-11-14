"use strict";
//CONSTANTS************************************************
const TODAY = new JDate();
TODAY._d.setHours(0, 0, 0, 0)


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

async function get_reports_by_users() {
	const url = `/hours/api/daily_report_management/${ACTIVE_YEAR}/${ACTIVE_MONTH}`;
	return await getRequest(url);
}

function updateTitle() {
	$("#reportTitle").text("Submit Report " + $("#month").val() + "/" + $("#day").val());
}

async function get_all_daily_reports() {

	let reports_by_users = await get_reports_by_users();
	
	const $userList = $('#userList');
	$.each(reports_by_users, function (userName, reports) {
		const listItem = $('<li></li>')
			.addClass('list-group-item user-item')
			.text(`${userName} (${reports.length} reports)`)
			.attr('data-user-id', userName); // Use userName or an ID from your data

		// Append the list item to the user list
		$userList.append(listItem);

		// Add a click event to each list item
		listItem.on('click', function () {
			console.log(`User ${userName} clicked`);
			load_user_reports(userName, reports);
		});
	});
	if (Object .keys(reports_by_users).length > 0) {
		let userName = Object.keys(reports_by_users)[0]
		let reports = Object.values(reports_by_users)[0]
		load_user_reports(userName, reports);
	}
}

function pre_load_user_reports() {
	const $reportsContainer = $('#reports_container');

	for (let day = TODAY.getDate(); day >= 1; day--) {
		const reportHtml = `
            <div class="report" id="report_${day}">
                <div class="card shadow mb-4">
                    <div class="card-body">
                        <h4 class="card-title fw-bold">Report #${day}</h4>
                        <div class="mb-3">
                            <p id="report_content_${day}" name="content" class="form-control" style="min-height: 120px;"></p>
                        </div>
                    </div>
                </div>

                <div class="card shadow mb-4">
                    <div class="card-body">
                        <h5 class="card-title fw-semibold">Vahid's Comment:</h5>
                        <p id="main_comment_${day}">No comment yet.</p>
                    </div>
                </div>

                <div class="card shadow mb-4">
                    <div class="card-body">
                        <h5 class="card-title fw-semibold">Koolaji's Comment:</h5>
                        <p id="sub_comment_${day}">No comment yet.</p>
                    </div>
                </div>

                <br/>
                <hr>
                <br/>
            </div>
        `;

		$reportsContainer.append(reportHtml);
	}
}

function load_user_reports(userName, reports) {
	// Update the report title
	$('#reportTitle').text(`${userName}'s Reports`);

	reports.forEach(r => {
		let day = r.day
		let html_report_content = $(`#report_content_${day}`)
		html_report_content.text(r.content);
	});

	// Clear existing report content
	$('#main_comment').text('');
	$('#sub_comment').text('');

	// Display the reports (example with the first two reports if available)
	if (reports.length > 0) {
		$('#main_comment').text(reports[0]?.content || 'No comment yet.');
	}
	if (reports.length > 1) {
		$('#sub_comment').text(reports[1]?.content || 'No comment yet.');
	}
}

$("document").ready(async function () {
	fillYears("#year");
	initialize_date_dropdowns();
	pre_load_user_reports();
	get_all_daily_reports();

	$("#year, #month").change(async function () {
		ACTIVE_YEAR = $("#year").val()
		ACTIVE_MONTH = $("#month").val()
		get_all_daily_reports();
	});

	$("#day").change(async function () {
		ACTIVE_DAY = $("#day").val();
		get_all_daily_reports();
	});

	$('#report_from').on('submit', async function (e) {
		e.preventDefault();

		$("#submit-report-spinner").removeClass('d-none');
		$("#submitReportBtn").prop('disabled', true)

		const content = $('#report_content').val();
		const url = `/hours/api/daily_report_user/${ACTIVE_YEAR}/${ACTIVE_MONTH}/${ACTIVE_DAY}`;

		let res = await postRequest(url, { content })

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
	});
});
