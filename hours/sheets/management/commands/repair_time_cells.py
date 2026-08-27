from django.core.management.base import BaseCommand, CommandError

from sheets.models import Sheet, TIME_INPUT_COLUMNS, coerce_time_cell


class Command(BaseCommand):
	help = (
		"Repair duration cells that are not canonical hh:mm.\n\n"
		"Cells whose intent is unambiguous (blank, the legacy JSON int 0, \"8\", or a "
		"decimal like \"0.5\" meaning half an hour) are rewritten in place; anything "
		"else is reported and skipped unless --set gives it an explicit value.\n\n"
		"Touched sheets are re-normalized so every row Total and the sheet total/mean "
		"are recomputed. This deliberately bypasses the submitted lock -- only the API "
		"enforces that, and a submitted sheet with a corrupt cell cannot be fixed by "
		"its owner through the UI."
	)

	def add_arguments(self, parser):
		parser.add_argument(
			"--dry-run", action="store_true",
			help="Report what would change without writing anything.",
		)
		parser.add_argument(
			"--sheet", type=int, action="append", dest="sheets", default=[],
			help="Limit to this sheet id (repeatable).",
		)
		parser.add_argument(
			"--set", action="append", dest="overrides", default=[],
			metavar="SHEET:DAY:COLUMN=hh:mm",
			help="Explicit value for a cell that cannot be coerced (repeatable).",
		)
		parser.add_argument(
			"--zero-unfixable", action="store_true",
			help="Set any remaining uncoercible cell to 00:00.",
		)

	def parse_overrides(self, raw_list):
		"""'3362:5:Rest=00:30' -> {(3362, 5, 'Rest'): '00:30'}"""
		overrides = {}
		for raw in raw_list:
			if "=" not in raw:
				raise CommandError(f"--set needs SHEET:DAY:COLUMN=hh:mm, got {raw!r}")
			key, value = raw.split("=", 1)
			parts = key.split(":")
			if len(parts) != 3:
				raise CommandError(f"--set needs SHEET:DAY:COLUMN=hh:mm, got {raw!r}")
			sheet_id, day, column = parts
			canonical = coerce_time_cell(value)
			if canonical is None:
				raise CommandError(f"--set value {value!r} is not a valid time")
			try:
				overrides[(int(sheet_id), int(day), column)] = canonical
			except ValueError:
				raise CommandError(f"--set needs numeric SHEET and DAY, got {raw!r}")
		return overrides

	def handle(self, *args, **options):
		dry_run = options["dry_run"]
		overrides = self.parse_overrides(options["overrides"])
		zero_unfixable = options["zero_unfixable"]

		queryset = Sheet.objects.all().order_by("id")
		if options["sheets"]:
			queryset = queryset.filter(id__in=options["sheets"])

		changed_sheets = 0
		changed_cells = 0
		skipped = []

		for sheet in queryset:
			rows = sheet.data or []
			if not isinstance(rows, list):
				continue

			edits = []
			for row in rows:
				if not isinstance(row, dict):
					continue
				day = row.get("Day")
				for column in TIME_INPUT_COLUMNS:
					if column not in row:
						continue
					current = row[column]
					fixed = coerce_time_cell(current)
					if fixed is None:
						override = overrides.get((sheet.id, day, column))
						if override is not None:
							fixed = override
						elif zero_unfixable:
							fixed = "00:00"
						else:
							skipped.append((sheet.id, sheet.user_name, day, column, current))
							continue
					# An empty cell already reads as zero everywhere; rewriting it to
					# "00:00" changes no total and would bury the real repairs in noise.
					if current == "" and fixed == "00:00":
						continue
					if fixed != current:
						edits.append((row, day, column, current, fixed))

			if not edits:
				continue

			self.stdout.write(
				f"sheet {sheet.id} {sheet.user_name} {sheet.year}/{sheet.month}"
				f"{' [submitted]' if sheet.submitted else ''}"
			)
			for _row, day, column, current, fixed in edits:
				self.stdout.write(f"    day {day:>2} {column:<11} {current!r} -> {fixed!r}")

			old_total, old_mean = sheet.total, sheet.mean
			if dry_run:
				self.stdout.write(f"    total {old_total} mean {old_mean} (unchanged, dry run)")
			else:
				for row, _day, column, _current, fixed in edits:
					row[column] = fixed
				# normalize_sheet() recomputes every row Total, then save() re-runs
				# transform() and rewrites the sheet total/mean.
				sheet.normalize_sheet()
				sheet.refresh_from_db()
				self.stdout.write(
					f"    total {old_total} -> {sheet.total}, mean {old_mean} -> {sheet.mean}"
				)

			changed_sheets += 1
			changed_cells += len(edits)

		if skipped:
			self.stdout.write(self.style.WARNING(f"\n{len(skipped)} cell(s) could not be coerced:"))
			for sheet_id, user_name, day, column, current in skipped:
				self.stdout.write(
					self.style.WARNING(
						f"    sheet {sheet_id} {user_name} day {day} {column} = {current!r}"
					)
				)
			self.stdout.write(
				self.style.WARNING(
					"Pass --set SHEET:DAY:COLUMN=hh:mm for each, or --zero-unfixable."
				)
			)

		verb = "would change" if dry_run else "changed"
		self.stdout.write(
			self.style.SUCCESS(f"\n{verb} {changed_cells} cell(s) in {changed_sheets} sheet(s)")
		)
