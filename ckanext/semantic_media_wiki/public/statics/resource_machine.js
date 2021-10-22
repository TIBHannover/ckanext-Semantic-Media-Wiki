$(document).ready(function(){
    $.ajax({
        url: $('#get_link_url').val(),
        cache:false,   
        dataType: 'json',      
        type: "GET",
        success: function(result){
            if(result == '0'){
                $('#machine_link_box').hide();
            }
            else{
                $('#machine_url_anchor').attr('href', result[0]);
                $('#machine_url_anchor').text(result[0]);

            }            
        }
    });



});

