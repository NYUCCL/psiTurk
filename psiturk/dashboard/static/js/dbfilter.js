
var DEFAULT_FILTERS = {
    'searchFilter': undefined,
    'comp': {}
}


var FILTER_TYPES = {
    'string': {
        'contains': {
            'title': 'contains',
            'comparator': (a, b) => a.includes(b)
        },
        'equals': {
            'title': 'equals',
            'comparator': (a, b) => a == b
        }
    },
    'num': {
        'greaterthan': {
            'title': '>',
            'comparator': (a, b) => a > b
        },
        'equals': {
            'title': '=',
            'comparator': (a, b) => a == b
        },
        'lessthan': {
            'title': '<',
            'comparator': (a, b) => a < b
        },
    },
    'date': {
        'greaterthan': {
            'title': '>',
            'comparator': (a, b) => new Date(a) > new Date(b)
        },
        'equals': {
            'title': '=',
            'comparator': (a, b) => new Date(a) == new Date(b)
        },
        'lessthan': {
            'title': '<',
            'comparator': (a, b) => new Date(a) < new Date(b)
        }
    },
    'bool': {
        'is': {
            'title': 'exists',
            'comparator': (a, b) => a
        }, 
        'not': {
            'title': 'missing',
            'comparator': (a, b) => !a
        }
    }
}


/**
 * Handles filtering a database table. Functions independently from the DB view,
 * as it only tells the database what to render and does not require any
 * communication back to itself.
 */
 export class DatabaseFilters {

    // Constructor initializes the filters with the names of the columns in the
    // database and DOM elements into which to put the database filters.
    constructor(domelements, columns, onChange) {
        this._buildElements(domelements);
        this.cols = columns;
        this.n = 0;
        this.filters = {
            'search': {
                'text': '',
                'active': false
            },
            'cols': {}
        };

        // Save the onchange handler
        this.onChangeHandler = onChange;

        // Prepend the database filters elements to the DOM root
        this.DOM$.filters.prepend(this.DOM$.layout);
    }

    // Builds the HTML elements of the database filters
    _buildElements(rootdom) {
        let count = $('<small class="text-muted">(0 matching)</small>');
        let searchCbox = $('<input type="checkbox" aria-label="Checkbox for search filter">');
        let searchInput = $('<input type="text" class="form-control" aria-label="Search filter input">');
        let filterLayout = $('<div></div>');
        let addFilterButton = $('<button class="btn btn-secondary btn-sm btn-block mt-2" type="button" id="button-addon1" style="opacity: 0.8;">+ Add another database filter...</button>');
        this.DOM$ = {
            ...rootdom,
            count: count,
            search_CB: searchCbox,
            search_I: searchInput,
            filterLayout: filterLayout,
            addFilter_B: addFilterButton,
            layout: $('<div></div>').append(
                    $('<div class="text-light mb-1"></div>')
                        .append($('<span>Filters </span>')
                        .append(count)))
                    .append($('<div class="input-group mb-1"></div>')
                        .append($('<div class="input-group-prepend"></div>')
                            .append($('<div class="input-group-text"></div>')
                                .append(searchCbox))
                            .append($('<div class="input-group-text">Search</div>')))
                        .append(searchInput))
                    .append(filterLayout)
                    .append(addFilterButton)
        };

        // LISTENERS
        // Add a new filter
        this.DOM$.addFilter_B.on('click', this.addFilter.bind(this));
        searchInput.on('change', (event) => {
            this.filters.search.text = event.target.value;
            this.onFilterChange();});
        searchCbox.on('click', (event) => {
            this.filters.search.active = event.target.checked;
            this.onFilterChange();});
    }

    // Adds a database filter into the row, saving a filter entry into the array
    // and keeping a reference to its dom element.
    addFilter() {
        let filter_CB = $('<input type="checkbox" aria-label="Filter checkbox">');
        let col_B = $('<button class="btn btn-light dropdown-toggle px-1" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="border-radius: 0px;">Column</button>');
        let col_DD = this._dropDownColOptions();
        let comp_B = $('<button class="btn btn-light dropdown-toggle px-1" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="border-radius: 0px;">Compare</button>');
        let comp_DD = $('<div class="dropdown-menu"></div>');
        let filter_I = $('<input type="text" class="form-control" aria-label="Filter input" disabled>');
        let delete_B = $('<button class="btn btn-primary" type="button" id="button-addon1">x</button>');
        let newFilter = 
            $('<div class="input-group mb-1"></div>')
                .append($('<div class="input-group-prepend"></div>')
                    .append($('<div class="input-group-text"></div>')
                        .append(filter_CB))
                    .append($('<div class="btn-group"></div>')
                        .append(col_B)
                        .append(col_DD))
                    .append($('<div class="btn-group"></div>')
                        .append(comp_B)
                        .append(comp_DD)))
                .append(filter_I)
                .append($('<div class="input-group-append">')
                    .append(delete_B));

        // Add the filter to the list of filters
        let index = '' + this.n;
        this.filters.cols[index] = {
            col: -1,
            comp: undefined,
            text: '',
            active: false,
            DOM$: {
                root: newFilter,
                active: filter_CB,
                col: col_B,
                comp: comp_B,
                input: filter_I
            }
        };
        this.n += 1;

        // When filtered column changes
        col_DD.find('button').on('click', (event) => {
            let col = $(event.currentTarget).data('col');
            this.filters.cols[index].col = col;
            col_B.html(event.currentTarget.innerHTML);
            filter_I.prop('disabled', true);
            this.filters.cols[index].comp = undefined;
            comp_B.html('Compare');
            comp_DD.empty();
            comp_DD.append(this._dropDownCompOptions(col, index, comp_B, filter_I));
        });
        // When the input changes from user input
        filter_I.on('change', (event) => {
            this.filters.cols[index].text = event.target.value;
            if (this.filters.cols[index].comp) {
                this.onFilterChange();
            }
        });
        // When the filter is activated
        filter_CB.on('click', (event) => {
            this.filters.cols[index].active = event.target.checked;
            this.onFilterChange();
        })

        // Delete button filter destroyer
        delete_B.on('click', () => { 
            newFilter.remove(); 
            delete(this.filters.cols[index]);
        });

        // Append the filter to the DOM
        this.DOM$.filterLayout.append(newFilter);
    }

    // Centralize filter changes here
    onFilterChange() {
        this.onChangeHandler(this.filters);
    }

    // Generates jquery element of the columns for a filter's dropdown options
    _dropDownColOptions() {
        let dropdown = $('<div class="dropdown-menu"></div>');
        this.cols.forEach((col, i) => {
            dropdown.append($('<button class="dropdown-item" type="button" data-col="' + i + '">' + col.title + '</button>'));
        });
        return dropdown;
    }

    // Generates jquery element of the comparators for a filter's dropdown options
    _dropDownCompOptions(colIndex, filterIndex, comp_B, filter_I) {
        let type = this.cols[colIndex].type;
        let items = [];
        Object.entries(FILTER_TYPES[type]).forEach(([key, value], _) => {
            let option = $('<button class="dropdown-item" type="button" data-comp="' + key + '">' + value.title + '</button>');
            items.push(option);
            option.on('click', (event) => {
                filter_I.prop('disabled', false);
                comp_B.html(event.currentTarget.innerHTML);
                this.filters.cols[filterIndex].comp = $(event.currentTarget).data('comp');
                this.onFilterChange();
            });
        })
        return items;
    }
}