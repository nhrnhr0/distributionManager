import { Calendar } from '@fullcalendar/core';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import listPlugin from '@fullcalendar/list';
import interactionPlugin, { Draggable } from '@fullcalendar/interaction';

document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');
    var unscheduledEl = document.getElementById('unscheduled-events');

    var events = init_events(); // Initialize scheduled events
    var unscheduledEvents = init_unscheduled_events(); // Initialize unscheduled events

    // Render unscheduled events in sidebar
    renderUnscheduledEvents(unscheduledEvents, unscheduledEl);
    new Draggable(unscheduledEl, {
        itemSelector: '.fc-event',
    });
    // Initialize the FullCalendar
    var calendar = new Calendar(calendarEl, {
        events: events,
        plugins: [dayGridPlugin, timeGridPlugin, listPlugin, interactionPlugin],
        initialView: 'dayGridMonth',
        locale: 'he',
        eventStartEditable: true,

        dateClick: function (info) {
            // Navigate to timeGridDay view on date click
            calendar.changeView('timeGridDay', info.dateStr);
            console.log(`Switched to timeGridDay view for date: ${info.dateStr}`);
        },
        eventDidMount: function (info) {
            if (info.event.extendedProps.is_sent)
            {
                // Apply line-through style if is_sent is true
                info.el.style.textDecoration = 'line-through';
            }
        },
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
        editable: true,
        droppable: true, // Enable dropping external events into the calendar
        eventReceive: function (info) {
            let draggedEvent = info.event;
            draggedEvent.setAllDay(false);

            console.log(`Event added: ${draggedEvent.title} at ${draggedEvent.start}`);
            console.log(draggedEvent);
            // Remove event from the unscheduled list
            // unscheduledEvents = unscheduledEvents.filter(event => event.title !== draggedEvent.title);
            // refreshUnscheduledEvents();
            update_message_date(draggedEvent.extendedProps.obj_id, draggedEvent.start);
            info.draggedEl.parentNode.removeChild(info.draggedEl);

        },
        eventDrop: function (info) {
            console.log(`Event moved: ${info.event.title} to ${info.event.start}`);
            console.log(info.event);


            const id = info.event.extendedProps.obj_id;
            // alert("id: " + id + ", new date: " + info.event.start);
            update_message_date(id, info.event.start);
        },
        eventClick: function (info) {
            console.log(`Event clicked: ${info.event.title}`);
            // go to message page /dashboard/messages/edit/51af3e/
            window.location.href = '/dashboard/messages/edit/' + info.event.extendedProps.msg_uid;

        },
    });
    calendar.render();

    // Function to refresh and re-render unscheduled events
    // function refreshUnscheduledEvents() {
    //     unscheduledEl.innerHTML = '';
    //     renderUnscheduledEvents(unscheduledEvents, unscheduledEl);
    // }
});

function update_message_date(id, new_date) {
    const UPDATE_CALENDAR_URL = '/dashboard/calendar/set-date/';
    const csrftoken = getCookie('csrftoken');
    const data = {
        'id': id,
        'new_date': new_date
    };
    fetch(UPDATE_CALENDAR_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            $.notify("הודעה עודכנה בהצלחה",
                {
                    autoHideDelay: 2000,
                    position: 'right bottom',
                    className: 'success'
                });
        })
        .catch((error) => {
            console.error('Error:', error);
        });

}

// Function to initialize scheduled events with `send_at` dates
function init_events() {
    var events = [];
    for (var i = 0; i < msgs.length; i++)
    {
        if (msgs[i].send_at)
        {
            var event = {
                is_sent: msgs[i].is_sent,
                title: msgs[i].category + " - " + msgs[i].message.substring(0, 10),
                start: msgs[i].send_at,
                allDay: false,
                color: hashStringToColor(msgs[i].category),
                msg_uid: msgs[i].message_uid,
                obj_id: msgs[i].id
            };
            events.push(event);
        }
    }
    return events;
}

// Function to get unscheduled events (without `send_at` dates)
function init_unscheduled_events() {
    var unscheduledEvents = [];
    for (var i = 0; i < msgs.length; i++)
    {
        if (!msgs[i].send_at)
        {
            unscheduledEvents.push({
                is_sent: msgs[i].is_sent,
                title: msgs[i].category + " - " + msgs[i].message.substring(0, 10),
                color: hashStringToColor(msgs[i].category),
                category: msgs[i].category,
                message: msgs[i].message,
                msg_uid: msgs[i].message_uid,
                obj_id: msgs[i].id
            });
        }
    }
    return unscheduledEvents;
}

// Render unscheduled events in the sidebar
function renderUnscheduledEvents(events, container) {
    // create a html element for each event <div data-event='{ "title": "my event", "duration": "02:00" }' class='fc-event'>my event</div>
    events.forEach(event => {
        let eventEl = document.createElement('div');
        eventEl.innerText = event.title;
        eventEl.className = 'fc-event';
        eventEl.style.backgroundColor = event.color;
        eventEl.setAttribute('data-event', JSON.stringify({
            title: event.title,
            category: event.category,
            message: event.message,
            msg_uid: event.msg_uid,
            obj_id: event.obj_id,
            is_sent: event.is_sent,
        }));
        container.appendChild(eventEl);
    });


}

// Helper function to generate color based on a string
function hashStringToColor(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++)
    {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const hue = Math.abs(hash % 360);
    const saturation = 70 + (Math.abs(hash) % 30);
    const lightness = 50 + (Math.abs(hash) % 20);

    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}
