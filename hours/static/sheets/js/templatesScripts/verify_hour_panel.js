"use strict";
//CONSTANTS************************************************
const today = new JDate();
const currentYear = today.getFullYear();
const currentMonth = today.getMonth();
let allUsersData = [];
let selectedUserId = null;
// ********************************************************


function fillYears(year) {
	for (let i = window.START_YEAR; i <= year; i++) {
		$("#year").append($("<option>").text(i));
	}
}

let isLoadingVerificationData = false;
let latestLoadRequestId = 0;

async function loadData() {
	if (isLoadingVerificationData) {
		return;
	}

	isLoadingVerificationData = true;
	const requestId = ++latestLoadRequestId;

	const year = $("#year").val();
	const month = $("#month").val();
	const path = `verify_hours/${year}/${month}`;

	try {
		await GlobalLoader.wrap(async () => {
			const response = await apiService.get(
				path,
				{},
				{},
				"Fetching Verification Data"
			);

			if (!response.ok) return;

			/*
			  Safety check:
			  If a newer loadData request somehow started, ignore this older result.
			*/
			if (requestId !== latestLoadRequestId) {
				return;
			}

			allUsersData = response.data;

			updateStaffGroupDropdown();
			renderUserLists();

			if (typeof window.spreadTable === "object" && window.spreadTable) {
				window.spreadTable.destroy();
				window.spreadTable = null;
			}

			$("#spreadsheet").empty();
			$("#no-user-selected").show();
			$("#selected-user-name").text("Select a user");

			$("#verify-btn").prop("disabled", true).show();
			$("#unverify-btn").hide();
			$("#supreme-verify-btn").hide();
			$("#supreme-unverify-btn").hide();

			selectedUserId = null;
		}, "Loading verification data...");

	} catch (error) {
		console.error("Error loading verification data:", error);

	} finally {
		isLoadingVerificationData = false;
	}
}

function updateStaffGroupDropdown() {
	const groups = new Set(allUsersData.map(u => u.staffGroup).filter(g => g !== undefined && g !== null));
	const currentSelection = $("#staff_group").val() || "all";

	const $dropdown = $("#staff_group");
	$dropdown.empty();
	$dropdown.append(`<option value="all">All</option>`);

	[...groups].sort((a, b) => a - b).forEach(group => {
		$dropdown.append($("<option>").val(group).text(group));
	});

	// Restore selection if it still exists, otherwise default to "all"
	const selectionExists = [...groups].some(g => String(g) === String(currentSelection));
	if (selectionExists || currentSelection === "all") {
		$dropdown.val(currentSelection);
	} else {
		$dropdown.val("all");
	}
}

function hhmm2minutes(str) {
	if (typeof str !== 'string' || !str.includes(":"))
		return 0
	const [h, m] = str.split(":");
	return Number(h) * 60 + Number(m)
}

function getTableProjects(tableData) {
	if (!tableData || tableData.length === 0) return [];
	const allHeaders = new Set(Object.keys(tableData[0]));
	const defaultHeaders = new Set(['Day', 'WeekDay', 'Attendance', 'Auto Hours', 'Rest', 'Remote', 'Total', 'Hours', 'Description']);
	const tableProjects = new Set([...allHeaders].filter(x => !defaultHeaders.has(x)));
	return [...tableProjects]
}

