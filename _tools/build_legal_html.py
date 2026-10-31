#!/usr/bin/env python3
"""Builds the public legal pages for synaptofit.com from a single source of truth.
Emits: index.html, privacy.html, terms.html, disclaimer.html, delete-account.html
Re-run after editing CONTENT below; re-upload the changed files."""

import re, html, os

VERSION = "2.0"
UPDATED = "18 October 2026"

# Path the pages are served under. "" = site root, "/legal" = synaptofit.com/legal/...
BASE = "/legal"

# Trading details — change here, re-run, re-upload.
TRADER  = "Connor Trimble"
ADDR_1L = "92 Exton Road, Chichester PO19 8BT, United Kingdom"
ADDR_BL = "92 Exton Road<br>Chichester PO19 8BT<br>United Kingdom"

CSS = """
:root{--gold:#D4AF37;--gold-dim:#9c7f28;--ink:#f2f2f2;--muted:#9a9a9a;--line:#262626;
 --bg:#0A0A0A;--bg-2:#121212;--soft:#161616}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
 font:16px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
 -webkit-text-size-adjust:100%;-webkit-font-smoothing:antialiased}
/* the frame matches the homepage exactly: same width, header and footer */
.wrap{max-width:1040px;margin:0 auto;padding:0 24px}
a{color:var(--gold)}
header{position:sticky;top:0;z-index:10;background:rgba(10,10,10,.88);
 backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.bar{display:flex;align-items:center;justify-content:space-between;height:66px}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);
 font-weight:700;font-size:19px;letter-spacing:.01em}
.brand span{color:var(--gold)}
.brand img{width:26px;height:26px;display:block}
nav.top a{color:var(--muted);text-decoration:none;margin-left:26px;font-size:14.5px}
nav.top a:hover,nav.top a[aria-current]{color:var(--ink)}
@media(max-width:720px){nav.top a{margin-left:16px;font-size:13.5px}nav.top a.hide-sm{display:none}}
/* legal tabs */
.tabs{border-bottom:1px solid var(--line);background:var(--bg-2)}
.tabs .wrap{display:flex;flex-wrap:wrap;gap:4px 24px;padding-top:12px;padding-bottom:0}
.tabs a{color:var(--muted);text-decoration:none;font-size:14px;padding:6px 0 11px;
 border-bottom:2px solid transparent}
.tabs a:hover{color:var(--ink)}
.tabs a[aria-current]{color:var(--ink);border-bottom-color:var(--gold)}
@media(max-width:720px){.tabs .wrap{gap:0 16px}.tabs a{font-size:13.5px;padding-bottom:8px}}
/* document: the frame is full width, the reading text keeps a comfortable line length */
main{padding:40px 0 64px}
main .wrap>*{max-width:760px}
main .wrap>table,main .wrap>.cards{max-width:none}
h1{font-size:34px;line-height:1.2;margin:0 0 6px;letter-spacing:-.015em}
.sub{color:var(--muted);font-size:14px;margin:0 0 30px}
h2{font-size:21px;margin:40px 0 12px;padding-top:16px;border-top:1px solid var(--line)}
h3{font-size:16px;margin:24px 0 8px;color:#c9c9c9}
p{margin:0 0 14px}
ul{margin:0 0 16px;padding-left:22px}
li{margin-bottom:8px}
strong{color:#ffffff}
table{border-collapse:collapse;width:100%;margin:0 0 20px;font-size:14.5px;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top}
th{background:var(--soft);font-weight:600;color:var(--gold)}
.callout{background:var(--soft);border-left:3px solid var(--gold);padding:16px 20px;
 margin:0 0 24px;border-radius:0 6px 6px 0}
.callout p:last-child{margin-bottom:0}
.cards{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin:26px 0}
@media(max-width:800px){.cards{grid-template-columns:1fr}}
.card{border:1px solid var(--line);border-radius:12px;padding:22px 24px;background:var(--bg-2);
 text-decoration:none;color:inherit;display:block}
.card:hover{border-color:var(--gold)}
.card b{display:block;font-size:16.5px;margin-bottom:6px}
.card span{color:var(--muted);font-size:14.3px;line-height:1.55;display:block}
/* footer: same as the homepage */
footer{border-top:1px solid var(--line);padding:46px 0 60px;color:var(--muted);font-size:14px}
footer a{color:var(--muted)}
footer a:hover{color:var(--gold)}
.foot-grid{display:flex;justify-content:space-between;gap:34px;flex-wrap:wrap;margin-bottom:28px}
.foot-grid h4{color:var(--ink);font-size:14px;margin:0 0 10px;letter-spacing:.04em;text-transform:uppercase}
.foot-grid p{margin:0 0 6px;line-height:1.6}
.foot-links a{display:block;margin-bottom:7px;text-decoration:none}
.fine{border-top:1px solid var(--line);padding-top:20px;font-size:13.2px;line-height:1.7}
@media print{body{background:#fff;color:#000}a{color:#000}header{position:static}
 header,.tabs,footer{border-color:#ccc;background:#fff}}
"""

