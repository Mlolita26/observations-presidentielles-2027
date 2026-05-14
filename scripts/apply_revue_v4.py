"""
Applique les 3 actions automatisables issues de la revue v2 / rapport gisements.

1. Action 1 : Encart "Volume de données disponibles" par fiche candidat
   - Modifie candidats.json en ajoutant un champ `_volume_donnees` lu par
     build_static_pages.py et le rendu dynamique
2. Action 2 : Bardella → mention légale "DSP non exigible pour eurodéputé"
   - Modifie le payload patrimoine.patrimoine_declare de Bardella
3. Action 3 : Sources primaires sur positions synthèses
   - Pour chaque candidat × chaque sujet, attribue source_url quand vide
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'


def load(name): return json.loads((DATA / name).read_text(encoding='utf-8'))
def save(name, obj): (DATA / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')


# ----------------------------------------------------------------------------
# ACTION 1 — Volume de données disponibles par fiche
# ----------------------------------------------------------------------------

VOLUME_NOTES = {
    'bardella': {
        'titre': "Volume de données disponibles : très élevé",
        'detail': "Eurodéputé depuis 2019, sur toute la fenêtre 2020-2026. 24 112 votes nominaux traçables au Parlement européen (dataset HowTheyVote.eu), 24 votes-clés sélectionnés ici. Profil le plus documenté du panel.",
    },
    'philippe': {
        'titre': "Volume de données parlementaires : nul sur la fenêtre 2020-2026",
        'detail': "Édouard Philippe n'a exercé aucun mandat parlementaire entre 2020 et 2026 (Premier ministre 2017-2020, puis maire du Havre depuis 2010). Les positions de la fiche s'appuient sur ses tribunes, discours et programme Horizons. Aucun vote nominal disponible — c'est une caractéristique structurelle du mandat, pas un manque d'activité politique.",
    },
    'retailleau': {
        'titre': "Volume de données disponibles : moyen-élevé",
        'detail': "Sénateur de Vendée 2004-21/10/2024 puis depuis le 13/11/2025. Activité parlementaire publiée dans les tables nominatives du Sénat. Période ministre Intérieur (sept. 2024-nov. 2025) sans votes parlementaires. Quelques scrutins-clés du Sénat 2020-2024 référencés ici.",
    },
    'melenchon': {
        'titre': "Volume de données parlementaires récentes : nul depuis 22/06/2022",
        'detail': "Jean-Luc Mélenchon est sans mandat électif depuis le 22 juin 2022. Sa fiche parlementaire renvoie principalement à son mandat de député (XVe lég., 2017-2022). Période 2022-2026 documentée par ses prises de position publiques (livres, allocutions, manifestations).",
    },
    'attal': {
        'titre': "Volume de données disponibles : moyen, fragmenté",
        'detail': "Gabriel Attal a alterné député (2017-2018, depuis juillet 2024) et ministre (sept. 2018-juillet 2024, dont Premier ministre janv.-sept. 2024). Les votes nominaux disponibles couvrent essentiellement la période où il était parlementaire. Pendant ses fonctions ministérielles, il portait les textes au lieu de les voter (non comptabilisés dans les votes).",
    },
}


def apply_action_1(cand):
    for slug, payload in VOLUME_NOTES.items():
        cand['candidats'][slug]['_volume_donnees'] = payload
    return cand


# ----------------------------------------------------------------------------
# ACTION 2 — Mention DSP non exigible Bardella
# ----------------------------------------------------------------------------

def apply_action_2(cand):
    bardella = cand['candidats']['bardella']
    pat = bardella.setdefault('patrimoine', {})
    # Patrimoine déclaré : reformulation explicite
    current = pat.get('patrimoine_declare', {})
    new_value = (
        "Eurodéputé sans mandat exécutif national → la déclaration de situation patrimoniale (DSP) "
        "n'est pas exigible légalement (art. 11 de la loi du 11 octobre 2013 relative à la transparence "
        "de la vie publique). Seule la déclaration d'intérêts et d'activités (DIA) est obligatoire. "
        "DIA 2024 consultable sur HATVP. Patrimoine net non public."
    )
    pat['patrimoine_declare'] = {
        'value': new_value,
        'source_url': 'https://www.hatvp.fr/fiche-nominative/?declarant=bardella-jordan',
        'source_label': 'HATVP — page nominative Jordan Bardella (DIA seule, DSP non exigible)',
    }
    return cand


# ----------------------------------------------------------------------------
# ACTION 3 — Sources primaires sur positions synthèses
# ----------------------------------------------------------------------------

# (candidat, sujet) -> (url, label) si vide source_url
POSITION_SOURCES = {
    # Philippe — programme Horizons + tribunes
    ('philippe', 'immigration'): ('https://horizonsleparti.fr/', 'Programme Horizons — politique migratoire'),
    ('philippe', 'climat'): ('https://horizonsleparti.fr/', 'Programme Horizons — transition énergétique'),
    ('philippe', 'fiscalite'): ('https://horizonsleparti.fr/', 'Programme Horizons — fiscalité'),
    ('philippe', 'retraites'): ('https://horizonsleparti.fr/', 'Programme Horizons + déclarations'),
    ('philippe', 'europe'): ('https://horizonsleparti.fr/', 'Programme Horizons — Europe (Renew)'),
    ('philippe', 'securite'): ('https://horizonsleparti.fr/', 'Programme Horizons — sécurité'),
    ('philippe', 'ukraine'): ('https://horizonsleparti.fr/', 'Déclarations publiques Philippe sur l\'Ukraine'),
    # Retailleau — programme LR + tribunes Le Figaro + scrutins Sénat
    ('retailleau', 'immigration'): ('https://republicains.fr/', 'Programme LR + Place Beauvau (ministre Intérieur)'),
    ('retailleau', 'climat'): ('https://www.senat.fr/senateur/retailleau_bruno04033b.html', 'Sénat — votes Retailleau loi Climat 2021, Nucléaire 2023'),
    ('retailleau', 'fiscalite'): ('https://republicains.fr/', 'Programme LR — fiscalité'),
    ('retailleau', 'retraites'): ('https://republicains.fr/', 'Programme LR + scrutin Sénat 2023'),
    ('retailleau', 'europe'): ('https://republicains.fr/', 'Programme LR — droite gaulliste pro-européenne'),
    ('retailleau', 'securite'): ('https://www.interieur.gouv.fr/ministres/bruno-retailleau', 'Communiqués ministère Intérieur 2024-2025'),
    ('retailleau', 'ukraine'): ('https://republicains.fr/', 'Programme LR — soutien Ukraine'),
    # Mélenchon — programme LFI 2022 + melenchon.fr
    ('melenchon', 'immigration'): ('https://melenchon.fr/', 'Programme L\'Avenir en commun LFI 2022'),
    ('melenchon', 'climat'): ('https://melenchon.fr/', 'Programme L\'Avenir en commun — planification écologique'),
    ('melenchon', 'fiscalite'): ('https://melenchon.fr/', 'Programme L\'Avenir en commun — fiscalité'),
    ('melenchon', 'retraites'): ('https://melenchon.fr/', 'Programme LFI 2022 — abrogation réforme 2023'),
    ('melenchon', 'europe'): ('https://melenchon.fr/', 'Programme L\'Avenir en commun — plan A/plan B UE'),
    ('melenchon', 'securite'): ('https://melenchon.fr/', 'Programme LFI — libertés publiques'),
    ('melenchon', 'ukraine'): ('https://melenchon.fr/', 'Allocutions Mélenchon 2022-2026 sur l\'Ukraine'),
    # Attal — DPG AN + ligne gouvernementale Renaissance
    ('attal', 'immigration'): ('https://www.assemblee-nationale.fr/dyn/17/comptes-rendus', 'AN — DPG Attal 30/01/2024 + scrutins L17'),
    ('attal', 'climat'): ('https://www.assemblee-nationale.fr/dyn/17/comptes-rendus', 'AN — DPG Attal 30/01/2024 + PLF 2024'),
    ('attal', 'fiscalite'): ('https://www.assemblee-nationale.fr/dyn/17/comptes-rendus', 'AN — DPG Attal 30/01/2024 + PLF 2024 (ministre Comptes publics)'),
    ('attal', 'retraites'): ('https://www.assemblee-nationale.fr/dyn/17/comptes-rendus', 'AN — porte-parole gouv. Borne 2023 (49.3)'),
    ('attal', 'europe'): ('https://gabrielattal.fr/', 'Site officiel Attal + Renaissance'),
    ('attal', 'securite'): ('https://www.assemblee-nationale.fr/dyn/17/comptes-rendus', 'AN — PPL Attal sécurité + loi Darmanin'),
    ('attal', 'ukraine'): ('https://gabrielattal.fr/', 'Renaissance — ligne gouvernementale soutien Ukraine'),
    # Bardella climat : déjà sourcé via HowTheyVote, on garde
}


def apply_action_3(cand):
    n_added = 0
    for (slug, sujet_key), (url, label) in POSITION_SOURCES.items():
        c = cand['candidats'].get(slug, {})
        positions = c.get('positions', {})
        if sujet_key not in positions:
            continue
        p = positions[sujet_key]
        if not p.get('source_url'):
            p['source_url'] = url
            p['source_label'] = label
            n_added += 1
    return cand, n_added


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    cand = load('candidats.json')
    print('Action 1 — Volume de données par candidat...')
    cand = apply_action_1(cand)
    print(f'  {len(VOLUME_NOTES)} encarts ajoutés.')
    print('Action 2 — Mention DSP non exigible (Bardella)...')
    cand = apply_action_2(cand)
    print('  OK.')
    print('Action 3 — Sources primaires sur positions synthèses...')
    cand, n = apply_action_3(cand)
    print(f'  {n} sources ajoutées.')
    save('candidats.json', cand)
    print('candidats.json sauvegardé.')


if __name__ == '__main__':
    main()
