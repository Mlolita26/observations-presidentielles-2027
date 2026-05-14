"""
Génère des pages HTML statiques pré-rendues pour les sujets, candidats, glossaire.

Sortie :
 - sujet-{id}.html × 11 (un par sujet)
 - candidat-{slug}.html × 5 (un par candidat)
 - glossaire-static.html × 1

Ces pages sont des copies "snapshot" pré-rendues du contenu dynamique. Elles sont
visibles par les bots/crawlers (Claude WebFetch, GPTbot, Google Search) sans
exécution JS, et permettent l'indexation et le partage social.

Les pages dynamiques originales (sujet.html?id=X, candidat.html?nom=X) sont
conservées pour les humains naviguant via le JS interne.

Usage : py scripts/build_static_pages.py
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
        return f'{val} <a href="{h(src)}" target="_blank" rel="noopener" class="source-link" style="font-size:0.8em">[source]</a>'
    return val


def html_header(title, description, canonical):
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{h(title)}</title>
<meta name="description" content="{h(description)}">
<meta name="robots" content="index,follow">
<link rel="stylesheet" href="assets/styles.css">
<link rel="canonical" href="{h(canonical)}">
</head>
<body>
<header class="site-header">
  <div class="container">
    <div class="site-header__inner">
      <a href="index.html" class="site-title">Observations&nbsp;Présidentielles&nbsp;2027</a>
      <p class="site-subtitle">Observatoire citoyen non partisan</p>
    </div>
    <nav class="site-nav" aria-label="Navigation principale">
      <a href="index.html">Accueil</a>
      <a href="comparer.html">Comparer</a>
      <a href="glossaire-static.html">Glossaire</a>
      <a href="methodologie.html">Méthodologie</a>
      <a href="apercu.html">Aperçu complet</a>
    </nav>
  </div>
</header>
<main class="container">
"""


HTML_FOOTER = """
<footer class="site-footer" style="margin-top:3rem; padding:2rem 0; border-top:1px solid #D4D0C7;">
  <div class="container">
    <p><a href="methodologie.html">Méthodologie</a> · <a href="glossaire-static.html">Glossaire</a> · <a href="apercu.html">Aperçu complet</a> · <a href="methodologie.html#mentions">Mentions légales</a></p>
    <p>Données extraites le 12 mai 2026. Licence : CC BY 4.0. Observatoire non partisan, non rattaché à aucun parti.</p>
  </div>
</footer>
</main>
</body>
</html>
"""


# ----------------------------------------------------------------------------
# Page CANDIDAT
# ----------------------------------------------------------------------------

