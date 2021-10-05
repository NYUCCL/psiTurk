Vue.component('hit-table-row', {
    props: ['hit'],
    computed: {
        hit_data: function(){
            return this.hit.options
        }
    },
    methods: {
        expire: function(){
            fetch('/api/hit/' + this.hit_data.hitid, {
                method: 'PATCH',
                body: JSON.stringify({
                    'is_expired': true
                }),
                headers: {
                    'Content-Type': 'application/json',
                },
            }).then((response)=>{
                return response.json()
            }).then(hit_patch=>{
                vm_flash_messages.add_success_message('Successfully expired hit: ' + this.hit_data.hitid)
                this.$emit('update:hit', hit_patch)
            }).catch(error => console.error('Error:', error))
        },
        delete_hit: function(){
            fetch('/api/hit/' + this.hit_data.hitid, {
                method: 'DELETE'
            })
            .then((response)=>{
                if (!response.ok){
                    return response.json().then(json=>{
                        vm_flash_messages.add_error_message(json.exception, json.message)
                    })
                }
                vm_flash_messages.add_success_message('Successfully deleted hit: ' + this.hit_data.hitid)
                this.$emit('delete:hit')
            })
        },
        approve_all: function(){
            fetch('/api/hit/' + this.hit_data.hitid, {
                method: 'PATCH',
                body: JSON.stringify({
                    'action': 'approve_all'
                }),
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(response=>{
                return response.json()
            }).then(hit_patch=>{
                vm_flash_messages.add_success_message('Approved all for hit: ' + this.hit_data.hitid)
                this.$emit('update:hit', hit_patch)
            }).catch(error=> console.error('Error:', error))
        }
    },
    template: `
    <tr>
        <td>
            <dl>
                <dt>HitId</dt>
                <dd>{{ hit_data.hitid }}</dd>
                
                <dt>Title</dt>
                <dd>{{ hit_data.title }}</dd>            
            </dl>
        </td>
        <td>{{ hit_data.status }}</td>
        <td>
            <div class='dropdown'>
                <button class='btn btn-sm btn-outline-dark dropdown-toggle' 
                    type='button' data-toggle='dropdown'
                >Action</button>
                <div class='dropdown-menu'>
                    <a
                        v-if='!!hit_data.number_submissions_needing_action'
                        v-on:click='approve_all'
                        class='dropdown-item'
                        href='#'
                    >Approve all</a>
                    <a  
                        v-if='!hit_data.is_expired'
                        v-on:click='expire'
                        class='dropdown-item'
                        href='#'
                    >Expire</a>
                    <a  
                        v-else
                        v-on:click='delete_hit'
                        class='dropdown-item'
                        href='#'
                    >Delete</a>
                </div>
            </div>
        </td>
        <td>{{ hit_data.max_assignments }}</td>
        <td>{{ hit_data.number_assignments_completed }}</td>
        <td>{{ hit_data.number_assignments_available }}</td>
        <td>{{ hit_data.number_assignments_pending }}</td>
        <td>{{ hit_data.number_submissions_needing_action }}</td>
        <td>{{ hit_data.duration_in_seconds / 60 }}</td>
        <td>{{ hit_data.reward }}</td>
        <td>{{ new Date(hit_data.creation_time) }}</td>
        <td>{{ new Date(hit_data.expiration) }}</td>
        <td>{{ hit_data.is_expired }}</td>
    </tr>
    `
})

let vm_hits = new Vue({
    el: '#hits',
    data: () => ({
        hits: [],
        show_active: true,
        show_hits: 'show_all_hits',
        filter_map: {
            // 'Assignable'|'Unassignable'|'Reviewable'|'Reviewing'|'Disposed',
            'only_show_active_hits': [],
            'only_show_reviewable_hits': []
        }
    }),
    computed: {
        filtered_hits: function(){
            if (this.show_hits == 'show_all_hits'){
                return this.hits
            } else if (this.show_hits == 'only_show_active_hits'){
                return this.active_hits
            } else if (this.show_hits == 'only_show_reviewable_hits'){
                return this.hits.filter(hit=>{
                    return ['Reviewable','Reviewing'].includes(hit.options.status)
                })
            } else {
                return this.hits
            }
        },
        expired_hits: function(){
            return this.hits.filter(hit=>{
                return hit.options.is_expired
            })
        },
        active_hits: function(){
            return this.hits.filter(hit=>{
                return !hit.options.is_expired
            })
        },
        any_outstanding_submissions: function(){
            return this.hits.some(hit=>{
                return hit.options.number_submissions_needing_action > 0
            })
        },
        any_unexpired: function(){
            return this.hits.some(hit=>{
                return !hit.options.is_expired
            })
        },
        any_deletable: function(){
            return this.hits.some(hit=>{
                return hit.options.is_expired && hit.options.number_submissions_needing_action == 0
            })
        }
    },
    created: function(){
        this.fetch_all_hits()
    },
    methods: {
        fetch_all_hits: function(){
            fetch('/api/hits/').then((response)=>{
                return response.json()
            })
            .then((json)=>{
                this.hits = json
            })            
        },
        delete_hit: function(hit){
            this.hits.splice(this.hits.indexOf(hit), 1)
        },
        update_hit: function(hit, hit_data){
            this.$set(this.hits, this.hits.indexOf(hit), hit_data)
        },
        expire_all: function(){
            fetch('/api/hits/action/expire_all').then((response)=>{
                return response.json()
            })
            .then(json=>{
                for (let _result of json) {
                    if (_result.success) {
                        vm_flash_messages.add_success_message('Successfully expired hit: ' + _result.data.hit_id)
                    } else {
                        vm_flash_messages.add_error_message(json.exception, 
                            'Failed to expire hit: ' + _result.data.hit_id)
                    }
                }
                this.fetch_all_hits()
            })
        },
        delete_all: function(){
            fetch('/api/hits/action/delete_all').then(response=>{
                return response.json()
            })
            .then(json=>{
                for (let _result of json) {
                    if(_result.success) {
                        vm_flash_messages.add_success_message('Successfully deleted hit: ' + _result.data.hit_id)
                    } else {
                        vm_flash_messages.add_error_message(_result.exception.exception,
                            _result.exception.message)
                    }
                }
                this.fetch_all_hits()
            })
        },
        approve_all: function(){
            fetch('/api/hits/action/approve_all').then(response=>{
                return response.json()
            })
            .then(json=>{
                for (let _result of json) {
                    if(_result.success) {
                        if (_result.data.results.length) {
                            vm_flash_messages.add_success_message('Approved all assignments for hit: ' + _result.data.hit_id)
                        }
                    } else {
                        vm_flash_messages.add_error_message(_result.exception.exception)
                    }
                }
                this.fetch_all_hits()
            })
        }
    }
})