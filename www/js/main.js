var deepLink = function(target,book,link) {
	var iFrame = "<iframe src='epub-output/" + book + "/OEBPS/xhtml/" + link + "' frameborder=0 />";
	console.log(iFrame);
	$(target).html(iFrame);
	$(target + ' iframe').css('width','100%');
	$(target + ' iframe').css('height','100%');
}

var currentHighlight = "";

$(document).ready(function() {
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
				deepLink('.bookviewer',$(this).attr('data-book'),$(this).attr('data-location'));
				var $parent = ($($this.parent()).parent());
				var textNode = $parent.children()[3];
				var text = $(textNode).text();
				$('body').unhighlight(currentHighlight);
				currentHighlight = text;
				$('body').highlight(text);
			});
		}
	});
});
