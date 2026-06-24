"use strict";
// CONSTANTS************************************************
const today = new JDate();
const currentYear = today.getFullYear();
const currentMonth = today.getMonth();
const VERIFY_HOURS_MODE = window.VERIFY_HOURS_MODE || "manager";
let approvalPayload = { sections: { currentQueue: [], other: [], unsubmitted: [], approved: [] }, labels: {} };
let selectedUserId = null;
let selectedRole = null;
let selectedDetail = null;

const AutoHourCol = 3;
const RestCol = 4;
const RemoteCol = 5;
const TotalCol = 6;
// ********************************************************

function fillYears(year) {
	for (let i = window.START_YEAR; i <= year; i++) {
		$("#year").append($("<option>").text(i));
	}
}

let isLoadingVerificationData = false;
let latestLoadRequestId = 0;

function getApiPath(extraQuery = "") {
	const year = $("#year").val();
	const month = $("#month").val();
	const params = new URLSearchParams(extraQuery.startsWith("?") ? extraQuery.slice(1) : extraQuery);
	params.set("mode", VERIFY_HOURS_MODE);
	return `verify_hours/${year}/${month}?${params.toString()}`;
}

function flattenSections() {
	const sections = approvalPayload.sections || {};
	return [
		...(sections.currentQueue || []),
		...(sections.other || []),
		...(sections.unsubmitted || []),
		...(sections.approved || []),
	];
}

async function loadData() {
	if (isLoadingVerificationData) return;

	isLoadingVerificationData = true;
	const requestId = ++latestLoadRequestId;

	try {
		await GlobalLoader.wrap(async () => {
			const response = await apiService.get(
				getApiPath(),
				{},
				{},
				"Fetching Verification Data"
			);

			if (!response.ok) return;
			if (requestId !== latestLoadRequestId) return;

			approvalPayload = response.data || { sections: { currentQueue: [], other: [], unsubmitted: [], approved: [] }, labels: {} };
			updateSectionLabels();
			updateStaffGroupDropdown();
			renderUserLists();

			clearSelectedUser();
		}, "Loading verification data...");
	} catch (error) {
		console.error("Error loading verification data:", error);
	} finally {
		isLoadingVerificationData = false;
	}
}

function updateSectionLabels() {
	const labels = approvalPayload.labels || {};
	$("#current-queue-title").text(labels.currentQueue || "Needs your approval");
	$("#other-title").text(labels.other || "Other / not ready");
	$("#unsubmitted-title").text(labels.unsubmitted || "Unsubmitted");
	$("#approved-title").text(labels.approved || "Approved by you");
}

function clearSelectedUser() {
	if (typeof window.spreadTable === "object" && window.spreadTable) {
		window.spreadTable.destroy();
		window.spreadTable = null;
	}
	$("#spreadsheet").empty();
	$("#no-user-selected").show();
	$("#selected-user-name").text("Select a person");
	$("#selected-user-status").empty();
	$("#comments-card").addClass("d-none");
	$("#verify-btn").prop("disabled", true).text("Verify");
	$("#reject-btn").prop("disabled", true).text("Reject");
	$(".list-group-item").removeClass("active");
	selectedUserId = null;
	selectedRole = null;
	selectedDetail = null;
}

function updateStaffGroupDropdown() {
	const users = flattenSections();
	const groups = new Set(users.map(u => u.staffGroup).filter(g => g !== undefined && g !== null));
	const currentSelection = $("#staff_group").val() || "all";

	const $dropdown = $("#staff_group");
	$dropdown.empty();
	$dropdown.append(`<option value="all">All</option>`);

	[...groups].sort((a, b) => a - b).forEach(group => {
		$dropdown.append($("<option>").val(group).text(group));
	});

	const selectionExists = [...groups].some(g => String(g) === String(currentSelection));
	if (selectionExists || currentSelection === "all") {
		$dropdown.val(currentSelection);
	} else {
		$dropdown.val("all");
	}
}

function hhmm2minutes(str) {
	if (typeof str !== 'string' || !str.includes(":")) return 0;
	const [h, m] = str.split(":");
	return Number(h) * 60 + Number(m);
}

function minutes2hhmm(mins) {
	if (!mins || mins < 0) mins = 0;
	const h = Math.floor(mins / 60);
	const m = mins % 60;
	return `${h < 10 ? '0' : ''}${h}:${m < 10 ? '0' : ''}${m}`;
}

function calculateRowTotalMinutes(row) {
	const auto = hhmm2minutes(row["Auto Hours"] || "00:00");
	const rest = hhmm2minutes(row["Rest"] || "00:00");
	const remote = hhmm2minutes(row["Remote"] || "00:00");
	let totalM = auto + remote - rest;
	if (totalM < 0) totalM = 0;
	return totalM;
}

