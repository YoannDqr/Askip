pk = "";
solde = "";
produits = [];

$(document).ready(function(){
    $('.datatable').DataTable({
        dom: 'Bfrtip',
        buttons: ['copy', 'excel', 'pdf']
    });
});

function delClient(pkClient){
    $.ajax({
        method: "POST",
        url: "/comif/ajaxDeleteUser/",
        data: {pk:pkClient, csrfmiddlewaretoken: $("#csrf_token").text()}
    })
}

function choose_client(pk_client, solde_client){
    pk = pk_client;
    solde = parseInt(solde_client.split(',')[0]) + parseInt(solde_client.split(',')[1])*0.01
    
    if(solde > -5){
        $(".commande").fadeIn('fast');
        $("[name='client']").attr('value', pk_client);
        $(".client>th").css('border', 'none');
        $("#client_" + pk_client+" > th").css('border-top', '5px solid yellow').css('border-bottom', '5px solid yellow');
    }
    else{
        $("#commande").fadeOut('fast');
    }
}

function addProduit(prix, pk_produit){
    prix = parseInt(prix.split(',')[0]) + parseInt(prix.split(',')[1])*0.01;
    if(solde - prix < -5 && produits.indexOf(pk_produit) < 0){
        $("#produits_"+pk_produit)[0].checked = false;
    }
    else if(produits.indexOf(pk_produit) >= 0){
        produits.splice([produits.indexOf(pk_produit)]);
        solde += prix * parseInt($("#qte_"+pk_produit)[0].value);
        $("#qte_" + pk_produit)[0].value = 0
        $("#produits_"+pk_produit)[0].checked = false;
    }
    else if(solde - prix > -5){
        solde -= prix;
        $("#qte_" + pk_produit)[0].value = 1;
        produits.push(pk_produit);
    }
}

function add_qte(pk_produit, prix, stock){
    prix = parseInt(prix.split(',')[0]) + parseInt(prix.split(',')[1])*0.01;
    qte = $("#qte_"+pk_produit)[0].value;
    
    if(solde - prix > -5 && parseInt(qte) < stock){
        $("#qte_" + pk_produit)[0].value = parseInt(qte) + 1;
        solde -= prix;
        if(produits.indexOf(pk_produit) < 0){
            produits.push(pk_produit);
        }
        $("#produits_"+pk_produit)[0].checked = true;
    }
}

function del_qte(pk_produit, prix, stock){
    prix = parseInt(prix.split(',')[0]) + parseInt(prix.split(',')[1])*0.01;
    qte = $("#qte_"+pk_produit)[0].value;
    
    if(qte > 0){
        $("#qte_" + pk_produit)[0].value = parseInt(qte) - 1;
        solde += prix;
        if(qte == 1 && produits.indexOf(pk_produit) >= 0){
            produits.slice(produits.indexOf(pk_produit));
            $("#produits_"+pk_produit)[0].checked = false;
        }
        
    }
}
