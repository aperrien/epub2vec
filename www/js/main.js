var initHighlightAPI = function(jq) {
	/*
	 * jQuery Highlight plugin
	 *
	 * Based on highlight v3 by Johann Burkard
	 * http://johannburkard.de/blog/programming/javascript/highlight-javascript-text-higlighting-jquery-plugin.html
	 *
	 * Copyright (c) 2009 Bartek Szopka
	 *
	 * Licensed under MIT license.
	 *
	 */

	jq.extend({
			// TODO make this work even if the <p> node includes styles, links or other spans interrupting the text
	    highlight: function (node, re, nodeName, className) {
	        if (node.nodeType === 3) {
	            var match = node.data.match(re);
	            if (match) {
	                var highlight = document.createElement(nodeName || 'span');
	                highlight.className = className || 'highlight';
	                var wordNode = node.splitText(match.index);
	                wordNode.splitText(match[0].length);
	                var wordClone = wordNode.cloneNode(true);
	                highlight.appendChild(wordClone);
	                wordNode.parentNode.replaceChild(highlight, wordNode);
	                return 1; //skip added node in parent
	            }
	        } else if ((node.nodeType === 1 && node.childNodes) && // only element nodes that have children
	                !/(script|style)/i.test(node.tagName) && // ignore script and style nodes
	                !(node.tagName === nodeName.toUpperCase() && node.className === className)) { // skip if already highlighted
	            for (var i = 0; i < node.childNodes.length; i++) {
	                i += jq.highlight(node.childNodes[i], re, nodeName, className);
	            }
	        }
	        return 0;
	    }
	});

	jq.fn.unhighlight = function (options) {
	    var settings = { className: 'highlight', element: 'span' };
	    jq.extend(settings, options);

	    return this.find(settings.element + "." + settings.className).each(function () {
	        var parent = this.parentNode;
	        parent.replaceChild(this.firstChild, this);
	        parent.normalize();
	    }).end();
	};

	jq.fn.highlight = function (words, options) {
	    var settings = { className: 'highlight', element: 'span', caseSensitive: false, wordsOnly: false };
	    jq.extend(settings, options);

	    if (words.constructor === String) {
	        words = [words];
	    }
	    words = jq.grep(words, function(word, i){
	      return word != '';
	    });
	    words = jq.map(words, function(word, i) {
	      return word.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&");
	    });
	    if (words.length == 0) { return this; };

	    var flag = settings.caseSensitive ? "" : "i";
	    var pattern = "(" + words.join("|") + ")";
	    if (settings.wordsOnly) {
	        pattern = "\\b" + pattern + "\\b";
	    }
	    var re = new RegExp(pattern, flag);

	    return this.each(function () {
	        jq.highlight(this, re, settings.element, settings.className);
	    });
	};
};

var deepLink = function(target,book,link, $button) {
	var iFrame = "<iframe id='bookFrame' src='epub-output/" + book + "/" + link + "' frameborder=0 />";
	$(target).html(iFrame);
	$(target + ' iframe').css('width','100%');
	$(target + ' iframe').css('height','100%');
	var iFrameWindow= document.getElementById('bookFrame').contentWindow;

	var $parent = ($($button.parent()).parent());
	var textNode = $parent.children()[3];
	var text = $(textNode).text();

	var loadiFramejQuery = function(iFrameWindow) {
			var iFramejQuery = iFrameWindow.$;
			if (typeof iFramejQuery == 'undefined') {
				var s = iFrameWindow.document.createElement("script");
				s.type = "text/javascript";
				s.src = "/www/js/jquery.min.js";
				s.onload = function() {
					iFramejQuery = iFrameWindow.$;
					initHighlightAPI(iFramejQuery);
					$('body').unhighlight(currentHighlight);
					iFramejQuery('body').unhighlight(currentHighlight);
					currentHighlight = text;
					$('body').highlight(text);
					iFramejQuery('body').highlight(text);
					iFramejQuery('.highlight').css('background-color','yellow');
					iFramejQuery('body').scrollTop(
					    iFramejQuery('.highlight').offset().top - iFramejQuery('body').offset().top + iFramejQuery('body').scrollTop() - 250
					);
				};
				iFrameWindow.document.head.appendChild(s);
			}
	};

	setTimeout(function(){
		loadiFramejQuery(iFrameWindow);
	}, 500);

}

var currentHighlight = "";
var currentCluster = $('.clusterPicker').val();
var clusterData = {};
$('.activeCluster span').text($('.clusterPicker').val());

var updateActiveCluster = function() {
	currentCluster = $('.clusterPicker').val();
	$('.activeCluster span').text($('.clusterPicker').val());
	$('.clusterTable').children().remove();
	for (i in clusterData.data) {
		var cluster = clusterData.data[i][0];
		var book = clusterData.data[i][1];
		var location = clusterData.data[i][2];
		var text = clusterData.data[i][3];
		if (cluster == currentCluster) {
			$('.clusterTable').append('<tr><td><div class="openMe" data-book=' + book + ' data-location=' + location + '>Open</div></td><td>' + cluster + '</td><td>' + book + '</td><td class="text">' + text + '</td></tr>');
		}
	}
	$('.openMe').bind('click',function() {
		var $this = $(this);
		deepLink('.bookviewer',$(this).attr('data-book'),$(this).attr('data-location'),$this);
	});
};

var loadClusters = function(clusterCSV) {
	Papa.parse('clusters/' + clusterCSV, {
		download: true,
		complete: function(results) {
			clusterData = results;
			updateActiveCluster();
			$('.value').bind('click',function() {
				updateActiveCluster();
			});
			$('.next').bind('click',function() {
				var currentVal = Math.floor($('.clusterPicker').val());
				$('.clusterPicker').val(currentVal + 1);
				updateActiveCluster();
			});
			$('.prev').bind('click',function() {
				var currentVal = Math.floor($('.clusterPicker').val());
				$('.clusterPicker').val(currentVal - 1);
				updateActiveCluster();
			});
		}
	});
};

$(document).ready(function() {
	$('.results').hide()
	initHighlightAPI($);
	$.get('clusters/available-clusters.txt',function(data){
		var files = data.split("\n");
		files.map(function(file){
			$('.filelist').append("<div class='filename'>" + file + "</div>");
		});
		$('.filename').bind('click',function() {
			loadClusters($.trim($(this).text()));
			$('.resultPicker').hide();
			$('.results').show();
		});
	});
});
