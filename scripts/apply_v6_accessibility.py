"""
Revue v6 — Accessibilité pour utilisateur non politisé.

 - Ajoute `enonce_simple` à chaque position publique (1-2 phrases courtes, langage simple)
 - Garde l'`enonce` actuel comme "détail" (techniquement complet)
 - Le rendu (script.js + build_static_pages.py) sera adapté pour afficher
   enonce_simple par défaut, et l'original sous un bouton "Détail"
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'


# Versions simples — 1-2 phrases courtes, vocabulaire courant
POSITIONS_SIMPLES = {
    # ---- Immigration ----
    ('bardella', 'immigration'): "Veut beaucoup moins d'immigration. Pour la fin du regroupement familial (faire venir sa famille en France). Au Parlement européen, a voté contre le grand texte d'asile de 2024.",
    ('philippe', 'immigration'): "Veut mieux contrôler l'immigration, sans extrême. Position de fermeté modérée.",
    ('retailleau', 'immigration'): "Veut beaucoup moins d'immigration. Ligne très ferme assumée. Ministre de l'Intérieur depuis 2024, il pilote la politique migratoire.",
    ('melenchon', 'immigration'): "Pour un accueil digne des migrants. Contre les lois qui durcissent les conditions d'entrée et de séjour.",
    ('attal', 'immigration'): "Pour une politique migratoire ferme. A soutenu les lois d'immigration récentes (Darmanin 2024, Retailleau).",

    # ---- Europe ----
    ('bardella', 'europe'): "Veut moins de pouvoirs pour l'Union européenne et plus pour la France. Vision d'une « Europe des nations ».",
    ('philippe', 'europe'): "Très favorable à l'Union européenne. Veut renforcer la coopération européenne.",
    ('retailleau', 'europe'): "Favorable à l'Europe mais souveraine : une « Europe des nations confiantes » plutôt qu'une Europe centralisée.",
    ('melenchon', 'europe'): "Critique l'Europe actuelle qu'il juge trop libérale. Veut la transformer profondément, voire en désobéir aux traités.",
    ('attal', 'europe'): "Très favorable à l'Europe. Vision pro-marché commun et coopération renforcée.",

    # ---- Climat ----
    ('bardella', 'climat'): "Pour le nucléaire, contre les éoliennes. Au Parlement européen, a voté contre la plupart des grandes lois écologistes (loi climat, restauration nature, pesticides). Opposé au Pacte vert européen.",
    ('philippe', 'climat'): "Pour le nucléaire et une transition écologique progressive, sans rupture brutale avec l'économie actuelle.",
    ('retailleau', 'climat'): "Pour le nucléaire. Critique certaines normes écologistes qu'il juge trop contraignantes pour les entreprises et l'agriculture.",
    ('melenchon', 'climat'): "Pour une planification écologique forte (l'État pilote la transition). Veut sortir progressivement du pétrole et du nucléaire.",
    ('attal', 'climat'): "Pour le nucléaire ET les énergies renouvelables ensemble. Position du gouvernement actuel.",

    # ---- Économie / Fiscalité ----
    ('bardella', 'fiscalite'): "Veut baisser la TVA sur les produits du quotidien (alimentation, énergie). Évoque une taxe sur les très gros pollueurs.",
    ('philippe', 'fiscalite'): "Veut stabiliser les impôts et alléger les charges des entreprises pour favoriser l'emploi.",
    ('retailleau', 'fiscalite'): "Veut baisser les impôts et réduire les dépenses de l'État.",
    ('melenchon', 'fiscalite'): "Pour taxer beaucoup plus les hauts revenus et les grandes fortunes. Veut rétablir l'ISF (impôt sur la fortune).",
    ('attal', 'fiscalite'): "Veut baisser les impôts pour aider les entreprises à produire en France.",

    # ---- Retraites ----
    ('bardella', 'retraites'): "Contre la retraite à 64 ans. A voté contre la réforme de 2023.",
    ('philippe', 'retraites'): "Pour la retraite à 64 ans. A soutenu la réforme de 2023.",
    ('retailleau', 'retraites'): "Pour la retraite à 64 ans. A soutenu la réforme de 2023.",
    ('melenchon', 'retraites'): "Totalement contre la retraite à 64 ans. Veut revenir à 60 ans.",
    ('attal', 'retraites'): "Pour la retraite à 64 ans. A défendu la réforme au gouvernement (porte-parole, puis ministre).",

    # ---- Sécurité ----
    ('bardella', 'securite'): "Pour plus de police et des peines plus fermes. Veut des « peines minimum » automatiques pour les criminels.",
    ('philippe', 'securite'): "Pour plus de fermeté mais sans toucher aux libertés fondamentales.",
    ('retailleau', 'securite'): "Pour plus de police et des sanctions plus dures. Ministre de l'Intérieur depuis 2024.",
    ('melenchon', 'securite'): "Critique l'approche tout-sécuritaire. Pour plus de moyens dans l'éducation et le social pour prévenir.",
    ('attal', 'securite'): "Pour la fermeté. A soutenu les lois sécurité du gouvernement (loi Darmanin notamment).",

    # ---- Ukraine ----
    ('bardella', 'ukraine'): "Soutien plutôt prudent. Pour l'aide financière, mais contre l'envoi d'armes lourdes.",
    ('philippe', 'ukraine'): "Soutien sans réserve à l'Ukraine.",
    ('retailleau', 'ukraine'): "Soutien sans réserve à l'Ukraine.",
    ('melenchon', 'ukraine'): "Soutient le peuple ukrainien attaqué, mais contre l'envoi d'armes. Critique de l'OTAN.",
    ('attal', 'ukraine'): "Soutien sans réserve à l'Ukraine.",

    # ---- Société ----
    ('bardella', 'societe'): "Pour le droit à l'IVG, mais contre son inscription dans la Constitution. Plutôt opposé à l'aide à mourir.",
    ('philippe', 'societe'): "Pour l'inscription de l'IVG dans la Constitution. Pour la loi sur la fin de vie.",
    ('retailleau', 'societe'): "Contre l'inscription de l'IVG dans la Constitution. Contre l'aide à mourir.",
    ('melenchon', 'societe'): "Pour étendre le droit à l'IVG. Pour la loi sur la fin de vie.",
    ('attal', 'societe'): "Pour l'inscription de l'IVG dans la Constitution (porté par son gouvernement). Pour l'aide à mourir.",
}


def main():
    cand_d = json.loads((DATA / 'candidats.json').read_text(encoding='utf-8'))
    candidats = cand_d['candidats']
    n_added = 0
    for (slug, sujet_key), simple in POSITIONS_SIMPLES.items():
        c = candidats.get(slug, {})
        positions = c.setdefault('positions', {})
        if sujet_key not in positions:
            positions[sujet_key] = {'value': simple, 'enonce_simple': simple}
        else:
            positions[sujet_key]['enonce_simple'] = simple
        n_added += 1
    (DATA / 'candidats.json').write_text(
        json.dumps(cand_d, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print(f'OK : {n_added} positions enonce_simple ajoutées dans candidats.json')


if __name__ == '__main__':
    main()
