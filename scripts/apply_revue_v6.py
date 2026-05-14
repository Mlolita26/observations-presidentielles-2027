"""
Revue v6 : vulgarisation du contenu pour un utilisateur peu informé.

1. Ajout d'un champ `enonce_simple` à chaque position publique (1-2 phrases
   en langage courant, sans jargon).
2. Le champ `value` existant (texte technique) devient le « détail dépliable ».
3. Intros pédagogiques ajoutées aux tableaux financiers (campagnes, partis)
   directement dans les générateurs (script.js, build_static_pages.py).

Usage : py scripts/apply_revue_v6.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'


# ----------------------------------------------------------------------------
# Versions VULGARISÉES des positions (1-2 phrases courtes, langage simple)
# Clé : (slug_candidat, key_position) -> texte simple
# ----------------------------------------------------------------------------

POSITIONS_SIMPLES = {
    # ====== JORDAN BARDELLA (RN) ======
    ('bardella', 'immigration'): "Veut beaucoup moins d'immigration. Pour la fin du regroupement familial. A voté contre la grande réforme européenne de 2024.",
    ('bardella', 'europe'): "Critique l'Union européenne. Veut rendre plus de pouvoirs aux États. Prône une « Europe des nations ».",
    ('bardella', 'climat'): "Pour le nucléaire, contre les éoliennes. A voté contre la plupart des grandes lois écologistes européennes. Pour la taxe carbone aux frontières (CBAM).",
    ('bardella', 'fiscalite'): "Veut baisser la TVA sur les produits de base (alimentation, énergie). Évoque une taxe sur les plus gros pollueurs.",
    ('bardella', 'retraites'): "Contre la retraite à 64 ans. Veut un retour à 62 ans sous conditions.",
    ('bardella', 'securite'): "Pour plus de police et des peines plus fermes. Soutient l'idée de peines minimum automatiques.",
    ('bardella', 'ukraine'): "Soutien prudent. Pour aider financièrement, contre l'envoi d'armes lourdes à l'Ukraine.",
    ('bardella', 'societe'): "Pour le droit à l'IVG dans la loi, contre son inscription dans la Constitution. Réservé sur l'aide à mourir.",
    # ====== ÉDOUARD PHILIPPE (Horizons) ======
    ('philippe', 'immigration'): "Veut mieux contrôler l'immigration, avec fermeté mais sans extrême.",
    ('philippe', 'europe'): "Très favorable à l'Union européenne. Veut renforcer la coopération entre États membres.",
    ('philippe', 'climat'): "Pour le nucléaire et une transition écologique progressive, sans rupture brutale.",
    ('philippe', 'fiscalite'): "Veut moins de charges sur les entreprises et une stabilité des impôts.",
    ('philippe', 'retraites'): "A soutenu la retraite à 64 ans.",
    ('philippe', 'securite'): "Pour plus de fermeté, mais sans toucher aux libertés fondamentales.",
    ('philippe', 'ukraine'): "Soutien sans réserve à l'Ukraine.",
    ('philippe', 'societe'): "Pour l'IVG dans la Constitution. Pour la loi fin de vie.",
    # ====== BRUNO RETAILLEAU (LR) ======
    ('retailleau', 'immigration'): "Veut beaucoup moins d'immigration. Ligne très ferme, assumée publiquement.",
    ('retailleau', 'europe'): "Favorable à l'Europe mais souverainiste. Parle d'une « Europe des nations confiantes ».",
    ('retailleau', 'climat'): "Pour le nucléaire. Critique certaines normes écologistes qu'il juge trop contraignantes pour l'économie.",
    ('retailleau', 'fiscalite'): "Veut baisser les impôts et les dépenses de l'État.",
    ('retailleau', 'retraites'): "A soutenu la retraite à 64 ans.",
    ('retailleau', 'securite'): "Pour plus de police et des sanctions plus dures. Ministre de l'Intérieur depuis septembre 2024.",
    ('retailleau', 'ukraine'): "Soutien sans réserve à l'Ukraine.",
    ('retailleau', 'societe'): "Contre l'inscription de l'IVG dans la Constitution. Contre l'aide à mourir.",
    # ====== JEAN-LUC MÉLENCHON (LFI) ======
    ('melenchon', 'immigration'): "Pour un accueil digne des migrants. Contre les lois qui durcissent les conditions d'immigration.",
    ('melenchon', 'europe'): "Critique l'Europe libérale actuelle. Veut la transformer en profondeur, sinon en sortir.",
    ('melenchon', 'climat'): "Pour une planification écologique forte. Veut sortir du pétrole et du nucléaire.",
    ('melenchon', 'fiscalite'): "Pour taxer beaucoup plus les hauts revenus et les grandes fortunes. Veut rétablir l'ISF.",
    ('melenchon', 'retraites'): "Totalement contre la retraite à 64 ans. Veut revenir à 60 ans.",
    ('melenchon', 'securite'): "Critique l'approche tout-sécuritaire. Veut plus de moyens éducatifs et sociaux.",
    ('melenchon', 'ukraine'): "Soutien à l'Ukraine comme peuple agressé, mais contre l'envoi d'armes et critique de l'OTAN.",
    ('melenchon', 'societe'): "Pour étendre le droit à l'IVG. Pour la loi fin de vie.",
    # ====== GABRIEL ATTAL (Renaissance) ======
    ('attal', 'immigration'): "Pour une politique ferme. A soutenu les lois immigration récentes.",
    ('attal', 'europe'): "Très favorable à l'Europe. Vision pro-marché commun.",
    ('attal', 'climat'): "Pour le nucléaire et les énergies renouvelables ensemble. Ligne du gouvernement.",
    ('attal', 'fiscalite'): "Veut baisser les impôts pour aider les entreprises à produire en France.",
    ('attal', 'retraites'): "A défendu la retraite à 64 ans, qu'il portait au gouvernement.",
    ('attal', 'securite'): "Pour la fermeté. A soutenu les lois sécurité récentes en tant que ministre.",
    ('attal', 'ukraine'): "Soutien sans réserve à l'Ukraine.",
    ('attal', 'societe'): "Pour l'IVG dans la Constitution (texte porté par son gouvernement). Pour l'aide à mourir (a voté pour à l'AN).",
}


def main():
    cand = json.loads((DATA / 'candidats.json').read_text(encoding='utf-8'))

    n_added = 0
    for (slug, pos_key), simple_text in POSITIONS_SIMPLES.items():
        c = cand['candidats'].get(slug, {})
        positions = c.get('positions', {})
        if pos_key in positions:
            positions[pos_key]['enonce_simple'] = simple_text
            n_added += 1

    (DATA / 'candidats.json').write_text(
        json.dumps(cand, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    print(f'Positions vulgarisées ajoutées : {n_added} / {len(POSITIONS_SIMPLES)}')
    print('OK.')


if __name__ == '__main__':
    main()
