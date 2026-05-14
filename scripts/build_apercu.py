"""
Génère `apercu.html` : page unique pré-rendue contenant TOUT le contenu du site
en HTML statique, pour bots/crawlers/Claude WebFetch.

Lit les JSON produits par build_site_data.py et produit un seul gros fichier
HTML. Aucun JavaScript requis pour voir le contenu.

Usage : py scripts/build_apercu.py
"""
from __future__ import annotations
import json
import sys
from html import escape
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
OUT = ROOT / 'apercu.html'

CANDIDAT_ORDER = ['bardella', 'philippe', 'retailleau', 'melenchon', 'attal']


def h(s):
    return escape('' if s is None else str(s))


def fmt_pos(p):
    code = (p or {}).get('position') or 'N/A'
    m = {
        'POUR': ('vote--pour', 'POUR ✓'),
        'CONTRE': ('vote--contre', 'CONTRE ✗'),
        'ABSTENTION': ('vote--abstention', 'ABSTENTION ⊝'),
        'ABSENT': ('vote--absent', 'ABSENT ⊘'),
    }.get(code, ('vote--na', code))
    return f'<span class="vote {m[0]}">{m[1]}</span>'


def field_payload(payload):
    if not payload or payload.get('value') in (None, ''):
        return '<em style="color:#888">non renseigné</em>'
    val = h(payload['value'])
    src = payload.get('source_url')
    if src:
        return f'{val} <a href="{h(src)}" target="_blank" rel="noopener" style="font-size:0.8em">[source]</a>'
    return val


