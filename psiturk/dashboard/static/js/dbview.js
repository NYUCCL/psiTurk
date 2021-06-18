// Defines a database view for manipulating HITs and Workers
var DEFAULT_SORT = {
    'last': undefined,
    'forwards': true
}

/**
 * View for a database.
 */
export class DatabaseView {

    // Injects a database view into the parent element
    constructor(domelements, callbacks, name="", filter=undefined) {
        this.DOM$ = {
            ...domelements,
            root: $('<div id="dbContainer_' + this.name + '" class="db-container"></div>'),
            tableView: $('<div id="tableView_"' + this.name +' class="db-tableView no-scrollbar"></div>'),
            table: $('<table id="table_' + this.name + '" class="db-table"><thead class="db-thead"></thead><tbody class="db-tbody"></tbody></table>')
        };
        this.callbacks = callbacks; 
        this.name = name;
        this.filter = filter;

        // Index of the selected row
        this.selectedRowIndex = undefined;

        // Build elements
        this.DOM$.display.append(
            this.DOM$.root.append(
                this.DOM$.tableView.append(
                    this.DOM$.table)));

        // Begin the database invisibly (before data loads)
        this.visible = false;
        this.DOM$.root.hide();

        // Initialize data
        this.updateData([], [], false);
    }

    // Hides the database and shows a "loading" icon
    clearData() {
        this.DOM$.root.fadeOut();
        this.visible = false;
    }

    // Updates the data, builds headers does not re-render unless specified
    async updateData(newData, fields, rerender=true, resetFilter=false) {
        this.data = newData;
        this.fields = fields;
        this.sort = DEFAULT_SORT;

        // Reset headers of columns
        let tHead$ = this.DOM$.table.find('thead');
        tHead$.empty();
        let headerTr$ = $('<tr><th>#</th></tr>');
        for (const [key, value] of Object.entries(fields)) {
            let th$ = $('<th/>');
            for (const [property, cssValue] of Object.entries(value['style'])) {
                th$.css(property, cssValue);
            }
            let sortLink$ = $('<a>' + value['title'] + '</a>')
            sortLink$.on('click', () => { 
                this.sortByColumn(key); 
            });
            headerTr$.append(th$.append(sortLink$));
        }
        tHead$.append(headerTr$);

        if (rerender) {
            // If filters exist, reset them
            if (this.filter && resetFilter) {
                this.filter.reset();
            }
            await this.renderTable();
        }

        return Promise.resolve();
    }

    // Re-renders the table based on the order, discriminator tells whether to
    // render the current row.
    async renderTable() {
        // Maintain previously selected row
        let selectedRow = this.DOM$.table.find('tr.selected');
        if (selectedRow) {
            selectedRow = selectedRow.attr('id');
        }

        let tBody$ = this.DOM$.table.find('tbody');
        tBody$.empty();

        // Insert the actual data into the body
        let totalRows = 0;
        for (let i = 0; i < this.data.length; i++) {
            if (this.filter && !this.filter.passes(this.data[i])) { continue; }
            let row$ = $('<tr><td>' + (i+1) + '</td></tr>');
            row$.attr('id', 'row_' + this.name + '_' + i);
            for (const [key, value] of Object.entries(this.fields)) {
                let cellValue = this.data[i][key];
                if (!cellValue) {
                    if (value['type'] == "num")
                        cellValue = 0;
                    else
                        cellValue = "";
                }
                // Custom bool rendering
                if (value['type'] == 'bool' && cellValue) {
                    cellValue = "<img src='" + BLUE_RIBBON_PATH + "' class='db-boolimg'>"
                }
                let data$ = $('<td/>').html(cellValue);
                data$.css('overflow-x', 'auto');
                for (const [property, cssValue] of Object.entries(value['style'])) {
                    data$.css(property, cssValue);
                }
                row$.append(data$);
            }
            let currentRow = totalRows;
            row$.on("click", (event) => {
                let index = /_([0-9]*)$/g.exec(event.currentTarget.id);
                let selected = parseInt(index[1]);
                this.callbacks['onSelect'](this.data[selected]);
                this.selectedRowIndex = currentRow;
                $(event.currentTarget).addClass('selected').siblings().removeClass('selected');
            })
            tBody$.append(row$);
            totalRows++;
        }

        if (selectedRow) { $('#' + selectedRow).click(); } 

        // If wasn't visible before, now make visible
        if (!this.visible) {
            this.visible = true;
            this.DOM$.root.fadeIn();
        }

        // Call the onFilter handler
        if (this.filter) {
            this.filter.updateFilterCounts(totalRows);
        }
    }

    // Selects the previous row from the currently selected
    selectPreviousRow() {
        let rows = this.DOM$.table.find('tbody tr');
        if (rows.length > 0 && this.selectedRowIndex > 0) {
            this.selectedRowIndex--;
            console.log(this.selectedRowIndex, this.totalRows, rows);
            $(rows[this.selectedRowIndex]).click();
        }
    }

    // Seletcs the next row from the currently selected
    selectNextRow() {
        let rows = this.DOM$.table.find('tbody tr');
        if (rows.length > 0 && this.selectedRowIndex < rows.length - 1) {
            this.selectedRowIndex++;
            console.log(this.selectedRowIndex, this.totalRows, rows);
            $(rows[this.selectedRowIndex]).click();
        }
    }

    // Sorts the table based on the header clicked
    sortByColumn(colTitle) {
        var switching = true;
        let byColIndex = Object.keys(this.fields).indexOf(colTitle) + 1;
        // Determine switch direction (swap from last)
        // If the last sort was on this column, reverse the sort, otherwise just do forwards
        let switchDirection = this.sort['last'] == byColIndex ? !this.sort['forwards'] : true;
        while (switching) {
            switching = false;
            let rows = this.DOM$.table.find('tbody>tr');
            // Loop through all the rows
            let shouldSwitch = false;
            for (let i = 0; i < (rows.length - 1) && !(shouldSwitch); i++) {
                let first = $(rows[i]).find('td:eq(' + byColIndex + ')').html();
                let second = $(rows[i+1]).find('td:eq(' + byColIndex + ')').html();

                // Determine comparator from column type, default is string compare
                if (switchDirection) {
                    if (Object.entries(this.fields)[byColIndex][1]['type'] == 'date') {
                        shouldSwitch = new Date(first) < new Date(second);
                    } else if (Object.entries(this.fields)[byColIndex][1]['type'] == 'num') {
                        shouldSwitch = parseFloat(first) < parseFloat(second);
                    } else {
                        shouldSwitch = first.toLowerCase() < second.toLowerCase();
                    }
                } else {
                    if (Object.entries(this.fields)[byColIndex][1]['type'] == 'date') {
                        shouldSwitch = new Date(first) > new Date(second);
                    } else if (Object.entries(this.fields)[byColIndex][1]['type'] == 'num') {
                        shouldSwitch = parseFloat(first) > parseFloat(second);
                    } else {
                        shouldSwitch = first.toLowerCase() > second.toLowerCase();
                    }
                }

                // If should switch matches switch direction, then go
                if (shouldSwitch) {
                    rows[i].parentNode.insertBefore(rows[i+1], rows[i]);
                    switching = true;
                }
            }
        }
        this.sort['last'] = byColIndex;
        this.sort['forwards'] = switchDirection;
    }
}