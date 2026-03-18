import subprocess
import sys
import datetime
from pathlib import Path

def upgrade_all():
    print("🔄 Mise à jour de tous les modules Python dans le venv...")

    # Récupération des paquets obsolètes
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--outdated"],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print("❌ Erreur pour récupérer les paquets obsolètes.")
        print(result.stderr)
        return

    outdated = []
    lines = result.stdout.splitlines()
    for line in lines[2:]:
        if line.strip():
            pkg = line.split()[0]
            outdated.append(pkg)

    if not outdated:
        print("✅ Tous les paquets sont déjà à jour.")
    else:
        for package in outdated:
            print(f"⬆️ Mise à jour de {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", package])

    # Création du fichier requirements daté
    today = datetime.date.today().isoformat()
    backup_dir = Path("/home/ravaste/backups/requierement_bot")
    backup_dir.mkdir(parents=True, exist_ok=True)

    filename = backup_dir / f"requirements_du_{today}.txt"
    print(f"📝 Sauvegarde des dépendances dans {filename}")
    with open(filename, "w") as f:
        subprocess.run([sys.executable, "-m", "pip", "freeze"], stdout=f)

    # Garder uniquement les 7 plus récents
    files = sorted(backup_dir.glob("requirements_du_*.txt"), key=lambda f: f.stat().st_mtime, reverse=True)
    for old_file in files[7:]:
        print(f"🗑️ Suppression de l’ancien fichier : {old_file}")
        old_file.unlink()

    print("✅ Mise à jour et sauvegarde terminées !")

if __name__ == "__main__":
    upgrade_all()