def render_candidat(slug, candidats, sujets, votes):
    c = candidats[slug]
    n_votes = sum(1 for v in votes if (v.get('positions', {}).get(slug, {}).get('position') not in (None, 'N/A', 'N_APPLICABLE')))
    n_votes_total = len(votes)

    parts = []
    parts.append(html_header(
        title=f"{c['nom']} — Fiche candidat — Observations Présidentielles 2027",
        description=f"Fiche détaillée de {c['nom']} ({c['parti']}) : parcours, positions par sujet, patrimoine, affaires judiciaires, financement de campagne. Données publiques sourcées, neutralité absolue.",
        canonical=f"https://mlolita26.github.io/observations-presidentielles-2027/candidat-{slug}.html",
    ))

    parts.append('<p style="margin: 1rem 0;"><a href="index.html">← Retour à l\'accueil</a> · <a href="candidat.html?nom=' + slug + '">Voir la version interactive</a></p>')

    # En-tête candidat
    parts.append(f"""<header class="candidat-hero">
  <img class="photo" src="assets/photos/{h(slug)}.svg" alt="Photo placeholder — {h(c['nom'])}">
  <div>
    <h1>{h(c['nom'])}</h1>
    <span class="parti">{h(c['parti'])}</span>
    <p class="baseline">""")
    # Baseline
    ident = c.get('identite', {})
    bits = [f"{c['nom']}, {c['parti']}."]
    if ident.get('mandat_principal'):
        bits.append(f"{h(ident['mandat_principal'].get('value', ''))}.")
    if ident.get('candidature_2027'):
        bits.append(f"Candidature 2027 : {h(ident['candidature_2027'].get('value', ''))}.")
    parts.append(' '.join(bits))
    parts.append('</p></div></header>')

    parts.append(f"""
<p class="disclaimer">Données arrêtées au 12 mai 2026. <strong>Volume de données disponibles pour ce candidat&nbsp;:</strong> {n_votes} votes-clés référencés sur {n_votes_total} textes (le volume reflète la nature et la durée du mandat, pas l'activité — voir <a href="methodologie.html#biais">méthodologie</a>).</p>
""")

    # L'essentiel — 4 cartes
    parts.append('<section class="section-block"><h2>L\'essentiel</h2><div class="indicators-grid">')
    cand_27 = ident.get('candidature_2027', {})
    mandat = ident.get('mandat_principal', {})
    pat = c.get('patrimoine', {}).get('patrimoine_declare', {})
    act = c.get('activite_parlementaire', {}).get('presence_hemicycle', {})
    for label, v in [
        ('Candidature 2027', cand_27),
        ('Mandat actuel', mandat),
        ('Patrimoine net', pat),
        ('Présence parlementaire', act),
    ]:
        val = h(v.get('value', '—')) if v else '—'
        src = v.get('source_url') if v else None
        src_html = f' <a href="{h(src)}" target="_blank" rel="noopener" style="font-size:0.8em">[source]</a>' if src else ''
        parts.append(f'<article class="indicator-card"><span class="ic-label">{h(label)}</span><span class="ic-value">{val[:80]}</span><span class="ic-detail">{src_html}</span></article>')
    parts.append('</div></section>')

    # Identité complète
    parts.append('<section class="section-block"><h2>Identité et parcours</h2><dl style="display:grid; grid-template-columns: 200px 1fr; gap:0.5rem 1rem;">')
    for key, label in [
        ('date_naissance', 'Date de naissance'),
        ('lieu_naissance', 'Lieu de naissance'),
        ('formation', 'Formation'),
        ('profession_origine', "Profession d'origine"),
        ('premiere_election', 'Première élection'),
        ('fonctions_gouvernementales', 'Fonctions gouvernementales'),
        ('presidence_parti', 'Présidence de parti'),
    ]:
        if ident.get(key):
            parts.append(f'<dt><strong>{h(label)}</strong></dt><dd>{field_payload(ident[key])}</dd>')
    parts.append('</dl></section>')

    # Positions par sujet (8 cartes)
    parts.append('<section class="section-block" id="positions"><h2>Positions sur les 8 sujets de politique publique</h2><div class="candidate-positions-grid">')
    politiques = [s for s in sujets if s['type'] == 'politique']
    for s in politiques:
        pkey = s.get('positions_key')
        pos = (c.get('positions') or {}).get(pkey or s['id'])
        if not pos:
            pos = (c.get('positions') or {}).get(s['id'])
        parts.append(f'<article class="candidate-position-card"><h4>{h(s["titre"])}</h4>')
        parts.append('<div class="cpc-section"><span class="cpc-section-label">Ce qu\'il dit</span>')
        if pos and pos.get('value'):
            parts.append(f'<div class="cpc-section-content">{h(pos["value"])}</div>')
            if pos.get('source_url'):
                parts.append(f'<div style="margin-top:0.3em">{field_payload(pos)}</div>')
        else:
            parts.append('<div class="cpc-section-content non-trouve">Position non synthétisée sur ce sujet (voir <a href="sujet-' + h(s['id']) + '.html">page du sujet</a> pour le détail).</div>')
        parts.append('</div>')
        # Votes-clés du candidat sur ce sujet
        theme_filter = s.get('votes_filter', {}).get('themes') or []
        matched = [v for v in votes if any(t.lower() in (v.get('theme') or '').lower() for t in theme_filter if t)]
        cand_votes = [(v, (v.get('positions') or {}).get(slug, {})) for v in matched]
        cand_votes = [(v, p) for v, p in cand_votes if p.get('position') and p['position'] not in ('N/A', 'N_APPLICABLE')][:2]
        if cand_votes:
            parts.append('<div class="cpc-section"><span class="cpc-section-label">Ce qu\'il a voté</span><div class="cpc-section-content">')
            for v, p in cand_votes:
                parts.append(f'<div class="cpc-vote-line">{fmt_pos(p)} <span>{h(v["texte"])[:60]} ({h(v.get("annee"))})</span></div>')
            parts.append('</div></div>')
        parts.append(f'<a class="cpc-link" href="sujet-{h(s["id"])}.html">Comparer aux autres sur ce sujet →</a>')
        parts.append('</article>')
    parts.append('</div></section>')

    # Patrimoine
    pat_full = c.get('patrimoine', {})
    if pat_full:
        parts.append('<section class="section-block"><h2>Patrimoine et intérêts (HATVP)</h2><dl style="display:grid; grid-template-columns: 200px 1fr; gap:0.5rem 1rem;">')
        for key, label in [
            ('patrimoine_declare', 'Patrimoine déclaré'),
            ('revenus_annuels', 'Revenus annuels'),
            ('activites_annexes', 'Activités annexes'),
            ('participations', 'Participations / SCI'),
            ('conjoint', 'Conjoint·e (activité)'),
            ('evolution_patrimoine', 'Évolution entrée/sortie de mandat'),
        ]:
            if pat_full.get(key):
                parts.append(f'<dt><strong>{h(label)}</strong></dt><dd>{field_payload(pat_full[key])}</dd>')
        parts.append('</dl></section>')

    # Affaires
    aff = c.get('affaires', [])
    real = [a for a in aff if a.get('intitule') and 'Aucune affaire' not in (a.get('intitule') or '')]
    parts.append('<section class="section-block"><h2>Affaires judiciaires</h2>')
    if not real:
        parts.append('<p class="affaires-empty">Aucune affaire judiciaire notable connue publiquement à ce jour.</p>')
    else:
        parts.append('<p class="preinno" style="font-style:italic; color:#666; border-bottom:1px solid #C9A961; padding-bottom:0.5em">⚖ Présomption d\'innocence stricte respectée pour les procédures en cours. Pour les condamnations définitives, le statut est explicité comme tel.</p>')
        for a in real:
            src = a.get('source_url')
            src_html = f' <a href="{h(src)}" target="_blank" rel="noopener" style="font-size:0.8em">[source]</a>' if src else ''
            parts.append(f'<div class="affaire-item" style="padding:0.8em 0; border-bottom:1px dashed #ccc">')
            parts.append(f'<p><strong>{h(a.get("intitule"))}</strong>{src_html}</p>')
            parts.append(f'<p><em>Nature :</em> {h(a.get("nature"))}</p>')
            parts.append(f'<p><em>Statut juridique :</em> {h(a.get("statut_juridique"))}</p>')
            parts.append(f'<p><em>Période :</em> {h(a.get("annee"))}</p>')
            parts.append('</div>')
    parts.append('</section>')

    # Financement
    fin = c.get('financement', {})
    if fin:
        parts.append('<section class="section-block"><h2>Financement</h2><dl style="display:grid; grid-template-columns: 200px 1fr; gap:0.5rem 1rem;">')
        for key, label in [
            ('derniere_campagne', 'Dernière campagne'),
            ('total_depenses', 'Total dépenses'),
            ('origine_fonds', 'Origine des fonds'),
            ('compte_valide', 'Validation CNCCFP'),
            ('financement_parti', 'Financement du parti'),
        ]:
            if fin.get(key):
                parts.append(f'<dt><strong>{h(label)}</strong></dt><dd>{field_payload(fin[key])}</dd>')
        parts.append('</dl></section>')

    parts.append(HTML_FOOTER)
    return '\n'.join(parts)


