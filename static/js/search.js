google.load('search' , '1');
google.load("jquery", "1.3.2");
google.load("jqueryui", "1.7.1");

function searchInterface(){
	/* Modals */
	var myOpen = function(hash){
		if($(".jqmWindow:visible").length > 0){
			z = parseInt($(".jqmOverlay:last").css('z-index'));
			console.log(hash.o.css('z-index', (z+2)));
			console.log(hash.w.css('z-index', (z+3)));
		}
		
		hash.w.css('left', ($(window).width() - hash.w.outerWidth()) / 2);
		hash.w.css('top', ($(window).height() -  hash.w.outerHeight()) / 2);
		hash.w.fadeIn("normal");
		if(hash.w.find("#map").length > 0){
			openMapModal();
		}				
	};
	
	function openMapModal(){
		gmap.checkResize();
		centerMapOnHood(neighborhoodData[0]);
		showHoodName(neighborhoodData[0].name);
		showHoodDesc(neighborhoodData[0]);
		updateColumnDisplay(pagerStart, getHoodDisplayCount());
		setRightColHeight();
	}
	
	var element;
	$('#nPrefsDialog').jqm({modal: true, trigger: '.nChooserLink', onShow: myOpen, closeClass: 'closeModalBtn'});
	$('#nPrefsDialog').jqmAddTrigger("#editPrefs");
	
	$('#nChooserDialog').jqm({modal: true, onShow: myOpen, closeClass: 'closeModalBtn'});
	$('#nChooserDialog').jqmAddClose('#editPrefs');
	$('#nChooserDialog').jqmAddClose('#explorerBtn');
	
	$('#hoodList').jqm({modal: true, trigger: '#hoodListBtn', onShow: myOpen, closeClass: 'closeModalBtn'});
	$('#hoodList').jqmAddClose('.nChooserLink');
	$('#hoodList').jqmAddClose('.finish');
	
	$('#featureList').jqm({modal: true, trigger: '#featureListBtn', onShow: myOpen, closeClass: 'closeModalBtn'});
	$('#featureList').jqmAddClose('.finish');
	
	$(".menu > span").live("click", function(){
		
		$(this).siblings(".areaHoods").toggle();
		
		if($(this).parent().hasClass("open")){
			$(this).parent().removeClass("open");
		}
		else{
			$(this).parent().addClass("open");			
		}
	});
	
	$(".hoodMenuLink").click(function(event){		
		if($(this).hasClass("menuSelected")){
			$(this).removeClass("menuSelected");
			var hood_id = $(this).attr('id').replace('menu_hood_', '');
			$("#tag_hood_"+hood_id).remove();
		}
		else{
			var html = buildTag($(this).text(), 'hood', $(this).attr('id').replace('menu_hood_', ''));
			$("#selectedHoods").append(html);
			$(this).addClass("menuSelected");
		}
	});		
	
	$(".featureMenuLink").click(function(event){
		if($(this).hasClass("menuSelected")){
			$(this).removeClass("menuSelected");
			var feature_id = $(this).attr('id').replace('menu_feature_', '');
			$("#tag_feature_"+feature_id).remove();
		}
		else{
			var html = buildTag($(this).text(), 'feature', $(this).attr('id').replace('menu_feature_', ''));
			$("#selectedFeatures").append(html);
			$(this).addClass("menuSelected");
		}
	});
	
	/* Auto-complete */
	$("#hoodInput").autocomplete(hoodList, {
		multiple: true,
		mustMatch: true,
		autoFill: true,
		formatItem: function(row, i, max) {
			return row.name;
		},
		formatMatch: function(row, i, max) {
			return row.name;
		},
		formatResult: function(row) {
			return row.name;
		},
		width: 160
	});
	
	$("#hoodInput").result(function(event, data, formatted) {
		if($("#tag_hood_"+data.neighborhood_id).length == 0){
			var html = buildTag(formatted, 'hood', data.neighborhood_id);
			$("#selectedHoods").append(html);
			$("#menu_hood_"+data.neighborhood_id).addClass("menuSelected");
		}
		$("#hoodInput").val("");
	});
	
	$("#featureInput").autocomplete(featureList, {
		multiple: true,
		mustMatch: true,
		autoFill: true,
		formatItem: function(row, i, max) {
			return row.name;
		},
		formatMatch: function(row, i, max) {
			return row.name;
		},
		formatResult: function(row) {
			return row.name;
		},
		width: 160
	});
	
	$("#featureInput").result(function(event, data, formatted) {
		if($("#tag_feature_"+data.feature_id).length == 0){	
			var html = buildTag(formatted, 'feature', data.feature_id);
			$("#selectedFeatures").append(html);
			$("#menu_feature_"+data.feature_id).addClass("menuSelected");
		}
		$("#featureInput").val("");
	});
	
	$(".selectedTagsContainer").click(function(){
		$(this).children(".tagInput").focus();
	});			

	$(".closeTag").live("click", function(){
		var hood_id = $(this).parent().attr('id').replace('tag_hood_', '');
		$("#menu_hood_"+hood_id).removeClass("menuSelected");
		$(this).parent().remove();
	});
	
	/* Price Slider */
	$("#priceSlider").slider({range: true,
		min: 0,
		max: 6000,
		step: 50,
		values: [$("#priceFloor").val(), $("#priceCeiling").val()],
		slide: function(event, ui) {
			if(ui.values[1] == 6000){
				over = '+';
			}
			else{
				over = '';
			}
			
			$("#priceFloor").val(ui.values[0]);
			$("#priceCeiling").val(ui.values[1]);
		}
	});
	
	$("#priceFloor").blur(function(event){
		$("#priceSlider").slider('values', 0, $(this).val());
		checkRange($("#priceSlider"), $(this));
	});
	
	$("#priceCeiling").blur(function(event){	
		$("#priceSlider").slider('values', 1, $(this).val());
		checkRange($("#priceSlider"), $(this));
	});	
	
	function checkRange(slider, input){
		if(input.val() < slider.slider('option', 'min')){
			input.val(slider.slider('option', 'min'));
		}
		
		if(input.val() >= slider.slider('option', 'max')){
			input.val(slider.slider('option', 'max') + '+');
		}
	}		

	/* Form submission */
	$("#searchForm").submit(function(){
		var ids = new Array();
		$.each($("#selectedHoods").children(".tag"), function(){
			ids.push($(this).attr('id').replace('tag_hood_', ''));
		});
		$("#neighborhoods").val(ids.toString());
		
		var feature_ids = new Array();
		$.each($("#selectedFeatures").children(".tag"), function(){
			feature_ids.push($(this).attr('id').replace('tag_feature_', ''));
		});
		$("#features").val(feature_ids.toString());
	});
	
	/**************************************************/
	
	/* Preferences */
	$(".preference").click(function(){
		$(this).toggleClass('pSelected');
	});
	
	$(".extra").click(function(){
		if($(this).hasClass("expanded")){
			$(this).children("div").fadeOut("normal");
			$(this).removeClass("expanded");
			removeError($(this));
		}
		else{
			$(this).addClass("expanded");
			$(this).children("div").fadeIn("normal", function(){
				$(this).find("input").focus();
			});
		}
	});
	
	/* Ensures that a click event isn't fired on the parent div, deselecting the preference*/
	$(".extraInput").click(function(event){
		event.stopPropagation();
	});		
	
	$(".geocode").blur(function(event){
		var geocoder = new GClientGeocoder();
		element = $(this);
		
		if($(this).val().length != 0){
			geocoder.getLatLng($(this).val(), function(point){
				if(!point){
					element.parents(".extra").addClass("prefError");
					$("#prefsErrorMessage").fadeIn("normal");
				}
				else{
					removeError(element.parents(".extra"));		
				}
			});
		}
		else{
			removeError($(this).parents(".extra"));	
		}
		
	});
	
	function removeError(element){
		if(element.hasClass("prefError")){
			element.removeClass("prefError");
			if(!stillErrors()){
				$("#prefsErrorMessage").fadeOut("normal");
			}
		}	
	}
	
	function stillErrors(){
		if($(".prefError").size() != 0){
			return true;	
		}
		else{
			return false;	
		}
	}	
	
	function submitPrefs(){
		if(stillErrors()){
			$("#prefsErrorMessage").effect('pulsate', {times: 2});
		}
		else{
			/* @todo toggle a waiting animation, send preferences to server, 
			   then launch the next modal when the neighborhood data comes back*/
			$("#nPrefsDialog").jqmHide();
			$("#nChooserDialog").jqmShow();
		}	
	}
	
	
	/* wait a little bit to ensure that the geocoder can do its job if the user submits
	 right after typing in an address */
	$("#submitPrefs").click(function(){
		setTimeout(submitPrefs, 200);
	});
	
	
	/**************************************************/
	/* Neighborhood Explorer */

	/* Initialization */
	pagerStart = 0;
	$.each(neighborhoodData, function(i, el){
		$("#hoodContainer").append(buildHood(el));
	});	
	$(".hood:first").addClass("detailed");
	/* End Init */
	
	
	$(window).resize(function(){
		updateColumnDisplay(pagerStart, getHoodDisplayCount());
		setRightColHeight();
	});
		
	$(".hood").live("click", function(){
		$(".detailed").removeClass("detailed");
		$(this).addClass("detailed");
		showHoodName(neighborhoodData[$(".hood").index($(this))].name);
		showHoodDesc(neighborhoodData[$(".hood").index($(this))]);
		centerMapOnHood(neighborhoodData[$(".hood").index($(this))]);				
	});
	
	$(".hood input").live("click", function(){
		if($(this).attr('checked')){
			$(this).parent().addClass('selected');
			updateBottomBarHoods();
		}
		else{
			$(this).parent().removeClass('selected');
			updateBottomBarHoods();
		}
	});
	
	$("#prev").click(function(){
		if(pagerStart != 0){
			count = getHoodDisplayCount();
			pagerStart = (pagerStart - count < 0) ? (0) : (pagerStart - count);
			updateColumnDisplay(pagerStart, count);
		}
	});
	
	$("#next").click(function(){		
		count = getHoodDisplayCount();
		if(pagerStart + count < neighborhoodTotal){
			if($(".hood").length - pagerStart <= 20){				
				$.getJSON("/search/page_hoods?start=" + $(".hood").length + "&count=20", function(data){
					$.each(data, function(i, el){
						neighborhoodData.push(el);
						$("#hoodContainer").append(buildHood(el));
					});
					
					pagerStart += count;
					updateColumnDisplay(pagerStart, count);
				});
			}
			else{
				pagerStart += count;
				updateColumnDisplay(pagerStart, count);
			}
		}
	});
			
	$("#explorerBtn").click(function(){
		$.each($(".hood input:checked"), function(){
			var html = buildTag($(this).next().children(".hoodName").text(), 'hood', $(this).val());
			$("#selectedHoods").append(html);
			$("#menu_hood_"+$(this).val()).addClass("menuSelected");
		});
	});
	
	function setRightColHeight(){
		$("#rightColumn").height($("#nChooserDialog").innerHeight() - $("#nChooserDialog .bottomBar").outerHeight() - 50);
	}
	
	/* Determine how many hoods we can display in the modal window. Take the window height, 
	subtract the height of the bottom bar and the intro text above the hoods, then divide by 
	hood display height. */
	function getHoodDisplayCount(){	
		/* @todo This is ugly as hell, but the old approach was returning 0 because position
		   isn't calculated until the modal is displayed, and the timing is weird */
		// start = $(".hood:first").position().top;
		
		start = 113;
		colHeight = $("#nChooserDialog").innerHeight() - $("#bottomBar").outerHeight() - $("#pagerContainer").outerHeight();		
		var stack = 0;
		var theCount = 0;
		
		$.each($(".hood"), function(i, el){
			stack += $(this).outerHeight();
			if(stack > colHeight - start){
				theCount = i - 1;
				return false;
			}
		});
		
		return theCount;
	}
	
	/* Since the explorer is modal, and we're not supporting scrolling for the neighborhood 
	column, we need to ensure that only display the number of neighborhoods that can fit 
	vertically in the window. */
	function updateColumnDisplay(start, count){
		$(".hood").hide();
		$.each($(".hood"), function(i, el){
			if(i >= start && i < start + count){
				$(this).show();
			}
		});
		$("#hoodPage").text((start+1) + "-" + ((start+count > neighborhoodTotal) ? (neighborhoodTotal) : (start+count))  + " of " + neighborhoodTotal);
	}
	
	
	function buildHood(data){	
		return '<div class="hood" id="'+data.neighborhood_id+'"><input type="checkbox" name="hoods[]" value="'+data.neighborhood_id+'" class="floatLeft" /> <div class="floatLeft hoodText"><a href="#" class="hoodName">'+data.name+'</a> <span class="smallGray"><strong> - '+data.unitCount+' Units</strong></span><br /><span class="smallGray">Avg. 1BR - $'+data.oneBrMedian+' | 2BR - $'+data.twoBrMedian+'</span></div></div>';	
	}
	
	function showHoodName(name){
		$("#rightColumn > h1.colTitle").text(name);
	}
	
	function showHoodDesc(data){
		$("#hoodDesc").html("<h2>A little bit about "+data.name+"</h2>"+data.description);
		
		$.getJSON("/search/hood_pics?hood_id=" + data.neighborhood_id, function(fData){
			$("#hoodDesc").append("<h2>"+data.name+" Photos</h2>");
			$("#hoodDesc").append("<ul class=\"flickrHoodGallery gallery_demo\">");
			$.each(fData, function(i, el){
				$("ul.flickrHoodGallery").append('<li><img class="hoodFlickrPhoto" src="'+el+'" /></li>');
			});
			$("#hoodDesc").append("</ul>");	
			
			$('ul.flickrHoodGallery').galleria({clickNext : false});
		});
				
		
	}
	
	function updateBottomBarHoods(){
		var hoods = new Array();
		$.each($(".hood input:checked"), function(){
			hoods.push($(this).next().children(".hoodName").text());
		});
		
		$("#selectedNeighborhoods").text(hoods.join(", "));
		$("#selectedNeighborhoods").effect("highlight");
	}	
}

google.setOnLoadCallback(searchInterface);