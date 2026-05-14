/* Observations Présidentielles 2027 — v2 (refonte par sujets)
   Vanilla JS, aucune dépendance, aucun appel API externe. */

(function () {
  'use strict';

  // ========================================================================
  // Constantes
  // ========================================================================

  const CANDIDATS_ORDER = ['bardella', 'philippe', 'retailleau', 'melenchon', 'attal'];

  const ICON_LINK = '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path fill="currentColor" d="M9 2v1.5h3.4L7 8.9 8.1 10l5.4-5.4V8H15V2H9zm-6 2v9h9V8.5h-1.5V11.5H4.5v-6H8V4H3z"/></svg>';

  // Termes du glossaire à détecter automatiquement dans les textes affichés.
  // L'ordre importe : un terme plus long doit précéder un terme plus court (« mise en examen » avant « examen »).
  const GLOSSARY_AUTO_TERMS = [
    { re: /\b(t[ée]moin assist[ée])\b/gi, id: 'temoin-assiste' },
    { re: /\b(mis en examen|mise en examen)\b/gi, id: 'mis-en-examen' },
    { re: /\b(condamn[ée]\s+(?:en\s+)?1[èeé]?re?\s+instance|condamnation\s+1[èeé]?re?\s+instance)\b/gi, id: 'condamne-1ere-instance' },
    { re: /\b(condamn[ée]\s+(?:en\s+)?appel)\b/gi, id: 'condamne-appel' },
    { re: /\b(condamn[ée]\s+d[ée]finitivement|condamnation d[ée]finitive)\b/gi, id: 'condamne-definitif' },
    { re: /\bCJR\b/g, id: 'cjr' },
    { re: /\bclassement sans suite\b/gi, id: 'classement-sans-suite' },
    { re: /\bHATVP\b/g, id: 'hatvp' },
    { re: /\bDSP\b/g, id: 'dsp' },
    { re: /\bDIA?\b/g, id: 'dia' },
    { re: /\bpantouflage\b/gi, id: 'pantouflage' },
    { re: /\bconflit d['']int[ée]r[ée]ts\b/gi, id: 'conflit-interets' },
    { re: /\bCNCCFP\b/g, id: 'cnccfp' },
    { re: /\br[ée]formation\b/gi, id: 'reformation' },
    { re: /\bplafond(?:\s+de\s+d[ée]penses)?\b/gi, id: 'plafond-depenses' },
    { re: /\b(?:scrutin\s+solennel|scrutins\s+solennels)\b/gi, id: 'scrutin-solennel' },
    { re: /\bcoh[ée]sion(?:\s+(?:de\s+)?groupe)\b/gi, id: 'cohesion-groupe' },
    { re: /\bshadow\s+rapporteur\b/gi, id: 'rapporteur' },
    { re: /\brapporteur\s+(?:fictif|titulaire)\b/gi, id: 'rapporteur' },
    { re: /\bproposition\s+de\s+loi\b/gi, id: 'proposition-loi' },
    { re: /\bamendements?\b/gi, id: 'amendement' },
    { re: /\b49\.3\b/g, id: '49-3' },
    { re: /\bmotion\s+de\s+censure\b/gi, id: 'motion-censure' },
    { re: /\bConf[ée]rence\s+des\s+pr[ée]sidents\b/gi, id: 'conference-presidents' },
    { re: /\bMEP\b/g, id: 'mep' },
    { re: /\bgroupe\s+ID\b/g, id: 'groupe-id' },
    { re: /\bgroupe\s+PfE\b/gi, id: 'groupe-pfe' },
    { re: /\bPatriots\s+for\s+Europe\b/gi, id: 'groupe-pfe' },
    { re: /\bFrontex\b/g, id: 'frontex' },
    { re: /\bAI\s+Act\b/g, id: 'ai-act' },
    { re: /\bCBAM\b/g, id: 'cbam' },
    { re: /\bPacte\s+(?:UE\s+)?[Aa]sile(?:\s+et\s+Migration)?\b/g, id: 'pacte-asile-ue' },
    { re: /\bUkraine\s+Facility\b/gi, id: 'ukraine-facility' },
  ];

  // ========================================================================
  // Cache + utilitaires
  // ========================================================================

  const cache = {};
  async function loadJSON(path) {
    if (cache[path]) return cache[path];
    const res = await fetch(path);
    if (!res.ok) throw new Error(`HTTP ${res.status} on ${path}`);
    const data = await res.json();
    cache[path] = data;
    return data;
  }

  function escapeHtml(s) {
    if (s == null) return '';
    return String(s)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');
  }

  function getParam(name) {
    return new URLSearchParams(window.location.search).get(name);
  }

  function showError(container, msg) {
    container.innerHTML = `<p class="message message--error">${escapeHtml(msg)}</p>`;
  }

  function truncate(s, max) {
    if (s == null) return '';
    const str = String(s);
    return str.length > max ? str.slice(0, max - 1) + '…' : str;
  }

  function isNonTrouve(value) {
    if (value == null) return false;
    return /^(NON\s*TROUV[ÉE]|A\s+COMPLETER|À\s+COMPLÉTER|^ND$)/i.test(String(value).trim());
  }

  function sourceLink(url, label) {
    if (!url) return '';
    const safeLabel = escapeHtml(label || 'Voir la source');
    const truncated = safeLabel.length > 80 ? safeLabel.slice(0, 77) + '…' : safeLabel;
    return ` <a class="source-link" href="${escapeHtml(url)}" target="_blank" rel="noopener" title="${safeLabel}" aria-label="Source : ${truncated}">${ICON_LINK}<span>source</span></a>`;
  }

  // Met automatiquement les termes connus du glossaire dans des <span class="term">.
  // À utiliser sur des chaînes déjà passées par escapeHtml().
  function injectGlossaryTerms(escapedHtml) {
    if (!escapedHtml) return '';
    let out = escapedHtml;
    for (const { re, id } of GLOSSARY_AUTO_TERMS) {
      out = out.replace(re, (match) => `<span class="term" data-term="${id}" tabindex="0">${match}</span>`);
    }
    return out;
  }

  // Convertit une valeur brute en HTML enrichi avec termes glossaire.
  function richText(value) {
    if (value == null) return '';
    return injectGlossaryTerms(escapeHtml(String(value)));
  }

  function votePastille(position, detail, compact = false) {
    const map = {
      'POUR': { cls: 'pour', txt: 'POUR', glyph: '✓' },
      'CONTRE': { cls: 'contre', txt: 'CONTRE', glyph: '✗' },
      'ABSTENTION': { cls: 'abstention', txt: 'ABST.', glyph: '⊝' },
      'ABSENT': { cls: 'absent', txt: 'ABS.', glyph: '⊘' },
      'N/A': { cls: 'na', txt: '—', glyph: '—' },
      'AUTRE': { cls: 'autre', txt: '?', glyph: '?' },
    };
    const m = map[position] || map['AUTRE'];
    const titleAttr = detail ? ` title="${escapeHtml(detail)}"` : '';
    const inlineCls = compact ? ' vote--inline' : '';
    return `<span class="vote vote--${m.cls}${inlineCls}" aria-label="${m.txt}"${titleAttr}>${m.glyph} ${m.txt}</span>`;
  }

  function voteLegend() {
    return `<p class="vote-legend" aria-label="Légende des positions de vote">
      <span>${votePastille('POUR')} pour le texte</span>
      <span>${votePastille('CONTRE')} contre le texte</span>
      <span>${votePastille('ABSTENTION')} abstention</span>
      <span>${votePastille('ABSENT')} absent au scrutin</span>
      <span>${votePastille('N/A')} pas d'application (sans mandat / autre chambre)</span>
    </p>`;
  }

  // ========================================================================
  // Glossaire — tooltips
  // ========================================================================

  let GLOSSAIRE_INDEX = null; // {id: entry}

  async function loadGlossaire() {
    if (GLOSSAIRE_INDEX) return GLOSSAIRE_INDEX;
    try {
      const list = await loadJSON('data/glossaire.json');
      GLOSSAIRE_INDEX = {};
      for (const entry of list) GLOSSAIRE_INDEX[entry.id] = entry;
    } catch (e) {
      console.warn('Glossaire non chargé', e);
      GLOSSAIRE_INDEX = {};
    }
    return GLOSSAIRE_INDEX;
  }

  function initTooltips(root = document.body) {
    // Lazy : enrichir chaque .term avec un popover au survol (CSS gère display).
    root.querySelectorAll('.term[data-term]').forEach(el => {
      if (el.dataset.tipInit === '1') return;
      el.dataset.tipInit = '1';
      const id = el.dataset.term;
      const entry = GLOSSAIRE_INDEX && GLOSSAIRE_INDEX[id];
      if (!entry) return;
      const popover = document.createElement('span');
      popover.className = 'glossary-popover';
      popover.setAttribute('role', 'tooltip');
      popover.innerHTML = `<strong>${escapeHtml(entry.terme)}</strong>${escapeHtml(entry.definition_courte)} <a href="glossaire.html#${escapeHtml(entry.id)}">Voir le glossaire →</a>`;
      el.appendChild(popover);
    });
    // Accessibilité clavier : Entrée / Espace ouvrent/ferment le popover
    root.addEventListener('keydown', (ev) => {
      if (!(ev.key === 'Enter' || ev.key === ' ')) return;
      const el = ev.target.closest('.term[data-term]');
      if (!el) return;
      ev.preventDefault();
      el.classList.toggle('is-open');
    });
  }

  // ========================================================================
  // Helpers candidat → vue
  // ========================================================================

  function candidatPhoto(slug, nom, cls = '') {
    return `<img class="${cls || 'photo'}" src="assets/photos/${escapeHtml(slug)}.svg" alt="Photo placeholder — ${escapeHtml(nom)}">`;
  }

  function bestSourceUrl(payload, fallback) {
    if (payload && payload.source_url) return payload.source_url;
    return fallback || null;
  }

  function getValue(payload) {
    if (!payload) return null;
    return payload.value != null ? String(payload.value) : null;
  }

  // Trouve un nombre € dans une chaîne (patrimoine déclaré). Renvoie un float ou null.
  function parseEuros(text) {
    if (!text) return null;
    // Cherche des nombres avec unités M€ ou k€ ou €
    const cleaned = String(text).replace(/\s/g, ' ').replace(/EUR/gi, '€');
    let m = cleaned.match(/(\d+(?:[.,]\d+)?)\s*M€/i);
    if (m) return parseFloat(m[1].replace(',', '.')) * 1e6;
    m = cleaned.match(/(\d+(?:[.,]\d+)?)\s*k€/i);
    if (m) return parseFloat(m[1].replace(',', '.')) * 1e3;
    // Pattern "1 370 000" ou "1.152.000" ou "13 519 579 €"
    m = cleaned.match(/(\d[\d\s.]{4,})\s*€/);
    if (m) {
      const num = m[1].replace(/[\s.]/g, '').replace(',', '.');
      const v = parseFloat(num);
      return isNaN(v) ? null : v;
    }
    return null;
  }

  function formatEuros(v) {
    if (v == null) return null;
    if (v >= 1e6) return (v / 1e6).toLocaleString('fr-FR', { maximumFractionDigits: 2 }) + ' M€';
    if (v >= 1e3) return (v / 1e3).toLocaleString('fr-FR', { maximumFractionDigits: 0 }) + ' k€';
    return v.toLocaleString('fr-FR') + ' €';
  }

  // ========================================================================
  // PAGE INDEX
  // ========================================================================

  async function renderIndex() {
    try {
      const [data, sujets] = await Promise.all([
        loadJSON('data/candidats.json'),
        loadJSON('data/sujets.json'),
        loadGlossaire(),
      ]);

      // Section A : sujets politiques (8 cartes)
      const sGrid = document.getElementById('sujets-politiques');
      const politiques = sujets.filter(s => s.type === 'politique');
      sGrid.innerHTML = politiques.map(renderSujetCard).join('');
      sGrid.removeAttribute('aria-busy');

      // Section B : 5 candidats
      const cGrid = document.getElementById('candidats-cards');
      cGrid.innerHTML = CANDIDATS_ORDER.map(slug => renderIndexCandidatCard(data.candidats[slug])).join('');
      cGrid.removeAttribute('aria-busy');

      // Section C : Transparence (3 cartes ministats)
      const tCards = document.getElementById('transparence-cards');
      const transverses = sujets.filter(s => s.type === 'transverse');
      const totalAffaires = CANDIDATS_ORDER.reduce((acc, slug) => {
        const aff = (data.candidats[slug].affaires || []).filter(a => a.intitule && !/Aucune affaire/i.test(a.intitule));
        return acc + aff.length;
      }, 0);
      const fin = await loadJSON('data/financement.json');
      const stats = {
        patrimoine: { big: '5', desc: 'Candidats, dont les déclarations HATVP sont analysées. Patrimoine, revenus, biens, participations.' },
        affaires: { big: String(totalAffaires), desc: `Procédure${totalAffaires > 1 ? 's' : ''} judiciaire${totalAffaires > 1 ? 's' : ''} connue${totalAffaires > 1 ? 's' : ''} publiquement, présomption d'innocence stricte respectée.` },
        financement: { big: String(fin.comptes_partis_2024.length), desc: `Partis politiques analysés (comptes annuels CNCCFP 2024) + ${fin.campagnes_par_candidat.length} comptes de campagne décortiqués.` },
      };
      tCards.innerHTML = transverses.map(s => {
        const st = stats[s.id] || { big: '?', desc: s.teasing };
        return `<a class="ministat-card" href="sujet-${escapeHtml(s.id)}.html">
          <span class="ms-big">${escapeHtml(st.big)}</span>
          <span class="ms-title">${escapeHtml(s.titre)}</span>
          <span class="ms-desc">${escapeHtml(st.desc)}</span>
        </a>`;
      }).join('');

      initTooltips();
    } catch (err) {
      const grid = document.getElementById('sujets-politiques') || document.body;
      showError(grid, `Impossible de charger les données : ${err.message}`);
      console.error(err);
    }
  }

  function renderSujetCard(sujet) {
    const cls = sujet.type === 'transverse' ? 'sujet-card sujet-card--transverse' : 'sujet-card';
    return `<a class="${cls}" href="sujet-${escapeHtml(sujet.id)}.html">
      <span class="sc-icon" aria-hidden="true">${escapeHtml(sujet.icon_letter || sujet.titre[0])}</span>
      <span class="sc-content">
        <span class="sc-title">${escapeHtml(sujet.titre)}</span>
        <span class="sc-teasing">${escapeHtml(sujet.teasing || '')}</span>
      </span>
    </a>`;
  }

  function renderIndexCandidatCard(c) {
    if (!c) return '';
    const baseline = buildCandidatBaseline(c);
    const candidature = c.identite && c.identite.candidature_2027;
    const candStatus = candidature ? truncate(candidature.value, 60) : '—';
    return `<article class="card-candidat">
      ${candidatPhoto(c.slug, c.nom)}
      <h3>${escapeHtml(c.nom)}</h3>
      <p class="parti">${escapeHtml(c.parti)}</p>
      <p style="font-size: 0.88rem; color: var(--c-text-soft); margin: 0 0 0.75rem;">${escapeHtml(baseline)}</p>
      <dl class="indicateurs">
        <div><dt>Candidature 2027&nbsp;:</dt><dd>${escapeHtml(candStatus)}</dd></div>
      </dl>
      <a class="btn" href="candidat-${escapeHtml(c.slug)}.html">Voir la fiche</a>
    </article>`;
  }

  function buildCandidatBaseline(c) {
    // 1 phrase : nom + parti + mandat actuel + statut candidature
    const mandat = c.identite && c.identite.mandat_principal && c.identite.mandat_principal.value;
    const cand = c.identite && c.identite.candidature_2027 && c.identite.candidature_2027.value;
    const candShort = cand ? (cand.includes('Déclaré') ? cand.replace(/\([^)]+\)/g, '').trim() : 'Pressenti') : '';
    const mandatShort = mandat ? truncate(mandat, 65) : '';
    return [mandatShort, candShort].filter(Boolean).join(' · ');
  }

  // ========================================================================
  // PAGE SUJET (cœur du site)
  // ========================================================================

  async function renderSujetPage() {
    const id = getParam('id') || 'immigration';
    await renderSujet(id, null, document.getElementById('sujet-content'), {
      titreElement: document.getElementById('sujet-titre'),
      definitionElement: document.getElementById('sujet-definition'),
      otherSujetsElement: document.getElementById('other-sujets'),
    });
  }

  /**
   * Rendu d'un sujet, partagé entre sujet.html et comparer.html.
   * candidatsSlice : null = tous ; sinon liste de slugs
   * dom : { titreElement, definitionElement, otherSujetsElement } (optionnel)
   */
  async function renderSujet(id, candidatsSlice, container, dom = {}) {
    try {
      const [data, votes, sujets] = await Promise.all([
        loadJSON('data/candidats.json'),
        loadJSON('data/votes-cles.json'),
        loadJSON('data/sujets.json'),
        loadGlossaire(),
      ]);
      const sujet = sujets.find(s => s.id === id);
      if (!sujet) {
        showError(container, `Sujet inconnu : "${id}". Sujets disponibles : ${sujets.map(s => s.id).join(', ')}.`);
        return;
      }
      const slugs = candidatsSlice && candidatsSlice.length ? candidatsSlice : CANDIDATS_ORDER;

      if (dom.titreElement) dom.titreElement.textContent = sujet.titre;
      if (dom.definitionElement) dom.definitionElement.innerHTML = richText(sujet.definition);
      document.title = `${sujet.titre} — Observations Présidentielles 2027`;

      // Construction des blocs selon le type de sujet
      let html = '';

      if (sujet.type === 'politique') {
        html += renderSujetPolitique(sujet, data.candidats, votes, slugs);
      } else if (sujet.id === 'patrimoine') {
        html += renderSujetPatrimoine(data.candidats, slugs);
      } else if (sujet.id === 'affaires') {
        html += renderSujetAffaires(data.candidats, slugs);
      } else if (sujet.id === 'financement') {
        const fin = await loadJSON('data/financement.json');
        html += renderSujetFinancement(fin, data.candidats, slugs);
      }

      container.innerHTML = html;

      // Liens vers autres sujets
      if (dom.otherSujetsElement) {
        const others = sujets.filter(s => s.id !== id);
        dom.otherSujetsElement.innerHTML = others.map(renderSujetCard).join('');
      }

      initTooltips();
    } catch (err) {
      showError(container, `Impossible de charger le sujet : ${err.message}`);
      console.error(err);
    }
  }

  function renderSujetPolitique(sujet, candidats, votes, slugs) {
    // Bloc 1 : Où se situent les 5 candidats (positions publiques)
    let positions = `<section class="section-block">
      <h2>Où se situent les candidats</h2>
      <p class="lead">Position publique synthétique extraite des programmes, tribunes ou déclarations officielles. Cliquez sur « Voir la fiche » pour le détail.</p>
      <div class="position-row">`;
    for (const slug of slugs) {
      const c = candidats[slug];
      if (!c) continue;
      const pkey = sujet.positions_key || sujet.id;
      const positionPayload = (c.positions && (c.positions[pkey] || c.positions[sujet.id])) || null;
      const positionValue = positionPayload ? positionPayload.value : null;
      const positionSimple = positionPayload ? positionPayload.enonce_simple : null;
      const positionUrl = positionPayload ? positionPayload.source_url : null;
      const nonTrouve = !positionValue || isNonTrouve(positionValue);
      // Préférer la version simple si disponible
      const mainText = nonTrouve ? 'Position non synthétisée sur ce sujet (voir fiche candidat).' : (positionSimple || positionValue);
      const valueCls = nonTrouve ? ' non-trouve' : '';
      positions += `<article class="position-card">
        <div class="pc-header">
          ${candidatPhoto(slug, c.nom, 'pc-photo')}
          <div>
            <div class="pc-name">${escapeHtml(c.nom)}</div>
            <div class="pc-parti">${escapeHtml(c.parti)}</div>
          </div>
        </div>
        <div class="pc-position${valueCls}">${richText(mainText)}</div>
        <div class="pc-source">${sourceLink(positionUrl, positionPayload && positionPayload.source_label)}</div>
        <a class="pc-link" href="candidat-${escapeHtml(slug)}.html#positions">Voir sa fiche →</a>
      </article>`;
    }
    positions += `</div></section>`;

    // Bloc 2 : Votes-clés liés au sujet
    const themeList = sujet.votes_filter && sujet.votes_filter.themes ? sujet.votes_filter.themes : [];
    const textIncludes = sujet.votes_filter && sujet.votes_filter.textes_includes ? sujet.votes_filter.textes_includes : [];
    const matched = votes.filter(v => {
      const theme = (v.theme || '').toLowerCase();
      const texte = (v.texte || '').toLowerCase();
      const themeMatch = themeList.some(t => theme.includes(t.toLowerCase()));
      const textMatch = textIncludes.some(t => texte.includes(t.toLowerCase()));
      return themeMatch || textMatch;
    });

    let votesBloc = '';
    if (matched.length) {
      votesBloc = `<section class="section-block">
        <h2>Ce qu'ils ont voté sur le sujet</h2>
        <p class="lead">${matched.length} texte${matched.length > 1 ? 's' : ''} parlementaire${matched.length > 1 ? 's' : ''} lié${matched.length > 1 ? 's' : ''} au sujet. Survolez une pastille pour le détail.</p>
        ${voteLegend()}
        <div class="table-wrap"><table class="data-table">
          <thead><tr><th>Année</th><th>Texte</th>${slugs.map(s => `<th>${escapeHtml(candidats[s].nom.split(' ').slice(-1)[0])}</th>`).join('')}<th>Source</th></tr></thead>
          <tbody>${matched.map(v => {
            const cells = slugs.map(s => {
              const p = (v.positions || {})[s] || { position: 'N/A' };
              return `<td>${votePastille(p.position, p.detail)}</td>`;
            }).join('');
            const someSrc = slugs.map(s => (v.positions || {})[s]).find(p => p && p.source_url);
            const src = someSrc ? sourceLink(someSrc.source_url, someSrc.source_label || v.source_label) : '';
            const titre = v.titre_fr || v.texte;
            const resume = v.resume ? `<details style="margin-top:0.25rem"><summary style="cursor:pointer; font-size:0.82rem; color:var(--c-accent)">Résumé</summary><p style="font-size:0.88rem; color:var(--c-text-soft); margin:0.3rem 0 0">${escapeHtml(v.resume)}</p></details>` : '';
            // Lister les contextes atypiques (sous le tableau)
            const ctxList = Object.entries(v.positions || {}).filter(([_, p]) => p && p.contexte).map(([slug, p]) => `<li><strong>${escapeHtml(slug)}</strong> — ${escapeHtml(p.contexte)}</li>`).join('');
            const ctxBlock = ctxList ? `<details style="margin-top:0.3rem"><summary style="cursor:pointer; font-size:0.82rem; color:var(--c-gold)">⚠ Contextes de vote atypiques</summary><ul style="font-size:0.85rem; margin:0.3rem 0 0; padding-left:1.5rem">${ctxList}</ul></details>` : '';
            return `<tr><td class="numeric">${escapeHtml(String(v.annee || ''))}</td><td><div>${richText(titre)}</div>${resume}${ctxBlock}</td>${cells}<td>${src}</td></tr>`;
          }).join('')}</tbody>
        </table></div>
      </section>`;
    }

    // Bloc 3 : Cohérence discours / actes
    let dvaBloc = '';
    if (sujet.discours_themes && sujet.discours_themes.length) {
      const dvaItems = [];
      for (const slug of slugs) {
        const c = candidats[slug];
        const dva = (c.discours_vs_actes || []).filter(d => sujet.discours_themes.some(t => (d.theme || '').toLowerCase().includes(t.toLowerCase())));
        if (dva.length) dvaItems.push({ slug, c, entries: dva });
      }
      if (dvaItems.length) {
        dvaBloc = `<section class="section-block">
          <h2>Cohérence discours / actes</h2>
          <p class="lead">Comparaison entre ce que le candidat dit publiquement et ce qu'on peut vérifier dans ses actes (votes, décisions, comportements).</p>
          <div class="candidate-positions-grid">${dvaItems.map(({ slug, c, entries }) => {
            return entries.map(d => `<article class="candidate-position-card">
              <h4>${escapeHtml(c.nom)}</h4>
              <div class="cpc-section">
                <span class="cpc-section-label">Ce qu'il dit</span>
                <div class="cpc-section-content">${richText(d.discours || '—')}</div>
              </div>
              <div class="cpc-section">
                <span class="cpc-section-label">Ce qu'il a fait</span>
                <div class="cpc-section-content">${richText(d.actes || '—')}</div>
              </div>
              <div class="pc-source">${sourceLink(d.source_url, 'Source')}</div>
            </article>`).join('');
          }).join('')}</div>
        </section>`;
      }
    }

    return positions + votesBloc + dvaBloc;
  }

  function renderSujetPatrimoine(candidats, slugs) {
    // Construit l'échelle commune sur le patrimoine net
    const data = slugs.map(slug => {
      const c = candidats[slug];
      const pat = c.patrimoine && c.patrimoine.patrimoine_declare;
      const raw = pat && pat.value;
      const parsed = parseEuros(raw);
      return { slug, c, raw, parsed, url: pat && pat.source_url };
    });
    const maxV = Math.max(...data.map(d => d.parsed || 0)) || 1;

    let bars = '<div class="bar-chart-compact">';
    for (const d of data) {
      const pct = d.parsed ? Math.max(2, (d.parsed / maxV) * 100) : 0;
      const display = d.parsed ? formatEuros(d.parsed) : (d.raw ? truncate(d.raw, 28) : 'NON TROUVÉ');
      const cls = isNonTrouve(d.raw) || !d.parsed ? ' non-trouve' : '';
      bars += `<div class="bcc-row">
        <span class="bcc-label">${escapeHtml(d.c.nom)}</span>
        <span class="bcc-track"><span class="bcc-fill" style="width:${pct.toFixed(1)}%"></span></span>
        <span class="bcc-value${cls}">${escapeHtml(display)}${sourceLink(d.url, 'HATVP')}</span>
      </div>`;
    }
    bars += '</div>';

    let block1 = `<section class="section-block">
      <h2>Patrimoine net déclaré — comparé</h2>
      <p class="lead">Patrimoine net (actif moins passif) tel qu'il figure dans la déclaration HATVP la plus récente. Les déclarations ne portent pas toutes sur la même année — voir détail.</p>
      ${bars}
      <p style="font-size:0.85rem; color: var(--c-text-soft); margin-top: 0.5rem;">Mentions « NON TROUVÉ » signalent une déclaration disponible mais non extraite du PDF brut (voir fiche candidat pour la voie de recours).</p>
    </section>`;

    let revRows = slugs.map(slug => {
      const c = candidats[slug];
      const rev = c.patrimoine && c.patrimoine.revenus_annuels;
      const cls = !rev || isNonTrouve(rev.value) ? ' non-trouve' : '';
      return `<tr>
        <td><strong>${escapeHtml(c.nom)}</strong></td>
        <td class="${cls.trim()}">${richText(rev ? rev.value : '—')}</td>
        <td>${sourceLink(rev && rev.source_url, rev && rev.source_label)}</td>
      </tr>`;
    }).join('');

    let block2 = `<section class="section-block">
      <h2>Revenus annuels et activités annexes</h2>
      <p class="lead">Source : déclarations HATVP successives. Les revenus reflètent l'indemnité du mandat + revenus annexes déclarés.</p>
      <div class="table-wrap"><table class="data-table">
        <thead><tr><th>Candidat</th><th>Revenus annuels (résumé)</th><th>Source</th></tr></thead>
        <tbody>${revRows}</tbody>
      </table></div>
    </section>`;

    let detailRows = slugs.map(slug => {
      const c = candidats[slug];
      const p = c.patrimoine || {};
      return `<tr>
        <td><strong>${escapeHtml(c.nom)}</strong></td>
        <td>${richText(getValue(p.participations) || '—')}</td>
        <td>${richText(getValue(p.conjoint) || '—')}</td>
        <td>${richText(getValue(p.activites_annexes) || '—')}</td>
      </tr>`;
    }).join('');
    let block3 = `<section class="section-block">
      <h2>Participations, conjoint, activités annexes</h2>
      <div class="table-wrap"><table class="data-table">
        <thead><tr><th>Candidat</th><th>Participations / SCI</th><th>Conjoint·e (activité)</th><th>Activités annexes</th></tr></thead>
        <tbody>${detailRows}</tbody>
      </table></div>
    </section>`;

    return block1 + block2 + block3;
  }

  function renderSujetAffaires(candidats, slugs) {
    let out = `<section class="section-block">
      <h2>Toutes les procédures connues, par candidat</h2>
      <p class="lead">Pour chaque candidat, les procédures judiciaires connues publiquement sont listées avec leur <span class="term" data-term="condamne-1ere-instance">statut juridique précis</span>. <strong>La présomption d'innocence est strictement respectée</strong> : aucun terme définitif n'est employé tant qu'une condamnation n'est pas devenue définitive.</p>`;
    for (const slug of slugs) {
      const c = candidats[slug];
      out += `<h3 style="margin-top: 1.5rem;">${escapeHtml(c.nom)}</h3>`;
      out += renderAffairesBlock(c.affaires || []);
    }
    out += '</section>';
    return out;
  }

  function renderAffairesBlock(affaires) {
    const realCases = (affaires || []).filter(a => a.intitule && !/Aucune affaire/i.test(a.intitule));
    if (!realCases.length) {
      return `<p class="affaires-empty">Aucune affaire judiciaire notable connue publiquement à ce jour.</p>`;
    }
    const preinno = `<p class="preinno">⚖ Présomption d'innocence respectée — statut juridique précis indiqué pour chaque procédure.</p>`;
    const items = realCases.map(a => `<div class="affaire-item">
      <p class="intitule">${richText(a.intitule)}${sourceLink(a.source_url, a.source_label || 'Source')}</p>
      <p class="statut">${richText(a.statut_juridique || '—')}</p>
      <p class="meta">Nature&nbsp;: ${richText(a.nature || '—')} · Période&nbsp;: ${escapeHtml(String(a.annee || '—'))}</p>
    </div>`).join('');
    return `<div class="affaires-block">${preinno}${items}</div>`;
  }

  function renderSujetFinancement(fin, candidats, slugs) {
    // Bloc 1 : Comptes de campagne
    let block1 = `<section class="section-block">
      <h2>Comptes de campagne récents analysables</h2>
      <aside style="background:#F0EFEA; border-left:3px solid var(--c-accent); padding:0.875rem 1.125rem; border-radius:4px; margin:0.75rem 0 1rem; font-size:0.92rem">
        <p style="margin:0 0 0.5rem"><strong>💡 Comprendre ce tableau</strong></p>
        <p style="margin:0; line-height:1.55">Quand un candidat fait campagne, il doit déclarer <strong>chaque euro dépensé</strong> à un organisme public, la <span class="term" data-term="cnccfp">CNCCFP</span>. L'État rembourse une partie de ces dépenses si le candidat a fait au moins 5 % des voix. Si la CNCCFP juge qu'une dépense n'est pas justifiée ou pas liée à la campagne, elle la <strong>refuse</strong>&nbsp;: c'est une «&nbsp;<span class="term" data-term="reformation">réformation</span>&nbsp;». Plus il y a de réformations, plus le compte a posé problème.</p>
      </aside>
      <div class="table-wrap"><table class="data-table">
        <thead><tr><th>Candidat</th><th>Élection</th><th>Date décision</th><th class="numeric">Dépenses</th><th class="numeric">Recettes</th><th>Remboursement</th><th><span class="term" data-term="reformation">Réformations</span></th><th>Source</th></tr></thead>
        <tbody>${(fin.campagnes_par_candidat || []).map(c => `<tr>
          <td><strong>${escapeHtml(c.candidat_nom || '')}</strong></td>
          <td>${escapeHtml(c.election || '')}</td>
          <td>${escapeHtml(String(c.date_decision || ''))}</td>
          <td class="numeric">${escapeHtml(c.depenses || '')}</td>
          <td class="numeric">${escapeHtml(c.recettes || '')}</td>
          <td>${escapeHtml(c.remboursement || '')}</td>
          <td>${richText(c.reformations || '')}</td>
          <td>${sourceLink(c.source_url, 'CNCCFP / JORF')}</td>
        </tr>`).join('')}</tbody>
      </table></div>
    </section>`;

    // Bloc 2 : Comptes des partis
    let block2 = `<section class="section-block">
      <h2>Comptes des partis politiques — exercice 2024</h2>
      <aside style="background:#F0EFEA; border-left:3px solid var(--c-accent); padding:0.875rem 1.125rem; border-radius:4px; margin:0.75rem 0 1rem; font-size:0.92rem">
        <p style="margin:0 0 0.5rem"><strong>💡 Comprendre ce tableau</strong></p>
        <p style="margin:0 0 0.4rem; line-height:1.55">Chaque parti politique publie ses comptes annuels. Voici comment lire les colonnes&nbsp;:</p>
        <ul style="margin:0; padding-left:1.4rem; line-height:1.55">
          <li><strong>Produits</strong>&nbsp;: l'argent que le parti a reçu dans l'année (cotisations des adhérents, dons, aide de l'État).</li>
          <li><strong>Aide publique</strong>&nbsp;: subvention versée par l'État. Calculée selon le score aux législatives + nombre de parlementaires affiliés.</li>
          <li><strong>Dettes</strong>&nbsp;: ce que le parti doit rembourser. <em>Dont banques</em>&nbsp;: emprunté à des banques. <em>Dont personnes physiques</em>&nbsp;: emprunté à des particuliers (sujet sensible historiquement, car peut indiquer des financements politiques privés).</li>
        </ul>
        <p style="margin:0.5rem 0 0; line-height:1.55; font-style:italic; color:var(--c-text-soft)">Une cellule vide signifie&nbsp;: dette nulle ou non significative dans cette catégorie selon la CNCCFP.</p>
      </aside>
      <p class="lead" style="margin-top:0.5rem">Source officielle&nbsp;: ${sourceLink(fin.partis_source_url, fin.partis_source_label || 'CNCCFP — PDF officiel')}</p>
      <div class="table-wrap"><table class="data-table">
        <thead><tr><th>Parti</th><th>Total bilan</th><th class="numeric">Produits 2024</th><th><span class="term" data-term="aide-publique-partis">Aide pub. 2024</span></th><th>Aide pub. 2025</th><th>Dettes</th><th>Dont banques</th><th>Dont pers. physiques</th></tr></thead>
        <tbody>${(fin.comptes_partis_2024 || []).map(p => `<tr>
          <td><strong>${escapeHtml(p.parti || '')}</strong></td>
          <td>${escapeHtml(p.total_bilan || '')}</td>
          <td class="numeric">${escapeHtml(p.produits_2024 || '')}</td>
          <td>${escapeHtml(p.aide_publique_2024 || '')}</td>
          <td>${escapeHtml(p.aide_publique_2025 || '')}</td>
          <td>${escapeHtml(p.dettes_total || '')}</td>
          <td>${escapeHtml(p.dont_banques || '')}</td>
          <td>${escapeHtml(p.dont_personnes_physiques || '')}</td>
        </tr>`).join('')}</tbody>
      </table></div>
    </section>`;

    return block1 + block2;
  }

  // ========================================================================
  // PAGE CANDIDAT — v2
  // ========================================================================

  async function renderCandidatV2() {
    const slug = getParam('nom');
    const article = document.getElementById('candidat-article');
    if (!slug || !CANDIDATS_ORDER.includes(slug)) {
      showError(article, `Candidat inconnu. Valeurs acceptées : ${CANDIDATS_ORDER.join(', ')}.`);
      return;
    }
    try {
      const [data, votes, sujets, fin] = await Promise.all([
        loadJSON('data/candidats.json'),
        loadJSON('data/votes-cles.json'),
        loadJSON('data/sujets.json'),
        loadJSON('data/financement.json'),
        loadGlossaire(),
      ]);
      const c = data.candidats[slug];
      document.title = `${c.nom} — Observations Présidentielles 2027`;

      const html = renderCandidatHero(c) +
        renderCandidatEssentiel(c) +
        renderCandidatParcours(c) +
        renderCandidatPositions(c, votes, sujets) +
        renderCandidatPatrimoine(c, data.candidats) +
        renderCandidatJustice(c) +
        renderCandidatFinancement(c, fin) +
        renderCandidatSources(c, fin);

      article.innerHTML = html;
      article.removeAttribute('aria-busy');
      initTooltips();
    } catch (err) {
      showError(article, `Impossible de charger la fiche : ${err.message}`);
      console.error(err);
    }
  }

  function renderCandidatHero(c) {
    const baseline = buildCandidatLongBaseline(c);
    const vol = c._volume_donnees || {};
    const volBlock = vol.titre ? `<aside style="background:#FCFAF3; border:2px solid #C9A961; border-radius:4px; padding:1rem 1.25rem; margin:1rem 0">
      <p style="font-style:italic; color:var(--c-accent); margin:0 0 0.5rem"><strong>📊 ${escapeHtml(vol.titre)}</strong></p>
      <p style="margin:0; font-size:0.93rem; color:var(--c-text-soft)">${escapeHtml(vol.detail || '')}</p>
    </aside>` : '';
    return `<header class="candidat-hero">
      ${candidatPhoto(c.slug, c.nom)}
      <div>
        <h1>${escapeHtml(c.nom)}</h1>
        <span class="parti">${escapeHtml(c.parti)}</span>
        <p class="baseline">${richText(baseline)}</p>
      </div>
    </header>
    ${volBlock}
    <p class="disclaimer">Données arrêtées au 12 mai 2026. Survolez un terme souligné en pointillé doré pour ouvrir sa définition. Cliquez sur l'icône <span aria-hidden="true">↗</span> à droite d'une donnée pour ouvrir la source officielle.</p>`;
  }

  function buildCandidatLongBaseline(c) {
    // Phrase factuelle 1-2 lignes construite à partir des données
    const ident = c.identite || {};
    const parts = [];
    parts.push(`${c.nom}, ${c.parti}.`);
    if (ident.mandat_principal) parts.push(`${ident.mandat_principal.value}.`);
    if (ident.fonctions_gouvernementales && !/^Aucune/i.test(ident.fonctions_gouvernementales.value || '')) {
      parts.push(`Anciennes fonctions : ${truncate(ident.fonctions_gouvernementales.value, 120)}.`);
    }
    if (ident.candidature_2027) parts.push(`Candidature 2027 : ${ident.candidature_2027.value}.`);
    return parts.join(' ');
  }

  function renderCandidatEssentiel(c) {
    const ident = c.identite || {};
    const act = c.activite_parlementaire || {};
    const pat = c.patrimoine || {};

    const cand = ident.candidature_2027;
    const mandat = ident.mandat_principal;
    const patValue = pat.patrimoine_declare;
    const presence = act.presence_hemicycle;

    const card = (label, value, detail, url, sourceLabel) => {
      const valDisplay = value ? escapeHtml(value) : '—';
      const detailHtml = detail ? `<span class="ic-detail${isNonTrouve(value) ? ' non-trouve' : ''}">${richText(detail)}</span>` : '';
      return `<article class="indicator-card">
        <span class="ic-label">${escapeHtml(label)}</span>
        <span class="ic-value">${valDisplay}</span>
        ${detailHtml}
        <span class="ic-source">${sourceLink(url, sourceLabel)}</span>
      </article>`;
    };

    // Statut 2027
    const candValue = cand ? truncate(cand.value, 50) : '—';
    const candDetail = cand && cand.value && cand.value.length > 50 ? cand.value : '';

    // Patrimoine net : extraire un nombre € si possible
    const patRaw = patValue ? patValue.value : null;
    const patNum = parseEuros(patRaw);
    const patDisplay = patNum ? formatEuros(patNum) : (patRaw ? truncate(patRaw, 30) : 'NON TROUVÉ');
    const patDetail = patRaw && patRaw !== patDisplay ? truncate(patRaw, 180) : '';

    // Présence
    const presenceValue = presence ? truncate(presence.value, 40) : '—';
    const presenceDetail = presence && presence.value && presence.value.length > 40 ? presence.value : '';

    return `<section class="section-block">
      <h2>L'essentiel</h2>
      <div class="indicators-grid">
        ${card('Candidature 2027', candValue, candDetail, cand && cand.source_url, cand && cand.source_label)}
        ${card('Mandat actuel', mandat ? truncate(mandat.value, 50) : '—', mandat && mandat.value && mandat.value.length > 50 ? mandat.value : '', mandat && mandat.source_url, mandat && mandat.source_label)}
        ${card('Patrimoine net', patDisplay, patDetail, patValue && patValue.source_url, patValue && patValue.source_label)}
        ${card('Activité parlementaire', presenceValue, presenceDetail, presence && presence.source_url, presence && presence.source_label)}
      </div>
    </section>`;
  }

  function renderCandidatParcours(c) {
    const ident = c.identite || {};
    // Construction d'une timeline à partir des champs disponibles
    const events = [];
    if (ident.premiere_election) events.push({ label: 'Première élection', value: ident.premiere_election.value });
    if (ident.fonctions_gouvernementales && !/^Aucune/i.test(ident.fonctions_gouvernementales.value || '')) {
      events.push({ label: 'Fonctions gouvernementales', value: ident.fonctions_gouvernementales.value });
    }
    if (ident.presidence_parti && !/^Aucune/i.test(ident.presidence_parti.value || '')) {
      events.push({ label: 'Présidence de parti', value: ident.presidence_parti.value });
    }
    if (ident.mandat_principal) events.push({ label: 'Mandat actuel', value: ident.mandat_principal.value });
    if (ident.candidature_2027) events.push({ label: 'Candidature 2027', value: ident.candidature_2027.value, url: ident.candidature_2027.source_url, sourceLabel: ident.candidature_2027.source_label });

    const items = events.map(e => `<li>
      <span class="tv-label">${escapeHtml(e.label)}</span>
      <span class="tv-detail">${richText(e.value)}${sourceLink(e.url, e.sourceLabel)}</span>
    </li>`).join('');

    return `<section class="section-block">
      <h2>Parcours politique</h2>
      <p class="lead">Principaux jalons reconstitués depuis les déclarations officielles, Wikipédia et la presse vérifiée.</p>
      <ul class="timeline-visual">${items}</ul>
    </section>`;
  }

  function renderCandidatPositions(c, votes, sujets) {
    const politiques = sujets.filter(s => s.type === 'politique');
    const cards = politiques.map(sujet => {
      const pkey = sujet.positions_key;
      const positionPayload = pkey ? (c.positions && c.positions[pkey]) : null;
      const positionValue = positionPayload ? positionPayload.value : null;
      const nonTrouve = !positionValue || isNonTrouve(positionValue);

      // Trouver 1-2 votes-clés du candidat sur ce sujet
      const themeList = sujet.votes_filter && sujet.votes_filter.themes || [];
      const textIncludes = sujet.votes_filter && sujet.votes_filter.textes_includes || [];
      const matched = votes.filter(v => {
        const theme = (v.theme || '').toLowerCase();
        const texte = (v.texte || '').toLowerCase();
        return themeList.some(t => theme.includes(t.toLowerCase())) || textIncludes.some(t => texte.includes(t.toLowerCase()));
      }).map(v => ({ ...v, candidatPos: (v.positions || {})[c.slug] })).filter(v => v.candidatPos && v.candidatPos.position !== 'N/A').slice(0, 2);

      let votesHtml = '';
      if (matched.length) {
        votesHtml = matched.map(v => `<div class="cpc-vote-line">${votePastille(v.candidatPos.position, v.candidatPos.detail, true)} <span title="${escapeHtml(v.texte || '')}">${escapeHtml(truncate(v.titre_fr || v.texte, 65))} (${escapeHtml(String(v.annee || ''))})</span></div>`).join('');
      } else {
        votesHtml = '<em style="color: var(--c-text-faint); font-size: 0.85rem;">Pas de vote-clé recensé pour ce candidat sur ce sujet (mandat non concerné ou texte non emblématique).</em>';
      }

      const positionContent = nonTrouve
        ? '<span class="cpc-section-content non-trouve">Position non synthétisée dans le tableur source.</span>'
        : `<div class="cpc-section-content">${richText(truncate(positionValue, 280))}</div>`;

      return `<article class="candidate-position-card">
        <h4>${escapeHtml(sujet.titre)}</h4>
        <div class="cpc-section">
          <span class="cpc-section-label">Ce qu'il dit</span>
          ${positionContent}
          ${positionPayload && positionPayload.source_url ? `<div style="margin-top: 0.25rem;">${sourceLink(positionPayload.source_url, positionPayload.source_label)}</div>` : ''}
        </div>
        <div class="cpc-section">
          <span class="cpc-section-label">Ce qu'il a voté</span>
          <div class="cpc-section-content">${votesHtml}</div>
        </div>
        <a class="cpc-link" href="sujet-${escapeHtml(sujet.id)}.html">Comparer aux autres sur ce sujet →</a>
      </article>`;
    }).join('');

    return `<section class="section-block" id="positions">
      <h2>Ses positions sur les 8 grands sujets</h2>
      <p class="lead">Pour chaque sujet, ce que le candidat dit publiquement et ce qu'il a voté (ou ce qui est applicable à son mandat). Cliquez sur « Comparer » pour voir les autres candidats.</p>
      <div class="candidate-positions-grid">${cards}</div>
    </section>`;
  }

  function renderCandidatPatrimoine(c, allCandidats) {
    const pat = c.patrimoine || {};
    const patValue = pat.patrimoine_declare;
    const patRaw = patValue ? patValue.value : null;
    const patNum = parseEuros(patRaw);

    // Barre comparative au panel
    const series = CANDIDATS_ORDER.map(slug => {
      const cc = allCandidats[slug];
      const v = cc.patrimoine && cc.patrimoine.patrimoine_declare;
      return { slug, nom: cc.nom, num: parseEuros(v && v.value), raw: v && v.value };
    });
    const maxV = Math.max(...series.map(s => s.num || 0)) || 1;
    const bars = series.map(s => {
      const isCurrent = s.slug === c.slug;
      const pct = s.num ? Math.max(2, (s.num / maxV) * 100) : 0;
      const display = s.num ? formatEuros(s.num) : (s.raw ? 'NON TROUVÉ' : '—');
      return `<div class="bcc-row">
        <span class="bcc-label${isCurrent ? ' is-current' : ''}">${escapeHtml(s.nom)}</span>
        <span class="bcc-track"><span class="bcc-fill${isCurrent ? ' is-current' : ''}" style="width:${pct.toFixed(1)}%"></span></span>
        <span class="bcc-value${(!s.num) ? ' non-trouve' : ''}">${escapeHtml(display)}</span>
      </div>`;
    }).join('');

    const others = `<div class="money-grid">
      <div class="money-card"><div class="mc-label">Revenus annuels</div><div class="mc-value" style="font-size: 0.95rem; font-weight: 500;">${richText(truncate(getValue(pat.revenus_annuels) || '—', 180))}</div></div>
      <div class="money-card"><div class="mc-label">Participations / SCI</div><div class="mc-value" style="font-size: 0.95rem; font-weight: 500;">${richText(truncate(getValue(pat.participations) || '—', 180))}</div></div>
      <div class="money-card"><div class="mc-label">Activités annexes rémunérées</div><div class="mc-value" style="font-size: 0.95rem; font-weight: 500;">${richText(truncate(getValue(pat.activites_annexes) || '—', 180))}</div></div>
      <div class="money-card"><div class="mc-label">Conjoint·e (activité déclarée)</div><div class="mc-value" style="font-size: 0.95rem; font-weight: 500;">${richText(truncate(getValue(pat.conjoint) || '—', 180))}</div></div>
    </div>`;

    return `<section class="section-block">
      <h2>Patrimoine et intérêts</h2>
      <p class="lead">Source : déclarations à la <span class="term" data-term="hatvp">HATVP</span> (<span class="term" data-term="dsp">DSP</span> et/ou <span class="term" data-term="dia">DIA</span>). La barre du candidat est en bleu plein ; les autres en transparence pour comparaison.</p>
      <div class="bar-chart-compact">${bars}</div>
      ${others}
      <p style="font-size: 0.85rem; color: var(--c-text-soft); margin-top: 0.5rem;">${sourceLink(patValue && patValue.source_url, 'Déclaration HATVP — voir détail')}</p>
    </section>`;
  }

  function renderCandidatJustice(c) {
    return `<section class="section-block">
      <h2>Affaires judiciaires</h2>
      <p class="lead">Toutes les procédures connues publiquement à ce jour. <strong>Présomption d'innocence stricte</strong> : aucun terme définitif n'est employé tant qu'une <span class="term" data-term="condamne-definitif">condamnation n'est pas devenue définitive</span>. Pour comprendre les statuts, voir le <a href="glossaire.html#temoin-assiste">glossaire</a>.</p>
      ${renderAffairesBlock(c.affaires || [])}
    </section>`;
  }

  function renderCandidatFinancement(c, fin) {
    const f = c.financement || {};
    // Trouver le compte de campagne lié au candidat
    const campagne = (fin.campagnes_par_candidat || []).find(x => (x.candidat_nom || '').toLowerCase().includes(c.slug));
    // Trouver le parti
    const partiNom = c.parti;
    const parti = (fin.comptes_partis_2024 || []).find(p => {
      const pn = (p.parti || '').toLowerCase();
      const cn = partiNom.toLowerCase();
      return pn.includes(cn) || cn.includes(pn);
    });

    let campagneHtml = '';
    if (campagne) {
      campagneHtml = `<h3 style="margin-top: 1rem;">Compte de campagne — ${escapeHtml(campagne.election || '')}</h3>
        <div class="money-grid">
          <div class="money-card"><div class="mc-label">Dépenses</div><div class="mc-value">${escapeHtml(campagne.depenses || '—')}</div></div>
          <div class="money-card"><div class="mc-label">Recettes</div><div class="mc-value">${escapeHtml(campagne.recettes || '—')}</div></div>
          <div class="money-card"><div class="mc-label">Remboursement État</div><div class="mc-value" style="font-size: 0.95rem;">${escapeHtml(campagne.remboursement || '—')}</div></div>
          <div class="money-card"><div class="mc-label"><span class="term" data-term="reformation">Réformations</span></div><div class="mc-value" style="font-size: 0.9rem; font-weight: 500;">${richText(truncate(campagne.reformations || '—', 160))}</div></div>
        </div>
        <p style="font-size: 0.85rem;">Décision <span class="term" data-term="cnccfp">CNCCFP</span> du ${escapeHtml(String(campagne.date_decision || '—'))} ${sourceLink(campagne.source_url, 'CNCCFP / JORF')}</p>`;
    } else {
      const fc = f.derniere_campagne;
      if (fc) {
        campagneHtml = `<h3 style="margin-top: 1rem;">Dernière campagne analysable</h3>
          <p>${richText(fc.value)} ${sourceLink(fc.source_url, fc.source_label)}</p>`;
      }
    }

    let partiHtml = '';
    if (parti) {
      partiHtml = `<h3 style="margin-top: 1.5rem;">Compte du parti — ${escapeHtml(parti.parti)} (exercice 2024)</h3>
        <div class="money-grid">
          <div class="money-card"><div class="mc-label">Total bilan</div><div class="mc-value">${escapeHtml(parti.total_bilan)}</div></div>
          <div class="money-card"><div class="mc-label">Produits 2024</div><div class="mc-value">${escapeHtml(parti.produits_2024)}</div></div>
          <div class="money-card"><div class="mc-label"><span class="term" data-term="aide-publique-partis">Aide publique 2024</span></div><div class="mc-value">${escapeHtml(parti.aide_publique_2024)}</div></div>
          <div class="money-card"><div class="mc-label">Aide publique 2025</div><div class="mc-value">${escapeHtml(parti.aide_publique_2025)}</div></div>
          <div class="money-card"><div class="mc-label">Dettes totales</div><div class="mc-value">${escapeHtml(parti.dettes_total)}</div></div>
          <div class="money-card"><div class="mc-label">Dont banques</div><div class="mc-value">${escapeHtml(parti.dont_banques)}</div></div>
          <div class="money-card"><div class="mc-label">Dont personnes physiques</div><div class="mc-value">${escapeHtml(parti.dont_personnes_physiques)}</div></div>
        </div>
        <p style="font-size: 0.85rem;">${sourceLink(fin.partis_source_url, fin.partis_source_label || 'CNCCFP')}</p>`;
    }

    return `<section class="section-block">
      <h2>Argent du parti et de la campagne</h2>
      <p class="lead">Le financement de la vie politique est contrôlé par la <span class="term" data-term="cnccfp">CNCCFP</span>. Toutes les décisions sont publiées au Journal officiel.</p>
      ${campagneHtml}
      ${partiHtml}
    </section>`;
  }

  function renderCandidatSources(c, fin) {
    // Collecter toutes les URLs uniques de la fiche
    const urls = new Set();
    function harvest(obj) {
      if (!obj || typeof obj !== 'object') return;
      if (obj.source_url) urls.add(obj.source_url);
      for (const k in obj) {
        const v = obj[k];
        if (v && typeof v === 'object') harvest(v);
        if (Array.isArray(v)) v.forEach(harvest);
      }
    }
    harvest(c.identite);
    harvest(c.activite_parlementaire);
    harvest(c.patrimoine);
    harvest(c.positions);
    harvest(c.financement);
    harvest(c.synthese);
    (c.affaires || []).forEach(a => { if (a.source_url) urls.add(a.source_url); });
    (c.discours_vs_actes || []).forEach(d => { if (d.source_url) urls.add(d.source_url); });
    // Ajouter sources campagne / parti
    const campagne = (fin.campagnes_par_candidat || []).find(x => (x.candidat_nom || '').toLowerCase().includes(c.slug));
    if (campagne && campagne.source_url) urls.add(campagne.source_url);
    urls.add(fin.partis_source_url);

    const sorted = Array.from(urls).filter(Boolean).sort();
    const items = sorted.map(u => `<li><a href="${escapeHtml(u)}" target="_blank" rel="noopener">${escapeHtml(u)}</a></li>`).join('');

    return `<section class="section-block">
      <h2>Toutes les sources de cette fiche</h2>
      <p class="lead">${sorted.length} sources distinctes utilisées pour reconstituer cette fiche. Cliquez pour ouvrir.</p>
      <div class="bibliography"><ul>${items}</ul></div>
    </section>`;
  }

  // ========================================================================
  // PAGE COMPARER
  // ========================================================================

  async function renderComparerPage() {
    try {
      const [data, sujets] = await Promise.all([
        loadJSON('data/candidats.json'),
        loadJSON('data/sujets.json'),
        loadGlossaire(),
      ]);

      const sujetsGrid = document.getElementById('comparer-sujets-grid');
      sujetsGrid.innerHTML = sujets.map(s => {
        const cls = s.type === 'transverse' ? 'sujet-card sujet-card--transverse' : 'sujet-card';
        return `<a class="${cls}" href="#" data-sujet-id="${escapeHtml(s.id)}">
          <span class="sc-icon" aria-hidden="true">${escapeHtml(s.icon_letter || s.titre[0])}</span>
          <span class="sc-content">
            <span class="sc-title">${escapeHtml(s.titre)}</span>
            <span class="sc-teasing">${escapeHtml(s.teasing || '')}</span>
          </span>
        </a>`;
      }).join('');

      const form = document.getElementById('comparer-form');
      const output = document.getElementById('comparer-output');
      const choices = document.getElementById('comparer-choices');
      choices.innerHTML = CANDIDATS_ORDER.map(s => `<label><input type="checkbox" name="cand" value="${escapeHtml(s)}" checked> ${escapeHtml(data.candidats[s].nom)}</label>`).join('');

      const step1 = document.getElementById('step-1');
      const step2 = document.getElementById('step-2');
      const step3 = document.getElementById('step-3');
      const sujetsBloc = document.getElementById('comparer-sujets');

      let currentSujetId = null;

      function showSubject(id) {
        currentSujetId = id;
        step1.classList.remove('is-active');
        step2.classList.add('is-active');
        sujetsBloc.hidden = true;
        form.hidden = false;
        rerender();
      }

      function showSubjectChoice() {
        currentSujetId = null;
        step2.classList.remove('is-active');
        step3.classList.remove('is-active');
        step1.classList.add('is-active');
        sujetsBloc.hidden = false;
        form.hidden = true;
        output.innerHTML = '';
      }

      function rerender() {
        const selected = Array.from(form.querySelectorAll('input[name="cand"]:checked')).map(x => x.value);
        if (selected.length < 2) {
          output.innerHTML = '<p class="message">Sélectionnez au moins 2 candidats à comparer.</p>';
          return;
        }
        step3.classList.add('is-active');
        renderSujet(currentSujetId, selected, output, {});
      }

      sujetsGrid.addEventListener('click', (ev) => {
        const a = ev.target.closest('[data-sujet-id]');
        if (!a) return;
        ev.preventDefault();
        showSubject(a.dataset.sujetId);
      });
      form.addEventListener('change', rerender);
      document.getElementById('comparer-change-subject').addEventListener('click', showSubjectChoice);

      // Pré-sélection éventuelle via ?theme=
      const preset = getParam('theme');
      if (preset && sujets.find(s => s.id === preset)) {
        showSubject(preset);
      }

      initTooltips();
    } catch (err) {
      showError(document.getElementById('comparer-output'), `Impossible de charger les données : ${err.message}`);
      console.error(err);
    }
  }

  // ========================================================================
  // PAGE GLOSSAIRE
  // ========================================================================

  async function renderGlossairePage() {
    const container = document.getElementById('glossaire-content');
    const tocList = document.getElementById('toc-list');
    try {
      const entries = await loadJSON('data/glossaire.json');
      GLOSSAIRE_INDEX = {};
      for (const e of entries) GLOSSAIRE_INDEX[e.id] = e;

      // Regrouper par catégorie
      const byCat = {};
      for (const e of entries) {
        (byCat[e.categorie] = byCat[e.categorie] || []).push(e);
      }
      const cats = Object.keys(byCat);
      tocList.innerHTML = cats.map(cat => `<li><a href="#cat-${escapeHtml(slugify(cat))}">${escapeHtml(cat)}</a> (${byCat[cat].length})</li>`).join('');

      const target = (window.location.hash || '').replace('#', '');
      const html = cats.map(cat => {
        const items = byCat[cat].map(e => `<article class="glossaire-entry${e.id === target ? ' is-target' : ''}" id="${escapeHtml(e.id)}">
          <h3>${escapeHtml(e.terme)}</h3>
          <p class="court">${escapeHtml(e.definition_courte)}</p>
          <p class="long">${escapeHtml(e.definition_longue)}</p>
        </article>`).join('');
        return `<section class="glossaire-section">
          <h2 id="cat-${escapeHtml(slugify(cat))}">${escapeHtml(cat)}</h2>
          ${items}
        </section>`;
      }).join('');
      container.innerHTML = html;

      // Scroll vers l'ancre si fournie
      if (target) {
        const el = document.getElementById(target);
        if (el) setTimeout(() => el.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50);
      }
    } catch (err) {
      showError(container, `Impossible de charger le glossaire : ${err.message}`);
      console.error(err);
    }
  }

  function slugify(s) {
    return String(s).toLowerCase()
      .replaceAll(/[àâä]/g, 'a').replaceAll(/[éèêë]/g, 'e').replaceAll(/[îï]/g, 'i')
      .replaceAll(/[ôö]/g, 'o').replaceAll(/[ûüù]/g, 'u').replaceAll('ç', 'c')
      .replaceAll(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  }

  // ========================================================================
  // Dispatcher
  // ========================================================================

  document.addEventListener('DOMContentLoaded', () => {
    const page = document.body.dataset.page;
    if (page === 'index') renderIndex();
    else if (page === 'candidat') renderCandidatV2();
    else if (page === 'sujet') renderSujetPage();
    else if (page === 'comparer') renderComparerPage();
    else if (page === 'glossaire') renderGlossairePage();
  });
})();
