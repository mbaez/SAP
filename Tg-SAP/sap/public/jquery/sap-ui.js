$(function()
	{
		$('#dialog').dialog({
			autoOpen: false,
			width: 600,
			buttons: {
				"Ok": function() {
					$(this).dialog("close");
				},
				"Cancel": function() {
					$(this).dialog("close");
				}
			}
		});
		// Dialog Link
		$('#dialog_link').click(function(){
			$('#dialog').dialog('open');
			return false;
		});

	}
);