# Tabs under the header on every legal page (slug, label).
TABS = [("index", "Overview"), ("privacy", "Privacy Policy"), ("terms", "Terms of Service"),
        ("disclaimer", "Health Disclaimer"), ("delete-account", "Delete Account")]

def esc(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\[\[(.+?)\|(.+?)\]\]', r'<a href="\2">\1</a>', t)
    t = t.replace('&lt;br&gt;', '<br>')   # allow explicit line breaks in source text
    return t

def render(blocks):
    out = []
    for kind, val in blocks:
        if kind == 'h2':   out.append(f"<h2>{esc(val)}</h2>")
        elif kind == 'h3': out.append(f"<h3>{esc(val)}</h3>")
        elif kind == 'p':  out.append(f"<p>{esc(val)}</p>")
        elif kind == 'note':
            inner = "".join(f"<p>{esc(p)}</p>" for p in val)
            out.append(f'<div class="callout">{inner}</div>')
        elif kind == 'ul':
            li = "".join(f"<li>{esc(i)}</li>" for i in val)
            out.append(f"<ul>{li}</ul>")
        elif kind == 'table':
            head, rows = val[0], val[1:]
            th = "".join(f"<th>{esc(c)}</th>" for c in head)
            tr = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in rows)
            out.append(f"<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>")
        elif kind == 'raw': out.append(val)
    return "\n".join(out)

def page(slug, title, subtitle, blocks, desc):
    tabs = ""
    for s, label in TABS:
        cur = ' aria-current="page"' if s == slug else ''
        href = f"{BASE}/" if s == "index" else f"{BASE}/{s}.html"
        tabs += f'<a href="{href}"{cur}>{label}</a>'
    doc = f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — SynaptoFit</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="index,follow">
