// Defines a database view for manipulating HITs and Workers

var DEFAULT_FILTERS = {
    'searchFilter': undefined,
    'comp': {}
}

var DEFAULT_SORT = {
    'last': undefined,
    'forwards': true
}

var FILTER_TYPES = {
    'string': {
        'contains': {
            'title': 'CONTAINS',
            'comparator': (a, b) => a.includes(b)
        },
        'equals': {
            'title': 'EQUALS',
            'comparator': (a, b) => a == b
        }
    },
    'num': {
        'greaterthan': {
            'title': 'GREATERTHAN',
            'comparator': (a, b) => a > b
        },
        'equals': {
            'title': 'EQUALS',
            'comparator': (a, b) => a == b
        },
        'lessthan': {
            'title': 'LESSTHAN',
            'comparator': (a, b) => a < b
        },
    },
    'date': {
        'greaterthan': {
            'title': 'GREATERTHAN',
            'comparator': (a, b) => new Date(a) > new Date(b)
        },
        'equals': {
            'title': 'EQUALS',
            'comparator': (a, b) => new Date(a) == new Date(b)
        },
        'lessthan': {
            'title': 'LESSTHAN',
            'comparator': (a, b) => new Date(a) < new Date(b)
        }
    },
    'bool': {
        'is': {
            'title': 'IS',
            'comparator': (a, b) => a
        }, 
        'not': {
            'title': 'NOT',
            'comparator': (a, b) => !a
        }
    }
}

/**
 * View for a database.
 */
export class DatabaseView {

