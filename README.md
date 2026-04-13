# 🏴‍☠️ Osiris - L'Entité Pirate Polyvalente

**Osiris** n'est pas qu'un simple bot Discord. C'est un érudit, un loup de mer arrogant, et le gardien de **La Citadelle**. Propulsé par **GPT-4o**, il gère tout : de la culture générale aux rappels de sport, en passant par la surveillance thermique de mon serveur Minecraft.

---

## ⚓ Les Systèmes de Bord (Cogs)

### 🧠 Intelligence Artificielle & Social (`Misc` & `Events`)
- **Personnalité Contextuelle** : Osiris reconnaît les membres de l'équipage. Il est fidèle à son Capitaine **Berkant (Beber)**, respectueux envers **Babou**, protecteur avec le frère de Beber, mais impitoyable et violent avec **Enes** ou **Marco**.
- **Mémoire Dynamique** : Capable de résumer ses propres conversations pour garder le fil sans saturer sa mémoire.
- **Accueil & Adieux** : Accueille les nouveaux moussaillons et rend hommage aux membres qui quittent le navire via des messages générés par l'IA.

### 🧩 Le Roi des Devinettes (`Devinette`)
- **Défis Quotidiens** : Une devinette ultra-difficile est générée chaque jour.
- **Système de Points Dégressif** : 
    - *Moins d'1h* : 9, 8 ou 7 points.
    - *Entre 1h et 4h* : 6, 5 ou 4 points (accès à Internet autorisé).
    - *Après 4h* : 3, 2 ou 1 point (accès total aux recherches).
- **Résistance aux Crashs** : Sauvegarde l'état des timers et de la question en cours pour reprendre exactement là où il s'est arrêté en cas de redémarrage.

### 🎰 Le Casino du Pirate (`Gambling`)
- **Le Grand Roll** : Un système de probabilités "complexes" (J'ai juste faire des gros environs) pour obtenir des rôles légendaires.
- **Loot Table Mythique** :
    - `Sa Majesté` (0.8%), `Puissance Incontrôlable` (1.5%), `Cœur Pur` (2.5%).
    - `Le Dernier de l'Époque Oubliée` (0.0001%).
    - **Alerte Système** : Tomber sur `0.000001%` déclenche une infiltration système (Menace Système). Un admin en gros

### 📅 Gestion du Temps & Scolarité (`Ade`)
- **Synchronisation ADE** : Récupère automatiquement les emplois du temps de l'Université (AMU) pour les groupes **TP1** et **TP2**.
- **Rappels Automatiques** : Envoie le planning chaque matin à 7h30 ou la veille au soir.
- **Suivi de Stage** : Compteur automatique des jours de stage effectués.

### 🌡️ Administration & Surveillance (`Admin`)
- **Sentinel Thermique** : Surveille la température CPU du serveur toutes les minutes.
- **Sécurité Minecraft** : En cas de surchauffe (>80°C), Osiris coupe le serveur Minecraft automatiquement et le relance après 1h de refroidissement.
- **Le Bus 🚌** : Système de modération "Expéditif". Envoyer quelqu'un "sous le bus" (Mute) avec configuration automatique des permissions du salon de réanimation.

### 🎵 Musique & Audio (`Music`)
- **Jukebox Pirate** : Lecture de musique via YouTube ou fichiers locaux.
- **Synthèse Vocale (TTS)** : Osiris peut parler dans le salon vocal avec une voix de pirate grave et rocailleuse (TTS OpenAI).
- **Invocations** : Commandes spéciales pour invoquer Mahoraga (JJK) ou célébrer l'ange né en enfer (Gogeta).

### 🏋️ Programme de Sport (`Sport`)
- **Coaching de 16 semaines** : Un programme évolutif (Full Body & Cardio) qui s'adapte chaque semaine.
- **Rappels Persistants** : Harcèle le capitaine toutes les 30 minutes jusqu'à ce qu'il confirme avoir terminé sa séance.

### 📺 Alertes de Stream (`Stream`)
- **Twitch Watch** : Surveille en temps réel les lives de tes streamers favoris (Hideyosh_, Saturnesmile, Flapiix) et envoie une alerte riche (Embed) avec le titre et l'aperçu du live.

### 🎮 Interactions Twitch
- **Abordage Dynamique** : Rejoignez n'importe quel chat Twitch instantanément via une commande Discord.
- **Système de Défis (`!defi`)** : Osiris génère des devinettes de culture générale ultra-difficiles. 
    - L'IA génère la question et la réponse au format JSON.
    - Osiris reformule la question avec son style pirate.
    - Il détecte automatiquement la bonne réponse dans le chat et félicite le vainqueur.
- **Détection de Mention** : Répond automatiquement lorsqu'on prononce son nom dans le chat.

### 💻 Contrôle via Discord
- **Commandes de Flotte** : Pilotez les mouvements du bot Twitch depuis votre serveur Discord.
- **Logs en temps réel** : Suivez les activités d'Osiris (connexions, messages reçus, erreurs) directement dans la console.
---

## 🛠 Installation & Setup

1. **Dépendances** :
   Dans le fichier req.txt
   
2. Fichier .env a la racine du bot ( a coté du main.py )
```bash
BOT_DISCORD=
SERPAPI_KEY=
OPENAI_API_KEY=
PROJECT=
ORGANIZATION=
BOTMC=
TWITCH_TOKKEN=
TWITCH_CLIENT_ID=
TWITCH_CHANNEL_OSIRIS=
```
