
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
    constructor(domelements, columns) {
        this._buildElements(domelements);
        this.cols = columns;
        this.filters = {
            'search': '',
            'cols': []
        };

        // Prepend the database filters elemeents to the DOM root
        this.DOM$.filters.prepend(this.DOM$.layout);

        this.addFilter();
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
    }

    // Adds a database filter into the row, saving a filter entry into the array
    // and keeping a reference to its dom element.
    addFilter() {
        let filter_CB = $('<input type="checkbox" aria-label="Filter checkbox">');
        let col_B = $('<button class="btn btn-light dropdown-toggle px-1" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="border-radius: 0px;">Column</button>');
        let col_DD = this._dropDownOptions();
        let comp_B = $('<button class="btn btn-light dropdown-toggle px-1" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="border-radius: 0px;">Compare</button>');
        let comp_DD = $('<div class="dropdown-menu"></div>');
        let filter_I = $('<input type="text" class="form-control" aria-label="Filter input">');
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


        //! TODO: Add filter listeners

        // Add the filter to the list of filters
        this.filters.cols.push({
            DOM$: {
                root: newFilter,
                active: filter_CB,
                col: col_B,
                comp: comp_B,
                input: filter_I
            }
        });

        // Append the filter to the DOM
        this.DOM$.filterLayout.append(newFilter);
    }

    // Generates jquery element of the columns for a filter's dropdown optionss
    _dropDownOptions() {
        let dropdown = $('<div class="dropdown-menu"></div>');
        this.cols.forEach((col, i) => {
            dropdown.append($('<button class="dropdown-item" type="button" data-col="' + i + '">' + col.title + '</button>'));
        });
        return dropdown;
    }
}