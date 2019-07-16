Vue.component('assignment-table-row',{
    props: ['assignment'],
    template: ``
})

let vm_assignments = new Vue({
    el: '#assignments',
    data: ()=>({
        assignments: [],
        bonus_reason: ''
    }),
    computed: {
        any_assignments: function(){
            return !!this.assignments.length
        },
        any_assignments_pending_approval: function(){
            return !!this.assignments_pending_approval.length
        },
        any_autobonusable_assignments: function(){
            return !!this.assignments.some(assignment=>{
                return assignment.status == 5
            })
        },
        assignments_pending_approval: function(){
            return this.assignments.filter(assignment=>{
                return assignment.status == 4
            })
        }
    },
    methods: {
        fetch_all_assignments: function(){
            fetch('/api/assignments/').then(response=>{
                return response.json()
            })
            .then(json=>{
                this.assignments = json
            })
        },
        approve_all: function(){
            fetch('/api/assignments/action/approve_all').then(response=>{
                return response.json()
            })
            .then(json=>{
                let successes = json.filter(entry=>{
                    return entry.success
                })
                if (successes.length){
                    vm_flash_messages.add_success_message('Approved ' + successes.length + ' assignments')
                }
                let _errors = json.filter(entry=>{
                    return !entry.success
                })
                for (let _error of _errors){
                    vm_flash_messages.add_error_message(_error.exception.exception, _error.exception.message)
                }
                
                this.fetch_all_assignments()
            })
        },
        bonus_all: function(){
            fetch('/api/assignments/action/bonus_all',{
                method: 'POST',
                body: JSON.stringify({'reason': this.bonus_reason}),
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(response=>{
                if(!response.ok){
                    response.json().then(json=>{
                        vm_flash_messages.add_error_message(json.exception, json.message)
                    })
                    throw new Error()
                }
                return response.json()
            }).then(json=>{
                ({successes, errors} = this.split_success_and_failures(json))
                if (successes.length){
                    vm_flash_messages.add_success_message('Auto-bonused ' + successes.length + ' assignments')
                }
                for (let _error of errors){
                    vm_flash_messages.add_error_message(_error.exception.exception, _error.exception.message + ' for assignment_id ' + _error.data.assignment_id)
                }
            }).then(()=>{
                this.fetch_all_assignments()
            }).catch(error=>{
                // do nothing
            })
        },
        split_success_and_failures: function(results){
            let successes = results.filter(entry=>{
                return entry.success
            })
            let errors = results.filter(entry=>{
                return !entry.success
            })
            return {'successes': successes, 'errors': errors}
        }
    },
    created: function(){
        this.fetch_all_assignments()
    },
})