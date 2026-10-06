$(document).ready(function(){
    let dest_url = $('#dataset_id_for_sample').val();
    get_resource_link($('#samplesTableRow') ,dest_url);
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
                    block += build(result[i][0], result[i][1], result[i][2]);
                }
                $(target).append(block);
                $('.sample-link').fadeIn();
            }           
        }
    });
}

function build(url, name, exists){
    let sampleName = '<div class="sample-name-tag">' + name + '</div>';
    if (!exists) {
        return '<span class="sample-link-unavailable">' + sampleName + '</span>';
    }
    let anchor = '<a href="' + url + '" target="_blank" class="sample-link">' + sampleName + '</a>';
    return '<span>' + anchor + '</span>';

}
