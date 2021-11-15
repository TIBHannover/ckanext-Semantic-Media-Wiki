$(document).ready(function(){
    let dest_url = $('#dataset_id_for_machine').val();
    get_resource_link($('#machinesTableRow') ,dest_url);

});

function get_resource_link(target, url){    
    $.ajax({
        url: url,
        cache:false,   
        dataType: 'json',     
        type: "GET",
        success: function(result){            
            if(result !== '0'){
                let block = ''; 
                for (let i=0; i < result.length; i++){
                    block += build(result[i][0], result[i][1]);
                }
                $(target).append(block);
                $('.machine-link').fadeIn();
            }           
        }
    });
}

function build(url, name){
    let machineName = '<div class="machine-name-tag">' + name + '</div>';
    let anchor = '<a href="' + url + '" target="_blank" class="machine-link">' + machineName + '</a>';
    return '<span>' + anchor + '</span>';

}