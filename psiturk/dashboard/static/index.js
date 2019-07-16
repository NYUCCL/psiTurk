Vue.component('distinct-value-set', {
    props: ['grouping_key', 'filter_values'],
    computed: {
        group_distinct_values: function(){
            return this.$parent.distinct_values[this.grouping_key]
        }
    },
    template:   `<div>
                    <h4>{{grouping_key}}</h4>
                    <template v-if='filter_values[grouping_key]'>
                        <distinct-value-checkbox 
                            v-for='distinct_value in group_distinct_values'
                            v-bind:key='distinct_value'
                            v-bind:filter_value_label="distinct_value"
                            v-bind:distinct_value="distinct_value"
                            v-bind:grouping_key="grouping_key"
                            v-model:filter_checked="filter_values[grouping_key][distinct_value]"
                        ></distinct-value-checkbox>
                    </template>
                </div>`
})

Vue.component('distinct-value-checkbox', {
    props: {
        grouping_key: String,
        filter_checked: Boolean,
        filter_value_label: null
    },
    model: {
        prop: 'filter_checked',
        event: 'change'
    },
    template: `
        <div class='form-check form-check-inline'>
            <input class='form-check-input' type='checkbox' 
                v-bind:id="'checkbox-' + grouping_key + '-' + filter_value_label"
                v-bind:checked='filter_checked'
                v-on:change="$emit('change', $event.target.checked)"
                >
            <label class='form-check-label' 
                :for="'checkbox-' + grouping_key + '-' + filter_value_label"
            >{{filter_value_label}}</label>
        </div>
    `
})



var d3app = new Vue({
    el: '#workers_data',
    data: {
        rollup_value: new Map([['count', v => v.length]]),
        rollup_grouping: new Map([
            ['codeversion', d => d.codeversion],
            ['mode', d => d.mode],
            ['condition', d => d.cond],
            ['status', d => d.status],
        ]),
        raw_data: [],
        only_show_complete_status: true,
        group_by_condition: true,
        only_latest_codeversion: true,
        filter_values: {},
        complete_statuses: [3,4,5,7],
        latest_codeversion: current_codeversion,
    },
    computed: {
        keys: function() {
            return this.grouping_keys.concat(Array.from(this.rollup_value.keys()))
        },
        current_rollup_grouping: function(){
            let _rollup_grouping = new Map(this.rollup_grouping)
            if (!this.group_by_condition){
                _rollup_grouping.delete('condition')
            }
            if (this.only_show_complete_status){
                _rollup_grouping.delete('status')
            }
            if (this.only_latest_codeversion){
                _rollup_grouping.delete('codeversion')
            }
            return _rollup_grouping
        },
        grouping_keys: function(){
            return Array.from(this.current_rollup_grouping.keys())
        },
        mapped_data: function() {
            let _worker_data = this.raw_data
            if (this.only_show_complete_status){
                _worker_data = _worker_data.filter(row => {
                    return this.complete_statuses.includes(row.status)
                })
            }
            if (this.only_latest_codeversion){
                _worker_data = _worker_data.filter(row => {
                    return row.codeversion == this.latest_codeversion
                })
            }
            var worker_data_counts = d3.rollup(_worker_data,
                ...this.rollup_value.values(), ...this.current_rollup_grouping.values())
            return worker_data_counts
        },
        flat_data: function(){
            let _flat_data = this.flatten_data(this.mapped_data)
            // const sortAlphaNum = ([a], [b]) => a.localeCompare(b, 'en', { numeric: true })
            _flat_data.sort(this.super_sorter)
            return _flat_data
        },
        distinct_values: function(){
            let distincts = {}
            this.grouping_keys.forEach((key, index) => {
                let _distincts = [...new Set(this.flat_data.map(entry => entry[index]))]
                distincts[key] = _distincts
            })
            return distincts
        },
        filter_values_with_defaults: function(){            
            let new_filter_values = {}
            Object.keys(this.distinct_values).forEach(distinct_key=>{
                if (this.distinct_values[distinct_key].length){
                    new_filter_values[distinct_key] = {}
                    this.distinct_values[distinct_key].forEach(distinct_value => {
                        new_filter_values[distinct_key][distinct_value] = true
                    })   
                }
            })
            
            Object.assign(new_filter_values, this.filter_values)
            this.filter_values = new_filter_values
            return new_filter_values            
        },
        
        filtered_data: function(){
            let _filter_values = this.filter_values_with_defaults
            return this.flat_data.filter(row => { 
                return this.grouping_keys.every((key,index) => {
                    let value = row[index]
                    return _filter_values[key][value]
                })
            })
        }
    },
    created: function(){
        fetch('/api/assignments/')
        .then((response)=>{
            return response.json()
        })
        .then((json)=>{
            this.raw_data = json
        })
    },
    methods: {
        flatten_data: function(flatten_me){
            let rows = []
            if ( flatten_me instanceof Map) {
                for (let [key, value] of flatten_me.entries()) {
                    if (value instanceof Map) {
                        let _rows = this.flatten_data(value)
                        for (_row of _rows) {
                            rows.push([key].concat(_row))
                        }
                    } else {
                        rows.push([key, value])
                    }
                }
            }
            return rows
        },
        set_filter_values: function(key, selected) {
            this.distinct_values[key].forEach((value) => {
                this.filter_values[key][value] = selected.includes(value)
            })
        },
        super_sorter: function(a, b) {
            for (const[i,v] of this.grouping_keys.entries()){
                if (a[i] != b[i]){
                    return String(a[i]).localeCompare(String(b[i]), 'en', { numeric: true })
                }
            }
            return 0
        }
    }
})