function recalculateTableTotals(tableData, updateSpreadsheet = true) {
	if (!Array.isArray(tableData)) return { totalTime: 0, autoTime: 0, workedDaysCount: 0 };

	let totalTime = 0;
	let autoTime = 0;
	let workedDaysCount = 0;

	tableData.forEach((row, rowIndex) => {
		const totalM = calculateRowTotalMinutes(row);
		const newTotalStr = minutes2hhmm(totalM);

		row["Total"] = newTotalStr;
		totalTime += totalM;
		autoTime += hhmm2minutes(row["Auto Hours"] || "00:00");
		if (totalM) workedDaysCount += 1;

		if (updateSpreadsheet && window.spreadTable) {
			const currentTotal = window.spreadTable.getValueFromCoords(TotalCol, rowIndex);
			if (currentTotal !== newTotalStr) {
				window.spreadTable.setValueFromCoords(TotalCol, rowIndex, newTotalStr, true);
			}

			const cellElement = window.spreadTable.getCell("G" + (rowIndex + 1));
			if (cellElement) {
				cellElement.textContent = newTotalStr;
			}
		}
	});

	return { totalTime, autoTime, workedDaysCount };
}

function getTableProjects(tableData) {
	if (!tableData || tableData.length === 0) return [];
	const allHeaders = new Set(Object.keys(tableData[0]));
	const defaultHeaders = new Set([
		'Day',
		'WeekDay',
		'Attendance',
		'Auto Hours',
		'Rest',
		'Remote',
		'Total',
		'Hours',
		'Description',
		'Note Hours',
	]);
	const tableProjects = new Set([...allHeaders].filter(x => !defaultHeaders.has(x)));
	return [...tableProjects];
}

function constructTable(data) {
	data = Array.isArray(data) ? data : [];
	const columns = [
		{ type: 'text', title: 'Day', width: 50, readOnly: true },
		{ type: 'text', title: 'WeekDay', width: 80, readOnly: true },
		{ type: 'text', title: 'Attendance', width: 100, readOnly: true },
		{ type: 'numeric', title: 'Auto Hours', mask: 'hh:mm', width: 120, readOnly: true },
		{ type: 'numeric', title: 'Rest', mask: 'hh:mm', width: 120, readOnly: true },
		{ type: 'numeric', title: 'Remote', mask: 'hh:mm', width: 120, readOnly: true },
		{ type: 'numeric', title: 'Total', mask: 'hh:mm', width: 120, readOnly: true },
		{ type: 'textarea', title: 'Note Hours', width: 180, readOnly: true },
		{ type: 'textarea', title: 'Description', width: 200, readOnly: true },
	];

	if (data[0] && data[0]["Hours"] !== undefined) {
		columns.push({ type: 'numeric', title: 'Hours', mask: 'hh:mm', width: 120, readOnly: true });
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
		tableWidth: "100%",
		updateTable: function (el, cell, x, y, source, value, id) {
			if (value == "Fri") cell.style.color = 'red';
		}
	});
	window.spreadTable.hideIndex();

	recalculateTableTotals(orderedData);

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

function getRoleLabel(role) {
	if (role === "manager_level_1") return "Manager level 1";
	if (role === "manager_level_2") return "Manager level 2";
	if (role === "supreme") return "Supreme approval";
	return "";
}

function getStatusIcons(user) {
	let statusIcons = '';
	if (user.isSubmitted) statusIcons += ' <span title="Submitted">☑️</span>';
	if (user.managerLevel1Verified) statusIcons += ' <span title="Manager level 1 approved">✅ M1</span>';
	if (user.managerLevel2Verified) statusIcons += ' <span title="Manager level 2 approved">✅ M2</span>';
	if (user.supremeVerified) statusIcons += ' <span title="Supreme approval">👑</span>';
	if (user.isFullyApproved) statusIcons += ' <span title="Fully approved">🏁</span>';
	return statusIcons;
}

function renderSelectedStatus(user) {
	const submitted = user.isSubmitted ? "✅ Submitted" : "⏳ Not submitted";
	const m1 = user.managerLevel1Verified ? "✅ Manager level 1 approval" : "⏳ Manager level 1 approval";
	const m2 = user.managerLevel2Verified ? "✅ Manager level 2 approval" : "⏳ Manager level 2 approval";
	const supreme = user.supremeVerified ? "👑 Supreme approval" : "⏳ Supreme approval";
	let warning = user.isWarning ? `<span class="text-warning">⚠️ Device hours and total hours differ</span>` : "";
	let rejected = user.rejectionReason ? `<span class="text-danger">Rejected: ${user.rejectionReason}</span>` : "";
	$("#selected-user-status").html(`${submitted} <span>${m1}</span> <span>${m2}</span> <span>${supreme}</span> ${warning} ${rejected}`);
}

