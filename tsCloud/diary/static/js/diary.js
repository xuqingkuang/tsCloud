var chatWithUser;
var messagesContainer = $('#chatForm ul');

var constructMessageElement = function(message, postAt, type) {
	var postAtElement = $('<i>').html(postAt + ': ');
	var messageElement = $('<span>').html(message);
	return $('<li>').addClass(type).append(postAtElement).append(messageElement);
}

var listeningRemoteTalk = function() {
	$.ajax({
		url: 'api/receive_messages/',
		type: 'get',
		dataType:'json',
		cache: false,
		timeout: 50000, /* Timeout in ms */
		success: function(returnobj) {
			if (returnobj.rc == 200) {
				for (var i=0; (message = returnobj.messages[i]); i++) {
					messagesContainer.append(constructMessageElement(
						message.message, message.post_at, 'incoming'
					))
				}
				setTimeout(
					listeningRemoteTalk, /* Request next message */
					1000 /* ..after 1 seconds */
				);
			}
		},
		error: function(XMLHttpRequest, textStatus, errorThrown) {
			setTimeout(
				listeningRemoteTalk, /* Request next message */
				1000 /* ..after 1 seconds */
			);
		}
	})
}

var startChat = function(user) {
	// Reorganize the window for chat area
	var diaryWindow = $('.diary');
	var diaryWindowLayout = diaryWindow.find('.span12');
	if (!diaryWindowLayout.hasClass('span9')) {
		diaryWindowLayout.addClass('span9');
	}
	diaryWindow.find('.chat').show();
	// Start chat
	listeningRemoteTalk();
}

var updateEmotion = function(emotion_id) {
	$.ajax({
		url: 'api/update_emotion/',
		type: 'get',
		dataType:'json',
		data: {
			emotion_id: emotion_id,
		},
		success: function(returnobj) {
			if (returnobj.rc == 200) {
				chatWithUser = returnobj.chat_with_user;
				$('#foundSameEmotionPrompt').modal('show');
			}
			// TODO or NOTTODO: Prompto user no body have same emotion.
		}
	})
}

$(document).ready(function(e) {
	// Emotion icon changed.
	$('#emotionIcons a').click(function(e) {
		var self = $(this);
		var container = self.parents('.dropdown');
		
		// Change dropdown icon.
		var selected_icon = self.find('i');
		var selector_icon = container.find('a.dropdown-toggle > i');
		selector_icon.removeClass().addClass(selected_icon.attr('class'));
		
		// Check people with same emotions
		var emotion_icons = container.find('ul').find('i');
		updateEmotion(emotion_icons.index(selected_icon));
	});
	
	// Start chat when click ok
	$('#startChat').click(function(e) {
		$('#foundSameEmotionPrompt').modal('hide');
		startChat(chatWithUser);
	});
	
	// Post messages when chat form submitted
	$('#chatForm').submit(function(e) {
		e.preventDefault();
		var self = $(this);
		var input = self.find('input[name="message"]');
		var message = input.val();
		$.ajax({
			url: self.attr('action'),
			type: 'post',
			dataType:'json',
			data: {
				message: message,
			},
			success: function(returnobj) {
				var now = new Date();
				var now_str = now.format('H:M:m');
				messagesContainer.append(
					constructMessageElement(message, now_str, 'outgoing')
				);
				input.val('');
			}
		})
	})
})
