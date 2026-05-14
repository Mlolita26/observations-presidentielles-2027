"""
Applique les corrections issues de la revue Claude (14 mai 2026).

Modifie directement :
 - data/candidats.json (positions, affaires, sources)
 - data/votes-cles.json (Bardella CBAM)
 - data/sources.json (liens Wikipédia nominatifs)
Pas de régénération depuis v6 — les JSON deviennent source de vérité.

Lots A (factuel) + B (wording) + C (architecture accueil).
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'


def load(name):
    return json.loads((DATA / name).read_text(encoding='utf-8'))


def save(name, obj):
    (DATA / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')


def update_text_in_file(path: Path, replacements):
    """Effectue plusieurs search/replace dans un fichier texte."""
    text = path.read_text(encoding='utf-8')
    for old, new in replacements:
        text = text.replace(old, new)
    path.write_text(text, encoding='utf-8')


# ----------------------------------------------------------------------------
# LOT A.1 — Sujet Société rempli
# ----------------------------------------------------------------------------

SOCIETE_POSITIONS = {
    'bardella': {
        'value': "Position RN sur IVG : favorable au droit à l'IVG mais opposé à sa constitutionnalisation (abstention du groupe RN au Congrès du 4 mars 2024). Position sur fin de vie : prudente, le programme RN 2024 ne soutient pas l'aide à mourir.",
        'source_url': 'https://www.publicsenat.fr/',
        'source_label': 'Public Sénat — Congrès Versailles 04/03/2024 ; programme RN 2024',
    },
    'philippe': {
        'value': "Soutien à la constitutionnalisation de l'IVG. Soutien public au projet de loi sur la fin de vie (Horizons aligné sur la majorité présidentielle 2024 portant le texte).",
        'source_url': 'https://horizonsleparti.fr/',
        'source_label': 'Horizons — programme et déclarations publiques',
    },
    'retailleau': {
        'value': "CONTRE la constitutionnalisation de l'IVG (rare sénateur LR à avoir voté contre au Congrès du 4 mars 2024). Position publique CONTRE l'aide à mourir, constante (interventions Sénat et tribunes Le Figaro 2024-2025).",
        'source_url': 'https://www.publicsenat.fr/',
        'source_label': 'Public Sénat — Congrès Versailles 04/03/2024 + tribunes Le Figaro',
    },
    'melenchon': {
        'value': "Soutien fort au droit à l'IVG et à sa constitutionnalisation. Programme LFI 2022 inclut l'extension du délai légal d'IVG et un assouplissement de la loi sur la fin de vie.",
        'source_url': 'https://melenchon.fr/',
        'source_label': 'melenchon.fr et programme « L\'Avenir en commun » LFI 2022',
    },
    'attal': {
        'value': "POUR la constitutionnalisation de l'IVG (texte porté par le gouvernement Attal au Congrès du 4 mars 2024). POUR l'aide à mourir, vote nominal AN scrutin n°2107 du 27/05/2025.",
        'source_url': 'https://www.assemblee-nationale.fr/dyn/17/scrutins/2107',
        'source_label': 'AN — scrutin n°2107 du 27/05/2025 + Congrès Versailles 04/03/2024',
    },
}


def apply_lot_a1_societe(cand):
    for slug, payload in SOCIETE_POSITIONS.items():
        cand['candidats'][slug].setdefault('positions', {})['societe'] = payload
    return cand


# ----------------------------------------------------------------------------
# LOT A.2 — Mélenchon condamnation définitive
# ----------------------------------------------------------------------------

def apply_lot_a2_melenchon_condamnation(cand):
    affaires = cand['candidats']['melenchon'].get('affaires', [])
    for a in affaires:
        if a.get('intitule') and 'Perquisition LFI 2018' in a['intitule']:
            a['nature'] = 'Condamnation définitive'
            a['statut_juridique'] = (
                "Condamné le 09/12/2019 par le tribunal correctionnel de Bobigny à 3 mois "
                "d'emprisonnement avec sursis + 8 000 € d'amende pour rébellion, "
                "provocation à la rébellion et injure envers magistrats. Mélenchon a "
                "renoncé à l'appel : la condamnation est devenue définitive à l'expiration "
                "du délai d'appel (fin décembre 2019). La peine complémentaire "
                "d'inéligibilité n'a pas été prononcée."
            )
            a['annee'] = 'Faits 2018, condamnation 2019, définitive fin 2019'
    return cand


# ----------------------------------------------------------------------------
# LOT A.3 — Casse partis (Rassemblement national / La France insoumise)
# ----------------------------------------------------------------------------

CASSE_REPLACEMENTS = [
    # Variantes courantes
    ('Rassemblement National', 'Rassemblement national'),
    ('La France Insoumise', 'La France insoumise'),
    ('LA FRANCE INSOUMISE', 'La France insoumise'),
    ('RASSEMBLEMENT NATIONAL', 'Rassemblement national'),
]


def apply_lot_a3_casse_in_json(obj):
    """Récursivement remplace dans toutes les chaînes."""
    if isinstance(obj, dict):
        return {k: apply_lot_a3_casse_in_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [apply_lot_a3_casse_in_json(v) for v in obj]
    if isinstance(obj, str):
        out = obj
        for old, new in CASSE_REPLACEMENTS:
            out = out.replace(old, new)
        return out
    return obj


# ----------------------------------------------------------------------------
# LOT A.4 — Bardella CBAM clarifié (positions climat + vote 2023 ajouté)
# ----------------------------------------------------------------------------

def apply_lot_a4_bardella_cbam(cand, votes):
    # Reformuler la position climat Bardella pour préciser CBAM
    pos = cand['candidats']['bardella'].get('positions', {})
    if 'climat' in pos:
        old = pos['climat']['value']
        # Remplacer "POUR CBAM (2025)" par formulation distinguant 2023/2025
        if 'CBAM' in old:
            pos['climat']['value'] = (
                "A voté contre la majorité des grands textes climat européens 2020-2025 "
                "(Loi européenne climat 2020 et 2025, Nature Restoration 2023+2024, "
                "Pesticides 2023, Renewable Energy Directive 2023). Sur le CBAM "
                "(taxe carbone aux frontières) : abstention sur le vote initial du 18/04/2023, "
                "POUR sur la révision du 10/09/2025 (simplification et renforcement). "
                "Programme RN : pro-nucléaire, opposition au Pacte vert européen."
            )
    # Ajouter le vote 2023 dans votes-cles.json (si pas déjà présent)
    has_cbam_2023 = any(
        '2023' in str(v.get('annee', '')) and 'CBAM' in (v.get('texte') or '')
        for v in votes
    )
    if not has_cbam_2023:
        votes.append({
            'theme': 'Climat',
            'texte': 'Carbon Border Adjustment Mechanism — vote initial',
            'annee': 2023,
            'source_label': 'HowTheyVote.eu',
            'positions': {
                'bardella': {
                    'position': 'ABSTENTION',
                    'detail': 'Vote 18/04/2023 sur le mécanisme initial CBAM',
                    'source_url': 'https://howtheyvote.eu/votes/154165',
                    'source_label': 'HowTheyVote.eu vote 154165',
                },
                'philippe': {'position': 'N/A', 'detail': None},
                'retailleau': {'position': 'N/A', 'detail': None},
                'melenchon': {'position': 'N/A', 'detail': None},
                'attal': {'position': 'N/A', 'detail': None},
            },
        })
    return cand, votes


# ----------------------------------------------------------------------------
# LOT A.5 — Wikipédia génériques → pages nominatives
# ----------------------------------------------------------------------------

WIKI_NOMINATIF = {
    'bardella': 'https://fr.wikipedia.org/wiki/Jordan_Bardella',
    'philippe': 'https://fr.wikipedia.org/wiki/%C3%89douard_Philippe',
    'retailleau': 'https://fr.wikipedia.org/wiki/Bruno_Retailleau',
    'melenchon': 'https://fr.wikipedia.org/wiki/Jean-Luc_M%C3%A9lenchon',
    'attal': 'https://fr.wikipedia.org/wiki/Gabriel_Attal',
}


def apply_lot_a5_wikipedia(cand):
    for slug, url in WIKI_NOMINATIF.items():
        c = cand['candidats'].get(slug, {})
        for section in ('identite', 'patrimoine', 'positions'):
            sect = c.get(section, {})
            for k, v in sect.items():
                if isinstance(v, dict) and v.get('source_url') == 'https://fr.wikipedia.org/':
                    v['source_url'] = url
                    v['source_label'] = f'Wikipédia — {c.get("nom", slug)}'
    return cand


# ----------------------------------------------------------------------------
# LOT B — Reformulations neutralité
# ----------------------------------------------------------------------------

WORDING_REPLACEMENTS = [
    # B.1 — Bardella Ukraine : "soutien tardif, refus de certaines livraisons"
    (
        "Soutien tardif, refus de certaines livraisons (programme RN).",
        "Programme RN 2024 : soutien financier oui, refus des livraisons d'armes longue portée.",
    ),
    # B.2 — Mélenchon Ukraine : "position pacifiste contestée"
    (
        "Critique OTAN, position pacifiste contestée",
        "Critique de l'OTAN, refus des sanctions économiques (programme LFI 2022). Soutien à l'Ukraine en tant que peuple agressé mais refus de l'envoi d'armes.",
    ),
    # B.3 — Bardella climat : "Climato-prudent"
    (
        'Climato-prudent. Au PE :',
        'Au PE :',
    ),
    # B.4 — Mélenchon manifestation 1er mai 2025 : retirer "avec drapeaux palestiniens et soutien Gaza"
    (
        "1er mai 2025 Paris (avec drapeaux palestiniens et soutien Gaza)",
        "1er mai 2025 Paris (manifestation syndicale)",
    ),
    # B.5 — Bardella profession : "Permanent politique (RN dès 16 ans)"
    (
        'Permanent politique (RN dès 16 ans)',
        'Permanent du Rassemblement national (adhésion 2012)',
    ),
    # B.6 — Mélenchon présidence parti : "figure tutélaire LFI"
    (
        'Aucune (figure tutélaire LFI)',
        "Aucune fonction officielle. Fondateur du Parti de gauche (2008), co-fondateur de La France insoumise (2016)",
    ),
]


def apply_lot_b_wording_in_json(obj):
    if isinstance(obj, dict):
        return {k: apply_lot_b_wording_in_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [apply_lot_b_wording_in_json(v) for v in obj]
    if isinstance(obj, str):
        out = obj
        for old, new in WORDING_REPLACEMENTS:
            out = out.replace(old, new)
        return out
    return obj


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------

def main():
    print('Chargement des JSON existants...')
    cand = load('candidats.json')
    votes = load('votes-cles.json')
    sources = load('sources.json')

    print()
    print('=== LOT A — Factuel ===')
    print('A.1 Sujet Société (5 positions)...')
    cand = apply_lot_a1_societe(cand)
    print('A.2 Mélenchon condamnation définitive...')
    cand = apply_lot_a2_melenchon_condamnation(cand)
    print('A.3 Casse partis (Rassemblement national, La France insoumise)...')
    cand = apply_lot_a3_casse_in_json(cand)
    votes = apply_lot_a3_casse_in_json(votes)
    sources = apply_lot_a3_casse_in_json(sources)
    print('A.4 Bardella CBAM (vote 2023 ajouté, climat reformulé)...')
    cand, votes = apply_lot_a4_bardella_cbam(cand, votes)
    print('A.5 Liens Wikipédia nominatifs...')
    cand = apply_lot_a5_wikipedia(cand)

    print()
    print('=== LOT B — Wording neutralité ===')
    cand = apply_lot_b_wording_in_json(cand)
    print('Reformulations appliquées (6 phrases-cibles)')

    print()
    print('Sauvegarde...')
    save('candidats.json', cand)
    save('votes-cles.json', votes)
    save('sources.json', sources)

    # Patch HTML : casse partis dans les pages statiques
    print()
    print('=== LOT A.3 (suite) — Casse partis dans HTML/CSS/JS ===')
    for fname in ['index.html', 'candidat.html', 'comparer.html', 'sujet.html',
                  'glossaire.html', 'methodologie.html', 'README.md']:
        p = ROOT / fname
        if p.exists():
            update_text_in_file(p, CASSE_REPLACEMENTS)
    update_text_in_file(ROOT / 'assets' / 'script.js', CASSE_REPLACEMENTS)
    print('  Fichiers HTML/JS/README mis à jour.')

    print()
    print('OK. Lots A et B appliqués.')
    print(f'Voir data/revue_v3_actions.md pour les points fragiles à reconfirmer.')


if __name__ == '__main__':
    main()
