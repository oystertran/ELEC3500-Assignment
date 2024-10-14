HTTP/1.1 200 OK
Date: Sun, 13 Oct 2024 14:34:19 GMT
Server: Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/7.4.33 mod_perl/2.0.11 Perl/v5.16.3
Last-Modified: Mon, 19 Jul 2021 15:35:17 GMT
ETag: "3aa-5c77baf269740"
Accept-Ranges: bytes
Content-Length: 938
Content-Type: application/javascript

// Set navbar button active when linked
$(document).ready(function() {
	var path = $(location).attr('pathname').split('/').pop();
	$('.nav-item a').each(function() {
		if($(this).attr('href') == path) {
			$(this).parent().addClass('active');
		}
		else if(path == '' && $(this).attr('href') == 'index.php') { // index page
			$(this).parent().addClass('active');
		}
	});
	$('.dropdown-item').each(function() {
		if($(this).attr('href') == path) {
			$(this).parent().parent().addClass('active');
		}
	});
});

// Makes dropdowns maintain their color-scheme when a menu-entry is clicked
$(document).on('focus', '.dropdown-item', function() {
	$(this).parent().prev().css('color', '#FFFFFF');
	$(this).parent().prev().css('border-color', '#FFFFFF');
	$(this).parent().prev().css('background-color', '#840E0E');
});

$(document).on('mouseup', '.dropdown-item', function() {
	$(this).parent().prev().css('background-color', '#9c1207');
});
