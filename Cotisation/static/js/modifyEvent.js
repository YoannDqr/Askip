var nombreImage = 0;
var nombreCase = 0;
var settingsPointer = false;
var deletePointer = false
$(document).ready(function(){


    $("#photo-event").css('height', $(window).height()/2).css('min-height', $(window).height()/2);
    $("#content-event").css('min-height', $(window).height()/2);
    $("#photo-event>h1").css('transform','translate(0px,' + $('#photo-event').height()/2 + 'px)');

    $("#photo-event").click(() => $("input[type='file']").click());
    $("form#event-form>input[type='file']").change(() => $("#event-form").submit());


    $("select[name='taille_zone']").change( caseDisposition );

    $(".content-description").hover(
        function(){
            $(this.firstElementChild).slideDown();
            //$(this.firstElementChild).css('display','block');
            $(this.firstElementChild).next().css('opacity','0.33');
            const pk = $(this).attr('pk');
            const parentRow = $('div.row.description[pk=' + pk + ']');
            parentRow.attr('support-delete', 'false');

        },
        function(){
            $(this.firstElementChild).slideUp();
            $(this.firstElementChild).next().css('opacity','1');

            //$('textarea.change-text').css('display','none');
            //$('input.change-position').css('display','none');
            //$('button.validate').css('display','none');
        });

    $('div.row.description').hover(
        function(){
            const firstChild = $(this.firstElementChild);
            firstChild.attr('support-delete', 'true');
            if(!deletePointer) {
                firstChild.confirm({
                    title: 'Supprimer la sélection',
                    content: 'Est-vous sur de supprimer tout la ligne ?<br> Le contenu sera perdu',
                    buttons: {
                        confirm: () => deleteRow(this),
                        cancel: () => {
                        },
                    },
                });
                deletePointer = true;
            }

            const secondChild = firstChild.next();
            secondChild.attr('support-delete', 'true');
            if(!settingsPointer) {
                settingsPointer = true;
                secondChild.click(changeRowSettings);
            }

        },
        function(){
            const firstChild = $(this.firstElementChild);
            firstChild.attr('support-delete', 'false');
            firstChild.next().attr('support-delete', 'false');
        }
    );

    $("button.change-img").click(function(){
        modifyContent($(this).attr('pk'), 'img');
    });
    $("button.change-text").click(function(){
        modifyContent($(this).attr('pk'), 'text');
    });
    $("button.change-position").click(function(){
        modifyContent($(this).attr('pk'), 'position');
    });
    $("button.change-css").click(function(){
        modifyContent($(this).attr('pk'), 'css');
    });

    $('input.change-img').change(function(){
        const id = $(this).attr('pk');
        $("form[pk='" + id + "']").submit();
    });

    rowDescriptionHeight();
});

function changeRowSettings(){
    /*
     * Function called when the settings button related to a whole row is clicked.
     * Will show the formular used to create a brand new rows and add an input to tell the server
     * what row has been modified.
     */

    const id = $(this).attr('pk');

    const htmlButton = "<div class='form-group btn-modify' style='display:none;'>" +
                            "<button class='btn btn-default'" +
                                    "onclick='addHtmlTextInput(" + id + ")'>" +
                                "Modifier la ligne"+
                            "</button>" +
                       "</div>";
    $('#button').html(htmlButton);
    $($('.add-logo')[0]).click();
}

function addHtmlTextInput(id){
    const htmlInput = "<input type='hidden' name='modify_row' value='" + id + "'>";
    $('#add-content-form').append(htmlInput);
    $('#add-content-form').submit();
}


function deleteRow(elt){
    console.log(elt);
    $.ajax({
            method: "POST",
            url: "/cotisation/modify/evennement/delete_description/",
            data: {id:$(elt).attr('pk'), csrfmiddlewaretoken: $("#csrf_token").text()}
        })
        .done(function() {
            $(elt).remove();
        });
}

function caseDisposition(){
    /*
     * Delete all previous input.
     * If the number of case is lower than 3, then give to the user the possibility to give the position of
     * the different blocks.
     * If the number of case is equal to three, then just apply the imageNumber function.
     * If the number of case is equal to three, then just apply the imageNumber function.
     */

    $("form#add-content-form>div.case-disposition").remove();
    $("form#add-content-form>div.nombre-image").remove();
    $("form#add-content-form>div.add-image").remove();
    $("form#add-content-form>div.choix-text").remove();
    $("form#add-content-form>div.add-position").remove();
    $("form#add-content-form>div.choix-text-checkbox").remove();
    $("form#add-content-form>div.btn-submit").remove();
    $("form#add-content-form>div.btn-modify").css('display', 'none');


    nombreCase = this.value;
   
    var htmlOption = "<option value='NC'>Disposition des cases</option>";
    if(nombreCase == 1){
        htmlOption += "<option value='gauche'>Gauche</option>"        +
                             "<option value='centre'>Centre</option>" +
                      "<option value='droite'>Droite</option>";
    }
    else if(nombreCase == 2){
        htmlOption += "<option value='gauche'>Gauche</option>"        +
                      "<option value='droite'>Droite</option>";
    }

    if(nombreCase != 3 && nombreCase != 'NC'){
        var htmlSelect = "<div class='form-group case-disposition'>"    +
                            "<select name='case_disposition'"           +
                                    "class='form-control'"              +
                                    "onchange='imageNumber()'>"         +
                                htmlOption                              +
                            "</select>"                                 +
                      "</div>";
        $('form#add-content-form').append(htmlSelect);
    }
    else{
        imageNumber();
    }

}


