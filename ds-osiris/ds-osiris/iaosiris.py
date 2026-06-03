from moduleosiris import *
load_dotenv()

organization= os.getenv("ORGANIZATION")
project= os.getenv("PROJECT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client_ia = openai.AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    organization=organization
)


async def ia_osiris(message, facon_etre, memoire=None, max_token=200, temperement=0.9):
    if memoire is None:
        memoire = []

    system_prompt = (
        f"Tu es un assistant qui {facon_etre}. "
        f"Voici ton historique de conversation precedente : {memoire}. "
        "Reponds avec clarte, logique et style adapte."
    )

    user_prompt = f"Repond a ceci : '{message}'" if message.strip() else ""

    try:
        response = await client_ia.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_token,
            temperature=temperement,
            stream=False
        )

        full_reply = response.choices[0].message.content.strip()

        return full_reply if full_reply else "Je n ai pas compris ce que tu voulais."

    except Exception as e:
        print(f"Exception: {e}")
        return f"Erreur de traitement : {e}"

        
async def ia_devinette():
    with open('question.json', 'r') as fd:
        question_posee = json.load(fd)

    # prompt = (
    #     "Genere une devinette de culture generale EXTREMEMENT difficile, longue et detaillee, "
    #     "sur un fait historique, scientifique ou culturel d une extreme rarete, "
    #     "La question doit etre formulee avec plusieurs phrases, donnant des indices subtils, mais jamais suffisants pour une recherche directe. "
    #     "La reponse doit etre precise, courte (1 a 3 mots), et sans ambiguite. "
    #     "Respecte un format JSON STRICT : {\"question\": \"...\", \"answer\": \"...\"}. "
    #     "Ne fournis aucun texte ou explication supplementaire en dehors du JSON. "
    #     f"Ne repete aucune question presente dans cette liste : {question_posee}"
    # )
    prompt = (
        "Genere une devinette de culture generale d'un niveau moyen-dur, longue et detaillee, "
        "sur un fait historique, scientifique ou culturel"
        "La question doit etre formulee avec plusieurs phrases, donnant des indices subtils, mais jamais suffisants pour une recherche directe. "
        "La reponse doit etre precise, courte (1 a 3 mots), et sans ambiguite. "
        "Respecte un format JSON STRICT : {\"question\": \"...\", \"answer\": \"...\"}. "
        "Ne fournis aucun texte ou explication supplementaire en dehors du JSON. "
    )

    try:
        response = await client_ia.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        content = response.choices[0].message.content.strip()

        if not content:
            print("Reponse vide de l API")
            return ("Erreur : reponse vide", "Aucune")

        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.IGNORECASE).strip()
        data = json.loads(content)

        question = data.get("question")
        answer = data.get("answer")

        if not question or not answer:
            print("Le JSON ne contient pas les champs attendus.")
            return ("Erreur : JSON incomplet", "Aucune")

        return (question, answer)

    except Exception as e:
        print("Erreur:", e)
        return ("Erreur de traitement", str(e))