# ----------------------------------------------------------------------------
# Page SUJET
# ----------------------------------------------------------------------------

def render_sujet(sujet, candidats, votes):
    parts = []
    parts.append(html_header(
        title=f"{sujet['titre']} — Sujet — Observations Présidentielles 2027",
        description=f"Position des 5 candidats à la présidentielle 2027 sur {sujet['titre'].lower()}. Votes-clés et déclarations publiques sourcées.",
        canonical=f"https://mlolita26.github.io/observations-presidentielles-2027/sujet-{sujet['id']}.html",
    ))

    parts.append('<p style="margin: 1rem 0;"><a href="index.html">← Retour à l\'accueil</a> · <a href="sujet.html?id=' + h(sujet['id']) + '">Voir la version interactive</a></p>')

    parts.append(f'<section class="hero"><h1>{h(sujet["titre"])}</h1>')
    parts.append(f'<p class="baseline">{h(sujet.get("definition", ""))}</p></section>')

    # Position de chaque candidat
    if sujet.get('type') == 'politique':
        parts.append('<section class="section-block"><h2>Où se situent les 5 candidats</h2>')
        parts.append('<p class="lead">Position publique synthétique extraite des programmes, tribunes ou déclarations officielles.</p>')
        parts.append('<div class="position-row">')
        pkey = sujet.get('positions_key') or sujet['id']
        for slug in CANDIDAT_ORDER:
            c = candidats[slug]
            pos = (c.get('positions') or {}).get(pkey) or (c.get('positions') or {}).get(sujet['id'])
            parts.append(f'<article class="position-card">')
            parts.append(f'<div class="pc-header"><img class="pc-photo" src="assets/photos/{h(slug)}.svg" alt=""><div><div class="pc-name">{h(c["nom"])}</div><div class="pc-parti">{h(c["parti"])}</div></div></div>')
            if pos and pos.get('value'):
                parts.append(f'<div class="pc-position">{h(pos["value"])}</div>')
                if pos.get('source_url'):
                    parts.append(f'<div class="pc-source">{field_payload(pos)}</div>')
            else:
                parts.append('<div class="pc-position non-trouve">Position non synthétisée sur ce sujet (voir fiche candidat).</div>')
            parts.append(f'<a class="pc-link" href="candidat-{h(slug)}.html#positions">Voir sa fiche →</a>')
            parts.append('</article>')
        parts.append('</div></section>')

        # Votes-clés liés
        theme_filter = sujet.get('votes_filter', {}).get('themes') or []
        matched = [v for v in votes if any(t.lower() in (v.get('theme') or '').lower() for t in theme_filter if t)]
        if matched:
            parts.append(f'<section class="section-block"><h2>Ce qu\'ils ont voté sur le sujet</h2>')
            parts.append(f'<p class="lead">{len(matched)} texte{"s" if len(matched) > 1 else ""} parlementaire{"s" if len(matched) > 1 else ""} lié{"s" if len(matched) > 1 else ""} au sujet.</p>')
            parts.append('<div class="table-wrap"><table class="data-table"><thead><tr><th>Année</th><th>Texte</th>')
            for cs in CANDIDAT_ORDER:
                parts.append(f'<th>{h(candidats[cs]["nom"].split()[-1])}</th>')
            parts.append('<th>Source</th></tr></thead><tbody>')
            for v in matched:
                parts.append(f'<tr><td class="numeric">{h(v.get("annee"))}</td><td>{h(v.get("texte"))}</td>')
                for cs in CANDIDAT_ORDER:
                    p = (v.get('positions') or {}).get(cs, {})
                    parts.append(f'<td>{fmt_pos(p)}</td>')
                src = next((p.get('source_url') for p in (v.get('positions') or {}).values() if isinstance(p, dict) and p.get('source_url')), None)
                parts.append(f'<td>{("<a href=\""+h(src)+"\" target=\"_blank\" rel=\"noopener\">lien</a>") if src else ""}</td></tr>')
            parts.append('</tbody></table></div></section>')
    elif sujet['id'] == 'financement':
        # Cas transverse Financement
        try:
            fin_data = json.loads((DATA / 'financement.json').read_text(encoding='utf-8'))
            parts.append('<section class="section-block"><h2>Comptes de campagne récents</h2>')
            parts.append('<table class="data-table"><thead><tr><th>Candidat</th><th>Élection</th><th>Dépenses</th><th>Recettes</th><th>Remboursement</th><th>Réformations</th></tr></thead><tbody>')
            for cmp in fin_data.get('campagnes_par_candidat', []):
                parts.append(f'<tr><td>{h(cmp.get("candidat_nom"))}</td><td>{h(cmp.get("election"))}</td><td>{h(cmp.get("depenses"))}</td><td>{h(cmp.get("recettes"))}</td><td>{h(cmp.get("remboursement"))}</td><td>{h(cmp.get("reformations"))}</td></tr>')
            parts.append('</tbody></table>')
            parts.append('<h2>Comptes des partis 2024</h2>')
            parts.append('<table class="data-table"><thead><tr><th>Parti</th><th>Total bilan</th><th>Produits</th><th>Aide publique</th><th>Dettes</th><th>Dont banques</th><th>Dont pers. phys.</th></tr></thead><tbody>')
            for p in fin_data.get('comptes_partis_2024', []):
                parts.append(f'<tr><td>{h(p.get("parti"))}</td><td>{h(p.get("total_bilan"))}</td><td>{h(p.get("produits_2024"))}</td><td>{h(p.get("aide_publique_2024"))}</td><td>{h(p.get("dettes_total"))}</td><td>{h(p.get("dont_banques"))}</td><td>{h(p.get("dont_personnes_physiques"))}</td></tr>')
            parts.append('</tbody></table></section>')
        except Exception:
            pass
    elif sujet['id'] == 'affaires':
        parts.append('<section class="section-block"><h2>Affaires judiciaires par candidat</h2>')
        parts.append('<p class="preinno" style="font-style:italic">⚖ Présomption d\'innocence stricte respectée pour les procédures en cours.</p>')
        for slug in CANDIDAT_ORDER:
            c = candidats[slug]
            parts.append(f'<h3>{h(c["nom"])}</h3>')
            real = [a for a in (c.get('affaires') or []) if a.get('intitule') and 'Aucune affaire' not in (a.get('intitule') or '')]
            if not real:
                parts.append('<p><em>Aucune affaire judiciaire notable connue publiquement à ce jour.</em></p>')
            else:
                for a in real:
                    src = a.get('source_url')
                    src_html = f' <a href="{h(src)}" target="_blank" rel="noopener" style="font-size:0.8em">[source]</a>' if src else ''
                    parts.append(f'<div class="affaire-item"><p><strong>{h(a.get("intitule"))}</strong>{src_html}</p><p><em>{h(a.get("statut_juridique"))}</em></p></div>')
        parts.append('</section>')
    elif sujet['id'] == 'patrimoine':
        parts.append('<section class="section-block"><h2>Patrimoine déclaré par candidat</h2>')
        parts.append('<table class="data-table"><thead><tr><th>Candidat</th><th>Patrimoine</th><th>Revenus annuels</th><th>Participations / SCI</th></tr></thead><tbody>')
        for slug in CANDIDAT_ORDER:
            c = candidats[slug]
            pat = c.get('patrimoine', {})
            parts.append(f'<tr><td><strong>{h(c["nom"])}</strong></td>')
            for k in ('patrimoine_declare', 'revenus_annuels', 'participations'):
                v = pat.get(k)
                parts.append(f'<td>{field_payload(v) if v else "—"}</td>')
            parts.append('</tr>')
        parts.append('</tbody></table></section>')

    parts.append(HTML_FOOTER)
    return '\n'.join(parts)


