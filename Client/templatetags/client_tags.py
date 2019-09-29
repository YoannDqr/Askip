from django import template

register = template.Library()


@register.filter(name='poste')
def poste(cotisant):
    
    try:
        valeur = cotisant.personne.poste.all().get(association=cotisant.association)
        return valeur.titre
    except:
        return "NC"


@register.filter(name='col')
def col(a):
    return int(12/len(a))


@register.filter(name='nombre_reponse')
def nombre_reponse(vote):
    nombre = 0
    for reponse in vote.reponse.all():
        nombre += reponse.nb_reponse
    return nombre


@register.filter(name='accessibility')
def accessibility(vote):
    if vote.accessibility == 0:
        return "Tout le monde"
    elif vote.accessibility == 1:
        return "Cotisant uniquement"
    elif vote.accessibility == 2:
        return "Le CA uniquement"


@register.filter(name='nombre_participant')
def nombre_participant(event):
    return len(event.participant.all())


@register.filter(name='quorum')
def nombre_participant(vote):
    return nombre_reponse(vote) > len(vote.association.cotisant.all())*0.33


@register.filter(name='fusion_constraint')
def fusion_constraint(description, content):
    return not (description['fusion'] and content == "")
    # return True
