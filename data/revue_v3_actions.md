# Suivi des actions issues de la revue Claude (14 mai 2026)

Statut de chaque action de la revue critique, et **points fragiles à reconfirmer auprès d'une source primaire** avant publication définitive.

## Légende

- ✅ Appliqué et vérifié
- ⚠️ Appliqué, mais **à reconfirmer** auprès d'une source primaire
- 🟡 En cours
- ⬜ Pas encore traité
- ❌ Refusé / pas pertinent

---

## Points appliqués mais à reconfirmer

### §1.3 — Mélenchon condamnation perquisition LFI 2018 : « définitive » et non « 1ère instance »

**Modification appliquée** : statut juridique réécrit en « Condamnation définitive depuis fin décembre 2019 (renonciation à l'appel) ». Présomption d'innocence retirée pour cette affaire spécifique.

**À reconfirmer** :
- Que la renonciation à l'appel est elle-même publiquement sourcée (Mélenchon l'a-t-il annoncée formellement, ou simplement laissé expirer le délai ?).
- Source primaire : Dalloz Actualité 10/12/2019 + dépêches AFP.
- Vérifier qu'aucune procédure de révision ou de QPC n'est en cours en 2026.

### §1.4 — Bardella CBAM : abstention sur le vote initial 2023

**Modification appliquée** : ajout du vote initial CBAM 2023 avec position « abstention », distinction explicite avec la révision 2025.

**À reconfirmer** :
- Position exacte de Bardella sur le vote du 9 mai 2023 (TA9-0150/2023, Carbon Border Adjustment Mechanism initial).
- Vérifier dans le dataset HowTheyVote local que le vote_id correspondant existe et que la position de MEP 131580 est bien ABSTENTION ou DID_NOT_VOTE.

### §2.6 et §3.3 — Casse « Rassemblement national » et « La France insoumise »

**Modification appliquée** : search/replace global de « Rassemblement National » → « Rassemblement national » et « La France Insoumise » → « La France insoumise ».

**À reconfirmer** :
- Dénomination exacte dans les statuts du parti déposés au Journal officiel.
- Site officiel rassemblementnational.fr et lafranceinsoumise.fr (à vérifier sur le header / pied de page).
- AFP/Le Monde tendent à mettre les majuscules ; HATVP et CNCCFP utilisent souvent la version officielle.
- En cas de divergence : appliquer la version utilisée par le parti lui-même dans son site officiel.

---

## Points appliqués sans réserve

### §1.2 — Sujet Société rempli (5 cellules)
Voir CHANGELOG ci-dessous.

### §3.1 — Reformulations de neutralité
- « Soutien tardif, refus de certaines livraisons » → reformulation factuelle.
- « Position pacifiste contestée » → reformulation factuelle.
- « Climato-prudent » → liste factuelle de votes.
- « Avec drapeaux palestiniens et soutien Gaza » → retiré.
- « Figure tutélaire LFI » → reformulation factuelle.
- « Permanent politique (RN dès 16 ans) » → reformulation factuelle.

### §2.1 — Inversion de l'ordre sur l'accueil
Bloc « Les 5 candidats » remonté en premier, bloc « Comparer sur un sujet » en deuxième.

### §1.12 — Liens Wikipédia génériques
Remplacés par des pages nominatives `fr.wikipedia.org/wiki/<Slug_Candidat>`.

---

## Points non traités dans cette session

- §1.5 — Extraction DSP Mélenchon HATVP 2022 (PDF) → demande une action manuelle (voir `hatvp_collecte_manuelle.md`).
- §1.6 — Périodes différentes des agrégats NosDéputés à expliciter dans chaque libellé.
- §1.9 — Sourcer chaque position synthèse par 1 lien primaire (effort moyen).
- §1.10 — Marqueurs visuels de fiabilité (pictogrammes 🟢 🟡 🟠).
- §2.7 — Navigation séquentielle bas-de-page.
- §2.8 — Audit Lighthouse complet.
- §4.1 — Bloc « Cohérence discours / actes » : décision en attente (à déployer rigoureusement ou retirer).
- §4.3 — Date « dernière mise à jour » par fiche.
- §4.4 — Section « Limites » explicite.

---

## CHANGELOG des positions Société ajoutées

À publier après vérification auprès des sources :

| Candidat | IVG dans la Constitution (4 mars 2024) | Fin de vie (loi AN 27/05/2025) |
|---|---|---|
| Bardella | Position RN : favorable à l'IVG mais opposé à sa constitutionnalisation. Abstention RN au Congrès. | Position prudente, programme RN 2024 ne soutient pas l'aide à mourir. |
| Philippe | Soutien à la constitutionnalisation. Position favorable au projet fin de vie. | |
| Retailleau | CONTRE constitutionnalisation IVG (rare sénateur LR ayant voté contre au Congrès). | CONTRE l'aide à mourir (position publique constante). |
| Mélenchon | Soutien fort. Programme LFI 2022 inclut le droit à l'IVG et un assouplissement fin de vie. | Soutien à la légalisation. |
| Attal | POUR la constitutionnalisation IVG (porté par son gouvernement). | POUR aide à mourir (vote nominal AN scrutin 2107, 27/05/2025). |

**Sources à attacher avant publication** :
- IVG : compte rendu Congrès Versailles 04/03/2024.
- Fin de vie : scrutin AN n°2107 du 27/05/2025 (URL : https://www.assemblee-nationale.fr/dyn/17/scrutins/2107).
- Position RN : Marine Le Pen + groupe RN AN.
- Programmes LFI 2022 et RN 2024 : pages officielles datées.
