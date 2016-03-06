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
	var iFrame = "<iframe id='bookFrame' src='epub-output/" + book + "/OEBPS/xhtml/" + link + "' frameborder=0 />";
	$(target).html(iFrame);
	$(target + ' iframe').css('width','100%');
	$(target + ' iframe').css('height','100%');
	var iFrameWindow= document.getElementById('bookFrame').contentWindow;

	var $parent = ($($button.parent()).parent());
	var textNode = $parent.children()[3];
	var text = $(textNode).text();

	setTimeout(function(){
		var iFramejQuery = iFrameWindow.$;
		initHighlightAPI(iFramejQuery);
		$('body').unhighlight(currentHighlight);
		iFramejQuery('body').unhighlight(currentHighlight);
		currentHighlight = text;
		$('body').highlight(text);
		iFramejQuery('body').highlight(text);
		iFramejQuery('.highlight').css('background-color','yellow');
	}, 150);

}

var currentHighlight = "";

$(document).ready(function() {
	initHighlightAPI($);
	Papa.parse('clusters/1457125504_cluster_output.csv', {
		download: true,
		complete: function(results) {
			for (i in results.data) {
				var cluster = results.data[i][0];
				var book = results.data[i][1];
				var location = results.data[i][2];
				var text = results.data[i][3];
				if (cluster == 4) {
					$('.clusterTable').append('<tr><td><div class="openMe" data-book=' + book + ' data-location=' + location + '>Open</div></td><td>' + cluster + '</td><td>' + book + '</td><td class="text">' + text + '</td></tr>');
				}
			}

			$('.openMe').bind('click',function() {
				var $this = $(this);
				deepLink('.bookviewer',$(this).attr('data-book'),$(this).attr('data-location'),$this);
			});
		}
	});
});
