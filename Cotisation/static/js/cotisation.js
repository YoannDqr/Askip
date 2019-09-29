indicateurSujet = false;
indicateurDate = false;
indicateurMoyen = false;
indicateurCategorie = false;
indicateurMontant = false;
indicateurStartDateEvent = false;
indicateurEndDateEvent = false;
$(document).ready(function(){
    document.oncontextmenu = new Function("return false"); //enleve le clique droit
    $("#new_picture").change(function(){
        $('form#asso_picture').submit();
    })
    $('#startDate, #endDate, #eventDate, #eventEndDate').datetimepicker({
        format : 'YYYY-MM-DD hh:mm', 
        sideBySide : true,
        minDate : new Date()
    });
    $('#tresorerieDate').datetimepicker({format : 'YYYY-MM-DD'});


    /*$('#datetimepicker12').datetimepicker({
                format : 'YYYY-MM-DD',
                inline: true,
                sideBySide: true
            });*/
    //$("[data-action='selectDay']").append("Salut");


    $('.club').DataTable({
        dom: 'Bfrtip',
        buttons: ['copy', 'excel', 'pdf', {text:'New Club', action:newClub}]
    });
    $('.vote').DataTable({
        dom: 'Bfrtip',
        buttons: ['copy', 'excel', 'pdf', {text:'New Vote', action:newVote}]
    });
    $('.tresorerie').DataTable({
        dom: 'Bfrtip',
        buttons: ['copy', 'excel', 'pdf', {text:'New Depense', action:newTresorerie}]
    });
    $('.poste').DataTable({
        dom: 'Bfrtip',
        buttons: ['copy', 'excel', 'pdf', {text:'New Poste', action:newPoste}]
    });
    $('.event').DataTable({
        dom: 'Bfrtip',
        buttons: ['copy', 'excel', 'pdf', {text:'New Event', action:newEvent}]
    });
    $('.client').DataTable({
        dom: 'Bfrtip',
        buttons: ['copy', 'excel', 'pdf', {text:'New Cotisant', action:newCotisant}]
    });


//----------------------- CheckBox -----------------------------------------------------


    if( $("select#moyen_paye>option").length == 1){
        $("#new_moyen").fadeIn("quick");
    }

    if( $("select#categorie>option").length == 1){
        $("#new_categorie").fadeIn("quick");
    }

    $("#master_cotisation").change(function(){
        for(var elt of $("input.cotisant_check[type='checkbox']")){
            elt.checked = this.checked 
        }
    });

    $("#master_poste").change(function(){
        for(var elt of $("input.poste_check[type='checkbox']")){
            elt.checked = this.checked 
        }
    });

    $("#master_event").change(function(){
        for(elt of $("input.event_check[type='checkbox']")){
            elt.checked = this.checked 
        }
    });


    $("#master_votes").change(function(){
        for(elt of $("input.votes_check[type='checkbox']")){
            elt.checked = this.checked 
        }
    });

    $("#master_tresorerie").change(function(){
        for(elt of $("input.tresorerie_check[type='checkbox']")){
            elt.checked = this.checked 
        }
    });
//------------------------------------------------------------------------------
//--------------------- Create new field ---------------------------------------
    $("select#moyen_paye").change(function(){
        if(this.value == "NC"){
            $("#new_moyen").fadeIn("quick");
        }
        else{
            $("#new_moyen").fadeOut("quick");
        }
    });

    $("select#categorie").change(function(){
        if(this.value == "NC"){
            $("#new_categorie").fadeIn("quick");
        }
        else{
            $("#new_categorie").fadeOut("quick");
        }
    });

//-------------------------------------------------------------------------------
//------------------------------- Ajax modification inline ----------------------
    $(window).dblclick(function(){
        if(indicateurDate){
            newDate = $("input[name^='modif_date_'");
            for(elt of newDate){
                if(elt.value != ""){
                    newDate = "";
                    for(d of elt.value.split('-')){
                        newDate += d + " ";
                    }
                    newDate = new Date(newDate);
                    newDateF = "" + newDate;
                    sendAjax("date", elt.value, $(elt).attr('pk'));
                    $("#"+$(elt).attr('name').split("modif_")[1]).html(newDateF.slice(0,15));
                    indicateurDate = false;
                    
                }
            }
        }
        else if (indicateurSujet){
            sujets = $("input[name^='modif_sujet_'");
            for(elt of sujets){
                if(elt.value != ""){
                    sendAjax("sujet", elt.value, $(elt).attr('pk'));
                    $("#"+$(elt).attr('name').split("modif_")[1]).html(elt.value);
                    indicateurSujet = false;
                }
            }
        }

        else if (indicateurMoyen){
            moyens = $("input[name^='modif_moyen_'");
            for(elt of moyens){
                if(elt.value != ""){
                    sendAjax("moyen", elt.value, $(elt).attr('pk'));
                    $("#"+$(elt).attr('name').split("modif_")[1]).html(elt.value);
                    indicateurMoyen = false;
                }
            }
        }
        else if (indicateurCategorie){
            moyens = $("input[name^='modif_categorie_'");
            for(elt of moyens){
                if(elt.value != ""){
                    sendAjax("categorie", elt.value, $(elt).attr('pk'));
                    $("#"+$(elt).attr('name').split("modif_")[1]).html(elt.value);
                    indicateurCategorie = false;
                }
            }
        }
        else if (indicateurMontant){
            moyens = $("input[name^='modif_montant_'");
            for(elt of moyens){
                if(elt.value != ""){
                    sendAjax("montant", elt.value, $(elt).attr('pk'));
                    $("#"+$(elt).attr('name').split("modif_")[1]).html(elt.value);
                    indicateurMontant = false;
                }
            }
        }

        else if (indicateurStartDateEvent){
            moyens = $("input[name^='modif_startDateEvent_'");
            for(elt of moyens){
                if(elt.value != ""){

                    sendAjaxEvent("startDate", elt.value, $(elt).attr('pk'));
                    $("#"+$(elt).attr('name').split("modif_")[1]).html(elt.value);
                    indicateurStartDateEvent = false;
                }
            }
        }

        else if (indicateurEndDateEvent){
            moyens = $("input[name^='modif_endDateEvent_'");
            for(elt of moyens){
                if(elt.value != ""){

                    sendAjaxEvent("endDate", elt.value, $(elt).attr('pk'));
                    $("#"+$(elt).attr('name').split("modif_")[1]).html(elt.value);
                    indicateurEndDateEvent = false;
                }
            }
        }
    });
});

