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
        test: 'someting'
    }
})  

console.log(vm.test)