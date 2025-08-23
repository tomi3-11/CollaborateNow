const project_id = {{ project.id }};
const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/project/'
    + project_id
    + '/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    document.querySelector('#chat-log').innerHTML += (`<div><strong>${data.user}</strong>: ${data.message}</div>`);
};

chatSocket.onclose = function(e) {
    console.error("Chat socket closed unexpectedly");
};

document.querySelector('#chat-message-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.ariaValueMax;
    chatSocket.send(JSON.stringify({
        'message': message
    }));
    messageInputDom.value = '';
};