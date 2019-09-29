startDate = moment(new Date);
endDate = moment(new Date);
tableCompta = "";
$(document).ready(function(){

    $('.datatableType').DataTable({
        dom: 'Bfrtip',
        buttons: ['copy', 'excel', 'pdf', {text:'New Type', action:newType} ]
    });

    $('.datatableCategorie').DataTable({
        dom: 'Bfrtip',
        buttons: ['copy', 'excel', 'pdf', {text:'New Categorie', action:newCategorie} ]
    });

    $('.datatableProduit').DataTable({
        dom: 'Bfrtip',
        buttons: ['copy', 'excel', 'pdf', {text:'New Produit', action:newProduit} ]
    });

    tableCompta = $('.datatableCompta').DataTable({
        dom: 'Bfrtip',
        buttons: ['copy', 'excel', 'pdf' ]
    });
    

    $('.startDate, .endDate').datetimepicker({
        format : 'YYYY-MM-DD hh:mm', 
        sideBySide : true,
        defaultDate : new Date(),
    });
    
    $(".startDate").on('dp.change', startDateFunction);
    $(".endDate").on('dp.change', endDateFunction);
});

function startDateFunction(e){
    startDate = moment(e.date.format('YYYY-MM-DD hh:mm'));
    ajaxDate();
}

function endDateFunction(e){
    endDate = moment(e.date.format('YYYY-MM-DD hh:mm'));
    ajaxDate();
}

function ajaxDate(){
    start = startDate.format('YYYY-MM-DD hh:mm');
    end = endDate.format('YYYY-MM-DD hh:mm');
    console.log(start);
    console.log(end);
    $.ajax({
        method: "POST",
        url: "/comif/ajaxComptabilite/",
        data: {startDate:start, endDate:end, csrfmiddlewaretoken: $("#csrf_token").text()}
    })
    .done(function(messages){
        console.log(messages);

        $(".datatableCompta>tbody").html("");
        prix = 0;
        messages.forEach(function(message){
            date = moment(message.fields.date).format('YYYY-MM-DD hh:mm');
            prix += parseFloat(message.fields.prix);

            html = "\
            <tr>\
                <th>" + date + "</th>\
                <th>" + message.fields.description + "</th>\
                <th>" + message.fields.prix + "</th>\
            </tr>\
            ";

            $(".datatableCompta>tbody").append(html);
        });

        $("#prixTotal").text(prix);

        tableCompta.reload();
    })
    .fail(function(){
        alert("Erreur");
    });
}

function newType( e, dt, node, config ){
    $("#newTypeBtn").click();
}

function newCategorie( e, dt, node, config ){
    $("#newCategorieBtn").click();
}

function newProduit( e, dt, node, config ){
    $("#newProduitBtn").click();
}

function fillCompta(data, pk){
    html = "";
    $("#commande_btn").css("display", "block");
    $("#commande_id").attr('value', pk)
    data.forEach(function(produit){
        html += "\
        <tr>\
            <th><img style='max-width:50px;padding-right:25px;' src='/media/"+produit.image + "'>"+produit.nom+"</th>\
            <th>"+produit.prix+"</th>\
            <th>"+produit.qte+"</th>\
            <th><span onclick='delProduct("+pk+","+produit.pk+")' class='glyphicon glyphicon-remove' aria-hidden='true'></span></th>\
        </tr>\
        ";
    });
    $("#comptaTable>tbody").html(html);
}

function delCommande(pk_commande){
    $.ajax({
        method: "POST",
        url: "/comif/ajaxDeleteCommande/",
        data: {pk_commande:pk_commande, csrfmiddlewaretoken: $("#csrf_token").text()}
    })
    .done(function(){
        alert("Commande supprimé");
    });
}

function delProduct(pk_commande, pk_produit){
    $.ajax({
        method: "POST",
        url: "/comif/ajaxCommande/",
        data: {pk_commande:pk_commande, pk_produit:pk_produit, csrfmiddlewaretoken: $("#csrf_token").text()}
    })
    .done(function(){
        alert("Produit supprimé");
    });
}