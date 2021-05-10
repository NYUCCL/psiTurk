Vue.component('vue-flash-message', {
    props: ['message','category'],
    computed: {
        _category: function(){
            if (this.category == 'message') { 
                return 'info' 
            } else {
                return this.category
            }
        },
        _class: function(){
            return 'alert alert-dismissible alert-' + this._category
        }
    },
    template: `
        <div :class='_class' role='alert'>
            <button 
                v-on:click="$emit('close')" 
                type='button' class='close' aria-label='close'><span aria-hidden='true'>×</span></button>
            {{message}}
        </div>
    `
})
let vm_flash_messages = new Vue({
    el: '#vue-flash-messages',
    data: {
        messages: flask_messages || [] // [category, message]
    },
    methods: {
        close_message: function(index){
            this.messages.splice(index, 1)
        },
        add_message: function(message, category){
            this.messages.push([category, message])
        },
        add_error_message: function(type, message){
            this.messages.push(['danger', type + ': ' + message])
        },
        add_success_message: function(message){
            this.messages.push(['success', message])
        }
    }
})