function resolveActions(detail) {
	const p = detail.permissions || {};
	const candidates = [];
	if (selectedRole === "manager_level_1") {
		candidates.push([p.canVerifyManagerLevel1, "verify_manager_level_1", "Verify as manager level 1"]);
		candidates.push([p.canRejectManagerLevel1, "reject_manager_level_1", "Reject as manager level 1"]);
	} else if (selectedRole === "manager_level_2") {
		candidates.push([p.canVerifyManagerLevel2, "verify_manager_level_2", "Verify as manager level 2"]);
		candidates.push([p.canRejectManagerLevel2, "reject_manager_level_2", "Reject as manager level 2"]);
	} else if (selectedRole === "supreme") {
		candidates.push([p.canVerifySupreme, "verify_supreme", "Supreme approval"]);
		candidates.push([p.canRejectSupreme, "reject_supreme", "Supreme reject"]);
	} else {
		candidates.push([p.canVerifyManagerLevel1, "verify_manager_level_1", "Verify as manager level 1"]);
		candidates.push([p.canVerifyManagerLevel2, "verify_manager_level_2", "Verify as manager level 2"]);
		candidates.push([p.canVerifySupreme, "verify_supreme", "Supreme approval"]);
		candidates.push([p.canRejectManagerLevel1, "reject_manager_level_1", "Reject as manager level 1"]);
		candidates.push([p.canRejectManagerLevel2, "reject_manager_level_2", "Reject as manager level 2"]);
		candidates.push([p.canRejectSupreme, "reject_supreme", "Supreme reject"]);
	}

	const verify = candidates.find(([allowed, action]) => allowed && action.startsWith("verify"));
	const reject = candidates.find(([allowed, action]) => allowed && action.startsWith("reject"));
	return { verify, reject };
}

async function selectUser(userId, role) {
	selectedUserId = userId;
	selectedRole = role;

	$(".list-group-item").removeClass("active");
	$(`.user-item[data-id='${userId}'][data-role='${role}']`).addClass("active");

	try {
		await GlobalLoader.wrap(async () => {
			const response = await apiService.get(
				getApiPath(`?userId=${encodeURIComponent(userId)}&role=${encodeURIComponent(role || "")}`),
				{},
				{},
				"Fetching Sheet Data"
			);
			if (!response.ok) return;

			selectedDetail = response.data;
			$("#no-user-selected").hide();

			let warningIcon = selectedDetail.isWarning ? ' <span title="Total hours >= 1.1 * Auto hours">⚠️</span>' : '';
			$("#selected-user-name").html(`${selectedDetail.userName} <small class="text-muted">${getRoleLabel(role)}</small>${warningIcon}`);
			renderSelectedStatus(selectedDetail);

			const actions = resolveActions(selectedDetail);
			if (actions.verify) {
				$("#verify-btn").prop("disabled", false).data("action", actions.verify[1]).text(actions.verify[2]);
			} else {
				$("#verify-btn").prop("disabled", true).data("action", "").text("Verify");
			}

			if (actions.reject) {
				$("#reject-btn").prop("disabled", false).data("action", actions.reject[1]).text(actions.reject[2]);
			} else {
				$("#reject-btn").prop("disabled", true).data("action", "").text("Reject");
			}

			$("#comments-card").removeClass("d-none");
			$("#manager-level-1-comment")
				.val(selectedDetail.managerLevel1Comment || "")
				.prop("disabled", !(selectedDetail.permissions || {}).canEditManagerLevel1Comment);
			$("#manager-level-2-comment")
				.val(selectedDetail.managerLevel2Comment || "")
				.prop("disabled", !(selectedDetail.permissions || {}).canEditManagerLevel2Comment);

			constructTable(selectedDetail.sheetData);
		}, "Loading sheet...");
	} catch (error) {
		console.error("Error loading selected user:", error);
	}
}

