Vue.component('campaign-table-row',{
    props: ['campaign'],
    template: `
    <tr>
        <td>{{campaign.id}}</td>
        <td>{{campaign.codeversion}}</td>
        <td>{{campaign.mode}}</td>
        <td>{{campaign.hit_reward}}</td>
        <td>{{campaign.hit_duration_hours}}</td>
        <td>{{campaign.created}}</td>
        <td>{{campaign.ended}}</td>
        <td>{{campaign.goal}}</td>
        <td>{{campaign.assignments_per_round}}</td>
        <td>{{campaign.minutes_between_rounds}}</td>
    </tr>
    `
})

let vm_campaigns = new Vue({
    el: '#campaigns',
    data: { 
        services_manager,
        campaigns: [],
        create_goal_rounded: 0,
        assignments_per_round_rounded: 0,
        minutes_between_rounds_rounded: 0,
        extend_this_many_rounded: 0,
        update_active_campaign_goal_rounded: 0,
        completed_count: completed_count,
        available_count: available_count,
        pending_count: pending_count,
        maybe_will_complete_count: maybe_will_complete_count,
        hit_reward_rounded: parseFloat(0.00),
        hit_duration_hours_rounded: parseFloat(0.00)
    },
    computed: {
        create_goal: {
            get: function(){
                return this.create_goal_rounded
            },
            set: function(value){
                this.create_goal_rounded = Math.floor(value)
            }
        },
        assignments_per_round: {
            get: function(){
                return this.assignments_per_round_rounded
            },
            set: function(value){
                this.assignments_per_round_rounded = Math.floor(value)
            }
        },
        minutes_between_rounds: {
            get: function(){
                return this.minutes_between_rounds_rounded
            },
            set: function(value){
                this.minutes_between_rounds_rounded = Math.floor(value)
            }
        },
        hit_duration_hours: {
            get: function(){
                return this.hit_duration_hours_rounded
            },
            set: function(value){
                this.hit_duration_hours_rounded = parseFloat(Math.round(value * 100) / 100).toFixed(2);
            }
        },
        hit_reward: {
            get: function(){
                return this.hit_reward_rounded
            },
            set: function(value){
                this.hit_reward_rounded = parseFloat(Math.round(value * 100) / 100).toFixed(2);
            }
        },
        extend_this_many: {
            get: function(){
                return this.extend_this_many_rounded
            },
            set: function(value){
                this.extend_this_many_rounded = Math.floor(value)
            },
        },
        update_active_campaign_goal: {
            get: function(){
                return this.update_active_campaign_goal_rounded
            },
            set: function(value){
                this.update_active_campaign_goal_rounded = Math.floor(value)
            }
        },
        ended_campaigns: function(){
            return this.campaigns.filter(campaign=>{
                return !campaign.is_active
            })
        },
        active_campaign: function(){
            return this.campaigns.filter(campaign=>{
                return campaign.is_active
            })[0]
        },
        is_valid_extension: function(){
            return (this.extend_this_many + this.active_campaign.goal ) > this.completed_count
        },
        is_valid_update_active_goal: function(){
            return ( this.update_active_campaign_goal > this.completed_count )
        },
    },
    methods: {
        fetch_all_campaigns: function(){
            return fetch('/api/campaigns').then(response=>{
                return response.json()
            }).then(json=>{
                this.campaigns = json
            })
        },
        create_new_campaign: function(){
            fetch('/api/campaigns/',{
                method: 'POST',
                body: JSON.stringify({
                    'goal': this.create_goal,
                    'assignments_per_round': this.assignments_per_round,
                    'minutes_between_rounds': this.minutes_between_rounds,
                    'hit_duration_hours': parseFloat(this.hit_duration_hours),
                    'hit_reward': parseFloat(this.hit_reward)
                }),
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(response=>{
                if (!response.ok){
                    return response.json().then(json=>{
                        vm_flash_messages.add_error_message(json.exception, json.message)
                    })
                }
                this.fetch_all_campaigns().then(()=>{
                    vm_flash_messages.add_success_message('Successfully created new campaign.')
                })
            })
        },
        update_active_goal: function(){
            fetch('/api/campaigns/' + this.active_campaign.id,{
                method: 'PATCH',
                body: JSON.stringify({
                    'goal': this.update_active_campaign_goal
                }),
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(response=>{
                if(!response.ok){
                    return response.json().then(json=>{
                        vm_flash_messages.add_error_message(json.exception, json.message)
                    })
                }
                this.fetch_all_campaigns().then(()=>{
                    vm_flash_messages.add_success_message('Successfully updated active campaign.')
                })
            })
        },
        cancel_active: function(){
            fetch('/api/campaigns/' + this.active_campaign.id, {
                method: 'PATCH',
                body: JSON.stringify({
                    'is_active': false
                }),
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(response=>{
                if(!response.ok){
                    return response.json().then(json=>{
                        vm_flash_messages.add_error_message(json.exception, json.message)
                    })
                }
                this.fetch_all_campaigns().then(()=>{
                    vm_flash_messages.add_success_message('Successfully cancelled the active campaign.')
                })
            })
        },
    },
    created: function(){
        this.fetch_all_campaigns()
    }
})