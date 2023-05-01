import requests


def translate(text, target_language, source=None):
    url = 'https://translate.googleapis.com/translate_a/single'
    params = {
        'client': 'gtx',
        'sl': 'auto',
        'tl': target_language,
        'dt': 't',
        'q': text
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        translated_text = ""
        for sentence in response.json()[0]:
            translated_text += sentence[0]
        return translated_text
    else:
        return None

if __name__ == "__main__":
    # Example usage
    text = """Titre : "La Bataille de l'Océan Gris"
    Date : 12 septembre 1812
    Auteur: inconnu . :. :. :. :. 
    
    Les canons tonnent, les voiles claquent,
    Sur la mer grise, la mort attaque.
    Les navires s'affrontent sans merci,
    Dans cette guerre qui n'a pas de répit.
    
    Les hommes se battent avec vaillance,
    Espérant sortir de cette tourmente.
    Leur courage est mis à rude épreuve,
    Mais ils tiennent bon malgré les écueils.
    
    Le sang coule sur le pont des navires,
    Les blessés crient et appellent leur mère.
    Mais la bataille continue sans fin,
    Chaque camp cherchant à vaincre son voisin.
    
    Au milieu de ce chaos indescriptible,
    Le ciel se fait noir, les dieux sont terribles.
    La tempête se lève, l'océan s'agite,
    Et les navires s'entrechoquent avec violence.
    
    Finalement, un silence pesant s'abat,
    Seules les vagues viennent s'échouer.
    Les survivants regardent autour d'eux,
    Le coeur lourd, l'âme en peine, le corps tremblant de peur.
    
    Car cette guerre navale a eu raison d'eux,
    Elle a laissé dans leur coeur un goût amer.
    Ils se souviendront toujours de cette journée,
    Où la mort les a frôlés de si près."""
    target_language = 'en'
    translated_text = translate(text, target_language)
    print(translated_text)
