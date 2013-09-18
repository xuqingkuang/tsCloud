$(document).ready(function(e) {
	$(".charms").click(function (e) {
		e.preventDefault();
		$('#charms').charms('showSection', 'theme-charms-section');
	});

	$('select[name="category_id"]').change(function(e) {
		$(this).parent('form').trigger('submit');
	});

	$('.image').fancybox({type: 'iframe', 'width': '480px'});
})
