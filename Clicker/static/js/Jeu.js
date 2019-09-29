var jeu = {};
var gicle = 0;
var workers;
if(workers == undefined){
    workers = []
}

var move;
$(document).ready(function(){

    loadData();

    
    setInterval(function(){ 
        jeu['total'] += jeu['cps'] * 0.1;
        number = Number(jeu['total']);
        $("#Cagnotte").text(number.toExponential(2));
    }, 100);

});


function mvtClick(nb){
    if($(".gicle").length == 0){
        gicle = 0;
        
    }
    for(k =0; k < nb; k++){
        numero = gicle;
        gicle += 1;
        var $cagnotte = $("#cagnotte-block");
        var Xrd = -Math.random() - 1 ;
        var X = 0;
        var Yr = 0;
        var block = "<div class='gicle " + numero + "' style='display:inline-block; border-radius:50% 50%;width:20px; height:20px; z-index:1; transform:translate("+X+"px ,"+Yr+"px)'></div>";
        $cagnotte.html($cagnotte.html() + block);

        var a = Math.floor(Math.random() * Math.floor(100) + 50);
        var c = 0;
        var Xr = 0;

        /*if(Math.random() > 0.5){
            a = -a;
        }*/

        workers = workers.concat([{
            'numero':numero,
            'Xrd' : Xrd,
            'X':X,
            'Yr':Yr,
            'Xr':Xr,
            'a' : a,
            
        }]); 
    }    
}


move = setInterval(function(){
    if(workers.length == 0){
        $(".gicle").remove();
    }
    for(elt of workers){
        
        elt['Xr'] +=  elt['Xrd']/10;
        elt['X'] = elt['Xr'] + Math.floor(Math.random() * Math.floor(30));
        elt['Yr'] = elt['a'] * elt['Xr'] * elt['Xr'] - $("#clicker").outerHeight()/6 - 100;
        $('.gicle.' + elt['numero'] ).css("transform", "translate("+elt['X']+"px ,"+elt['Yr']+"px)").css("background", "#FFF"); 
        
        elt['Yr'] = elt['a'] * elt['Xr'] * elt['Xr'] - $("#clicker").outerHeight()/6 - 100;

        if(elt['Xr'] > $("#clicker").outerHeight() || elt['Yr'] > $("#clicker").outerWidth()){
            $(".gicle").remove("." + elt.numero);
            for(k=0; k < workers.length; k++){
                if(workers[k].numero == elt.numero){
                    workers.splice(k,1)
                }
            }
        }
    }
}, 75);

function loadData (){
    for(elt of $(".items") ){
        jeu[$(elt).attr('pk')] = {'pk':$(elt).attr('pk'), 'addCps':parseInt($(elt).attr("cps")), 'prix':parseFloat($(elt).attr("prix")), 'niveau':parseInt($(elt).attr("niv"))};
    }

    jeu['total'] = parseInt($("#total").attr('nb'));
    jeu['cps'] = parseInt($("#total").attr('cps'));
    return jeu;
}

function increment (){

    jeu['total'] = jeu['total'] + parseInt($("#first").attr("cps")) * parseInt(jeu[$("#first").attr("pk")].niveau) ;
    $compteur = $("#Cagnotte");
    nombre = Number(jeu['total']);
    $compteur.text(nombre.toExponential(2));

    mvtClick(Math.floor(Math.random() * Math.floor(19)) + 1);
}

function addCookie(pk){
    if(jeu['total'] >= jeu[pk]['prix']){
        new_prix = jeu[pk]['prix'] * 1.18;
        new_cps = jeu['cps'] + jeu[pk]['addCps'];

        jeu['total'] -= jeu[pk]['prix'];
        jeu[pk]['prix'] = new_prix;
        jeu[pk]['niveau'] += 1;
        if($("#first").attr("pk") != pk){
            jeu['cps'] = new_cps;
        }
        

        $(".items[pk="+pk+"] span.lvl").text(jeu[pk]['niveau']);
        nombre = Number(jeu[pk]['prix']);
        $(".items[pk="+pk+"] span.prix__").text(nombre.toExponential(2));
        $compteur = $("#Cagnotte");
        nombre2 = Number(jeu['total']);
        $compteur.text(nombre2.toExponential(2));

        graphical(pk);
    }
}

function graphical(pk){
    console.log(pk);
    var canvas = document.getElementById("canvas_"+pk);
    var ctx = canvas.getContext("2d");

    var img = new Image();
    var span = $("span.canvas_img_" + pk);
    img.src = $(span[Math.floor(Math.random() * Math.floor(span.length))]).attr('src');
    img.addEventListener('load', function() {
        x_max = $("canvas")[0].width - 50;
        y_max = $("canvas")[0].height - 50;
        x = Math.floor(Math.random() * Math.floor(x_max));
        y = Math.floor(Math.random() * Math.floor(y_max));
        ctx.drawImage(img, x,y,50,50);
      }, false);
}


save = setInterval(function(){
        //console.log("Jeu : " );
        //console.log(jeu);
        for(pk of Object.keys(jeu)){
            if(!isNaN(parseInt(pk))){
                //console.log("pk : " + pk);
                var elt = jeu[pk];
                $.ajax({
                    method: "POST",
                    url: "/clicker/save/",
                    data: { 
                        cps: jeu['cps'],
                        niveau:elt['niveau'],
                        lvl:elt['pk'],
                        total:jeu['total'],
                        csrfmiddlewaretoken: $("#csrf").attr('csrf'),
                    }
                })
                .done(function(messages){
                
                    
                })
                .fail(function(){
                    
                });
            }
        }
    }, 1000);