function imageNumber() {
    /*
     * Delete all olders inputs in the modal and display inputs for image number
     */

    $("form#add-content-form>div.nombre-image").remove();
    $("form#add-content-form>div.add-image").remove();
    $("form#add-content-form>div.choix-text").remove();
    $("form#add-content-form>div.add-position").remove();
    $("form#add-content-form>div.choix-text-checkbox").remove();
    $("form#add-content-form>div.btn-submit").remove();
    $("form#add-content-form>div.btn-modify").css('display', 'none');
    var value = nombreCase;

    var htmlOption = "<option value='NC'> Nombre d'image </option>";
    for (var i = 0; i <= value; i++) {
        htmlOption += "<option value='" + i + "'>" + i + " image</option>";
    }
    var htmlSelect = "<div class='form-group nombre-image'>"                        +
                        "<select onchange='imagePosition(this.value)'"              +
                                "class   ='form-control'"                           +
                                "name    ='nombre_image'>" + htmlOption             +
                        "</select>"                                                 +
                    "</div>";

    if (value != "NC") {
        $("form#add-content-form").append(htmlSelect)
    }
}

function imagePosition(value){
    /*
     * Delete old select input related to image position.
     * Display file input for images as well as input for images' positionning.
     * Display text input. The number of text input avalaible is 'value' - 3.
     */

    $(".add-image").remove();



    nombreImage = value;

    /*
     * Option for select related to image positionning.
     */
    var htmlPosition = "<option value='gauche'>Gauche</option>"   +
                    "<option value='centre'>Centre</option>"      +
                    "<option value='droite'>Droite</option>";

    /*
     * Display the select input for image positionning.
     */
    for(var i = 1; i <= value; i++){

        var htmlSelect = "<div class='form-group add-image'>"+
                                "<select class='form-control position-image' name='position_image_" + i + "'>"  +
                                        "<option value='NC'> Position de l'image " + i + "</option> "           +
                                        htmlPosition                                                            +
                                "</select>"                                                                     +
                                "<input type='file' name='image_" + i + "'/>"                                   +
                         "</div>";
        $("form#add-content-form").append(htmlSelect);
    }

    /*
     * Display text inputs
     */
    displayTextInput(value, false);
    $(".btn-modify").css('display', 'block');
    htmlPosition = '<div class="form-group add-position">'                                  +
                        '<label>Position de la ligne</label>'                               +
                        '<input class="form-control" name="position_row" type="number">'    +
                    '</div>' +
                    "<div class='form-group btn-submit'>"+
                           "<button type='submit' class='btn btn-default'> Créer une nouvelle ligne </button>"+
                     "</div>";
    $("form#add-content-form").append(htmlPosition);
}

function displayTextInput(value, fusionText){
    /*
     * Display text input. The number of text input avalaible is 'value' - 3.
     */
    $(".choix-text").remove();
    $(".add-position").remove();
    $(".choix-text-checkbox").remove();
    $(".btn-submit").remove();
    $(".btn-modify").css('display', 'none');
    var htmlTextInput = "";
    var label = "";
    for(var i = 1; i <= nombreCase - value; i++){
        if(fusionText){
            label = "Fusionné";
        }
        else{
            label = i;
        }
        htmlTextInput += "<div class='form-group choix-text'>" +
                            "<label>Texte " + label + "</label>" +
                            "<textarea class='form-control' name='text_" + i + "'></textarea>" +
                          "</div>";
    }

    if( nombreCase - value > 1 || fusionText) {
        /*
         * Possibility to merge all text input in one.
         */
        htmlTextInput += "<div class='form-group choix-text-checkbox'>" +
                            "<label>Fusionner les zones de textes</label>" +
                            "<input type='checkbox' " +
            "                       id='fusion-text' " +
            "                       name='fusion' " +
            "                       value='1' " +
            "                       onchange='fusionZoneText()'";
        if(fusionText){
            htmlTextInput += " checked=''";
        }
        htmlTextInput += "/></div>";

    }

    $("form#add-content-form").append(htmlTextInput);
}

function fusionZoneText(){
    /*
     * Merge all the text inputs.
     */
    var value = $("#fusion-text").prop("checked");
    $('.btn-submit').remove();
    $('.btn-modify').css('display', 'none');
    if(value){
        displayTextInput(nombreCase-1, true);
    }
    else{
        displayTextInput(nombreImage, false);
    }

    let htmlTextInput = '<div class="form-group add-position">'                                   +
                        '<label>Position de la ligne</label>'                                       +
                        '<input class="form-control" name="position_row" type="number">'            +
                    '</div>'                                                                        +
                    "<div class='form-group btn-submit'>"                                           +
                           "<button type='submit' class='btn btn-default'> Créer une nouvelle ligne </button>"       +
                     "</div>";

    $(".btn-modify").css('display', 'block');
    $("form#add-content-form").append(htmlTextInput);


}

function modifyContent(id, type){
    /*
     * Modifies the content of the row description related to the pk id.
     * Type argument tells if the added content is a text or an image.
     *
     * Type is text, image, css or position
     */

    if(type=="img") {
        $('input.change-img[pk=' + id + ']').click();
    }
    else if(type == "position"){
        $('div.change-position[pk=' + id + ']').css('display', 'block');
    }
    else if(type == "css"){
        $('div.change-css[pk=' + id + ']').css('display', 'block');
    }
    else{
        $('div.change-text[pk=' + id + ']').css('display','block');

        /*
         * The selected row is a fusion of different cells
         */
        if($('input[pk=' + id + '][name=\'fusion\']').length > 0){


        }
        else{

        }
    }
    $('button.validate[pk=' + id + ']').css('display','block');
}

function rowDescriptionHeight(){
    /*
     * Put all element of the row description at the same height
     */
    for(var elt of $("div.row.description")){
        const pk = $(elt).attr('pk');
        const height = $(elt).height();
        $('div.content-description[pk=' + pk + ']').css('min-height', height);
    }
}