import { DatabaseView } from './dbview.js';
import { DatabaseFilters } from './dbfilter.js';

var CAMPAIGN_FIELDS = {

}

class CampaignDBDisplay {

    // Create the Campaign display with references to the HTML elements it will
    // use as a basis for controls and in which it will fill in the database.
    constructor(domelements) {
        this.DOM$ = domelements;
        this.db = undefined;  // Main HIT database handler
    }

    // Build the database views into their respective elmeents. There is one
    // for the main database and another for the sub-assignments view
    init() {
        this.dbfilters = new DatabaseFilters(this.DOM$, 
            CAMPAIGN_FIELDS, this._filterChangeHandler.bind(this));
        this.db = new DatabaseView(this.DOM$, {
                'onSelect': this._campaignSelectedHandler.bind(this)
            }, 'campaigns', this.dbfilters);
        
        // Load the data
        this._loadCampaigns();
    }

    // Pulls the campaign data from the backend and loads it into the main database
    _loadCampaigns() {
        $.ajax({
            type: 'POST',
            url: '/api/campaigns/',
            data: JSON.stringify({
                codeversion: undefined
            }),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: (data) => {
                this.db.updateData(data, CAMPAIGN_FIELDS, {
                    'rerender': true,
                    'resetFilter': false,
                    'maintainSelected': false,
                    'index': 'HITId',
                    'callback': () => {
                        if (HIT_ID) {
                            $('#' + this.db.trPrefix + HIT_ID).click();
                        }
                    }
                });
            },
            error: function(errorMsg) {
                console.log(errorMsg);
                // alert('Error loading HIT data.');
                // location.reload();
            }
        });
    }

}
