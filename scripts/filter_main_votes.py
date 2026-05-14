"""
Filtre votes-bruts.json pour ne conserver que les votes PRINCIPAUX du Parlement européen.

Un même texte au PE génère souvent plusieurs scrutins :
 - vote sur chaque amendement
 - vote du texte modifié
 - vote final sur l'ensemble

Seul le vote final (is_main=True dans HowTheyVote) correspond à « la position du
candidat sur le texte ». Les autres sont du bruit qui crée des apparents
doublons dans le drill-down (POUR/CONTRE/POUR le même jour).

Ce script :
 - Lit `Howtheyvote/export/votes.csv` pour repérer les vote_id principaux.
 - Charge `data/votes-bruts.json`.
 - Pour chaque vote PE (ref commence par HTV:), supprime si is_main=False.
 - Garde tous les autres votes (AN, Sénat — pas concernés).
 - Sauvegarde.

Usage : py scripts/filter_main_votes.py
"""
from __future__ import annotations
import csv
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
PROJET = ROOT.parent
DATA = ROOT / 'data'
VOTES_CSV = PROJET / 'Howtheyvote' / 'export' / 'votes.csv'
VOTES_BRUTS_JSON = DATA / 'votes-bruts.json'


def main():
    print(f'Lecture {VOTES_CSV.name}...')
    is_main = {}
    with VOTES_CSV.open(encoding='utf-8', newline='') as f:
        rd = csv.DictReader(f)
        for r in rd:
            try:
                is_main[int(r['id'])] = (r.get('is_main') == 'True')
            except (ValueError, KeyError):
                pass
    n_main_total = sum(is_main.values())
    print(f'  {len(is_main)} votes PE, dont {n_main_total} votes principaux (is_main=True)')

    print(f'Chargement {VOTES_BRUTS_JSON.name}...')
    vb = json.loads(VOTES_BRUTS_JSON.read_text(encoding='utf-8'))
    n_before_total = sum(sum(len(arr) for arr in d.values()) for d in vb.values())
    print(f'  {n_before_total} votes bruts avant filtrage.')

    n_after_total = 0
    n_removed_pe = 0
    n_kept_non_pe = 0

    for slug, sujets in vb.items():
        for sujet_id, arr in sujets.items():
            kept = []
            for v in arr:
                ref = v.get('ref') or ''
                if ref.startswith('HTV:'):
                    try:
                        vid = int(ref.split(':')[1])
                    except (ValueError, IndexError):
                        # Garde par défaut si on ne peut pas parser
                        kept.append(v)
                        continue
                    if is_main.get(vid):
                        kept.append(v)
                    else:
                        n_removed_pe += 1
                else:
                    # Vote non-PE (AN, Sénat, Congrès) : on garde toujours
                    kept.append(v)
                    n_kept_non_pe += 1
            sujets[sujet_id] = kept
            n_after_total += len(kept)

    print(f'  {n_after_total} votes après filtrage.')
    print(f'  → {n_removed_pe} votes PE non principaux supprimés (amendements et intermédiaires).')
    print(f'  → {n_kept_non_pe} votes non-PE conservés (AN/Sénat/Congrès).')

    # Recompte par candidat pour info
    print()
    print('Par candidat :')
    for slug, sujets in vb.items():
        total = sum(len(arr) for arr in sujets.values())
        print(f'  {slug:12s} : {total} votes')

    VOTES_BRUTS_JSON.write_text(
        json.dumps(vb, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print()
    print('Sauvegardé.')


if __name__ == '__main__':
    main()
