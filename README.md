# 🏴‍☠️ Osiris - L'Entité Pirate Polyvalente

**Osiris** n'est pas qu'un simple bot Discord. C'est un érudit, un loup de mer arrogant, et le gardien de **La Citadelle**. Propulsé par **GPT-4o** et **Whisper**, il gère tout : de la culture générale aux rappels de sport, en passant par l'économie pirate, l'espionnage vocal et la surveillance thermique de mon serveur Minecraft.

---

## ⚓ Les Systèmes de Bord (Cogs)

### 🧠 Intelligence Artificielle & Social (`Misc` & `Events`)
- **Personnalité Contextuelle** : Osiris reconnaît les membres de l'équipage. Il est fidèle à son Capitaine **Berkant (Beber)**, respectueux envers **Babou**, protecteur avec le frère de Beber, mais impitoyable et violent avec **Enes** ou **Marco**.
- **Mémoire Dynamique** : Capable de résumer ses propres conversations pour garder le fil sans saturer sa mémoire (GPT-4o).
- **Accueil Visionnaire** : Accueille les nouveaux moussaillons en analysant leur photo de profil via **IA Vision** pour les humilier sur-mesure dès qu'ils posent un pied sur le pont.

### 💰 Économie Pirate & Justice (`BountyShop` & `Duels`)
- **Tableau des Primes** : Placez des doublons sur la tête d'un pirate. Les membres peuvent lancer une **Chasse** (mini-jeu de survie textuelle) pour empocher le butin. Système anti-triche inclus (cooldowns et phrases strictes).
- **Le Marché Noir** : Dépensez vos doublons pour envoyer quelqu'un à la cale (Timeout), placer une malédiction de perroquet, ou s'offrir une grâce présidentielle.
- **Duels d'Insultes** : Pariez vos doublons dans une joute verbale. Osiris juge l'originalité et la répartie pour désigner le vainqueur qui rafle la mise.
- **Prescription des Primes** : Les avis de recherche expirent automatiquement après 24h d'inactivité.

### 👁️ L'Observateur des Mers (`Observateur`)
- **L'Oreille des Abysses** : Transcrit automatiquement les messages vocaux Discord en texte via **OpenAI Whisper** et ajoute un commentaire moqueur sur l'éloquence du pirate.
- **Juge Musical & Gaming** : Surveille les activités (Spotify, Jeux) et interpelle publiquement ceux qui écoutent du contenu douteux ou passent trop de temps sur League of Legends.
- **Garde-Chiourme Vocal** : Lâche des punchlines cinglantes au premier misérable qui rejoint un salon vocal vide pour le traiter de chômeur.

### 🧩 Le Roi des Devinettes (`Devinette`)
- **Défis Quotidiens** : Une devinette ultra-difficile générée chaque jour avec pings automatiques des gagnants.
- **Système de Points Dégressif** : Le gain diminue avec le temps (accès à Internet et indices d'Osiris débloqués par paliers).
- **Résistance aux Crashs** : Sauvegarde l'état complet (timers, points, répondants) pour ne jamais perdre une session en cours.

### 🎰 Le Casino du Pirate (`Gambling`)
- **Le Grand Roll** : Probabilités complexes pour obtenir des rôles mythiques comme `Sa Majesté` ou `Cœur Pur`.
- **Menace Système** : Tomber sur le seuil critique (0.000001%) déclenche une alerte admin (Infiltration système).

### 📅 Gestion du Temps & Scolarité (`Ade`)
- **Synchronisation ADE** : Récupère les emplois du temps de l'Université (AMU) pour les groupes **TP1** et **TP2**.
- **Rappels Automatiques** : Envoi du planning chaque matin à 7h30 ou la veille.
- **Suivi de Stage** : Compteur automatique des jours restants avant la liberté.

### 🌡️ Administration & Surveillance (`Admin`)
- **Sentinel Thermique** : Surveillance CPU en temps réel. Si la température dépasse 80°C, Osiris coupe le serveur Minecraft par sécurité.
- **Le Bus 🚌** : Système de modération expéditif (Mute) avec gestion automatique des permissions de réanimation.

### 🏋️ Programme de Sport (`Sport`)
- **Coaching 16 semaines** : Programme évolutif (Full Body & Cardio).
- **Harcèlement de Motivation** : Rappels toutes les 30 minutes jusqu'à confirmation de la séance par le Capitaine.

---

## 🛠 Installation & Setup

1. **Dépendances** :
   Installez les requis via `pip install -r req.txt`. (Nécessite `ffmpeg` pour l'audio).

2. **Fichier .env** (à la racine) :
```bash
# DISCORD
BOT_DISCORD=TonTokenPrincipal
BOTMC=TokenSecondairePourMinecraft
SERPAPI_KEY=CleSerpApiPourImages

# OPENAI (GPT-4o, Whisper, Vision, TTS)
OPENAI_API_KEY=TaCleOpenIA
PROJECT=ID_Projet
ORGANIZATION=ID_Organisation

# TWITCH
TWITCH_TOKKEN=TokenOauthTwitch
TWITCH_CLIENT_ID=ClientIDTwitch
TWITCH_CHANNEL_OSIRIS=NomDuCompteCible
```
