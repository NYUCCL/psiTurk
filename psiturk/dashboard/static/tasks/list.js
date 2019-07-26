Vue.component('task-table-row', {
    props: ['task'],
    template: `
    <tr>
        <td>{{task.id}}</td>
        <td>{{task.name}}</td>
        <td><pre>{{JSON.stringify(task.kwargs, null, 2)}}</pre></td>
        <td>{{task.next_run_time}}</td>
        <td><pre>{{JSON.stringify(task.trigger, null, 2)}}</pre></td>
    </tr>
    `
})

let vm_tasks = new Vue({
    el: '#tasks',
    data: {
        tasks: [],
        approve_all_interval_trimmed: 0,
    },
    computed: {
        approve_all_task: function(){
            return this.tasks.filter(task=>{
                return task.id == 'approve_all'
            })[0]
        },
        exists_approve_all_task: function(){
            return !!this.approve_all_task
        },
        approve_all_interval: {
            get: function(){
                return this.approve_all_interval_trimmed
            },
            set: function(value){
                this.approve_all_interval_trimmed = parseFloat(Math.round(value * 100) / 100).toFixed(2);
            }
            
        }
    },
    methods: {
        fetch_tasks: function(){
            fetch('/api/tasks/').then(response=>{
                return response.json()
            }).then(json=>{
                this.tasks = json
            })
        },
        schedule_approve_all_task: function(){
            fetch('/api/tasks/', {
                method: 'POST',
                body: JSON.stringify({
                    'name': 'approve_all',
                    'interval': this.approve_all_interval,
                }),
                headers: {'Content-Type': 'application/json'}
            }).then(response=>{
                if (!response.ok){
                    return response.json().then(json=>{
                        vm_flash_messages.add_error_message(json.exception, json.message)
                    })
                }
                vm_flash_messages.add_success_message('Successfully scheduled "Approve All" task.')
                return this.fetch_tasks()
            })
        },
        delete_approve_all_task: function(){
            fetch('/api/tasks/' + this.approve_all_task.id,{
                method: 'DELETE'
            }).then(response=>{
                if(!response.ok){
                   return response.json().then(json=>{
                       vm_flash_messages.add_error_message(json.exception, json.message)
                   })
                }
                vm_flash_messages.add_success_message('Successfully deleted task ' + this.approve_all_task.id)
                return this.fetch_tasks()
                
            })
        }
    },
    created: function(){
        this.fetch_tasks();
    }
})