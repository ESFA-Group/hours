"use strict";
//CONSTANTS************************************************
const today = new JDate();
const currentYear = today.getFullYear();
const currentMonth = today.getMonth();
// ********************************************************


function fillYears(year) {
	for (let i = window.START_YEAR; i <= year; i++) {
		$("#year").append($("<option>").text(i));
	}
}

$("document").ready(async function () {

	fillYears(currentYear);
	$("#month").val(currentMonth);
	$("#year").val(currentYear);


	$("#year, #month").change(function () {
	});

});