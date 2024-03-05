$(document).ready(function() {
    $('#user-input-form').submit(function(event) {
        event.preventDefault();
        var userInput = $('#user-input').val();
        sendUserInput(userInput);
        $('#user-input').val('');
    });

    function sendUserInput(userInput) {
        $.ajax({
            type: 'POST',
            url: '/api/ideaentity', 
            contentType: 'application/json',
            data: JSON.stringify({ user_input: userInput }),
            success: function(data) {
                var botResponse = data.bot_response;
                displayBotMessage(botResponse);
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });
    }

    function displayBotMessage(botResponse) {
        $('#chat-window').append('<div class="bot-message">' + botResponse + '</div>');
    }
});