function constructTable(data) {
	const columns = [
		{ type: 'text', title: 'Day', width: 50, readOnly: true },
		{ type: 'text', title: 'WeekDay', width: 80, readOnly: true },
		{ type: 'text', title: 'Attendance', width: 80, readOnly: true },
		{ type: 'numeric', title: 'Auto Hours', mask: 'hh:mm', width: 120, readOnly: true },
		{ type: 'numeric', title: 'Rest', mask: 'hh:mm', width: 120, readOnly: true },
		{ type: 'numeric', title: 'Remote', mask: 'hh:mm', width: 120, readOnly: true },
		{ type: 'numeric', title: 'Total', mask: 'hh:mm', width: 120, readOnly: true },
		{ type: 'text', title: 'Description', width: 200, readOnly: true },
	];

	if (data[0] && data[0]["Hours"] !== undefined) {
		columns.push(
			{ type: 'numeric', title: 'Hours', mask: 'hh:mm', width: 120, readOnly: true },
		)
	}

	const projects = getTableProjects(data);
	for (const prj of projects) {
		columns.push({
			type: 'numeric',
			title: prj,
			mask: '#,##0.00 %',
			width: 100,
			readOnly: true
		});
	}

	const orderedData = data.map(row => {
		const newRow = {};
		columns.forEach(col => {
			const title = col.title;
			newRow[title] = row[title] !== undefined ? row[title] : '';
		});
		return newRow;
	});

	if (typeof window.spreadTable === 'object' && window.spreadTable) {
		window.spreadTable.destroy();
	}

	$("#spreadsheet").empty();

	window.spreadTable = jspreadsheet(document.getElementById('spreadsheet'), {
		data: orderedData,
		columns: columns,
		allowInsertColumn: false,
		allowInsertRow: false,
		allowDeleteRow: false,
		allowRenameColumn: false,
		tableOverflow: true,
		tableHeight: "150vh",
		updateTable: function (el, cell, x, y, source, value, id) {
			if (value == "Fri") {
				cell.style.color = 'red';
			}
		}
	});
	window.spreadTable.hideIndex();

	// Check for holidays
	const year = $("#year").val();
	const month = $("#month").val();

	EsfaPersianHolidays.getHolidays(year, month).then(holidays => {
		window.spreadTable.rows.forEach(row => {
			const dayColumn = 1;
			const weekDayColumn = 2;
			let day = Number(row.cells[dayColumn].textContent);

			if (holidays.includes(day)) {
				row.cells[weekDayColumn].style.color = 'red';
			}
		});
	}).catch(err => {
		console.warn("Could not fetch holidays:", err);
	});
}

function selectUser(userId) {
	selectedUserId = userId;
	const userData = allUsersData.find(u => u.userId === userId);
	if (!userData) return;

	// Update active state in sidebar
	$(".list-group-item").removeClass("active");
	$(`.user-item[data-id='${userId}']`).addClass("active");

	// Update main area
	$("#no-user-selected").hide();

	let warningIcon = userData.isWarning ? ' <span title="Total hours >= 1.1 * Auto hours">⚠️</span>' : '';
	let verificationIcons = '';
	if (userData.isVerified) verificationIcons += ' ✅';
	if (userData.isSupremeVerified) verificationIcons += ' 👑';

	$("#selected-user-name").html(`${userData.userName} (#${userData.staffGroup || 'No Group'})${warningIcon}${verificationIcons}`);

	// Standard buttons
	if (userData.isVerified) {
		$("#verify-btn").hide();
		$("#unverify-btn").prop("disabled", false).show();
	} else {
		$("#unverify-btn").hide();
		$("#verify-btn").prop("disabled", false).show();
	}

	// Supreme buttons
	if (window.USER.is_SupremeHourVerifier) {
		if (userData.isSupremeVerified) {
			$("#supreme-verify-btn").hide();
			$("#supreme-unverify-btn").prop("disabled", false).show();
		} else {
			$("#supreme-unverify-btn").hide();
			$("#supreme-verify-btn").prop("disabled", false).show();
		}
	} else {
		$("#supreme-verify-btn").hide();
		$("#supreme-unverify-btn").hide();
	}

	constructTable(userData.sheetData);
}