# ----------------------------------------------------------------------------
# Page GLOSSAIRE
# ----------------------------------------------------------------------------

def render_glossaire(glossaire):
    parts = []
    parts.append(html_header(
        title="Glossaire — Observations Présidentielles 2027",
        description="Définitions des termes techniques utilisés sur l'observatoire : juridique (témoin assisté, CJR…), HATVP, CNCCFP, parlementaires, Parlement européen.",
        canonical="https://mlolita26.github.io/observations-presidentielles-2027/glossaire-static.html",
    ))
    parts.append('<section class="hero"><h1>Glossaire</h1><p class="baseline">Les définitions ci-dessous concernent uniquement les termes utilisés sur ce site. Elles sont volontairement courtes et factuelles.</p></section>')

    # Grouper par catégorie
    by_cat = {}
    for e in glossaire:
        by_cat.setdefault(e['categorie'], []).append(e)
    parts.append('<nav style="background:#F0EFEA; padding:1em 1.5em; border:1px solid #D4D0C7; border-radius:4px; margin:1em 0"><strong>Catégories :</strong><ul style="columns:2; column-gap:2rem">')
    for cat in by_cat:
        parts.append(f'<li><a href="#cat-{h(cat.lower().replace(" ", "-"))}">{h(cat)} ({len(by_cat[cat])})</a></li>')
    parts.append('</ul></nav>')

    for cat, items in by_cat.items():
        parts.append(f'<section class="section-block"><h2 id="cat-{h(cat.lower().replace(" ", "-"))}">{h(cat)}</h2>')
        for e in items:
            parts.append(f'<article style="margin:0.8em 0; padding:0.8em 1em; border-left:2px solid #D4D0C7; background:#fff" id="{h(e["id"])}">')
            parts.append(f'<h3 style="margin:0 0 0.3em">{h(e["terme"])}</h3>')
            parts.append(f'<p>{h(e["definition_courte"])}</p>')
            if e.get('definition_longue'):
                parts.append(f'<p style="font-size:0.92em; color:#555">{h(e["definition_longue"])}</p>')
            parts.append('</article>')
        parts.append('</section>')

    parts.append(HTML_FOOTER)
    return '\n'.join(parts)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    cand_d = json.loads((DATA / 'candidats.json').read_text(encoding='utf-8'))
    candidats = cand_d['candidats']
    sujets = json.loads((DATA / 'sujets.json').read_text(encoding='utf-8'))
    votes = json.loads((DATA / 'votes-cles.json').read_text(encoding='utf-8'))
    glossaire = json.loads((DATA / 'glossaire.json').read_text(encoding='utf-8'))

    # Candidats
    print('Génération des fiches candidats...')
    for slug in CANDIDAT_ORDER:
        out = ROOT / f'candidat-{slug}.html'
        out.write_text(render_candidat(slug, candidats, sujets, votes), encoding='utf-8')
        print(f'  {out.name} ({out.stat().st_size//1024} ko)')

    # Sujets
    print('Génération des pages sujet...')
    for s in sujets:
        out = ROOT / f'sujet-{s["id"]}.html'
        out.write_text(render_sujet(s, candidats, votes), encoding='utf-8')
        print(f'  {out.name} ({out.stat().st_size//1024} ko)')

    # Glossaire
    print('Génération du glossaire statique...')
    out = ROOT / 'glossaire-static.html'
    out.write_text(render_glossaire(glossaire), encoding='utf-8')
    print(f'  {out.name} ({out.stat().st_size//1024} ko)')

    print()
    print(f'{len(CANDIDAT_ORDER) + len(sujets) + 1} fichiers HTML pré-rendus générés.')


if __name__ == '__main__':
    main()