function sendAjax(cible, valeur, pk){
    url = "/cotisation/tresorerie/" + cible + "/"
    $.ajax({
        method: "POST",
        url: url,
        data: {data: valeur, id:pk, csrfmiddlewaretoken: $("#csrf_token").text()}
    });
}

function sendAjaxEvent(cible, valeur, pk){
    url = "/cotisation/event/" + cible + "/";
    console.log("**********"+pk)
    $.ajax({
        method: "POST",
        url: url,
        data: {data: valeur, id:pk, csrfmiddlewaretoken: $("#csrf_token").text()}
    });
}

function date(pk){
    html = "<input pk='"+pk+"' class='form-control' name='modif_date_" + pk + "' type='date' value='" + $("#date_" + pk)[0].value + "'>";
    $("#date_" + pk).html(html);
    indicateurDate = true;
}

function sujet(pk){
    html = "<input pk='"+pk+"' class='form-control' name='modif_sujet_" + pk + "' type='text' value=''>";
    $("#sujet_" + pk).html(html);
    indicateurSujet = true;
}

function moyen(pk){
    html = "<input pk='"+pk+"' class='form-control' name='modif_moyen_" + pk + "' type='text' value=''>";
    $("#moyen_" + pk).html(html);
    indicateurMoyen = true;
}

function categorie(pk){
    html = "<input pk='"+pk+"' class='form-control' name='modif_categorie_" + pk + "' type='text' value=''>";
    $("#categorie_" + pk).html(html);
    indicateurCategorie = true;
}

function montant(pk){
    html = "<input pk='"+pk+"' class='form-control' name='modif_montant_" + pk + "' type='number' value='' step='0.01'>";
    $("#montant_" + pk).html(html);
    indicateurMontant = true;
}

function startDateEvent(pk){
    //html = "<input type='datetime-local' class='form-control' name='modif_startDateEvent_" + pk +"'/>";
    html = "\
        <div class='input-group date' id='eventStartDateModify'>\
            <input type='text' pk='" + pk + "' class='form-control' name='modif_startDateEvent_" + pk +"'/>\
            <span class='input-group-addon'>\
                <span class='glyphicon glyphicon-calendar'></span>\
            </span>\
        </div>";
    $("#startDateEvent_" + pk).html(html);
    indicateurStartDateEvent = true;
    $('#eventStartDateModify').datetimepicker({format : 'YYYY-MM-DD hh:mm', minDate: new Date(), sideBySide: true});
}

function endDateEvent(pk){
    //html = "<input type='datetime-local' pk='" + pk + "' class='form-control' name='modif_endDateEvent_" + pk + "' />"
    html = "\
        <div class='input-group date' id='eventEndDateModify'>\
            <input type='text' pk='" + pk + "' class='form-control' name='modif_endDateEvent_" + pk + "' />\
            <span class='input-group-addon'>\
                <span class='glyphicon glyphicon-calendar'></span>\
            </span>\
        </div>";
    $("#endDateEvent_" + pk).html(html);
    indicateurEndDateEvent = true;
    $('#eventEndDateModify').datetimepicker({format : 'YYYY-MM-DD hh:mm', minDate: new Date(), sideBySide: true});
}

function addReponse(){
    nb_reponse = $("textarea.reponse_vote").length;
    $("div#reponse_vote").append("\
        <div class='form-group'>\
            <textarea class='reponse_vote form-control' name='reponse_vote_" + nb_reponse + "'></textarea> \
        </div>\
    ");
}

function dropAjax(event, delta, revertFunc){
    evt = $("span#"+event.className[0]);
    id=evt.attr('pk');
    startDate = event.start.format('YYYY-MM-DD hh:mm');
    if(event.end != null){
        endDate = event.end.format('YYYY-MM-DD hh:mm');
    }
    else{
        endDate = event.start.format('YYYY-MM-DD hh:mm');
    }
    $.ajax({
        method: "POST",
        url: "/cotisation/modifyEventDate/",
        data: {id:id, startDate:startDate, endDate:endDate, csrfmiddlewaretoken:$("#csrf_token").text()}
    });
}

function newClub( e, dt, node, config ){
    $("#newClubBtn").click();
}
function newVote( e, dt, node, config ){
    $("#newVoteBtn").click();
}
function newTresorerie( e, dt, node, config ){
    $("#newTresorerieBtn").click();
}
function newPoste( e, dt, node, config ){
    $("#newPosteBtn").click();
}
function newEvent( e, dt, node, config ){
    $("#newEvent").click();
}
function newCotisant( e, dt, node, config ){
    $("#newCotisantBtn").click();
}


