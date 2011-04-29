google.load('search' , '1');
google.load("jquery", "1.3.2");
google.load("jqueryui", "1.7.1");

function loadRental(){
	
	var myOpen = function(hash){
		hash.w.css('left', ($(window).width() - hash.w.outerWidth()) / 2);
		hash.w.css('top', 90);
		hash.w.fadeIn("normal");
	};
	
	$('ul.rental_gallery').galleria({clickNext : false, history: false});
	
	$('#contactManagerForm').jqm({modal: true, trigger: '#contactLandlordBtn', onShow: myOpen, closeClass: 'closeModalBtn'});
	$('.jqmWindow').jqmAddClose('.modalCancel');
}

google.setOnLoadCallback(loadRental);
	