    // Injects a database view into the parent element
    constructor(domelements, callbacks, name="") {
        this.DOM$ = {
            ...domelements,
            root: $('<div id="dbContainer_' + this.name + '" class="db-container"></div>'),
            tableView: $('<div id="tableView_"' + this.name +' class="db-tableView no-scrollbar"></div>'),
            table: $('<table id="table_' + this.name + '" class="db-table"><thead class="db-thead"></thead><tbody class="db-tbody"></tbody></table>')
        };
        this.callbacks = callbacks; 
        this.name = name;

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
    async updateData(newData, fields, rerender=true, beforeReRender=undefined) {
        this.data = newData;
        this.fields = fields;
        this.sort = DEFAULT_SORT;
        this.order = [...Array(50).keys()];

        // Reset headers of columns
        let tHead$ = this.DOM$.table.find('thead');
        tHead$.empty();
        let headerTr$ = $('<tr/>');
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

        // Reset the filters
        if (rerender) { 
            if (beforeReRender) {
                beforeReRender();
            }
            await this.renderTable();
        }

        return Promise.resolve();
    }

    // Re-renders the table based on the order, discriminator tells whether to
    // render the current row.
    async renderTable(discriminator=undefined) {
        // Maintain previously selected row
        let selectedRow = this.DOM$.table.find('tr.selected');
        if (selectedRow) {
            selectedRow = selectedRow.attr('id');
        }

        let tBody$ = this.DOM$.table.find('tbody');
        tBody$.empty();

        // Insert the actual data into the body
        let totalRows = 0;
        for (let i = 0; i < this.order.length && i < this.data.length; i++) {
            if (discriminator && !discriminator(this.data[i])) { continue; }
            let row$ = $('<tr/>');
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
            row$.on("click", (event) => {
                let index = /_([0-9]*)$/g.exec(event.currentTarget.id);
                let selected = parseInt(index[1]);
                this.callbacks['onSelect'](this.data[selected]);
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
        if ('onFilter' in this.callbacks) {
            this.callbacks['onFilter'](totalRows);
        }

        return Promise.resolve();
    }

    // Sorts the table based on the header clicked
    sortByColumn(colTitle) {
        var switching = true;
        let byColIndex = Object.keys(this.fields).indexOf(colTitle);
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

export class DatabaseViewWithFilters extends DatabaseView {

    constructor(parentId, callbacks, name='') {
        super(parentId, callbacks, name);

        this.filters = DEFAULT_FILTERS;

        // Build filter layout
        this.filterLayout$ = $('<div id="dbFilterLayout_' + this.name + '" class="db-filtersLayout"></div>');
        this.filters$ = $('<ul id="dbFilters_' + this.name + '" class="db-filters"></ul>');
        this.searchCbox$ = $('<input type="checkbox" id="applySearch_' + this.name + '" class="db-filtersApplySearch">');
        this.searchInput$ = $('<input type="text" id="searchText_' + this.name + '" class="db-filtersSearchTextInput">');
        this.filterLayout$.append($('<span class="db-filtersListTitle">SEARCH</span>'))
            .append($('<div id="searchLayout_' + this.name + '" class="db-filtersSearchLayout"></div>')
                .append(this.searchCbox$)
                .append(this.searchInput$))
            .append($('<span class="db-filtersListTitle">FILTERS</span>'))
            .append(this.filters$);
        // Prepend it (before the table view from super constructor)
        // this.DOM$.filters.append(this.filterLayout$);

        // Add listeners to search filter
        this.searchCbox$.on('change', (event) => {
            if (event.target.checked) {
                this.filters.searchFilter = this.searchInput$.val();
            } else {
                this.filters.searchFilter = undefined;
            }
            this.updateFilterCounts();
            this.renderTable(); 
        });
        this.searchInput$.on('change', (event) => {
            if (this.searchCbox$.prop('checked')) {
                this.filters.searchFilter = event.target.value;
                this.updateFilterCounts();
                this.renderTable(); 
            }
        });
    }

    // ========== OVERRIDES ============

    // Override update data to include filtering functionality
    async updateData(newData, fields, rerender=true) {
        this.filters = DEFAULT_FILTERS;
        // Update the data and rerender filters before rerendering table
        return super.updateData(newData, fields, rerender, () => {
            this.renderFilters();
            this.updateFilterCounts();
        });
    }

    // Overridden rendertable simply uses the filtering function found here
    async renderTable() {
        return super.renderTable((row) => this.passesFilters(row));
    }

    // Tallies up the filter counts
    updateFilterCounts() {
        for (let i = 0; i < Object.keys(this.fields).length; i++) {
            let count = 0;
            this.data.forEach(row => {
                if (this.passesFilters(row, Object.keys(this.fields)[i])) {
                    count++;
                }
            })
            $('#count_' + this.name + '_' + i).text(count);
        }
    }

    // Resets the filters on the left
    renderFilters() {
        this.filters$.empty();
        this.filters.comp = {};
        let i = 0;
        for (const [key, value] of Object.entries(this.fields)) {
            this.filters.comp[key] = {'active': false, 'index': key, 'dataType': value['type'], 'type': Object.keys(FILTER_TYPES[value['type']])[0], 'value': ''};
            let li$ = $('<li id="' + i + '_li"></li>');
            let filterval$ = $('<input type="text" class="db-filterVal" id="filterVal_' + this.name + '_' + i + '" value="">');
            let filteroption$ = $('<select class="db-filterOption" id="filterType_' + this.name + '_' + i + '"></select>');
            for (const [key2, value2] of Object.entries(FILTER_TYPES[value['type']])) {
                filteroption$.append($('<option value="' + key2 + '">' + value2['title'] + '</option>'));
            }
            let filtercbox$ = $('<input type="checkbox" value="' + i + '">');

            // Event listeners for each filter
            filtercbox$.on('change', (event) => {
                this.filters.comp[key]['active'] = event.target.checked;
                if (event.target.checked) {
                    $('#filterCustom_' + this.name + '_' + key).css('display', 'block');
                } else {
                    $('#filterCustom_' + this.name + '_' + key).css('display', 'none');
                }
                this.updateFilterCounts();
                this.renderTable();  
            })
            filteroption$.on('change', (event) => {
                this.filters.comp[key]['type'] = event.target.value;
                this.updateFilterCounts();
                this.renderTable();
            });
            filterval$.on('change', (event) => {
                this.filters.comp[key]['value'] = event.target.value;
                this.updateFilterCounts();
                this.renderTable();
            })

            // Build the elements for each filter
            li$.append(filtercbox$)
                .append('(')
                .append($('<span id="count_' + this.name + '_' + i + '">?</span>)'))
                .append(') ' + value['title'])
                .append($('<div id="filterCustom_' + this.name + '_' + key + '" style="display: none"></div>')
                    .append($(filteroption$))
                    .append(filterval$));
            this.filters$.append(li$);        
            i++;
        }
    }

    // Checks if a given row passes the current filters and search key
    passesFilters(row, analyzeFilter=undefined) {
        // First check the col-specific filters 
        let passesFilter = Object.values(this.filters.comp).every((filter) => {
            if (filter['type'] == undefined || (!filter['active'] && filter['index'] != analyzeFilter)) {
                return true;
            } else {
                return FILTER_TYPES[filter['dataType']][filter['type']]['comparator'](row[filter['index']], filter['value']);
            }
        });

        // Now check the search filter on all columns
        if (this.filters.searchFilter != undefined && passesFilter) {
            passesFilter = false;
            for (const [_, value] of Object.entries(row)) {
                if (value && value.toString().toLowerCase().includes(this.filters.searchFilter.toLowerCase())) {
                    passesFilter = true;
                    break;
                }
            }
        }

        return passesFilter;
    }
}