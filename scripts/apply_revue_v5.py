"""
Revue v5 :
 - Ajoute titre_fr (traductions FR) pour les textes du Parlement européen
 - Ajoute resume (1-2 phrases) pour chaque vote-clé
 - Ajoute contexte_candidat pour les votes 'atypiques' (Mélenchon CONTRE climat
   parce qu'insuffisant, Bardella POUR AI Act malgré opposition régulations UE…)
 - Supprime apercu.html (le site interactif suffit)

Usage : py scripts/apply_revue_v5.py
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
# TRADUCTIONS FR pour les textes du Parlement européen
# Clé = texte original en anglais (ou fragment unique)
# ----------------------------------------------------------------------------

TRADUCTIONS_FR = {
    'European Climate Law': 'Loi européenne sur le climat',
    'Carbon Border Adjustment Mechanism: simplification and strengthening':
        'Mécanisme d\'ajustement carbone aux frontières (CBAM) — simplification et renforcement',
    'Carbon Border Adjustment Mechanism — vote initial':
        'Mécanisme d\'ajustement carbone aux frontières (CBAM) — vote initial',
    'Investments and reforms for European competitiveness and the creation of a Capital Markets Union':
        'Investissements et réformes pour la compétitivité européenne et l\'Union des marchés de capitaux',
    'Renewable Energy Directive': 'Directive énergies renouvelables (RED III)',
    'Asylum and migration management': 'Gestion de l\'asile et de la migration (Pacte UE)',
    'Common procedure for international protection in the Union':
        'Procédure commune de protection internationale dans l\'Union (Pacte UE)',
    '2022 discharge: European Border and Coast Guard Agency':
        'Décharge 2022 — Agence européenne de garde-frontières et de garde-côtes (Frontex)',
    'Amending Regulation (EU) 2024/792 establishing the Ukraine Facility':
        'Modification du règlement établissant la Facilité Ukraine',
    'Establishing the Ukraine Facility': 'Établissement de la Facilité Ukraine (50 Md€)',
    'Adequate minimum wages in the European Union': 'Salaires minimaux adéquats dans l\'Union européenne',
    'Common agricultural policy (CAP) 2021–2027': 'Politique agricole commune (PAC) 2021-2027',
    'Fair working conditions, rights and social protection for platform workers - New forms of employment linked to digital development':
        'Conditions de travail et protection sociale des travailleurs des plateformes numériques',
    'Improving working conditions in platform work': 'Amélioration des conditions de travail des travailleurs de plateformes',
    'Increasing the attractiveness of public capital markets and facilitating access to capital for SMEs – amending directive':
        'Renforcement des marchés de capitaux publics et accès au financement pour les PME',
    'Artificial Intelligence Act': 'Règlement européen sur l\'intelligence artificielle (AI Act)',
    'Sustainable use of plant protection products': 'Utilisation durable des produits phytosanitaires (pesticides)',
    'Nature restoration': 'Règlement sur la restauration de la nature',
    'Corporate sustainability due diligence': 'Devoir de vigilance des entreprises en matière de durabilité',
    'Situation in Hungary and frozen EU funds': 'Situation en Hongrie et fonds européens gelés',
    'Existence of a clear risk of a serious breach by Hungary of the values on which the Union is founded':
        'Hongrie — risque manifeste de violation grave des valeurs de l\'Union (Article 7 TUE)',
    'The human cost of Russia’s war against Ukraine and the urgent need to end Russian aggression: the situation of illegally detained civilians and prisoners of war, and the continued':
        'Coût humain de la guerre russe contre l\'Ukraine et civils détenus illégalement',
    'Definition of criminal offences and penalties for the violation of Union restrictive measures':
        'Sanctions pénales en cas de violation des mesures restrictives de l\'Union (Russie)',
    'Future of agriculture and the post-2027 common agricultural policy':
        'Avenir de l\'agriculture et politique agricole commune post-2027',
    'Loi européenne sur le climat (Fit for 55)':
        'Loi européenne sur le climat (paquet Fit for 55)',
}


# ----------------------------------------------------------------------------
# RÉSUMÉS — 1-2 phrases factuelles sur ce que la loi contient
# Clé = texte (français ou anglais, on cherche par titre)
# ----------------------------------------------------------------------------

RESUMES = {
    # ---- Climat ----
    'European Climate Law': 'Établit l\'objectif contraignant de neutralité climatique de l\'UE d\'ici 2050 et un objectif intermédiaire de -55 % d\'émissions de gaz à effet de serre en 2030 (par rapport à 1990).',
    'Carbon Border Adjustment Mechanism: simplification and strengthening':
        'Révision du CBAM (taxe carbone aux frontières) : simplifie les procédures pour les importateurs et renforce les outils anti-contournement (substitution, exportations).',
    'Carbon Border Adjustment Mechanism — vote initial':
        'Création du CBAM (taxe carbone aux frontières) : applique le prix du carbone européen aux importations à fort contenu carbone (acier, aluminium, ciment, engrais, hydrogène, électricité). Évite les délocalisations.',
    'Renewable Energy Directive': 'Directive RED III : porte à 42,5 % la part des énergies renouvelables dans la consommation finale de l\'UE en 2030, avec procédures d\'autorisation accélérées.',
    'Sustainable use of plant protection products': 'Proposition visant à réduire de 50 % l\'usage et les risques des pesticides chimiques d\'ici 2030, avec interdiction dans les zones sensibles. Rejetée au PE en novembre 2023.',
    'Nature restoration': 'Règlement obligeant les États membres à restaurer 20 % des terres et des mers de l\'UE d\'ici 2030 (zones humides, forêts, écosystèmes marins).',
    'Loi Climat et Résilience': 'Loi de 2021 traduisant des propositions de la Convention citoyenne pour le climat : interdiction des vols intérieurs sur les lignes < 2h30 (Art. 36), encadrement publicité énergies fossiles, rénovation thermique des bâtiments, zones à faibles émissions.',
    'Loi accélération production énergies renouvelables': 'Loi de 2023 facilitant l\'implantation d\'éoliennes, panneaux solaires et autres ENR, avec des « zones d\'accélération » définies par les communes.',
    'Loi relance du nucléaire': 'Loi de 2023 simplifiant les procédures de construction de nouveaux réacteurs nucléaires (programmation des EPR2) et levant certaines limites antérieures.',
    'Future of agriculture and the post-2027 common agricultural policy':
        'Rapport d\'initiative parlementaire sur les orientations de la prochaine PAC (après 2027). Non contraignant.',
    'Common agricultural policy (CAP) 2021–2027':
        'Réforme de la Politique agricole commune pour la période 2021-2027 : éco-régimes obligatoires, conditionnalité environnementale renforcée, redistribution des aides.',
    'Loi industrie verte': 'Loi de 2023 visant à attirer les industries vertes en France (procédures d\'autorisation raccourcies, crédit d\'impôt, fléchage de l\'épargne).',
    'Loi européenne sur le climat (Fit for 55)':
        'Paquet législatif européen pour atteindre -55 % d\'émissions en 2030 : révision du marché carbone (SEQE/ETS), CBAM, fonds social pour le climat, normes CO2 voitures.',
    # ---- Retraites ----
    'Réforme des retraites (49.3)': 'Réforme de 2023 reculant l\'âge légal de départ à la retraite de 62 à 64 ans et accélérant l\'allongement de la durée de cotisation (43 ans en 2027). Adoptée par engagement de responsabilité (49.3) le 16 mars 2023.',
    # ---- Immigration ----
    'Loi immigration Darmanin': 'Loi du 26 janvier 2024 sur le contrôle de l\'immigration : durcissement des conditions de regroupement familial, prestations sociales différenciées, expulsion d\'étrangers délinquants. Certaines dispositions censurées par le Conseil constitutionnel.',
    'Asylum and migration management': 'Règlement du Pacte UE asile et migration : mécanisme de solidarité obligatoire entre États membres (accueil ou contribution financière), gestion partagée des arrivées.',
    'Common procedure for international protection in the Union': 'Volet du Pacte UE asile : procédures accélérées d\'asile aux frontières externes, screening obligatoire.',
    '2022 discharge: European Border and Coast Guard Agency':
        'Vote d\'approbation (ou de rejet) de la gestion budgétaire 2022 de Frontex (Agence européenne de garde-frontières). Geste politique reflétant la position sur l\'agence.',
    'Pacte asile et migration UE': 'Ensemble de 10 textes adoptés le 10 avril 2024 réformant la politique européenne d\'asile et de gestion des frontières.',
    # ---- Économie / Travail ----
    'PLF 2024 (vote solennel)': 'Projet de loi de finances pour 2024 : budget de l\'État (recettes, dépenses, déficit). Adoption à l\'AN par 49.3, contre-vote sénatorial avec 7 Md€ d\'économies supplémentaires.',
    'PLF 2025 (vote solennel)': 'Projet de loi de finances pour 2025 : budget de l\'État dans un contexte de plan d\'économies post-censure Barnier. Adoption définitive le 6 février 2025.',
    'Loi plein emploi': 'Loi de 2023 visant le plein emploi : création de France Travail (ex-Pôle emploi), conditions renforcées d\'accompagnement des bénéficiaires du RSA (15 h d\'activité hebdo).',
    'Adequate minimum wages in the European Union': 'Directive européenne fixant un cadre pour les salaires minimaux dans l\'UE : critères d\'adéquation (60 % du salaire médian), promotion de la négociation collective.',
    'Fair working conditions, rights and social protection for platform workers - New forms of employment linked to digital development':
        'Résolution non contraignante du PE sur les conditions de travail des travailleurs des plateformes numériques (Uber, Deliveroo…).',
    'Improving working conditions in platform work': 'Directive européenne sur les travailleurs des plateformes : présomption de salariat dans certaines conditions, transparence des algorithmes de management.',
    'Increasing the attractiveness of public capital markets and facilitating access to capital for SMEs – amending directive':
        'Listing Act : modifications pour faciliter l\'introduction en bourse des PME européennes (allègement obligations d\'information).',
    # ---- Europe / Souveraineté ----
    'Règlement IA (AI Act)': 'Premier cadre juridique mondial sur l\'IA, adopté en mars 2024. Classe les systèmes d\'IA par niveau de risque (interdit / haut / limité / minimal) et impose des obligations proportionnées.',
    'Artificial Intelligence Act': 'Premier cadre juridique mondial sur l\'IA, adopté en mars 2024. Classe les systèmes d\'IA par niveau de risque et impose des obligations proportionnées.',
    'Corporate sustainability due diligence': 'Directive CSDDD : oblige les grandes entreprises à identifier et corriger les atteintes aux droits humains et à l\'environnement dans leur chaîne de valeur.',
    'Situation in Hungary and frozen EU funds': 'Résolution dénonçant les reculs démocratiques en Hongrie et soutenant le gel des fonds européens par la Commission.',
    'Existence of a clear risk of a serious breach by Hungary of the values on which the Union is founded':
        'Procédure de l\'Article 7 du TUE contre la Hongrie pour violation grave des valeurs européennes (État de droit, indépendance de la justice, libertés). Pouvant aller jusqu\'à la suspension des droits de vote au Conseil.',
    'Investments and reforms for European competitiveness and the creation of a Capital Markets Union':
        'Rapport sur la création d\'une véritable Union des marchés de capitaux : intégration financière, harmonisation des règles, financement des transitions.',
    # ---- Sécurité / Justice ----
    'Loi sécurité globale': 'Loi de 2021 renforçant les pouvoirs des polices municipales, encadrant l\'usage des drones, et le très controversé Article 24 sur la diffusion d\'images de policiers (censuré par le Conseil constitutionnel).',
    'Loi confortant les principes de la République (séparatisme)':
        'Loi du 24 août 2021 dite "séparatisme" : contrôle accru des associations, fermeture de lieux de culte radicaux, neutralité des agents publics, lutte contre la haine en ligne, encadrement de l\'instruction à domicile.',
    'Pass sanitaire / vaccinal': 'Lois sanitaires de 2021-2022 imposant un pass sanitaire puis vaccinal pour accéder aux lieux publics et événements, dans le cadre de la pandémie Covid-19.',
    'Loi orientation et programmation justice': 'Loi de programmation 2023-2027 pour la justice : 8 Md€ supplémentaires, embauche de 10 000 magistrats et greffiers, simplification de la procédure pénale.',
    'Motion de censure du gouvernement Barnier': 'Motion de censure transpartisane (RN + NFP) adoptée le 4 décembre 2024 par 331 voix, faisant tomber le gouvernement Barnier. Première motion adoptée depuis 1962.',
    # ---- Ukraine ----
    'Soutien financier à l\'Ukraine (Facilité UE)': 'Programme européen Ukraine Facility : 50 Md€ d\'aide combinant prêts et dons à l\'Ukraine pour la période 2024-2027 (fonctionnement et reconstruction).',
    'Establishing the Ukraine Facility': 'Création de la Facilité Ukraine : 50 Md€ d\'aide UE (prêts + dons) à l\'Ukraine sur 2024-2027.',
    'The human cost of Russia’s war against Ukraine and the urgent need to end Russian aggression: the situation of illegally detained civilians and prisoners of war, and the continued':
        'Résolution dénonçant le sort des civils ukrainiens détenus illégalement et les violations du droit humanitaire par la Russie.',
    'Definition of criminal offences and penalties for the violation of Union restrictive measures':
        'Directive harmonisant les sanctions pénales en cas de violation des sanctions européennes contre la Russie.',
    # ---- Société ----
    'IVG dans la Constitution': 'Loi constitutionnelle inscrivant dans la Constitution la "liberté garantie" pour la femme d\'avoir recours à l\'IVG. Adoptée au Congrès de Versailles le 4 mars 2024 par 780 voix contre 72.',
    'Fin de vie (projet de loi)': 'Projet de loi créant un droit à "l\'aide à mourir" sous conditions strictes (maladie incurable, souffrances réfractaires) et renforçant les soins palliatifs. Adopté en 1ère lecture à l\'AN le 27 mai 2025.',
}


# ----------------------------------------------------------------------------
# CONTEXTES — Votes "atypiques" méritant explication
# Clé = (titre_partiel, slug_candidat) -> texte de contexte affiché dans le détail
# ----------------------------------------------------------------------------

CONTEXTES_ATYPIQUES = [
    # Mélenchon CONTRE Loi Climat 2021 — jugée insuffisante
    ('Loi Climat et Résilience', 'melenchon',
     "Le groupe LFI a voté CONTRE l'ensemble du texte non par opposition à l'ambition climatique mais en jugeant la loi insuffisante au regard des recommandations de la Convention citoyenne pour le climat (notamment sur les vols intérieurs Art. 36, le rénovation thermique et l'absence de planification écologique contraignante)."),
    # Mélenchon CONTRE Séparatisme — ~40% des articles POUR
    ('Loi confortant les principes de la République (séparatisme)', 'melenchon',
     "Le groupe LFI a voté CONTRE l'ensemble du texte, mais POUR environ 40 % des articles examinés séparément (notamment sur l'égalité femmes-hommes et la lutte contre la haine en ligne). Position publique : Mélenchon a qualifié la loi de « inutile et dangereuse » (01/02/2021)."),
    # Retailleau CONTRE IVG Constitution — rare LR
    ('IVG dans la Constitution', 'retailleau',
     "Bruno Retailleau fait partie des rares sénateurs LR à avoir voté CONTRE la constitutionnalisation de l'IVG au Congrès du 4 mars 2024 (780 POUR / 72 CONTRE). Position défendue publiquement avant le vote : favorable au droit à l'IVG dans la loi ordinaire, mais opposé à son inscription constitutionnelle."),
    # Bardella POUR AI Act — pourtant souverainiste
    ('Artificial Intelligence Act', 'bardella',
     "Vote POUR atypique pour un eurodéputé du groupe ID/PfE habituellement opposé aux régulations européennes. Motif : protection des industries européennes face aux acteurs américains et chinois (alignement souverainiste-protectionniste)."),
    ('Règlement IA (AI Act)', 'bardella',
     "Vote POUR atypique pour un eurodéputé du groupe ID/PfE habituellement opposé aux régulations européennes. Motif : protection des industries européennes face aux acteurs américains et chinois (alignement souverainiste-protectionniste)."),
    # Bardella POUR CBAM 2025 — pas pro-climat mais protectionnisme
    ('Carbon Border Adjustment Mechanism: simplification', 'bardella',
     "Vote POUR la révision du CBAM, à mettre en regard de l'opposition générale du RN aux textes climat européens. La logique est protectionniste (taxer les importations carbonées) plus que climatique, alignée avec la doctrine souverainiste."),
    # Bardella POUR PAC 2021 — dissident de son groupe
    ('Common agricultural policy (CAP) 2021', 'bardella',
     "Vote POUR la PAC, dissident de la majorité du groupe ID à l'époque (qui a majoritairement voté CONTRE). Position cohérente avec l'attachement RN au monde agricole français."),
    # Bardella POUR plateformes — protection sociale
    ('Improving working conditions in platform work', 'bardella',
     "Vote POUR la directive plateformes (Uber, Deliveroo), à rebours de l'opposition habituelle du groupe ID aux textes sociaux européens. Motif : protection de catégories populaires de salariés."),
    # Mélenchon CONTRE Pass sanitaire
    ('Pass sanitaire / vaccinal', 'melenchon',
     "Le groupe LFI a voté CONTRE à l'unanimité, motion de rejet préalable portée par Mélenchon. Position publique : opposition au pass sur des bases de libertés publiques et de non-respect du consentement éclairé, pas anti-vaccinale (Mélenchon s'est lui-même fait vacciner et a appelé à la vaccination volontaire)."),
    # Mélenchon CONTRE Loi sécurité globale
    ('Loi sécurité globale', 'melenchon',
     "Opposition LFI sur les libertés publiques, notamment l'Article 24 (interdiction de diffuser des images de policiers identifiables) que le Conseil constitutionnel a finalement censuré le 20 mai 2021."),
    # Attal POUR fin de vie alors qu'il était PM
    ('Fin de vie (projet de loi)', 'attal',
     "Vote POUR au scrutin n°2107 du 27/05/2025. Position personnelle assumée au-delà de la simple discipline de groupe : le scrutin a permis un vote « selon sa conscience » au sein d'Ensemble pour la République."),
    # Retailleau pro-Sénat amendement art. 1 Climat
    ('Loi Climat et Résilience', 'retailleau',
     "Vote POUR au Sénat en 1ère lecture avec un amendement de Bruno Retailleau adopté sur l'article 1er constitutionnel. Position pragmatique de soutien sous condition d'amendements pro-Sénat."),
]


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    votes = json.loads((DATA / 'votes-cles.json').read_text(encoding='utf-8'))
    print(f'Chargement : {len(votes)} votes-clés')

    n_trad = 0
    n_resume = 0
    n_contexte = 0

    for v in votes:
        texte = v.get('texte') or ''
        # Traduction
        if texte in TRADUCTIONS_FR:
            v['titre_fr'] = TRADUCTIONS_FR[texte]
            n_trad += 1
        # Résumé (par titre original OU par titre FR)
        resume = RESUMES.get(texte) or RESUMES.get(v.get('titre_fr', ''))
        if resume:
            v['resume'] = resume
            n_resume += 1
        # Contextes atypiques
        for partial, slug, ctx in CONTEXTES_ATYPIQUES:
            if partial.lower() in texte.lower():
                # injecte dans v['positions'][slug]
                if 'positions' in v and slug in v['positions']:
                    v['positions'][slug].setdefault('contexte', ctx)
                    n_contexte += 1
                break  # un contexte par texte par candidat

    (DATA / 'votes-cles.json').write_text(
        json.dumps(votes, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    print(f'  titre_fr ajouté    : {n_trad}')
    print(f'  resume ajouté      : {n_resume}')
    print(f'  contextes atypiques: {n_contexte}')
    print()
    print('Suppression apercu.html...')
    apercu = ROOT / 'apercu.html'
    if apercu.exists():
        apercu.unlink()
        print('  Supprimé.')
    else:
        print('  Déjà absent.')
    print('OK.')


if __name__ == '__main__':
    main()
