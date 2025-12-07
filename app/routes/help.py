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
  <title>AYii – Aide au signalement (Propreté RATP)</title>
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 text-slate-800">
  <div class="max-w-3xl mx-auto px-4 py-6 space-y-5">
    <header class="space-y-1">
      <h1 class="text-2xl font-bold">Comment bien signaler un incident sur AYii – Propreté RATP ?</h1>
      <p class="text-sm text-slate-600">
        Quelques conseils pour que vos signalements soient vraiment utiles et puissent être traités rapidement
        par les équipes RATP.
      </p>
    </header>

    <!-- 1. Types d'incidents -->
    <section class="space-y-3 bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
      <h2 class="font-semibold">1. Choisissez le bon type d’incident</h2>
      <p class="text-sm">
        Sur AYii, les principaux types d’incidents de propreté sont&nbsp;:
      </p>
      <ul class="text-sm list-disc pl-5 space-y-1">
        <li><span class="font-semibold">urine</span> : présence d’urine au sol, sur un siège, dans un couloir ou un ascenseur</li>
        <li><span class="font-semibold">vomit</span> : vomi sur le quai, dans une rame ou un escalier</li>
        <li><span class="font-semibold">feces</span> : excréments visibles dans une zone de passage</li>
        <li><span class="font-semibold">blood</span> : traces de sang au sol, sur un mur ou un siège</li>
        <li><span class="font-semibold">syringe</span> : seringue ou matériel d’injection abandonné</li>
        <li><span class="font-semibold">broken_glass</span> : verre cassé, bouteille brisée, vitrine ou fenêtre fracturée</li>
        <li><span class="font-semibold">other</span> : autre incident de propreté ou de sécurité apparenté</li>
      </ul>
      <p class="text-xs text-slate-500">
        Choisissez la catégorie qui se rapproche le plus de la situation observée.
      </p>
    </section>

    <!-- 2. Position sur la carte -->
    <section class="space-y-3 bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
      <h2 class="font-semibold">2. Placez le point au bon endroit sur la carte</h2>
      <p class="text-sm">
        Zoomez si nécessaire et placez le point au plus près de l’endroit réel :
        quai, entrée, escalier, ascenseur, couloir, plateforme de bus, etc.
      </p>
      <p class="text-sm">
        Une bonne localisation permet aux équipes d’intervention de retrouver rapidement l’incident dans
        la bonne station, la bonne rame ou la bonne zone.
      </p>
    </section>

    <!-- 3. Photo / vidéo -->
    <section class="space-y-3 bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
      <h2 class="font-semibold">3. Ajoutez une photo ou une courte vidéo (fortement recommandé)</h2>
      <p class="text-sm">
        Une image claire vaut mieux qu’une longue description. Elle aide à estimer la gravité,
        le type de nettoyage nécessaire et le matériel à prévoir.
      </p>
      <ul class="text-sm list-disc pl-5 space-y-1">
        <li>📸 <span class="font-semibold">Une photo nette</span> suffit dans la majorité des cas.</li>
        <li>🎥 Si vous filmez, privilégiez des <span class="font-semibold">vidéos très courtes</span> (5 à 10 secondes max).</li>
      </ul>
      <p class="text-xs text-slate-500">
        Des vidéos trop longues peuvent être lentes à envoyer ou échouer si la connexion est faible.
      </p>
    </section>

    <!-- 4. Numéro de téléphone -->
    <section class="space-y-3 bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
      <h2 class="font-semibold">4. Laissez un numéro de téléphone joignable</h2>
      <p class="text-sm">
        Le numéro est <span class="font-semibold">optionnel</span>, mais très utile&nbsp;:
        il permet aux équipes RATP ou aux services concernés de vous rappeler en cas de question
        ou de difficulté à localiser l’incident.
      </p>
      <p class="text-sm">
        Les signalements avec <span class="font-semibold">photo ou vidéo</span> et
        <span class="font-semibold">numéro de téléphone</span> sont généralement traités en priorité.
      </p>
    </section>

    <!-- 5. Vérification avant envoi -->
    <section class="space-y-3 bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
      <h2 class="font-semibold">5. Vérifiez avant de confirmer</h2>
      <p class="text-sm">Avant de valider, prenez quelques secondes pour vérifier&nbsp;:</p>
      <ul class="text-sm list-disc pl-5 space-y-1">
        <li>le <span class="font-semibold">type d’incident</span> choisi ;</li>
        <li>la <span class="font-semibold">position</span> sur la carte (bonne station / bon endroit) ;</li>
        <li>la présence d’une <span class="font-semibold">photo ou vidéo</span> si possible ;</li>
        <li>votre <span class="font-semibold">numéro de téléphone</span> si vous acceptez d’être rappelé.</li>
      </ul>
    </section>

    <!-- 6. Cas sans média / sans téléphone -->
    <section class="space-y-3 bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
      <h2 class="font-semibold">6. Signalements sans média et sans téléphone</h2>
      <p class="text-sm">
        Les signalements <span class="font-semibold">sans photo/vidéo</span> et
        <span class="font-semibold">sans numéro de téléphone</span> sont parfois difficiles à exploiter,
        surtout dans des gares et stations très fréquentées.
      </p>
      <p class="text-sm">
        Quand c’est possible, essayez de joindre une image et de laisser un numéro joignable.
        Cela augmente fortement les chances que votre signalement soit compris et traité rapidement.
      </p>
    </section>

    <footer class="pt-4 text-xs text-center text-slate-500">
      Merci pour votre aide : chaque signalement bien renseigné contribue à maintenir
      le réseau plus propre et plus sûr pour tous les voyageurs.
    </footer>
  </div>
</body>
</html>
"""
