 let vm_tasks = new Vue({
     el: '#tasks',
     data: {
         tasks: [],
     },
     methods: {
         fetch_tasks: function(){
             fetch('/api/tasks/').then(response=>{
                 return response.json()
             }).then(json=>{
                 this.tasks = json
             })
         },
     },
     created: function(){
         this.fetch_tasks();
     }
 })