<link rel="icon" href="/logo.png">
<meta name="theme-color" content="#0A0A0A">
<style>{CSS}</style>
</head>
<body>
<header><div class="wrap bar">
<a class="brand" href="/"><img src="/logo.png" alt="" width="26" height="26"><b>Synapto<span>Fit</span></b></a>
<nav class="top"><a href="/#features">Features</a><a href="/#offline" class="hide-sm">Offline</a><a href="/#beta">Beta</a><a href="{BASE}/" aria-current="page">Legal</a></nav>
</div></header>
<div class="tabs"><div class="wrap">{tabs}</div></div>
<main><div class="wrap">
<h1>{html.escape(title)}</h1>
<p class="sub">{html.escape(subtitle)}</p>
{render(blocks)}
</div></main>
<footer><div class="wrap">
<div class="foot-grid">
<div><h4>SynaptoFit</h4><p>Offline-first fitness tracking.</p><p>Built in the UK.</p></div>
<div class="foot-links"><h4>Product</h4><a href="/#features">Features</a><a href="/#offline">How it works</a><a href="/#beta">Join the beta</a></div>
<div class="foot-links"><h4>Legal</h4><a href="{BASE}/privacy.html">Privacy Policy</a><a href="{BASE}/terms.html">Terms of Service</a><a href="{BASE}/disclaimer.html">Health Disclaimer</a><a href="{BASE}/delete-account.html">Delete your account</a></div>
<div class="foot-links"><h4>Contact</h4><a href="mailto:support@synaptofit.com">support@synaptofit.com</a><a href="mailto:privacy@synaptofit.com">privacy@synaptofit.com</a></div>
</div>
<div class="fine">
SynaptoFit is operated by {TRADER}, a sole trader based in the United Kingdom.<br>
Address for service: {ADDR_1L}.<br>
&copy; 2026 SynaptoFit. Legal documents version {VERSION} · Last updated {UPDATED}.
</div>
</div></footer>
</body>
</html>"""
    with open(f"{slug}.html", "w", encoding="utf-8") as f:
        f.write(doc)
    print("wrote", f"{slug}.html")

# ---------------------------------------------------------------- PRIVACY
PRIVACY = [
('note', ["SynaptoFit is a fitness tracker, so most of what you record in it is health data. "
          "We only process it with your explicit consent, we show no ads, we use no third-party "
          "analytics, and we never sell your data. Deleting your account in the app permanently "
          "deletes everything."]),
('h2','1. Who we are'),
('p',f'SynaptoFit ("SynaptoFit", "we", "us") is a fitness and gym tracking app operated by **{TRADER}**, a sole trader based in the United Kingdom, of {ADDR_1L}.'),
('p','For the purposes of the UK General Data Protection Regulation ("UK GDPR"), the Data Protection Act 2018 and, where applicable, the EU General Data Protection Regulation ("EU GDPR"), Connor Trimble is the **data controller** of your personal data.'),
('p','Contact for anything in this policy: **privacy@synaptofit.com**. General support: **support@synaptofit.com**.'),
('h2','2. The short version'),
('ul',['SynaptoFit is a health and fitness tracker, so most of what you record in it is **health data** — a special category under the GDPR. We only process it with your **explicit consent**, which you give during onboarding and can withdraw at any time.',
       'Your data lives primarily **on your own phone**. A copy syncs to our server so you can restore it and (in future) use features that need it.',
       'We show **no ads**, use **no third-party analytics or tracking SDKs**, and **never sell your data**. Nobody but the operator has access to the server.',
       'Deleting your account in the app **permanently deletes all of your data** from our server.']),
('h2','3. What data we collect'),
('h3','3.1 Account data'),
('ul',['Name, email address, and a password (stored only as a cryptographic hash — we cannot see your password)']),
('h3','3.2 Profile and onboarding data (includes health data)'),
('ul',['Date of birth, biological sex, height, starting weight',
       'Training goal, experience level, training days per week, session length',
       'Available equipment and any injuries you choose to disclose (injuries are optional and skippable)']),
('h3','3.3 Data you log while using the app (health data)'),
('ul',['Workouts: exercises, sets, reps, weights, RPE, rest, tempo, cardio time/distance/heart rate; custom exercises and presets',
       'Nutrition: foods logged, meals, macro totals; meal presets and custom meal sections',
       'Body: weight entries, body measurements, body-composition metrics (e.g. body fat %), water intake',
       'Progress photos, if you choose to take or upload them',
       'Targets you set, logging streaks, and preferences (units, theme, tracked measurements)',
       'A record of each safety warning the app shows you and whether you tapped "I understand" (the target, the warning, the app version and the time)']),
('h3','3.4 Technical data'),
('ul',['Authentication tokens to keep you signed in; basic server logs (e.g. request timestamps and IP addresses) generated in operating the service and used only for security and troubleshooting']),
('p','We do **not** collect your precise location, contacts, advertising identifiers, or any data from other apps. The app requests camera and photo-library permission only for the barcode scanner and progress photos, and the accelerometer is used only to animate the on-screen water jug — motion data never leaves your device.'),
('h2','4. Special category (health) data and your explicit consent'),
('p','Most data listed in 3.2 and 3.3 is "data concerning health" under Article 9 GDPR. We process it on the basis of your **explicit consent** (Article 9(2)(a)), which we ask for in a dedicated, separate step during onboarding — not buried in the Terms of Service.'),
('p','You may withdraw consent at any time in the app or by emailing privacy@synaptofit.com. Because the entire service consists of recording and analysing this data, withdrawing consent means we can no longer provide the service; you may then export your data (on request) and delete your account.'),
('h2','5. Why we process your data (purposes and lawful bases)'),
('table',[['Purpose','Data used','Lawful basis'],
 ['Creating and operating your account; syncing and restoring your logged data','Account data; all logged data','Contract (Art. 6(1)(b)); explicit consent for health data (Art. 9(2)(a))'],
 ['Showing your own trends, targets, streaks and dashboards','Logged data (processed largely on your device)','Contract; explicit consent for health data'],
 ['Safety warnings when a target looks risky (e.g. calorie floors, unsafe weight-loss rates), personalised via an estimate of your energy needs','Profile data + latest weight + the target you set','Explicit consent (Art. 9(2)(a))'],
 ['Keeping a record of each safety warning shown to you and whether you acknowledged it','The target, the warning, the app version and the time','Explicit consent (Art. 9(2)(a))'],
 ['Food search and barcode lookup','The search text or barcode only — sent without your name, email or any account identifier','Contract'],
 ['Service emails (e.g. password reset)','Email address','Contract'],
 ['Security, abuse prevention, troubleshooting','Technical data','Legitimate interests (Art. 6(1)(f))'],
 ['Complying with law','Whatever the law requires','Legal obligation (Art. 6(1)(c))']]),
('p','We do **not** use your data for advertising, profiling for marketing, or automated decisions with legal or similarly significant effects. If future features (such as AI-generated plans or a paid subscription) need new processing, we will update this policy and ask for any additional consent **before** those features touch your data.'),
('h2','6. Where your data lives'),
('ul',['**On your device:** the app is offline-first. Your logs are stored in a local database on your phone and most screens are computed entirely on-device.',
       '**On our server:** a copy of your account and logged data (including progress photos) syncs to a server located in the **United Kingdom**, so your data survives a lost or new phone. The server is accessible only over encrypted HTTPS connections and only to the operator.']),
('h2','7. Who else sees your data (recipients and processors)'),
('p','We never sell or rent personal data. The limited third parties involved in running SynaptoFit are:'),
('table',[['Service','What they receive','Role / location'],
 ['Apple (App Store / TestFlight)',"Standard app distribution data under Apple's own policies; we receive no personal data from Apple beyond aggregate install/crash statistics",'Independent controller (global)'],
 ['Google (Google Play)',"Standard app distribution and crash diagnostics under Google's policies",'Independent controller (global)'],
 ['Open Food Facts / Search-a-licious','Your food search text or scanned barcode only — never your identity','Independent service (EU); open-data project'],
 ['IONOS','Email content if you write to our support or privacy addresses; hosting of this website','Processor (UK/EU)'],
 ['Server hosting','Your synced account and logged data','Currently operated directly by us on our own server in the United Kingdom — there is no third-party hosting company involved. If we move to a managed hosting provider, we will update this policy before the move.']]),
('p','We may also disclose data if required by law, or to a successor operator if the business is transferred — in which case this policy would continue to apply and you would be notified.'),
('h2','8. International transfers'),
('p','Your synced data is stored in the UK. Where any limited transfer outside the UK/EEA occurs (for example email infrastructure), we rely on UK adequacy regulations or standard contractual clauses. Food searches sent to Open Food Facts are processed in the EU and contain no identity data.'),
('h2','9. How long we keep data'),
('ul',['Account and logged data: for as long as your account exists.',
       'Account deletion: deleting your account in the app (Profile → Delete account) **permanently and irreversibly deletes all your data** from the live database, including progress photos. Residual copies in server backups are overwritten within 30 days.',
       'Safety-warning records: kept for as long as your account exists, never edited, and deleted with your account.',
       'Server logs: kept for a short rolling period for security, then deleted.',
       'Emails to support/privacy: kept as long as needed to handle your request and for a reasonable record thereafter.']),
('h2','10. Security'),
('ul',['All traffic between the app and server is encrypted (HTTPS/TLS)',
       'Passwords are stored only as salted bcrypt hashes',
       'Access to the server and database is restricted to the operator, protected by credentialed access, and rate-limited against abuse',
       "The local database on your phone is protected by your device's own security (passcode/biometrics); session tokens are held in the platform's secure storage"]),
('p','No system is perfectly secure. If a breach occurs that risks your rights, we will notify the ICO and, where required, you, in line with our legal obligations.'),
('h2','11. Your rights'),
('p','Under the UK and EU GDPR you can, at any time:'),
('ul',['**Access** a copy of your data',
       '**Rectify** inaccurate data (largely self-service in the app)',
       '**Erase** your data (self-service: delete your account in the app)',
       '**Restrict** or **object to** processing',
       '**Port** your data to another service in a machine-readable format',
       '**Withdraw consent** at any time, without affecting prior processing']),
('p',"To exercise a right that isn't self-service in the app, email **privacy@synaptofit.com**. We respond within one month. You also have the right to complain to the **Information Commissioner's Office** ([[ico.org.uk|https://ico.org.uk]]) or, in the EU, your local supervisory authority."),
('h2','12. Children'),
('p','SynaptoFit is not intended for anyone under **16**. We do not knowingly collect data from under-16s; if we learn we have, we will delete it. Please contact privacy@synaptofit.com if you believe a child is using the app.'),
('h2','13. Users outside the UK and EU'),
('p','We offer the same protections in this policy to all users worldwide. If you are in a jurisdiction with its own privacy law (for example a US state privacy statute), you may have equivalent rights of access, deletion, correction and portability — exercise them via privacy@synaptofit.com. We do not sell or share personal data for advertising in any jurisdiction.'),
('h2','14. Changes to this policy'),
('p','We will post any changes here and update the version below. For material changes — especially any new use of health data — we will notify you in the app and, where required, ask for fresh consent before the change applies to you.'),
('h2','15. Contact'),
('p',f'{TRADER}, trading as SynaptoFit<br>{ADDR_BL}<br>privacy@synaptofit.com · support@synaptofit.com'),
]

# ---------------------------------------------------------------- TERMS
TERMS = [
('note', ["These Terms include a Health & Fitness Disclaimer at section 8. Please read it — "
          "SynaptoFit is not a medical device and gives no medical advice."]),
('h2','1. Who you are agreeing with'),
('p',f'These Terms of Service and End User Licence Agreement ("Terms") are a contract between you and **{TRADER}, trading as SynaptoFit**, a sole trader based in the United Kingdom, of {ADDR_1L} ("SynaptoFit", "we", "us"). Contact: **support@synaptofit.com**.'),
('p','By creating an account or using the SynaptoFit app (the "App"), you accept these Terms. If you do not agree, do not use the App.'),
('h2','2. What SynaptoFit is — and is not'),
('p','SynaptoFit is a self-directed fitness, nutrition and body tracking tool. It records what **you** choose to log, displays your own trends, lets you set your own targets, and may show informational safety notices when a target appears risky.'),
('p','**SynaptoFit is not a medical device and provides no medical, dietetic or professional advice.** See the Health & Fitness Disclaimer in section 8, which forms part of these Terms.'),
('h2','3. Eligibility and your account'),
('ul',['You must be at least **16 years old** to use the App.',
       'You must give accurate account information and keep your password secure. You are responsible for activity on your account.',
       'One account per person. You may delete your account at any time in the App; deletion permanently removes your data (see the Privacy Policy).',
       'We may suspend or close accounts that break these Terms, abuse the service, or attempt to compromise its security — where reasonable, we will warn you first.']),
('h2','4. Licence'),
('p','We grant you a personal, non-exclusive, non-transferable, revocable licence to install and use the App on devices you own or control, for your personal, non-commercial use, subject to these Terms and the rules of the app store you downloaded it from. You may not copy, modify, distribute, sell, rent, reverse-engineer or create derivative works of the App except as permitted by law.'),
('h2','5. Free core, beta access and future paid tiers'),
('ul',['**Free core promise:** the App\'s core logging features (workout, nutrition, body, composition and water logging, barcode scanning, and manual target setting) are free. We do not intend to move these behind a paywall.',
       '**Beta:** the App is currently in beta (e.g. via TestFlight). Beta software may contain bugs, may change or lose data, and features may be added, altered or removed without notice. Beta access can be withdrawn at any time.',
       '**Future paid tiers:** we plan optional paid subscriptions (e.g. automated goal-setting, curated nutrition data, AI features). Prices, terms and renewal/cancellation mechanics will be presented clearly before you pay, will be handled through the app store\'s billing system, and will be governed by additional terms at that time. Nothing is charged today.']),
('h2','6. Acceptable use'),
('p','You agree not to:'),
('ul',['use the App unlawfully, or to harm yourself or others',
       'probe, scan, overload or attempt to breach the service or its server, or access another person\'s data',
       'scrape the service, resell it, or use automated systems against our API',
       'upload content you have no right to upload, or anything malicious']),
('h2','7. Your content and data'),
('ul',['Everything you log — workouts, meals, measurements, photos — remains **yours**.',
       'You grant us a limited licence to store, sync, back up and process that content solely to operate and improve the service for you, as described in the Privacy Policy. We claim no other rights over it.',
       'You are responsible for what you upload (e.g. progress photos must be of you or uploaded with the subject\'s permission).']),
('h2','8. Health & fitness disclaimer'),
('p',f'**Read this section carefully. It forms part of these Terms.** It is also published separately at [[synaptofit.com/legal/disclaimer|{BASE}/disclaimer.html]].'),
('ul',['The App provides information and tracking tools only. Nothing in the App — including targets, progression suggestions, estimated energy needs, safety notices, or any future AI-generated plan — is medical advice, and none of it is tailored to your full medical circumstances.',
       'Consult a doctor or qualified professional before starting or changing any exercise or nutrition programme — **especially** if you are pregnant, under 18, elderly, have (or have had) any medical condition including heart conditions, high blood pressure, diabetes, an eating disorder, injuries, or are on medication.',
       'Exercise and dietary change carry inherent risk, including serious injury. You use the App at your own risk and are solely responsible for the decisions you make with it.',
       'Safety notices in the App are informational, are based on general population research, may not fire in every risky situation, and are **not** a substitute for professional supervision. Their absence does not mean a target is safe.',
       'Stop exercising and seek immediate medical help if you feel pain, dizziness, faintness or shortness of breath. In an emergency in the UK call **999**; elsewhere, call your local emergency number.',
       'If you are struggling with disordered eating, do not use calorie or weight targets and speak to your GP; support is available from organisations such as Beat ([[beateatingdisorders.org.uk|https://www.beateatingdisorders.org.uk]]).']),
('h2','9. Availability and changes'),
('ul',['The App is offline-first: your device keeps working without a connection, but sync, account features, food search and barcode lookup need the internet and our server to be reachable.',
       'The service is provided on a small, independent infrastructure and is offered "as available" — we do not guarantee uninterrupted operation, and maintenance or failures may cause downtime.',
       'We may update the App and these Terms. Material changes to the Terms will be notified in the App; continued use after the effective date is acceptance. If you do not accept, stop using the App and delete your account.']),
('h2','10. Intellectual property'),
('p','The App, its code, design, branding (including the SynaptoFit name and gold arrow mark) and content we created are owned by Connor Trimble and protected by law. Nutrition data from Open Food Facts is used under its open-data licence; exercise library content is ours.'),
('h2','11. Liability'),
('ul',['**Nothing in these Terms excludes or limits liability for:** death or personal injury caused by our negligence; fraud or fraudulent misrepresentation; or any liability that cannot be excluded under UK law, including your statutory rights as a consumer.',
       'Subject to that: the App is provided **free of charge**, "as is" and "as available", and we exclude all implied warranties to the extent the law allows.',
       'Subject to the first bullet, we are not liable for: losses from your exercise or dietary decisions (see section 8); loss of data where you have failed to allow the App to sync; losses from events outside our reasonable control; or business losses (the App is for personal use).',
       'Subject to the first bullet, our total liability to you in respect of the free service is limited to **£100**; if you later pay for a subscription, our total liability is limited to the amounts you paid us in the 12 months before the claim.']),
('h2','12. Apple App Store terms'),
('p',"If you downloaded the App from Apple's App Store, the following also applies:"),
('ul',['These Terms are between you and SynaptoFit only — not Apple. Apple has no obligation to provide maintenance or support for the App.',
       'In the event of any failure of the App to conform to an applicable warranty, you may notify Apple and Apple will refund any purchase price; to the maximum extent permitted by law, Apple has no other warranty obligation.',
       'Apple is not responsible for addressing any claims relating to the App, including product liability, regulatory compliance, or consumer protection claims, or for third-party IP claims regarding the App.',
       'You represent that you are not located in a country subject to a US Government embargo and are not on any US Government prohibited or restricted parties list.',
       'Apple and its subsidiaries are third-party beneficiaries of these Terms and may enforce them against you.',
       'You must also comply with any applicable third-party terms (e.g. your mobile network agreement).']),
('h2','13. General'),
('ul',['These Terms are governed by the laws of **England and Wales**, and disputes go to the courts of England and Wales — except that if you live in Scotland, Northern Ireland or an EU country, you keep the benefit of any mandatory consumer protections and courts of your home jurisdiction where the law grants them.',
       'If any clause is found invalid, the rest remain in force. A failure to enforce a right is not a waiver.',
       'You may not transfer your rights under these Terms; we may transfer ours as part of a business transfer, with your protections preserved.',
       'These Terms, the Privacy Policy and any future subscription terms are the entire agreement between us regarding the App.']),
('h2','14. Contact'),
('p',f'{TRADER}, trading as SynaptoFit<br>{ADDR_BL}<br>support@synaptofit.com'),
]

# ---------------------------------------------------------------- DISCLAIMER
DISCLAIMER = [
('note',["SynaptoFit is a tracking tool, not a medical device. It provides no medical, dietetic "
         "or professional advice. If something in the app conflicts with advice from your doctor, "
         "follow your doctor."]),
('h2','1. What the app does and does not do'),
('p','SynaptoFit records what you choose to log and shows you your own data. Nothing in the App — including targets, progression suggestions, estimated energy needs, safety notices, or any future AI-generated plan — is medical advice, and none of it is tailored to your full medical circumstances. It cannot see your medical history, medication, or anything you have not told it.'),
('h2','2. Speak to a professional first'),
('p','Consult a doctor or qualified professional before starting or changing any exercise or nutrition programme. This matters **especially** if you:'),
('ul',['are pregnant or have recently given birth',
       'are under 18 or elderly',
       'have or have had a heart condition, high blood pressure, diabetes, or any chronic illness',
       'have or have had an eating disorder or disordered eating',
       'are recovering from injury or surgery',
       'are taking medication that affects your heart rate, blood pressure, appetite or hydration']),
('h2','3. You accept the risk'),
('p','Exercise and dietary change carry inherent risk, including serious injury. You use the App at your own risk and are solely responsible for the decisions you make with it. SynaptoFit is not responsible for injury, illness or loss arising from your training or eating decisions.'),
('h2','4. About the safety notices in the app'),
('p','SynaptoFit may show a coloured notice when a target you set looks risky — for example a calorie target below an established floor, or a rate of weight loss above what research generally considers safe. These notices:'),
('ul',['are **informational only** and never block you from saving a target',
       'are based on **general population research**, not on your individual medical circumstances',
       'may not fire in every risky situation — **the absence of a warning does not mean a target is safe**',
       'are **not a substitute** for professional supervision']),
('h2','5. Stop and get help'),
('p','Stop exercising and seek immediate medical help if you feel chest pain, dizziness, faintness, unusual shortness of breath, or any pain that does not feel like normal training effort.'),
('p','**In an emergency in the UK, call 999.** Elsewhere, call your local emergency number.'),
('h2','6. Eating disorders'),
('p','Calorie counting and weight targets can be harmful for some people. If you are struggling with disordered eating, please do not use the calorie or weight target features, and speak to your GP.'),
('p','Support in the UK is available from Beat: [[beateatingdisorders.org.uk|https://www.beateatingdisorders.org.uk]].'),
('h2','7. Status of this disclaimer'),
('p',f'This disclaimer forms part of the [[SynaptoFit Terms of Service|{BASE}/terms.html]] (section 8). By using the App you accept it.'),
]

# ---------------------------------------------------------------- DELETE ACCOUNT
# The account-deletion page Google Play's Data safety form links to. It must work for
# someone who no longer has the app, and it must match Privacy Policy §9 and §11.
DELETE_ACCOUNT = [
('note',["You can delete your SynaptoFit account at any time, free of charge. Deleting it "
         "permanently erases your account and everything you have logged. It cannot be undone."]),
('h2','1. Delete it in the app (quickest)'),
('ul',['Open SynaptoFit and sign in.',
       'Go to **Profile → Delete account**.',
       'Confirm. Your account and data are deleted from our server straight away, and the app also clears your data from that phone.']),
('p','You need an internet connection for this, because the deletion happens on our server.'),
('h2',"2. Delete it without the app"),
('p',"If you have uninstalled SynaptoFit, changed phone, or can't sign in, email **privacy@synaptofit.com** with the subject **Delete my account**."),
('ul',['Send it from the email address on your SynaptoFit account, so we can confirm the account is yours. If you no longer have access to that address, say so and we will agree another way to check.',
       'We will delete your account and confirm by email. We respond within one month, and normally much sooner.']),
('p','Uninstalling the app does **not** delete your account. Your data stays on our server until you delete the account using one of the two methods above.'),
('h2','3. What is deleted'),
('ul',['Your account: name, email address and password',
       'Your profile and onboarding answers',
       'Everything you have logged: workouts, custom exercises and presets, nutrition and meal presets, weight, measurements, body composition, water, targets and streaks',
       'Your progress photos, including the image files themselves',
       'Your consent records and the record of safety warnings shown to you']),
('h2','4. What is kept, and for how long'),
('ul',['**Server backups:** any residual copies are overwritten within **30 days**.',
       '**Emails you sent us** (for example to support or privacy) are kept only as long as needed to deal with your request, and for a reasonable record afterwards.',
       '**Server logs** are kept for a short rolling period for security, then deleted.']),
('p',f'Nothing else is kept. Full details are in our [[Privacy Policy|{BASE}/privacy.html]] (sections 9 and 11).'),
('h2','5. Deleting only some of your data'),
('p','You do not have to delete your whole account to remove something. Individual entries, such as a workout, a meal, a weigh-in or a progress photo, can be deleted in the app at any time. For anything you cannot delete yourself, email **privacy@synaptofit.com**.'),
]

INDEX = [
('p','Legal documents for the SynaptoFit fitness tracking app.'),
('raw',f'''<div class="cards">
<a class="card" href="{BASE}/privacy.html"><b>Privacy Policy</b><span>What data we collect, why, and the rights you have over it. Covers health data and explicit consent.</span></a>
<a class="card" href="{BASE}/terms.html"><b>Terms of Service &amp; EULA</b><span>The agreement between you and SynaptoFit, including the licence, the free core promise, and liability.</span></a>
<a class="card" href="{BASE}/disclaimer.html"><b>Health &amp; Fitness Disclaimer</b><span>What the app is not: it is a tracking tool, not a medical device, and gives no medical advice.</span></a>
<a class="card" href="{BASE}/delete-account.html"><b>Delete your account</b><span>How to permanently delete your SynaptoFit account and data, in the app or by email.</span></a>
</div>'''),
('h2','Contact'),
('p','Privacy and data protection enquiries: **privacy@synaptofit.com**<br>Everything else: **support@synaptofit.com**'),
('p','SynaptoFit is operated by Connor Trimble, a sole trader based in the United Kingdom.'),
]

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)
    # In the synaptofit-web repo this script lives in _tools/, so write straight
    # into ../legal. Anywhere else, fall back to a local site/ folder.
    sibling = os.path.abspath(os.path.join(here, "..", "legal"))
    out = sibling if os.path.isdir(sibling) else "site"
    os.makedirs(out, exist_ok=True); os.chdir(out)
    print("writing to:", os.getcwd())
    page("index","SynaptoFit Legal", f"Version {VERSION} · Last updated {UPDATED}", INDEX,
         "Privacy policy, terms of service and health disclaimer for the SynaptoFit fitness tracking app.")
    page("privacy","Privacy Policy", f"Version {VERSION} · Last updated {UPDATED}", PRIVACY,
         "How SynaptoFit collects, uses and protects your health and fitness data under UK and EU GDPR.")
    page("terms","Terms of Service", f"Version {VERSION} · Last updated {UPDATED} · Includes End User Licence Agreement", TERMS,
         "The terms governing your use of the SynaptoFit app, including licence, liability and the health disclaimer.")
    page("disclaimer","Health & Fitness Disclaimer", f"Version {VERSION} · Last updated {UPDATED}", DISCLAIMER,
         "SynaptoFit is a tracking tool, not a medical device, and provides no medical advice.")
    page("delete-account","Delete your SynaptoFit account", "How to delete your account and data · Last updated 31 October 2026", DELETE_ACCOUNT,
         "How to permanently delete your SynaptoFit account and all of your data, in the app or by email.")
