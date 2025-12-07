# app/routes/help.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Help"])

@router.get("/aide", response_class=HTMLResponse)
async def aide():
    return """
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <title>Aide – Bien signaler un incident AYii RATP</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; padding: 16px; line-height: 1.5; color: #111827; }
    h1 { font-size: 1.5rem; margin-bottom: 0.75rem; }
    h2 { font-size: 1.1rem; margin-top: 1.25rem; margin-bottom: 0.5rem; }
    ul { padding-left: 1.1rem; }
    li { margin-bottom: 0.25rem; }
    strong { font-weight: 600; }
    .tag { display: inline-block; background: #f3f4f6; padding: 2px 6px; border-radius: 999px; font-size: 0.85rem; margin-right: 4px; }
  </style>
</head>
<body>
  <h1>Comment bien signaler un incident sur AYii – Propreté RATP ?</h1>

  <p>
    Quelques conseils pour que vos signalements soient vraiment utiles et
    puissent être traités rapidement par les équipes RATP.
  </p>

  <h2>1. Choisissez le bon type d’incident</h2>
  <p>Sur AYii, les principaux types d’incidents de propreté sont&nbsp;:</p>
  <ul>
    <li><span class="tag">urine</span> présence d’urine au sol, sur un siège, dans un couloir ou ascenseur</li>
    <li><span class="tag">vomit</span> vomi sur le quai, dans une rame ou un escalier</li>
    <li><span class="tag">feces</span> excréments visibles dans une zone de passage</li>
    <li><span class="tag">blood</span> traces de sang au sol, sur un mur ou un siège</li>
    <li><span class="tag">syringe</span> seringue ou matériel d’injection abandonné</li>
    <li><span class="tag">broken_glass</span> verre cassé, bouteille brisée, vitrine ou fenêtre fracturée</li>
    <li><span class="tag">other</span> autre incident de propreté ou de sécurité ne rentrant pas dans les catégories ci-dessus</li>
  </ul>
  <p>
    Choisissez la catégorie qui se rapproche le plus de la situation observée.
  </p>

  <h2>2. Placez le point au bon endroit sur la carte</h2>
  <p>
    Zoomez si nécessaire et placez le point au plus près de l’endroit réel :
    quai, entrée, escalier, ascenseur, couloir, plateforme du bus, etc.
  </p>
  <p>
    Une bonne localisation permet aux équipes d’intervention de retrouver
    rapidement l’incident dans le bon train, la bonne station ou la bonne zone.
  </p>

  <h2>3. Ajoutez une photo ou une courte vidéo (fortement recommandé)</h2>
  <p>
    Une image claire vaut mieux qu’une longue description. Elle aide à
    identifier la gravité, le type de nettoyage nécessaire et le matériel à
    prévoir.
  </p>
  <ul>
    <li>📸 <strong>Une photo nette</strong> suffit dans la plupart des cas.</li>
    <li>🎥 Si vous filmez, privilégiez des <strong>vidéos très courtes</strong> (5 à 10 secondes maximum).</li>
  </ul>
  <p>
    Des vidéos trop longues peuvent être plus lentes à envoyer ou échouer
    si la connexion est faible.
  </p>

  <h2>4. Laissez un numéro de téléphone joignable</h2>
  <p>
    Le numéro est <strong>optionnel</strong>, mais très utile : il permet aux
    équipes RATP ou aux services concernés de vous rappeler en cas de question
    ou de difficulté à localiser l’incident.
  </p>
  <p>
    Les signalements avec <strong>photo/vidéo</strong> et
    <strong>numéro de téléphone</strong> sont généralement traités en priorité.
  </p>

  <h2>5. Vérifiez avant de confirmer</h2>
  <p>Avant de valider, prenez quelques secondes pour vérifier&nbsp;:</p>
  <ul>
    <li>le <strong>type d’incident</strong> choisi ;</li>
    <li>la <strong>position</strong> sur la carte (bonne station / bon endroit) ;</li>
    <li>la présence d’une <strong>photo ou d’une vidéo</strong> si possible ;</li>
    <li>votre <strong>numéro de téléphone</strong> si vous acceptez d’être rappelé.</li>
  </ul>

  <h2>6. Signalements sans média et sans téléphone</h2>
  <p>
    Les signalements <strong>sans photo/vidéo</strong> et <strong>sans numéro de téléphone</strong>
    sont parfois difficiles à exploiter, surtout dans des gares et stations très fréquentées.
  </p>
  <p>
    Quand c’est possible, essayez de joindre une image et de laisser un numéro
    joignable. Cela augmente fortement les chances que votre signalement
    soit compris et traité rapidement.
  </p>

  <p style="margin-top: 1.5rem; font-size: 0.9rem; color: #6b7280;">
    Merci pour votre aide : chaque signalement bien renseigné contribue à maintenir
    le réseau plus propre et plus sûr pour tous les voyageurs.
  </p>
</body>
</html>
    """
