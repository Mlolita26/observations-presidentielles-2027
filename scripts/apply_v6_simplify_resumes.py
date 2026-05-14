"""
Revue v6 — Simplification des résumés et contextes atypiques.

Réécrit les `resume` et `contexte` qui contenaient trop de jargon institutionnel
(49.3, TUE, SEQE/ETS, « doctrine souverainiste-protectionniste »…) en version
accessible à un lecteur non politisé.

Usage : py scripts/apply_v6_simplify_resumes.py
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
# RÉSUMÉS simplifiés — clé = texte original (FR ou EN)
# ----------------------------------------------------------------------------

RESUMES_SIMPLES = {
    # Climat
    'European Climate Law':
        "Loi européenne qui engage l'Union européenne à atteindre zéro émission nette de CO₂ d'ici 2050, avec une étape à -55 % en 2030 par rapport à 1990.",
    'Carbon Border Adjustment Mechanism: simplification and strengthening':
        "Mise à jour de la taxe carbone aux frontières de l'Europe : moins de paperasse pour les importateurs, et plus de moyens pour empêcher les fraudes (entreprises qui essayent de contourner la taxe).",
    'Carbon Border Adjustment Mechanism — vote initial':
        "Création d'une taxe européenne sur les marchandises importées qui polluent beaucoup (acier, ciment, aluminium…). But : empêcher les entreprises européennes d'être pénalisées face à des pays sans règles écologiques.",
    'Renewable Energy Directive':
        "Loi européenne qui fixe un objectif : 42,5 % d'énergies renouvelables (éolien, solaire, etc.) dans l'énergie consommée en Europe d'ici 2030. Accélère aussi les autorisations pour construire ces installations.",
    'Sustainable use of plant protection products':
        "Proposition européenne pour diviser par deux l'usage des pesticides chimiques d'ici 2030 et les interdire dans les zones sensibles (écoles, parcs…). Rejetée par le Parlement européen en novembre 2023.",
    'Nature restoration':
        "Loi européenne qui oblige les pays à restaurer la nature dégradée : 20 % des terres et des mers (zones humides, forêts, mers) doivent être réparées d'ici 2030.",
    'Loi Climat et Résilience':
        "Loi française de 2021 issue de la Convention citoyenne pour le climat. Mesures principales : interdiction des vols intérieurs courts (quand un train < 2h30 existe), interdiction de la publicité pour les énergies fossiles, obligation de rénover les passoires thermiques, zones à faibles émissions dans les grandes villes.",
    'Loi accélération production énergies renouvelables':
        "Loi française de 2023 qui facilite la construction d'éoliennes et de panneaux solaires. Les communes peuvent désigner des « zones d'accélération » où les autorisations sont plus rapides.",
    'Loi relance du nucléaire':
        "Loi française de 2023 qui simplifie les procédures pour construire de nouveaux réacteurs nucléaires (les EPR2). Lève certaines règles qui limitaient le nucléaire.",
    'Future of agriculture and the post-2027 common agricultural policy':
        "Rapport du Parlement européen sur la future politique agricole européenne (après 2027). C'est un texte d'orientation, sans valeur contraignante.",
    'Common agricultural policy (CAP) 2021–2027':
        "Réforme de la politique agricole européenne pour 2021-2027 : les aides aux agriculteurs sont conditionnées à des pratiques plus respectueuses de l'environnement, et redistribuées différemment entre les exploitations.",
    'Loi industrie verte':
        "Loi française de 2023 pour attirer en France des usines fabriquant des produits « verts » (batteries, panneaux solaires, hydrogène…). Raccourcit les autorisations et offre des crédits d'impôt.",
    'Loi européenne sur le climat (Fit for 55)':
        "Paquet de plusieurs lois européennes pour atteindre -55 % d'émissions en 2030. Inclut une réforme du marché du carbone, la taxe carbone aux frontières (CBAM), des normes CO₂ pour les voitures, et un fonds pour aider les ménages modestes.",
    # Retraites
    'Réforme des retraites (49.3)':
        "Réforme de 2023 qui recule l'âge légal de départ à la retraite : de 62 à 64 ans. Le gouvernement l'a fait passer sans vote des députés en utilisant l'article 49.3 de la Constitution (qui permet d'adopter un texte sans le faire voter, sauf si une motion de censure renverse le gouvernement).",
    # Immigration
    'Loi immigration Darmanin':
        "Loi de janvier 2024 qui durcit les conditions d'immigration : limites au regroupement familial, durcissement des conditions pour toucher certaines aides sociales, facilités pour expulser les étrangers délinquants. Plusieurs articles ont été censurés par le Conseil constitutionnel.",
    'Asylum and migration management':
        "Texte européen (partie du Pacte asile et migration) qui oblige les pays de l'Union à se partager l'accueil des migrants. Soit ils accueillent, soit ils paient une contribution financière.",
    'Common procedure for international protection in the Union':
        "Texte européen (partie du Pacte asile et migration) qui crée des procédures accélérées pour traiter les demandes d'asile directement aux frontières de l'Europe.",
    '2022 discharge: European Border and Coast Guard Agency':
        "Vote du Parlement européen sur la gestion de Frontex en 2022. Frontex est l'agence européenne qui surveille les frontières extérieures de l'Union. Voter « pour la décharge » = approuver sa gestion, « contre » = la désapprouver.",
    'Pacte asile et migration UE':
        "Ensemble de 10 lois adoptées le 10 avril 2024 qui réforment toute la politique européenne d'asile et de migration : procédures plus rapides aux frontières, mécanisme de solidarité obligatoire entre pays.",
    # Économie / Travail
    'PLF 2024 (vote solennel)':
        "Budget de l'État français pour 2024. Le gouvernement l'a fait passer à l'Assemblée sans vote (article 49.3). Le Sénat a voté une version modifiée avec 7 milliards € d'économies supplémentaires.",
    'PLF 2025 (vote solennel)':
        "Budget de l'État français pour 2025. Adopté définitivement le 6 février 2025, après la censure du gouvernement Barnier et l'arrivée du gouvernement Bayrou.",
    'Loi plein emploi':
        "Loi de 2023 qui veut faire baisser le chômage : remplace Pôle emploi par « France Travail », et oblige les bénéficiaires du RSA à faire 15 heures d'activité par semaine (formation, recherche d'emploi…).",
    'Adequate minimum wages in the European Union':
        "Loi européenne qui fixe un cadre commun pour les salaires minimaux dans tous les pays de l'UE. Recommande qu'ils atteignent 60 % du salaire médian du pays.",
    'Fair working conditions, rights and social protection for platform workers - New forms of employment linked to digital development':
        "Résolution du Parlement européen sur les chauffeurs Uber, livreurs Deliveroo et autres travailleurs de plateformes numériques. Pas de valeur juridique, juste une prise de position.",
    'Improving working conditions in platform work':
        "Loi européenne sur les travailleurs des plateformes (Uber, Deliveroo…). Permet de les considérer comme salariés dans certains cas (au lieu d'indépendants), et oblige les plateformes à expliquer comment leurs algorithmes décident.",
    'Increasing the attractiveness of public capital markets and facilitating access to capital for SMEs – amending directive':
        "Loi européenne pour aider les petites et moyennes entreprises (PME) à entrer en bourse plus facilement. Allège les obligations de paperasse pour les sociétés cotées.",
    # Europe / Souveraineté
    'Règlement IA (AI Act)':
        "Première loi au monde qui encadre l'intelligence artificielle. Classe les systèmes d'IA par niveau de risque : interdits (notation sociale type Chine), à risque élevé (santé, justice…), à risque limité (chatbots), à risque minimal (jeux). Plus le risque est élevé, plus les obligations sont fortes.",
    'Artificial Intelligence Act':
        "Première loi au monde qui encadre l'intelligence artificielle. Classe les IA par niveau de risque, du plus dangereux (interdit) au moins risqué, et impose des règles plus strictes pour celles qui peuvent avoir un impact important (santé, justice, etc.).",
    'Corporate sustainability due diligence':
        "Loi européenne (directive CSDDD) qui oblige les grandes entreprises à vérifier que leurs fournisseurs (souvent à l'étranger) ne violent pas les droits humains ou ne polluent pas. Si elles le découvrent, elles doivent agir.",
    'Situation in Hungary and frozen EU funds':
        "Résolution du Parlement européen qui critique les reculs démocratiques en Hongrie et soutient la décision de l'UE de geler les fonds européens destinés à ce pays tant qu'il ne respecte pas l'État de droit.",
    'Existence of a clear risk of a serious breach by Hungary of the values on which the Union is founded':
        "Procédure de sanction au niveau européen contre la Hongrie pour ne pas respecter les valeurs de l'UE (indépendance de la justice, libertés, etc.). Peut aller jusqu'à priver la Hongrie de son droit de vote au Conseil européen.",
    'Investments and reforms for European competitiveness and the creation of a Capital Markets Union':
        "Rapport du Parlement européen qui propose de créer une vraie « Union des marchés de capitaux » en Europe : un marché financier unifié pour faciliter le financement des entreprises et de la transition écologique.",
    # Sécurité / Justice
    'Loi sécurité globale':
        "Loi française de 2021 qui élargit les pouvoirs des polices municipales et encadre l'usage des drones par la police. L'article le plus contesté (l'article 24, qui interdisait de filmer un policier identifiable) a été censuré par le Conseil constitutionnel.",
    'Loi confortant les principes de la République (séparatisme)':
        "Loi française d'août 2021 dite « contre le séparatisme ». Renforce le contrôle des associations, permet de fermer plus facilement des lieux de culte radicaux, impose la neutralité religieuse aux agents publics, lutte contre la haine en ligne et encadre l'instruction à domicile.",
    'Pass sanitaire / vaccinal':
        "Lois de 2021-2022 qui ont créé d'abord le pass sanitaire (preuve de vaccination, test négatif ou rétablissement) puis le pass vaccinal (seulement vaccination) pour accéder aux lieux publics et événements, pendant la pandémie de Covid-19.",
    'Loi orientation et programmation justice':
        "Loi de 2023 qui programme 8 milliards € supplémentaires pour la justice d'ici 2027 et l'embauche de 10 000 magistrats et greffiers. Simplifie aussi certaines procédures pénales.",
    'Motion de censure du gouvernement Barnier':
        "Vote des députés qui a fait tomber le gouvernement Michel Barnier le 4 décembre 2024. 331 députés (du RN et de la gauche réunis) ont voté la censure. C'était la première fois depuis 1962 qu'un gouvernement français était renversé par cette procédure.",
    # Ukraine
    'Soutien financier à l\'Ukraine (Facilité UE)':
        "Programme européen qui prévoit 50 milliards € d'aide à l'Ukraine pour 2024-2027 : une partie en prêts, une partie en dons. Sert à payer le fonctionnement de l'État ukrainien et la reconstruction.",
    'Establishing the Ukraine Facility':
        "Programme européen qui débloque 50 milliards € pour aider l'Ukraine sur 2024-2027 (prêts + dons). Sert au fonctionnement de l'État ukrainien et à la reconstruction du pays.",
    'The human cost of Russia’s war against Ukraine and the urgent need to end Russian aggression: the situation of illegally detained civilians and prisoners of war, and the continued':
        "Résolution du Parlement européen qui dénonce le sort des civils ukrainiens emprisonnés par la Russie et demande leur libération.",
    'Definition of criminal offences and penalties for the violation of Union restrictive measures':
        "Loi européenne qui harmonise les peines (prison, amendes) dans tous les pays de l'Union pour ceux qui contournent les sanctions contre la Russie.",
    # Société
    'IVG dans la Constitution':
        "Loi constitutionnelle qui inscrit dans la Constitution française la « liberté garantie » d'avorter pour les femmes. Adoptée le 4 mars 2024 au Congrès de Versailles (députés + sénateurs) par 780 voix pour et 72 contre.",
    'Fin de vie (projet de loi)':
        "Projet de loi qui crée un droit à « l'aide à mourir » sous conditions strictes (maladie incurable, souffrances qui ne peuvent pas être soulagées). Renforce aussi les soins palliatifs. Adopté en première lecture à l'Assemblée le 27 mai 2025.",
}


# ----------------------------------------------------------------------------
# CONTEXTES simplifiés — clé = (titre_partiel, slug)
# ----------------------------------------------------------------------------

CONTEXTES_SIMPLES = [
    ('Loi Climat et Résilience', 'melenchon',
     "Mélenchon n'a pas voté contre le climat, mais contre une loi qu'il jugeait trop molle. Pour lui, la loi ne reprenait pas assez les propositions de la Convention citoyenne pour le climat (notamment l'interdiction des vols intérieurs courts a été beaucoup réduite par rapport à ce qui était proposé)."),
    ('Loi sécurité globale', 'melenchon',
     "Mélenchon s'est opposé à cette loi à cause de l'article 24, qui interdisait de filmer les policiers en intervention. Il y voyait une atteinte à la liberté d'informer. Cet article a finalement été censuré par le Conseil constitutionnel."),
    ('Loi confortant les principes de la République (séparatisme)', 'melenchon',
     "Le groupe LFI a voté contre la loi dans son ensemble, mais a voté pour environ 40 % des articles examinés un par un (notamment ceux sur l'égalité hommes-femmes et la lutte contre la haine en ligne). Mélenchon a publiquement qualifié la loi d'« inutile et dangereuse »."),
    ('Pass sanitaire / vaccinal', 'melenchon',
     "Mélenchon a voté contre le pass sanitaire, mais ce n'est pas une position anti-vaccin : il s'est fait vacciner lui-même et a appelé à la vaccination volontaire. Son opposition portait sur les libertés (obligation d'avoir le pass pour accéder à des lieux publics)."),
    ('IVG dans la Constitution', 'retailleau',
     "Retailleau est un des rares sénateurs LR à avoir voté contre l'inscription de l'IVG dans la Constitution (780 pour, 72 contre au total). Il dit être favorable au droit à l'IVG dans la loi, mais pas à son inscription dans la Constitution."),
    ('Fin de vie (projet de loi)', 'attal',
     "Attal a voté pour la loi fin de vie. Sur ce texte sensible, son groupe à l'Assemblée a laissé chaque député voter « selon sa conscience », sans consigne. Attal a personnellement choisi le « pour »."),
    ('Règlement IA (AI Act)', 'bardella',
     "Bardella a voté pour cette loi européenne, alors que son groupe vote habituellement contre les nouvelles règles européennes. Raison : il considère que cette loi protège les entreprises européennes face aux géants américains et chinois de l'IA."),
    ('Artificial Intelligence Act', 'bardella',
     "Bardella a voté pour cette loi européenne, alors que son groupe vote habituellement contre les nouvelles règles européennes. Raison : il considère que cette loi protège les entreprises européennes face aux géants américains et chinois de l'IA."),
    ('Carbon Border Adjustment Mechanism: simplification', 'bardella',
     "Vote inhabituel : Bardella vote rarement pour des textes écologistes européens. Mais cette taxe vise les produits importés pollueurs (acier chinois, ciment turc…) et protège donc les industries européennes face à une concurrence déloyale. C'est pour cette raison de protection économique — pas pour l'écologie — que le RN l'a soutenue."),
    ('Common agricultural policy (CAP) 2021', 'bardella',
     "Bardella a voté pour cette réforme agricole européenne, alors que la majorité de son groupe a voté contre. Cohérent avec le soutien historique du RN aux agriculteurs français."),
    ('Improving working conditions in platform work', 'bardella',
     "Bardella a voté pour cette loi européenne qui protège les chauffeurs Uber et livreurs Deliveroo, alors que son groupe vote habituellement contre les textes sociaux européens. Position cohérente avec la défense des catégories populaires."),
    ('Loi Climat et Résilience', 'retailleau',
     "Retailleau a voté pour cette loi climat au Sénat, après avoir fait adopter un amendement modifiant l'article 1er sur la place de l'environnement dans la Constitution. Position pragmatique : soutien sous condition d'amendements pro-Sénat."),
]


def main():
    votes = json.loads((DATA / 'votes-cles.json').read_text(encoding='utf-8'))
    n_resumes = 0
    n_ctx = 0

    for v in votes:
        # Résumé : on cherche par titre original puis titre FR
        texte = v.get('texte') or ''
        if texte in RESUMES_SIMPLES:
            v['resume'] = RESUMES_SIMPLES[texte]
            n_resumes += 1
        elif v.get('titre_fr') in RESUMES_SIMPLES:
            v['resume'] = RESUMES_SIMPLES[v['titre_fr']]
            n_resumes += 1

        # Contextes : matching par titre partiel
        for partial, slug, ctx in CONTEXTES_SIMPLES:
            if partial.lower() in texte.lower():
                if 'positions' in v and slug in v['positions']:
                    v['positions'][slug]['contexte'] = ctx
                    n_ctx += 1
                break

    (DATA / 'votes-cles.json').write_text(
        json.dumps(votes, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    print(f'OK : {n_resumes} résumés simplifiés, {n_ctx} contextes simplifiés.')


if __name__ == '__main__':
    main()
