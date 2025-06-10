🎯 Objectif
Ce projet vise à fournir un script Python de scraping flexible et évolutif, permettant d'extraire automatiquement toutes les informations clés des fiches produits depuis des sites e-commerce sous WooCommerce ou Shopify.

🚀 Fonctionnalités
Extraction des fiches produits : Nom, lien, type (simple/variable), variantes (tailles, couleurs…).

Récupération de toutes les images (carrousel inclus), avec téléchargement local dans un dossier par produit.

Extraction de la description complète de chaque produit (sauvegardée en .txt).

Exploration automatique des pages de collection/catégorie, récupération du nom et lien de chaque produit.

Détection automatique du CMS (WooCommerce ou Shopify).

Gestion de la pagination (statique ou dynamique).

Vérification du bon téléchargement des images.

Double mode :

Statique : requests + BeautifulSoup (sites simples)

Dynamique : Selenium (JS/carrousels/pagination dynamique)

> **Note** : le mode dynamique nécessite Chrome/Chromedriver installés.

Format de sortie au choix : CSV, Excel (.xlsx), JSON.

📦 Structure des dossiers & fichiers
bash
Copier
ecom_scraper/
├── scraper.py
├── config.yaml
├── README.md
├── requirements.txt
├── /outputs/
│   ├── produits.csv|xlsx|json
│   ├── descriptions/
│   │    └── {nom_produit}.txt
│   └── images/
│        └── {nom_produit}/
│             ├── img1.jpg
│             └── img2.jpg
└── /utils/
     └── ...
⚙️ Installation
Cloner le dépôt

bash
Copier
git clone https://github.com/ton-utilisateur/ecom_scraper.git
cd ecom_scraper
Créer un environnement virtuel (optionnel mais recommandé)

bash
Copier
python -m venv venv
source venv/bin/activate  # ou .\venv\Scripts\activate sous Windows
Installer les dépendances

bash
Copier
pip install -r requirements.txt
Installer Chrome et Chromedriver (pour le mode dynamique)

Vous pouvez installer Chrome depuis <https://www.google.com/chrome/> et telecharger Chromedriver depuis <https://chromedriver.chromium.org/downloads>. Assurez-vous que la version de Chromedriver corresponde a celle de Chrome et que l'exécutable soit dans votre PATH.

🛠️ Utilisation
1. Configurer config.yaml
Renseigner l’URL de la page de collection à scraper

Exemple minimal :

```yaml
url: "https://exemple.com/collection"
mode: "static"  # ou "dynamic"
output_format: "csv"
output_dir: "outputs"
headless: true
```

Choisir le mode : statique ou dynamique

Sélectionner le format de sortie : csv, xlsx, json

Définir les chemins de sortie

2. Lancer le script
bash
Copier
python -m ecom_scraper.scraper --config config.yaml
3. Résultats
Un fichier de sortie au format choisi (outputs/produits.csv|xlsx|json)

Toutes les images téléchargées dans /outputs/images/{nom_produit}/

Les descriptions dans /outputs/descriptions/{nom_produit}.txt

📋 Format de sortie
nom_du_produit	lien_produit	type_produit	variantes	images (liste URL)	description (.txt)
...	...	...	...	...	...

✨ Exemples d’utilisation
Des fichiers de configuration types et des résultats d'exemple seront ajoutés ultérieurement.

🧩 TODO & Roadmap
 Interface graphique (PySide6)

 Mode batch multi-URL

 Gestion avancée des proxies/cookies/auth

 Ajout du scraping des avis clients

 Amélioration de la gestion des erreurs

📝 Contribution
Fork, PR bienvenues !

Pour toute suggestion : issues GitHub

📄 Licence
MIT (ou ce que tu veux)

➕ Remarques pour Codex
Penser à la structure modulaire pour faciliter la future intégration d’une interface.

Le script doit être documenté (docstrings, commentaires, logs propres).

Prévoir un système de logs (basique).

Séparer clairement le code par type de site (WooCommerce vs Shopify).

Penser au paramétrage flexible via config.yaml.
