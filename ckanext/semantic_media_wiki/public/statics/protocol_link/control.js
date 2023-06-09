$(document).ready(function(){
    
    $('#protocol-add-form').submit(function(e){        
        let protocol_name = $('#protocol_name');
        let protocol_url = $('#protocol_url');
        if(protocol_name.val() === ''){
            protocol_name.css('border', '2px solid red');
            $('#protocol_add_alert_box').show();
            e.preventDefault();

        }
        if(protocol_url.val() === ''){
            protocol_url.css('border', '2px solid red');
            $('#protocol_add_alert_box').show();
            e.preventDefault();
        }
    });



    $('#protocol_name').keydown(function(){
        $('#protocol_add_alert_box').hide();
        $(this).css('border', '');        
    });

    $('#protocol_url').keydown(function(){
        $('#protocol_add_alert_box').hide();        
        $(this).css('border', '');
    });



});