def main():
    candidats_d = json.loads((DATA / 'candidats.json').read_text(encoding='utf-8'))
    votes = json.loads((DATA / 'votes-cles.json').read_text(encoding='utf-8'))
    fin = json.loads((DATA / 'financement.json').read_text(encoding='utf-8'))
    sujets = json.loads((DATA / 'sujets.json').read_text(encoding='utf-8'))
    glossaire = json.loads((DATA / 'glossaire.json').read_text(encoding='utf-8'))
    sources = json.loads((DATA / 'sources.json').read_text(encoding='utf-8'))
    candidats = candidats_d['candidats']

    parts = []

    parts.append("""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Observations Présidentielles 2027 — Aperçu complet pré-rendu</title>
<meta name="description" content="Page unique contenant tout le contenu du site Observations Présidentielles 2027 en HTML statique, pour bots, crawlers et indexation. 5 candidats, 11 sujets, votes-clés, patrimoine, financement, glossaire.">
<meta name="robots" content="index,follow">
<link rel="stylesheet" href="assets/styles.css">
<link rel="canonical" href="https://mlolita26.github.io/observations-presidentielles-2027/">
<style>
.apercu-toc { background: #F0EFEA; border: 1px solid #D4D0C7; padding: 1rem 1.5rem; border-radius: 4px; margin: 1rem 0 2rem; }
.apercu-toc ul { columns: 2; column-gap: 2rem; }
.apercu-section { border-top: 1px solid #D4D0C7; padding-top: 1rem; margin-top: 2.5rem; }
.apercu-candidat { border: 1px solid #D4D0C7; border-radius: 6px; padding: 1rem 1.5rem; margin: 1rem 0; background: #fff; }
.apercu-candidat h3 { margin-top: 0; }
.apercu-positions { display: grid; grid-template-columns: 200px 1fr; gap: 0.5rem 1rem; font-size: 0.92rem; }
.apercu-positions dt { font-weight: 600; }
.apercu-votes-table { font-size: 0.85rem; width: 100%; border-collapse: collapse; margin: 0.5rem 0; }
.apercu-votes-table th, .apercu-votes-table td { border: 1px solid #D4D0C7; padding: 0.3rem 0.5rem; text-align: left; vertical-align: top; }
.apercu-votes-table th { background: #F0EFEA; }
</style>
</head>
<body>
<header class="site-header">
  <div class="container">
    <a href="index.html" class="site-title">Observations Présidentielles 2027</a>
    <p class="site-subtitle">Aperçu complet pré-rendu (HTML statique, pour bots et indexation)</p>
    <nav class="site-nav"><a href="index.html">Site interactif</a> · <a href="methodologie.html">Méthodologie</a> · <a href="glossaire.html">Glossaire</a></nav>
  </div>
</header>
<main class="container">
""")

    # Introduction
    parts.append(f"""
<section class="hero">
  <h1>Aperçu complet — toutes les données du site sur une page</h1>
  <p class="baseline">Cette page contient l'intégralité du contenu factuel du site, pré-rendue en HTML statique. Elle est destinée aux moteurs d'indexation, aux bots, et aux outils comme Claude WebFetch qui ne peuvent pas exécuter le JavaScript.</p>
  <p><strong>Date d'arrêt des données :</strong> 12 mai 2026. <strong>Source :</strong> tableur normalisé v6 (14 tables relationnelles). <strong>Métadonnées :</strong> {len(candidats)} candidats, {len(sujets)} sujets, {len(votes)} textes-clés référencés, {len(sources)} sources uniques, {len(glossaire)} termes de glossaire.</p>
</section>
""")

    # TOC
    parts.append('<nav class="apercu-toc" aria-label="Sommaire"><strong>Sommaire</strong><ul>')
    parts.append('<li><a href="#methodologie-resume">Méthodologie (résumé)</a></li>')
    parts.append('<li><a href="#candidats">Fiches candidats (5)</a></li>')
    for c in CANDIDAT_ORDER:
        parts.append(f'<li style="margin-left:1em">↪ <a href="#cand-{h(c)}">{h(candidats[c]["nom"])}</a></li>')
    parts.append('<li><a href="#sujets">Sujets de politique publique (11)</a></li>')
    for s in sujets:
        parts.append(f'<li style="margin-left:1em">↪ <a href="#sujet-{h(s["id"])}">{h(s["titre"])}</a></li>')
    parts.append('<li><a href="#votes-cles">Tous les votes-clés référencés</a></li>')
    parts.append('<li><a href="#financement">Financement (campagnes + partis)</a></li>')
    parts.append('<li><a href="#glossaire">Glossaire</a></li>')
    parts.append('<li><a href="#sources">Sources</a></li>')
    parts.append('</ul></nav>')

    # ===== MÉTHODOLOGIE RÉSUMÉ =====
    parts.append("""
<section class="apercu-section" id="methodologie-resume">
<h2>Méthodologie (résumé)</h2>
<p><strong>Mission :</strong> observatoire citoyen non partisan présentant une analyse factuelle, sourcée et neutre des cinq principaux candidats pressentis à l'élection présidentielle française de 2027.</p>
<p><strong>Période :</strong> 2020-2026. <strong>Date d'arrêt :</strong> 12 mai 2026.</p>
<p><strong>Règles éditoriales :</strong></p>
<ul>
<li>Neutralité absolue : aucun qualificatif politique subjectif. Partis nommés par leur dénomination officielle (Rassemblement National, La France Insoumise, Les Républicains, Horizons, Renaissance).</li>
<li>Présomption d'innocence stricte : aucun terme définitif tant qu'une condamnation n'est pas devenue définitive.</li>
<li>Sourçage systématique : chaque chiffre accompagné d'un lien vers la source primaire.</li>
<li>Datation : chaque chiffre horodaté.</li>
<li>Mentions « NON TROUVÉ » conservées et signalées avec voie de recours.</li>
</ul>
<p><strong>Sources primaires utilisées :</strong> HATVP, CNCCFP, Assemblée nationale, Sénat, Parlement européen, NosDéputés.fr, NosSénateurs.fr, Datan.fr, HowTheyVote.eu.</p>
<p><strong>Biais connus :</strong> mandats de durée et de nature inégales (eurodéputé vs sénateur vs maire vs sans mandat), sources hétérogènes, déclarations auto-déclaratives.</p>
</section>
""")

    # ===== FICHES CANDIDATS =====
    parts.append('<section class="apercu-section" id="candidats"><h2>Fiches candidats</h2>')
    for slug in CANDIDAT_ORDER:
        c = candidats.get(slug)
        if not c:
            continue
        parts.append(f'<article class="apercu-candidat" id="cand-{h(slug)}"><h3>{h(c["nom"])} — {h(c["parti"])}</h3>')

        # Identité
        ident = c.get('identite', {})
        parts.append('<h4>Identité</h4><div class="apercu-positions"><dl class="apercu-positions">')
        for key, label in [
            ('date_naissance', 'Date de naissance'),
            ('lieu_naissance', 'Lieu de naissance'),
            ('formation', 'Formation'),
            ('profession_origine', "Profession d'origine"),
            ('mandat_principal', 'Mandat actuel'),
            ('premiere_election', 'Première élection'),
            ('fonctions_gouvernementales', 'Fonctions gouvernementales'),
            ('presidence_parti', 'Présidence de parti'),
            ('candidature_2027', 'Candidature 2027'),
        ]:
            parts.append(f'<dt>{h(label)}</dt><dd>{field_payload(ident.get(key))}</dd>')
        parts.append('</dl></div>')

        # Activité parlementaire
        act = c.get('activite_parlementaire', {})
        if act:
            parts.append('<h4>Activité parlementaire</h4><dl class="apercu-positions">')
            for key, label in [
                ('presence_hemicycle', 'Présence hémicycle'),
                ('presence_commissions', 'Présence commissions'),
                ('interventions', 'Interventions en séance'),
                ('propositions_loi', 'Propositions de loi'),
                ('amendements', 'Amendements'),
                ('rapports', 'Rapports rédigés'),
                ('questions', 'Questions écrites/orales'),
                ('cohesion_groupe', 'Cohésion groupe'),
                ('conference_presidents_pe', 'Conférence des présidents PE'),
            ]:
                if act.get(key):
                    parts.append(f'<dt>{h(label)}</dt><dd>{field_payload(act.get(key))}</dd>')
            parts.append('</dl>')

        # Positions par sujet
        pos = c.get('positions', {})
        if pos:
            parts.append('<h4>Positions publiques par sujet</h4><dl class="apercu-positions">')
            for key, label in [
                ('immigration', 'Immigration'),
                ('europe', 'Europe'),
                ('climat', 'Climat / écologie'),
                ('fiscalite', 'Fiscalité'),
                ('retraites', 'Retraites'),
                ('securite', 'Sécurité / justice'),
                ('ukraine', 'Ukraine / Russie'),
                ('tribunes', 'Tribunes notables'),
                ('manifestations', 'Manifestations'),
            ]:
                if pos.get(key):
                    parts.append(f'<dt>{h(label)}</dt><dd>{field_payload(pos.get(key))}</dd>')
            parts.append('</dl>')

        # Patrimoine
        pat = c.get('patrimoine', {})
        if pat:
            parts.append('<h4>Patrimoine et intérêts (HATVP)</h4><dl class="apercu-positions">')
            for key, label in [
                ('patrimoine_declare', 'Patrimoine déclaré'),
                ('revenus_annuels', 'Revenus annuels'),
                ('activites_annexes', 'Activités annexes'),
                ('participations', 'Participations / SCI'),
                ('conjoint', 'Conjoint·e (activité)'),
                ('evolution_patrimoine', 'Évolution entrée/sortie de mandat'),
            ]:
                if pat.get(key):
                    parts.append(f'<dt>{h(label)}</dt><dd>{field_payload(pat.get(key))}</dd>')
            parts.append('</dl>')

        # Affaires
        aff = c.get('affaires', [])
        real_aff = [a for a in aff if a.get('intitule') and 'Aucune affaire' not in (a.get('intitule') or '')]
        if real_aff:
            parts.append('<h4>Affaires judiciaires (présomption d\'innocence stricte)</h4>')
            for a in real_aff:
                src = a.get('source_url')
                src_html = f' <a href="{h(src)}" target="_blank" rel="noopener" style="font-size:0.8em">[source]</a>' if src else ''
                parts.append(f'<p><strong>{h(a.get("intitule"))}</strong>{src_html}<br>')
                parts.append(f'Nature : {h(a.get("nature"))}<br>')
                parts.append(f'Statut juridique : {h(a.get("statut_juridique"))}<br>')
                parts.append(f'Période : {h(a.get("annee"))}</p>')
        else:
            parts.append('<h4>Affaires judiciaires</h4><p><em>Aucune affaire judiciaire notable connue publiquement à ce jour.</em></p>')

        # Financement
        finc = c.get('financement', {})
        if finc:
            parts.append('<h4>Financement (compte de campagne, parti)</h4><dl class="apercu-positions">')
            for key, label in [
                ('derniere_campagne', 'Dernière campagne'),
                ('total_depenses', 'Total dépenses'),
                ('origine_fonds', 'Origine des fonds'),
                ('prets_etrangers', 'Prêts bancaires étrangers'),
                ('compte_valide', 'Validation CNCCFP'),
                ('financement_parti', 'Financement du parti'),
            ]:
                if finc.get(key):
                    parts.append(f'<dt>{h(label)}</dt><dd>{field_payload(finc.get(key))}</dd>')
            parts.append('</dl>')

        parts.append('</article>')
    parts.append('</section>')

    # ===== SUJETS =====
    parts.append('<section class="apercu-section" id="sujets"><h2>Sujets de politique publique</h2>')
    for s in sujets:
        parts.append(f'<article class="apercu-candidat" id="sujet-{h(s["id"])}">')
        parts.append(f'<h3>{h(s["titre"])} <small style="color:#888">({h(s.get("type", "?"))})</small></h3>')
        parts.append(f'<p>{h(s.get("definition", ""))}</p>')

        # Positions de chaque candidat sur ce sujet
        pkey = s.get('positions_key')
        if pkey and s.get('type') == 'politique':
            parts.append('<h4>Positions des candidats sur ce sujet</h4><dl class="apercu-positions">')
            for slug in CANDIDAT_ORDER:
                c = candidats.get(slug, {})
                pos = (c.get('positions') or {}).get(pkey)
                parts.append(f'<dt>{h(c.get("nom", slug))}</dt><dd>{field_payload(pos)}</dd>')
            parts.append('</dl>')

        # Votes-clés du sujet
        themes_filter = (s.get('votes_filter') or {}).get('themes') or []
        if themes_filter:
            matched_votes = [v for v in votes if any(t.strip().lower() in (v.get('theme') or '').lower() for t in themes_filter if t.strip())]
            if matched_votes:
                parts.append(f'<h4>Votes-clés liés ({len(matched_votes)} textes)</h4>')
                parts.append('<table class="apercu-votes-table"><thead><tr><th>Année</th><th>Texte</th>')
                for cs in CANDIDAT_ORDER:
                    parts.append(f'<th>{h(candidats[cs]["nom"].split()[-1])}</th>')
                parts.append('</tr></thead><tbody>')
                for v in matched_votes:
                    parts.append(f'<tr><td>{h(v.get("annee"))}</td><td>{h(v.get("texte"))}</td>')
                    for cs in CANDIDAT_ORDER:
                        p = (v.get('positions') or {}).get(cs, {})
                        parts.append(f'<td>{fmt_pos(p)}</td>')
                    parts.append('</tr>')
                parts.append('</tbody></table>')
        parts.append('</article>')
    parts.append('</section>')

    # ===== TOUS LES VOTES-CLÉS =====
    parts.append('<section class="apercu-section" id="votes-cles"><h2>Tous les votes-clés référencés</h2>')
    parts.append(f'<p>{len(votes)} textes parlementaires emblématiques 2020-2026 (AN, Sénat, Parlement européen, Congrès). Les 24 000 votes bruts complémentaires de Jordan Bardella au PE sont disponibles dans <code>data/votes-bruts.json</code>.</p>')
    parts.append('<table class="apercu-votes-table"><thead><tr><th>Année</th><th>Thème</th><th>Texte</th>')
    for cs in CANDIDAT_ORDER:
        parts.append(f'<th>{h(candidats[cs]["nom"].split()[-1])}</th>')
    parts.append('<th>Source</th></tr></thead><tbody>')
    for v in sorted(votes, key=lambda x: (x.get('annee') or 0, x.get('theme') or '')):
        parts.append(f'<tr><td>{h(v.get("annee"))}</td><td>{h(v.get("theme"))}</td><td>{h(v.get("texte"))}</td>')
        for cs in CANDIDAT_ORDER:
            p = (v.get('positions') or {}).get(cs, {})
            parts.append(f'<td>{fmt_pos(p)}</td>')
        # première source dispo
        src = next((p.get('source_url') for p in (v.get('positions') or {}).values() if p.get('source_url')), None)
        parts.append(f'<td>{("<a href=\""+h(src)+"\" target=\"_blank\" rel=\"noopener\">lien</a>") if src else ""}</td></tr>')
    parts.append('</tbody></table></section>')

    # ===== FINANCEMENT =====
    parts.append('<section class="apercu-section" id="financement"><h2>Financement politique (CNCCFP)</h2>')
    parts.append('<h3>Comptes de campagne récents analysables</h3>')
    parts.append('<table class="apercu-votes-table"><thead><tr><th>Candidat</th><th>Élection</th><th>Date décision</th><th>Dépenses</th><th>Recettes</th><th>Remboursement</th><th>Réformations</th></tr></thead><tbody>')
    for cmp in fin.get('campagnes_par_candidat', []):
        parts.append(f'<tr><td>{h(cmp.get("candidat_nom"))}</td><td>{h(cmp.get("election"))}</td><td>{h(cmp.get("date_decision"))}</td><td>{h(cmp.get("depenses"))}</td><td>{h(cmp.get("recettes"))}</td><td>{h(cmp.get("remboursement"))}</td><td>{h(cmp.get("reformations"))}</td></tr>')
    parts.append('</tbody></table>')

    parts.append('<h3>Comptes des partis politiques (exercice 2024)</h3>')
    parts.append(f'<p><a href="{h(fin.get("partis_source_url"))}" target="_blank" rel="noopener">Source : {h(fin.get("partis_source_label", "CNCCFP"))}</a></p>')
    parts.append('<table class="apercu-votes-table"><thead><tr><th>Parti</th><th>Total bilan</th><th>Produits 2024</th><th>Aide publique 2024</th><th>Dettes</th><th>Dont banques</th><th>Dont pers. physiques</th></tr></thead><tbody>')
    for p in fin.get('comptes_partis_2024', []):
        parts.append(f'<tr><td>{h(p.get("parti"))}</td><td>{h(p.get("total_bilan"))}</td><td>{h(p.get("produits_2024"))}</td><td>{h(p.get("aide_publique_2024"))}</td><td>{h(p.get("dettes_total"))}</td><td>{h(p.get("dont_banques"))}</td><td>{h(p.get("dont_personnes_physiques"))}</td></tr>')
    parts.append('</tbody></table></section>')

    # ===== GLOSSAIRE =====
    parts.append('<section class="apercu-section" id="glossaire"><h2>Glossaire des termes techniques</h2>')
    by_cat = {}
    for e in glossaire:
        by_cat.setdefault(e['categorie'], []).append(e)
    for cat, items in by_cat.items():
        parts.append(f'<h3>{h(cat)} ({len(items)})</h3><dl class="apercu-positions">')
        for e in items:
            parts.append(f'<dt>{h(e["terme"])}</dt><dd>{h(e["definition_courte"])}<br><small style="color:#666">{h(e.get("definition_longue", ""))}</small></dd>')
        parts.append('</dl>')
    parts.append('</section>')

    # ===== SOURCES =====
    parts.append('<section class="apercu-section" id="sources"><h2>Sources utilisées</h2>')
    parts.append(f'<p>{len(sources)} sources distinctes référencées dans le tableur v6 normalisé.</p><ul>')
    for s in sources:
        parts.append(f'<li><a href="{h(s.get("url"))}" target="_blank" rel="noopener">{h(s.get("label"))}</a> — {h(s.get("organisation"))} / {h(s.get("type"))} / fiabilité {h(s.get("fiabilite"))}</li>')
    parts.append('</ul></section>')

    parts.append("""
<footer class="site-footer" style="margin-top:3rem; padding:2rem 0; border-top:1px solid #D4D0C7;">
<p>Aperçu généré le {} depuis le tableur normalisé v6. Licence des données : CC BY 4.0. Code ouvert.</p>
<p><a href="index.html">Retour au site interactif</a></p>
</footer>
</main>
</body>
</html>
""".format('12 mai 2026'))

    html = '\n'.join(parts)
    OUT.write_text(html, encoding='utf-8')
    print(f'OK : {OUT}')
    print(f'Taille : {OUT.stat().st_size / 1024:.1f} ko')
    print(f'Contenu : {len(candidats)} candidats, {len(sujets)} sujets, {len(votes)} votes-clés, {len(glossaire)} termes glossaire')


if __name__ == '__main__':
    main()
