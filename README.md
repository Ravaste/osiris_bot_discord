# 🏴‍☠️ Osiris - L'Entité Pirate Polyvalente

**Osiris** n'est pas qu'un simple bot Discord. C'est un érudit, un loup de mer arrogant, et le gardien de **La Citadelle**. Géré par son IA local Llama 3.1 , il gère tout : de la culture générale aux rappels de sport, en passant par l'économie pirate, Guet du gaillard et la surveillance thermique de mon serveur Minecraft.

---

## ⚓ Les Systèmes de Bord (Cogs)

### 🧠 Intelligence Artificielle & Social (`Misc` & `Events`)
- **Personnalité Contextuelle** : Osiris reconnaît les membres de l'équipage. Il est fidèle à son Capitaine **Berkant (Beber)**, respectueux envers **Babou**, protecteur avec le frère de Beber, mais impitoyable envers les souffres-douleurs de l'équipage **Enes** et **Marco**.
- **Mémoire Dynamique** : Capable de résumer ses propres conversations pour garder le fil sans saturer sa mémoire (GPT-4o).
- **Accueil Visionnaire** : Accueille les nouveaux moussaillons en analysant leur photo de profil via **IA Vision** pour les charrier dès qu'ils posent un pied sur le pont.

### 🎙️ Abordage vocal & Mini-Jeux (`Abordage vocal` & `Citation`)
- **Le "Qui a dit ça ?"** : Mini-jeu d'archives. Osiris fouille les 5000 derniers messages de la Taverne, ressort une citation hors contexte et génère des boutons interactifs pour que l'équipage devine l'auteur (récompense en points et système anti-spam inclus).

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
- **Machines à Sous & Pachinko** : Pariez vos points de devinettes dans des jeux de hasard impitoyables pour faire fortune ou tout perdre.

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
   Installez les requis via pip install -r req.txt. (Nécessite ffmpeg pour l'audio).

2. **Fichier .env** (à la racine) :
```
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
---

# 🏴‍☠️ Osiris - The Versatile Pirate Entity

**Osiris** is no ordinary Discord bot. He is a scholar, an arrogant sea dog, and the guardian of **The Citadel**. Powered by **Llama 3.1** , he handles everything: from general knowledge and workout reminders to pirate economy, voice espionage, and thermal monitoring of my Minecraft server.

---

## ⚓ Ship Systems (Cogs)

### 🧠 Artificial Intelligence & Social (`Misc` & `Events`)
- **Contextual Personality**: Osiris recognizes the crew members. He is loyal to his Captain **Berkant (Beber)**, respectful to **Babou**, protective of Beber's brother, but ruthless and violent with **Enes** or **Marco**.
- **Dynamic Memory**: Capable of summarizing his own conversations to keep track without overloading his memory (GPT-4o).
- **Visionary Welcome**: Welcomes new deckhands by analyzing their profile picture via **Vision AI** to custom-roast them as soon as they step on deck.

### 🎙️ Voice Harassment & Mini-Games (`Intrusion` & `Citation`)
- **"Who Said That?"**: Archive mini-game. Osiris digs through the last 5000 messages of the Tavern, pulls a wild out-of-context quote, and generates interactive UI buttons for the crew to guess the author (features point rewards and an anti-spam lock).

### 💰 Pirate Economy & Justice (`BountyShop` & `Duels`)
- **Bounty Board**: Place doubloons on a pirate's head. Members can launch a **Hunt** (text-based survival mini-game) to claim the loot. Anti-cheat system included (cooldowns and strict phrasing).
- **The Black Market**: Spend your doubloons to send someone to the brig (Timeout), cast a parrot's curse, or buy a presidential pardon.
- **Insult Duels**: Bet your doubloons in a verbal joust. Osiris judges originality and quick wit to declare the winner who takes the pot.
- **Bounty Expiration**: Wanted posters automatically expire after 24 hours of inactivity.

### 👁️ The Observer of the Seas (`Observateur`)
- **The Ear of the Abyss**: Automatically transcribes Discord voice messages to text via **OpenAI Whisper** and adds a mocking comment on the pirate's eloquence.
- **Music & Gaming Judge**: Monitors activities (Spotify, Games) and publicly calls out those listening to questionable content or spending too much time on League of Legends.
- **Voice Channel Warden**: Drops savage punchlines on the first miserable soul to join an empty voice channel, calling them out for having no life.

### 🧩 The Riddle King (`Devinette`)
- **Daily Challenges**: An ultra-hard riddle generated every day with automatic pings for the winners.
- **Degressive Point System**: The reward decreases over time (Internet access and Osiris' hints unlocked in tiers).
- **Crash Resistance**: Saves the complete state (timers, points, respondents) so an ongoing session is never lost to a blackout.

### 🎰 The Pirate's Casino (`Gambling`)
- **The Grand Roll**: Complex probabilities to obtain mythical roles like `His Majesty` or `Pure Heart`.
- **System Threat**: Hitting the critical threshold (0.000001%) triggers an admin alert (System Infiltration).
- **Slots & Pachinko**: Bet your riddle points in ruthless games of chance to make a fortune or lose it all.

### 📅 Time Management & Academics (`Ade`)
- **ADE Sync**: Fetches university schedules (AMU) for the **TP1** and **TP2** groups.
- **Automatic Reminders**: Sends the schedule every morning at 7:30 AM or the evening before.
- **Internship Tracker**: Automatic countdown of the days left until freedom.

### 🌡️ Administration & Monitoring (`Admin`)
- **Thermal Sentinel**: Real-time CPU monitoring. If the temperature exceeds 80°C, Osiris safely shuts down the Minecraft server.
- **The Bus 🚌**: Expedited moderation system (Mute) with automatic management of revival permissions.

### 🏋️ Workout Program (`Sport`)
- **16-Week Coaching**: Progressive workout plan (Full Body & Cardio).
- **Motivational Harassment**: Reminders every 30 minutes until the Captain confirms the workout is done.

---

## 🛠 Installation & Setup

1. **Dependencies**:
   Install requirements via pip install -r req.txt. (Requires ffmpeg for audio).

2. **.env File** (at the root):
```
# DISCORD
BOT_DISCORD=YourMainToken
BOTMC=SecondaryTokenForMinecraft
SERPAPI_KEY=SerpApiKeyForImages

# OPENAI (GPT-4o, Whisper, Vision, TTS)
OPENAI_API_KEY=YourOpenAIKey
PROJECT=Project_ID
ORGANIZATION=Organization_ID

# TWITCH
TWITCH_TOKKEN=TwitchOauthToken
TWITCH_CLIENT_ID=TwitchClientID
TWITCH_CHANNEL_OSIRIS=TargetAccountName
```