function renderUserLists() {
	const selectedGroup = $("#staff_group").val();

	let filteredUsers = allUsersData;
	if (selectedGroup !== "all") {
		filteredUsers = allUsersData.filter(u => String(u.staffGroup) === String(selectedGroup));
	}

	const unverifiedUsers = filteredUsers.filter(u => !u.isVerified && !u.isSupremeVerified);
	const verifiedUsers = filteredUsers.filter(u => u.isVerified || u.isSupremeVerified);

	$("#unverified-count").text(unverifiedUsers.length);
	$("#verified-count").text(verifiedUsers.length);

	const renderList = (users, containerId) => {
		const $container = $(`#${containerId}`);
		$container.empty();

		if (users.length === 0) {
			$container.append(`<li class="list-group-item text-muted text-center">No users</li>`);
			return;
		}

		users.sort((a, b) => a.userName.localeCompare(b.userName)).forEach(user => {
			let bgClass = "";
			if (user.isWarning) {
				bgClass = "list-group-item-warning";
			}

			const minsToHm = (mins) => {
				const h = Math.floor(mins / 60);
				const m = mins % 60;
				return `${h}:${m < 10 ? '0' : ''}${m}`;
			};

			const hoursInfo = `<small class="d-block">Auto: ${minsToHm(user.autoHours)} | Total: ${minsToHm(user.totalHours)}</small>`;

			let statusIcons = '';
			if (user.isVerified) statusIcons += ' <span title="Verified">✅</span>';
			if (user.isSupremeVerified) statusIcons += ' <span title="Supreme Verified">👑</span>';
			if (user.isWarning) statusIcons += ' <span title="Total hours >= 1.1 * Auto hours">⚠️</span>';

			const $item = $(`
                <li class="list-group-item list-group-item-action user-item ${bgClass}" data-id="${user.userId}" style="cursor: pointer;">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="fw-bold">${user.userName}</span>
                        <div>${statusIcons}</div>
                    </div>
                    ${hoursInfo}
                </li>
            `);

			$item.click(() => selectUser(user.userId));
			$container.append($item);
		});
	};

	renderList(unverifiedUsers, "unverified-list");
	renderList(verifiedUsers, "verified-list");

	// Re-select user if they are still in the list
	if (selectedUserId) {
		$(`.user-item[data-id='${selectedUserId}']`).addClass("active");
	}
}

let isUpdatingVerification = false;

async function verifySheet(isVerified, verifyType = "standard") {
	if (!selectedUserId || isUpdatingVerification) return;

	isUpdatingVerification = true;

	const userIdBeforeRefresh = selectedUserId;
	const year = $("#year").val();
	const month = $("#month").val();
	const path = `verify_hours/${year}/${month}`;

	try {
		await GlobalLoader.wrap(async () => {
			const response = await apiService.post(path, {
				userId: selectedUserId,
				isVerified: isVerified,
				verifyType: verifyType
			}, {}, "Updating Verification Status");

			if (!response.ok) return;

			jSuites.notification({
				name: "Success",
				title: isVerified ? "Sheet Verified" : "Sheet Unverified",
				message: "Successfully updated status.",
				timeout: 3000,
			});

			await loadData();

			if (userIdBeforeRefresh) {
				selectUser(userIdBeforeRefresh);
			}
		}, "Updating verification status...");

	} catch (error) {
		console.error("Error setting verification status:", error);

	} finally {
		isUpdatingVerification = false;
	}
}


$("document").ready(async function () {

	fillYears(currentYear);
	$("#month").val(currentMonth);
	$("#year").val(currentYear);

	await loadData();

	$("#year, #month").on("change", async function () {
		await loadData();
	});

	$("#staff_group").on("change", async function () {
		await GlobalLoader.wrap(async () => {
			renderUserLists();

			if (typeof window.spreadTable === "object" && window.spreadTable) {
				window.spreadTable.destroy();
				window.spreadTable = null;
			}

			$("#spreadsheet").empty();
			$("#no-user-selected").show();
			$("#selected-user-name").text("Select a user");

			$("#verify-btn").prop("disabled", true).show();
			$("#unverify-btn").hide();
			$("#supreme-verify-btn").hide();
			$("#supreme-unverify-btn").hide();

			selectedUserId = null;
		}, "Updating staff group...");
	});

	$("#verify-btn").click(() => verifySheet(true, "standard"));
	$("#unverify-btn").click(() => verifySheet(false, "standard"));
	$("#supreme-verify-btn").click(() => verifySheet(true, "supreme"));
	$("#supreme-unverify-btn").click(() => verifySheet(false, "supreme"));

});