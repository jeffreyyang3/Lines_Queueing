/*
    Queue.js
    Static script for the queue room.
    Participants will be displayed in a queue facing a door.

    I think I can use otree redwood to manipulate the html in the template,
    but I'm not certain about how much of what's in this file that I can 
    manipulate. 

    This document only describes static features: the room itself, the door, and the positions on the page where players can go
*/

var vm = new Vue({
    delimiters: ['{', '}'],
    el: '#app',
    data: {
        num_players: null,
        position: null,
        in_trade: false,
        requested: false,
        requesting: false,
        pay_rate: null,
        time_remaining_queue: null,
        time_remaining_advance: null,
        time_remaining_session: null,
        accumulated: null,
        round: null,
        alert_messages: {
            requested: 'You have been requested to swap',
            requesting: 'You have requested to swap',
            accepted: 'Your swap request has been accepted',
            accepting: 'You have accepted a swap request',
            denied: 'Your swap request has been declined',
            denying: 'You have declined a swap request'
        },
        current_alert: null,
        alert_duration: 3, //duration in s an alert is shown
        alert_fadeout: 1.5, // duration in s an alert fades out
        time: '100'
    }  
})  

