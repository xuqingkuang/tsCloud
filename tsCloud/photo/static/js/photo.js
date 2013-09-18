var Photo = {};

// Global variables
Photo.locked = false;
Photo.timestamp = 0;
Photo.gallery = null;

// Functions
Photo.generateThumbHTML = function(json) {
	var a = $('<a>')
		.attr('href', json.extras.get_absolute_url)
		.attr('title', json.fields.create_time)
		.addClass('tile square image new');
	$('<img>')
		.attr('src', json.extras.get_square_url)
		.attr('alt', json.fields.desc)
		.appendTo(a);
	a.fancybox({type: 'iframe', 'width': '800px'});
	return a;
}

Photo.updatePage = function(returnobj) {
	// Nothing updated
	if (returnobj.rc == 2)
		return false;

	 // Error handler
	if (returnobj.rc == 1) {
		alert(returnobj.msg);
		return false;
	}
	if (returnobj.data && returnobj.data != '') {
		Photo.timestamp = -5;
		Photo.locked = true;
		var objects = jQuery.parseJSON(returnobj.data);
		for (var i = 0; (obj = objects[i]); i++) {
			var html = Photo.generateThumbHTML(obj);
			$('#container-fluid > div.row-fluid').prepend(html);
		}
		Photo.locked = false;
	}
}

Photo.intervalCheck = function() {
	new jQuery.ajax({
		url: 'api/check/',
		method: 'get',
		async: false,
		dataType:'json',
		data: {
			timestamp: Photo.timestamp
		},
		success: Photo.updatePage
	});
}

Photo.timestampUpdater = function() {
	if (Photo.timestamp > 3 && Photo.timestamp % 8 == 0 && Photo.locked == false) {
		Photo.intervalCheck();
	}
	Photo.timestamp = Photo.timestamp + 1;
}

Photo.onLoad = function() {
	$(".charms").click(function (e) {
		e.preventDefault();
		$('#charms').charms('showSection', 'theme-charms-section');
	});
	$('.image').fancybox({type: 'iframe', 'width': '800px'});
	setInterval(Photo.timestampUpdater, 1000);
}
