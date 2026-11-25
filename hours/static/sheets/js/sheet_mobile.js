"use strict";
// Phone/touch helpers shared by the jspreadsheet pages (hours, verify, supreme verify).
// Load after jspreadsheet.min.js and before the page's own script.
window.SheetMobile = (function () {

    // Below Bootstrap's lg breakpoint the page sidebar stacks above the grid.
    function isNarrow() {
        return window.matchMedia('(max-width: 991.98px)').matches;
    }

    // jspreadsheet tableHeight. On phones, fit the scroll box to the screen so the header and the
    // horizontal scroll stay reachable, instead of a tall box nested in the page scroll.
    function tableHeight(desktopHeight) {
        return isNarrow() ? Math.max(360, window.innerHeight - 90) + "px" : desktopHeight;
    }

    // Touch editing for an editable grid (pass the #spreadsheet element; the table is read from
    // window.spreadTable at event time, so this survives the grid being rebuilt). Idempotent.
    function enableTouchEditing(sheetEl) {
        // Keep the editor open when the grid scrolls. With tableOverflow, jexcel closes the editor on
        // *any* scroll of its scroll box. That includes the scroll the browser itself does to bring
        // a just-focused input into view, or to make room for a phone's keyboard, so a tapped cell
        // could open and close at once. The close only matters for floating editors
        // (dropdown/calendar); this sheet's editors live inside the cell and scroll with it.
        // Scroll events don't bubble, but this capture listener on an ancestor runs before jexcel's
        // own listener on .jexcel_content and stops the event from reaching it.
        if (!sheetEl.dataset.keepEditorOnScroll) {
            sheetEl.dataset.keepEditorOnScroll = '1';
            sheetEl.addEventListener('scroll', function (e) {
                const t = window.spreadTable;
                if (t && t.edition && e.target === t.content) e.stopPropagation();
            }, true);
        }

        // Touch editing: jexcel only opens a cell after a motionless 500ms long-press, which nobody
        // discovers on a phone. Here a single tap on an editable cell opens its editor (a tap that
        // turns into a scroll doesn't). It is opened inside touchend (a user gesture), so iOS/Android
        // actually show the keyboard. jexcel's own touch listeners are on document, so these
        // grid-level ones run before them. Mouse behaviour (click selects) is unchanged.
        if (!sheetEl.dataset.touchEditFix) {
            sheetEl.dataset.touchEditFix = '1';
            let tapCell = null, tapMoved = false;
            sheetEl.addEventListener('touchstart', function (e) {
                tapCell = e.target.closest('tbody td[data-x]');
                tapMoved = false;
            }, { capture: true, passive: true });
            sheetEl.addEventListener('touchmove', function () { tapMoved = true; }, { capture: true, passive: true });
            sheetEl.addEventListener('touchend', function (e) {
                const t = window.spreadTable;
                const td = e.target.closest('tbody td[data-x]');
                if (!t || !td || tapMoved || td !== tapCell) return;
                if (t.edition) {
                    if (t.edition[0] === td) return;                  // tap inside the open editor
                    // jexcel ignores taps while a cell is being edited: commit it and move on.
                    e.preventDefault();
                    t.closeEditor(t.edition[0], true);
                }
                e.preventDefault();  // no synthetic mouse events: they would re-select and steal focus
                t.updateSelectionFromCoords(td.dataset.x, td.dataset.y);
                if (td.classList.contains('readonly')) return;
                t.openEditor(td, false);
                const ed = td.querySelector('input, textarea');
                if (ed) ed.focus();
            });
        }

        // Touch drag-to-fill: jexcel only drives the fill corner (.jexcel_corner, enlarged for touch
        // in the CSS) with the mouse; its touch handler ignores it. This replays the mouse flow:
        // press the corner -> updateCopySelection() under the finger -> copyData() on release.
        // If a cell is being edited, its value is committed first, so "type a value, drag the
        // handle down" works. The grid auto-scrolls while the finger is near its edges.
        if (!sheetEl.dataset.touchFillFix) {
            sheetEl.dataset.touchFillFix = '1';
            let filling = false, lastTouch = null, scrollRaf = null;

            const cellAt = (x, y) => {
                const el = document.elementFromPoint(x, y);
                return el ? el.closest('#spreadsheet tbody td[data-x]') : null;
            };
            const extendTo = (x, y) => {
                const td = cellAt(x, y);
                if (td) window.spreadTable.updateCopySelection(td.dataset.x, td.dataset.y);
            };
            const autoScroll = () => {
                scrollRaf = null;
                const t = window.spreadTable;
                if (!filling || !lastTouch || !t) return;
                const box = t.content.getBoundingClientRect(), EDGE = 40, STEP = 12;
                let dx = 0, dy = 0;
                if (lastTouch.clientY > box.bottom - EDGE) dy = STEP;
                else if (lastTouch.clientY < box.top + EDGE) dy = -STEP;
                if (lastTouch.clientX > box.right - EDGE) dx = STEP;
                else if (lastTouch.clientX < box.left + EDGE) dx = -STEP;
                if (dx || dy) {
                    t.content.scrollTop += dy;
                    t.content.scrollLeft += dx;
                    extendTo(lastTouch.clientX, lastTouch.clientY);
                }
                scrollRaf = requestAnimationFrame(autoScroll);
            };
            const stopFill = () => {
                filling = false;
                lastTouch = null;
                if (scrollRaf) cancelAnimationFrame(scrollRaf);
                scrollRaf = null;
            };

            sheetEl.addEventListener('touchstart', function (e) {
                const t = window.spreadTable;
                if (!t || !e.target.classList.contains('jexcel_corner') || e.touches.length !== 1) return;
                e.preventDefault();       // the finger drives the fill, not page scroll
                e.stopPropagation();      // keep jexcel's document handler from resetting the selection
                if (t.edition) t.closeEditor(t.edition[0], true);
                if (!t.selectedContainer) return;
                filling = true;
                lastTouch = e.touches[0];
                scrollRaf = requestAnimationFrame(autoScroll);
            }, { capture: true, passive: false });

            sheetEl.addEventListener('touchmove', function (e) {
                if (!filling) return;
                e.preventDefault();
                lastTouch = e.touches[0];
                extendTo(lastTouch.clientX, lastTouch.clientY);
            }, { capture: true, passive: false });

            const endFill = function (e) {
                if (!filling) return;
                const t = window.spreadTable;
                e.preventDefault();
                stopFill();
                if (e.type === 'touchend' && t.selection && t.selection.length > 0)
                    t.copyData(t.selection[0], t.selection[t.selection.length - 1]);
                t.removeCopySelection();
            };
            sheetEl.addEventListener('touchend', endFill, { capture: true, passive: false });
            sheetEl.addEventListener('touchcancel', endFill, { capture: true, passive: false });
        }
    }

    // Full-screen "focus" mode for the sheet. `host` becomes a fixed full-screen layer (see
    // sheet_mobile.css): its .sheet-focus-bar child stays on top, its .sheet-focus-body child
    // (holding the grid) fills the rest, and every other child is hidden. The page can't scroll,
    // so the grid is the only scroll area. It pushes a history entry so the phone's Back
    // button/gesture closes it instead of leaving the page; Esc closes it too.
    let focusHost = null, focusButton = null;

    function isFocused() {
        return !!focusHost && focusHost.classList.contains('sheet-focus');
    }

    function applyFocus(on) {
        if (!focusHost || isFocused() === on) return;
        focusHost.classList.toggle('sheet-focus', on);
        document.body.classList.toggle('sheet-focus-open', on);
        if (focusButton) {
            focusButton.setAttribute('aria-pressed', String(on));
            const icon = focusButton.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-expand', !on);
                icon.classList.toggle('fa-compress', on);
            }
            const label = focusButton.querySelector('span');
            if (label) label.textContent = on ? 'Exit' : 'Full screen';
        }
        const t = window.spreadTable;
        if (t && t.updateCornerPosition) requestAnimationFrame(() => t.updateCornerPosition());
    }

    // Leave focus mode from code (e.g. when the grid is cleared), keeping history consistent.
    function exitFocus() {
        if (!isFocused()) return;
        if (history.state && history.state.sheetFocus) history.back();   // popstate closes it
        else applyFocus(false);
    }

    function initFocusMode(host, button) {
        focusHost = host;
        focusButton = button;
        host.classList.add('sheet-focus-host');
        button.addEventListener('click', function () {
            if (isFocused()) {
                exitFocus();
            } else {
                history.pushState({ sheetFocus: true }, "");
                applyFocus(true);
            }
        });
        window.addEventListener('popstate', function () {
            applyFocus(!!(history.state && history.state.sheetFocus));
        });
        document.addEventListener('keydown', function (e) {
            const t = window.spreadTable;
            if (e.key === 'Escape' && !(t && t.edition) && isFocused()) exitFocus();
        });
        // A reload restores the pushed entry; start un-focused and drop it.
        if (history.state && history.state.sheetFocus) history.replaceState(null, "");
    }

    return { isNarrow, tableHeight, enableTouchEditing, initFocusMode, exitFocus, isFocused };
})();
