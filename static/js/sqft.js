$(document).ready(function(){
	$('.ui-state-default').hover(
		function() { $(this).addClass('ui-state-hover'); }, 
		function() { $(this).removeClass('ui-state-hover'); }
	);
	
	$('.closeModalBtn').hover(
		function() { $(this).removeClass('ui-state-active'); $(this).addClass('ui-state-hover'); }, 
		function() { $(this).removeClass('ui-state-hover'); $(this).addClass('ui-state-active'); }
	);
	
	$("#searchTab").click(function(){
		$('#searchContainer').fadeIn("normal");
	});
});

function objLength (obj) {
	i=0;
	for (j in obj) ++i;
	return i;
}

function createList(obj){
	var list = new Array();
	$.each(obj, function(i, el){
		$.each(el, function(j, val){
			list.push(val);
		});
	});
	return list;		
}

function buildTag(text, type, ID){
	return "<div class=\"tag ui-corner-all\" id=\"tag_"+ type +"_" + ID + "\"><a href=\"#\" class=\"ui-icon ui-icon-close floatLeft closeTag\"></a>" + text + "</div>";
}