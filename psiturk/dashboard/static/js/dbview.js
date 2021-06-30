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
            table: $('<table id="table_' + this.name + '" class="db-table"></table>'),
            thead: $('<thead class="db-thead"></thead>'),
            tbody: $('<tbody class="db-tbody"></tbody>')
        };
        this.callbacks = callbacks; 
        this.name = name;
        this.trPrefix = 'row_' + this.name + '_';
        this.filter = filter;

        // Data of the currently selected row
        this.index = undefined;
        this.selectedRowData = undefined;
        this.selectedRowID = undefined;
        this.selectedRowIndex = undefined;

        // Build elements
        this.DOM$.display.append(
            this.DOM$.root.append(
                this.DOM$.tableView.append(
                    this.DOM$.table.append(
                        this.DOM$.thead).append(
                        this.DOM$.tbody))));

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

    // Downloads the data as a .CSV
    downloadData(fileName='table') {
        let csv = 'i,';

        // Get the CSV headers
        var rows = this.DOM$.table.find('tr');
        let headers = Object.keys(this.fields);
        for (let i = 0; i < headers.length; i++) {
            csv += headers[i] + ',';
        }
        csv = csv.slice(0, -1) + '\n';

        // Now fill in the rows of data
        for (let i = 1; i < rows.length; i++) {
            let childs = $(rows[i]).children('td');
            csv += childs[0].innerHTML + ',';
            for (let j = 1; j < childs.length; j++) {
                let val = childs[j].innerHTML;
                switch (Object.values(this.fields)[j-1].type) {
                    case 'bool':
                        val = val == '' ? 'false' : 'true';
                        break;
                    case 'string':
                    case 'date':
                        val = val.replace(',', '');
                    default:
                        break;
                }
                csv += val + ',';
            }
            csv = csv.slice(0, -1) + '\n';
        }
        csv.slice(0, -1);

        // Build a download link and click on it, then remove it
        var element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,'  + encodeURIComponent(csv));
        element.setAttribute('download', fileName + '.csv');
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }

    // Updates the data, builds headers does not re-render unless specified
    updateData(newData, fields, options={'rerender': true, 'resetFilter': false, 'maintainSelected': true, 'index': undefined, 'callback': undefined}) {
        this.data = newData;
        this.fields = fields;
        this.sort = DEFAULT_SORT;
        this.index = options['index'];

        // Reset headers of columns
        this.DOM$.thead.empty();
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
        this.DOM$.thead.append(headerTr$);

        if (options['rerender']) {
            // If filters exist, reset them
            if (this.filter && options['resetFilter']) {
                this.filter.reset();
            }
            this.renderTable(options['maintainSelected'], options['callback']);
        } else {
            options['callback'] && options['callback']();
        }
    }

    // Re-renders the table based on the order, discriminator tells whether to
    // render the current row.
    renderTable(maintainSelected, callback) {
        this.DOM$.tbody.empty();
        // Insert the actual data into the body
        let totalRows = 0;
        for (let i = 0; i < this.data.length; i++) {
            if (this.filter && !this.filter.passes(this.data[i])) { continue; }
            let row$ = $('<tr><td>' + (i+1) + '</td></tr>');
            row$.attr('id', this.trPrefix + (this.index ? this.data[i][this.index] : i));
            row$.data('index', i);
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
                } else if (value['type'] == 'dollar' && cellValue) {
                    cellValue = '$' + parseFloat(cellValue).toFixed(2);
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
                this.selectedRowData = this.data[i];
                this.selectedRowID = event.currentTarget.id;
                this.selectedRowIndex = currentRow;
                this.callbacks['onSelect'](this.selectedRowData);
                $(event.currentTarget).addClass('selected').siblings().removeClass('selected');
            })
            this.DOM$.tbody.append(row$);
            totalRows++;
        }

        // Click the previously selected row by ID
        if (maintainSelected && this.selectedRowID) {
            $('#' + this.selectedRowID).click();
        } else {
            this.selectedRowData = undefined;
            this.selectedRowID = undefined;
            this.selectedRowIndex = undefined;
        }

        // If wasn't visible before, now make visible
        if (!this.visible) {
            this.visible = true;
            this.DOM$.root.fadeIn();
        }

        // Call the onFilter handler
        if (this.filter) {
            this.filter.updateFilterCounts(totalRows);
        }

        // Run callback for when finished
        callback && callback();
    }

    // Selects the previous row from the currently selected
    selectPreviousRow() {
        let rows = this.DOM$.table.find('tbody tr');
        if (rows.length > 0 && this.selectedRowIndex > 0) {
            this.selectedRowIndex--;
            $(rows[this.selectedRowIndex]).click();
        }
    }

    // Selects the next row from the currently selected
    selectNextRow() {
        let rows = this.DOM$.table.find('tbody tr');
        if (rows.length > 0 && this.selectedRowIndex < rows.length - 1) {
            this.selectedRowIndex++;
            $(rows[this.selectedRowIndex]).click();
        }
    }

    // Gets the currently showing data (the data that passes the filters)
    getDisplayedData() {
        return this.DOM$.tbody.find('tr').get().map((tr) => this.data[$(tr).data('index')]);
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