function renderUserLists() {
	const selectedGroup = $("#staff_group").val();
	const sections = approvalPayload.sections || { currentQueue: [], other: [], unsubmitted: [], approved: [] };

	const filterUsers = users => {
		if (selectedGroup === "all") return users || [];
		return (users || []).filter(u => String(u.staffGroup) === String(selectedGroup));
	};

	const renderList = (users, containerId, countId) => {
		const filteredUsers = filterUsers(users);
		$(`#${countId}`).text(filteredUsers.length);
		const $container = $(`#${containerId}`);
		$container.empty();

		if (filteredUsers.length === 0) {
			$container.append(`<li class="list-group-item text-muted text-center">No records</li>`);
			return;
		}

		filteredUsers.sort((a, b) => a.userName.localeCompare(b.userName)).forEach(user => {
			const hoursInfo = `<small class="d-block">Auto: ${minutes2hhmm(user.autoHours || 0)} | Total: ${minutes2hhmm(user.totalHours || 0)}</small>`;
			const roleInfo = user.role ? `<small class="text-muted">${getRoleLabel(user.role)}</small>` : "";
			const rejectedInfo = user.rejectionReason ? `<small class="d-block text-danger">Rejected: ${user.rejectionReason}</small>` : "";
			const statusIcons = getStatusIcons(user);
			const warningClass = user.isWarning ? " list-group-item-warning" : "";
			const warningIcon = user.isWarning ? ' <span title="Total hours >= 1.1 * Auto hours">⚠️</span>' : '';

			const $item = $(`
                <li class="list-group-item list-group-item-action user-item${warningClass}" data-id="${user.userId}" data-role="${user.role}" style="cursor: pointer;">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="fw-bold">${user.userName}${warningIcon}</span>
                        <div>${statusIcons}</div>
                    </div>
                    <div class="d-flex justify-content-between">
                        ${hoursInfo}
                        ${roleInfo}
                    </div>
                    ${rejectedInfo}
                </li>
            `);

			$item.click(() => selectUser(user.userId, user.role));
			$container.append($item);
		});
	};

	renderList(sections.currentQueue, "current-queue-list", "current-queue-count");
	renderList(sections.other, "other-list", "other-count");
	renderList(sections.unsubmitted, "unsubmitted-list", "unsubmitted-count");
	renderList(sections.approved, "approved-list", "approved-count");

	if (selectedUserId && selectedRole) {
		$(`.user-item[data-id='${selectedUserId}'][data-role='${selectedRole}']`).addClass("active");
	}
}

let isUpdatingVerification = false;

function getCommentPayload() {
	const payload = {};
	if (!$("#manager-level-1-comment").prop("disabled")) {
		payload.managerLevel1Comment = $("#manager-level-1-comment").val();
	}
	if (!$("#manager-level-2-comment").prop("disabled")) {
		payload.managerLevel2Comment = $("#manager-level-2-comment").val();
	}
	return payload;
}

async function postSheetAction(action) {
	if (!selectedUserId || isUpdatingVerification || !action) return;

	let reason = "";
	if (action.startsWith("reject")) {
		reason = window.prompt("Enter rejection reason (optional):", "") || "";
	}

	isUpdatingVerification = true;
	const userIdBeforeRefresh = selectedUserId;
	const roleBeforeRefresh = selectedRole;

	try {
		await GlobalLoader.wrap(async () => {
			const response = await apiService.post(getApiPath(), {
				userId: selectedUserId,
				action: action,
				reason: reason,
				...getCommentPayload(),
			}, {}, "Updating Verification Status");

			if (!response.ok) return;

			jSuites.notification({
				name: "Success",
				title: "Status updated",
				message: "The action was completed successfully.",
				timeout: 3000,
			});

			await loadData();

			const stillVisible = flattenSections().some(user =>
				String(user.userId) === String(userIdBeforeRefresh) && user.role === roleBeforeRefresh
			);
			if (stillVisible) {
				await selectUser(userIdBeforeRefresh, roleBeforeRefresh);
			}
		}, "Updating verification status...");
	} catch (error) {
		console.error("Error setting verification status:", error);
	} finally {
		isUpdatingVerification = false;
	}
}

async function saveComments() {
	if (!selectedUserId || isUpdatingVerification) return;
	isUpdatingVerification = true;

	try {
		await GlobalLoader.wrap(async () => {
			const response = await apiService.post(getApiPath(), {
				userId: selectedUserId,
				action: "save_comments",
				...getCommentPayload(),
			}, {}, "Saving Comments");

			if (!response.ok) return;
			jSuites.notification({
				name: "Success",
				title: "Comments saved",
				message: "Comments were saved.",
				timeout: 3000,
			});
		}, "Saving comments...");
	} catch (error) {
		console.error("Error saving comments:", error);
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

	$("#staff_group").on("change", function () {
		renderUserLists();
		clearSelectedUser();
	});

	$("#verify-btn").click(() => postSheetAction($("#verify-btn").data("action")));
	$("#reject-btn").click(() => postSheetAction($("#reject-btn").data("action")));
	$("#save-comments-btn").click(saveComments);
});
