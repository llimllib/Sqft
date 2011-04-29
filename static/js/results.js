$(document).ready(function(){
	
	function objLength (obj) {
		i=0;
		for (j in obj) ++i;
		return i;
	}	
	
	var myOpen = function(hash){
		if($(".jqmWindow:visible").length > 1){
			z = $(".jqmOverlay:last").css('z-index');
			hash.o.css('z-index', (z+2));
			hash.w.css('z-index', (z+3));
		}
		
		hash.w.css('left', ($(window).width() - hash.w.outerWidth()) / 2);
		// @todo maybe make this calculated again, rather than static?
		hash.w.css('top', 90);
		hash.w.fadeIn("normal");				
	};
	
	setMapHeight();		
	setListingsHeight();
	setSearchWidth();
	setSearchHeight();
	
	$(window).resize(function(){
		setMapHeight();
		setListingsHeight();
		setSearchWidth();
		setSearchHeight();
	});				
	
	$(".groupTitleBar > .floatLeft").click(function(){
		$(this).parent().next().toggle();
		var icon = $(this).children('span');
		
		if(icon.hasClass('ui-icon-triangle-1-e')){
			icon.removeClass('ui-icon-triangle-1-e').addClass('ui-icon-triangle-1-s');
		}
		else{			
			icon.removeClass('ui-icon-triangle-1-s').addClass('ui-icon-triangle-1-e');
		}
	});
	
	$(".groupTitleBar > .floatRight").click(function(){												   
		coords = $(this).children('a').attr('rel').replace(/[\(\)]/g, "");
		coords = coords.split(",");	
		gmap.panTo(new GLatLng(coords[0], coords[1]));
	});
	
	$("#edit_search").click(function(){
		$('#searchContainer').fadeIn("normal");
	});
	
	$("#searchContainer .closeModalBtn").click(function(){
		$('#searchContainer').fadeOut("normal");
	});	
	
	function setMapHeight(){
		$("#map").height($(window).height() - $("#header").outerHeight() - $("#footer").outerHeight(true));
	}		
	function setListingsHeight(){
		$("#resultsContainer").height($(window).height() - $("#header").outerHeight() - $("#footer").outerHeight(true) - $("#searchContainerStub").outerHeight() - $("#resultsHeader").outerHeight() + 2);
	}
	function setSearchWidth(){
		$("#searchContainer").width($("#resultsContainer").width());
	}
	function setSearchHeight(){
		$("#searchContainer").height($(window).height() - $("#header").outerHeight() - $("#footer").outerHeight(true) + 2);
	}		
});	