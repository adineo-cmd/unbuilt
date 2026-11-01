#!/usr/bin/env python3
"""Generates the Unbuilt website — a census of what humanity has built and what it hasn't.

Run from anywhere:  python3 build.py
Writes static HTML pages into this directory (index, fields, search, about, 404,
plus one page per field) and the shared assets.
"""
import html
import os

OUT = os.path.dirname(os.path.abspath(__file__))

FIELDS = [
    {
        "id": "software", "name": "Software & everyday apps",
        "note": "The most crowded room on earth. The gaps are in what software never bothered to do.",
        "built": [
            ["To-do and habit trackers", "Lists, streaks, reminders. Thousands exist; none is why you don't get things done.", "Your version will be number four thousand and one.", 5],
            ["Note-taking apps", "Second brains in every flavour: blocks, graphs, folders, markdown.", "Three giants plus hundreds of indies already fight over this.", 5],
            ["AI chatbot wrappers", "A thin interface over someone else's model, rented by the token.", "The model vendor ships your feature in their next update.", 5],
            ["Meeting-notetaker bots", "A bot joins the call, transcribes, summarizes, clogs the invite list.", "Named among 2026's most oversaturated AI categories — over a hundred funded rivals.", 5],
            ["Link-in-bio and QR tools", "One page of links. One square that opens a menu.", "Solved a decade ago; now given away for free.", 4],
        ],
        "unbuilt": [
            {"t": "Data divorce", "w": "One command exports everything every service knows about you, in formats you can actually reuse.", "why": "Leaving is the one feature no provider will ever build for you.", "closest": "Google Takeout — one company, one format.", "d": 3, "tags": ["privacy", "standards", "unsexy"]},
            {"t": "Software that dies gracefully", "w": "Apps that archive themselves and hand your data to a successor when they shut down.", "why": "Founders plan launches, not funerals — and users pay for neither.", "closest": "Nothing serious; startups just vanish.", "d": 2, "tags": ["infrastructure", "trust"]},
            {"t": "The honest slow-internet explainer", "w": "Tells you exactly which hop, device or ISP is eating your packets, in plain words.", "why": "ISPs prefer blame to remain a matter of opinion.", "closest": "traceroute — for engineers only.", "d": 3, "tags": ["networking", "consumer"]},
            {"t": "Cross-provider digital inheritance", "w": "A dead-man's switch that legally hands every account to the person you choose.", "why": "Each provider handles death alone; nobody spans them.", "closest": "Per-account inactive-account settings.", "d": 2, "tags": ["legal", "unsexy"]},
            {"t": "Explain-my-bill", "w": "Photograph any bill — medical, utility, telecom — and get an itemized audit plus a dispute letter.", "why": "Bill confusion is load-bearing revenue; auditing it is nobody's product.", "closest": "Rocket Money, subscriptions only.", "d": 3, "tags": ["consumer", "AI-assisted"]},
        ],
    },
    {
        "id": "ai", "name": "AI & machine learning",
        "note": "The model became a commodity. Trust in what it says did not.",
        "built": [
            ["\"ChatGPT for X\"", "A vertical skin, a generic model, no data moat.", "Writing assistants alone have over a hundred funded competitors.", 5],
            ["AI headshot generators", "Upload selfies, receive a blazer you don't own.", "A weekend-clone market with razor margins.", 5],
            ["Chat-with-your-PDF", "A vector database and a chat box, sold monthly.", "Bundled into every document tool that matters.", 5],
            ["Prompt libraries", "Collections of instructions, sold as courses.", "The models outgrew them.", 4],
            ["AI resume screeners", "A model that reads CVs and guesses fit.", "Legal exposure plus an arms race both sides lose.", 4],
        ],
        "unbuilt": [
            {"t": "Per-claim receipts", "w": "Every sentence of an AI answer carries its evidence and a confidence you can inspect.", "why": "Everyone benchmarks models; nobody ships accountability for one answer at a time.", "closest": "Citation modes — page-level, not claim-level.", "d": 4, "tags": ["trust", "infrastructure"]},
            {"t": "Licence auditor for AI-generated code", "w": "Scans a repository for training-data contamination and copyleft leakage, with legal-grade output.", "why": "Lawyers need defensible answers; current tools scan dependencies, not models.", "closest": "Software-composition analyzers.", "d": 3, "tags": ["developer", "regulated"]},
            {"t": "Models for the other 6,000 languages", "w": "On-device speech and text for languages with fewer than ten million speakers.", "why": "No market signal, enormous human value — the classic gap.", "closest": "Research weights with no product.", "d": 4, "tags": ["open-source", "under-served"]},
            {"t": "Bureaucracy copilot", "w": "Permits, appeals, visas, forms: every procedure as an executable, current checklist.", "why": "The data changes constantly and nobody maintains it.", "closest": "TurboTax — taxes only.", "d": 3, "tags": ["consumer", "unsexy"]},
            {"t": "Independent model crash tests", "w": "Published safety ratings for AI systems, like NCAP for cars.", "why": "Nobody funds the referee until regulators force one.", "closest": "Vendor-run benchmark coalitions.", "d": 4, "tags": ["trust", "policy"]},
        ],
    },
    {
        "id": "hardware", "name": "Hardware & devices",
        "note": "Where ideas go to die — which is exactly why the survivors win for a decade.",
        "built": [
            ["Smart plugs, bulbs, doorbells", "The same silicon with a different app icon.", "An aisle, not a market.", 5],
            ["Fitness bands and watches", "Steps, heart rate, sleep score, subscription.", "Two phone vendors plus a few survivors own it.", 5],
            ["Bluetooth trackers", "A coin, a speaker, a crowd-sourced radio map.", "AirTag's network made everyone else a rounding error.", 4],
            ["Consumer drones", "A camera that learned to hover.", "One dominant maker; the rest compete on price.", 4],
            ["Mechanical keyboards", "Clicky tokens of identity for desks.", "A thousand boutique makers, zero unsolved problems.", 4],
        ],
        "unbuilt": [
            {"t": "The $100 braille display", "w": "Refreshable braille cells that cost thousands today, made to cost one hundred.", "why": "Small apparent market, transformative real one — nobody has bet on volume.", "closest": "Orbit Reader: slow refresh, still $400+.", "d": 5, "tags": ["accessibility", "hardware"]},
            {"t": "Open hearing-aid firmware", "w": "Programmable, repairable hearing aids you tune yourself instead of visiting a clinic.", "why": "The 2022 US over-the-counter rule opened the market; locked firmware kept it shut.", "closest": "Audiologist-tuned presets.", "d": 3, "tags": ["health", "open-source"]},
            {"t": "Second-life battery walls", "w": "Graded, warrantied packs from crashed EVs powering homes at half price.", "why": "Grading used cells safely at consumer price is still unsolved.", "closest": "B2B pilots and hobbyists.", "d": 4, "tags": ["energy", "circular"]},
            {"t": "Repairability scanner", "w": "Point your phone at an appliance; get the teardown, parts list and prices.", "why": "Needs a crowdsourced parts database that doesn't exist yet.", "closest": "iFixit manuals, not scans.", "d": 3, "tags": ["circular", "crowdsourced"]},
            {"t": "The ten-dollar water tester", "w": "A reusable, phone-powered probe for lead, bacteria and salinity.", "why": "Lab testing costs $50 a sample and weeks of waiting.", "closest": "Test strips with wide error bars.", "d": 4, "tags": ["health", "global"]},
        ],
    },
    {
        "id": "health", "name": "Health & medicine",
        "note": "Tracking the body got solved. Getting care didn't.",
        "built": [
            ["Step counters", "A pedometer with an ecosystem.", "Free on every phone.", 5],
            ["Calorie trackers", "Databases, barcodes, guilt.", "Consolidated; differentiation is the colour of the rings.", 5],
            ["Symptom checkers", "Type your pain, receive anxiety and 'consult a doctor'.", "Liability caps the product at a brochure.", 4],
            ["Meditation apps", "A voice, a timer, a churn problem.", "Sleep and calm are already brands.", 4],
            ["Period trackers", "Cycle logs and predictions.", "Crowded, and privacy trust is broken.", 4],
        ],
        "unbuilt": [
            {"t": "Menopause care, done properly", "w": "Real protocols, monitoring and support for a transition half of humanity passes through.", "why": "Under-researched for a century; the patients are now the buyers.", "closest": "Telehealth clinics handing out hormones.", "d": 3, "tags": ["under-served", "clinical"]},
            {"t": "Home labs with a doctor loop", "w": "Finger-prick panel, licensed review, treatment plan inside 48 hours.", "why": "Regulated differently in every jurisdiction — painful, therefore open.", "closest": "Cash-pay functional-medicine startups.", "d": 4, "tags": ["regulated", "consumer"]},
            {"t": "A real interaction checker", "w": "Your complete medication and supplement list, checked against national data, in plain language.", "why": "The data exists; the interface assumes a pharmacist.", "closest": "Printouts and static web pages.", "d": 2, "tags": ["safety", "unsexy"]},
            {"t": "Phage-therapy logistics", "w": "Matching antibiotic-resistant infections to bacteriophage banks, worldwide.", "why": "A regulatory no-man's-land with a handful of cases per hospital.", "closest": "A few research centres.", "d": 5, "tags": ["biotech", "regulated"]},
            {"t": "Triage by actual availability", "w": "Therapists matched by real open slots, price and specialism, not directory ads.", "why": "Directories earn from listings, not from the match working.", "closest": "A phone book with reviews.", "d": 3, "tags": ["mental health", "consumer"]},
        ],
    },
    {
        "id": "climate", "name": "Climate & energy",
        "note": "Everyone built a dashboard. Almost nobody built the machine.",
        "built": [
            ["Carbon footprint calculators", "A quiz that converts your flights into guilt units.", "Non-binding numbers change nothing.", 5],
            ["ESG reporting suites", "Spreadsheets with a compliance accent.", "Rules loosened; buyers hesitated.", 4],
            ["Solar CRMs", "Lead generation and install scheduling for panel sellers.", "One vertical SaaS playbook, applied.", 4],
            ["EV charging apps", "Maps of chargers, half of them broken.", "The problem is the chargers, not the map.", 4],
            ["Utility portals", "A graph of your usage and a PDF bill.", "Built by regulated monopolies; feels like it.", 3],
        ],
        "unbuilt": [
            {"t": "The AC retrofit kit", "w": "A bolt-on module that makes dumb air conditioners variable-speed and 30% cheaper to run.", "why": "Billions of installed units, fragmented designs, uncomfortable margins.", "closest": "Smart plugs making dumb devices dumber.", "d": 4, "tags": ["hardware", "climate"]},
            {"t": "Heat-pump fit-checker", "w": "Scan your home, get a real thermal model, honest cost and payback, and a contractor shortlist.", "why": "Requires building-physics data nobody has aggregated.", "closest": "Installer quotes — sales pitches.", "d": 3, "tags": ["software", "climate"]},
            {"t": "Grid-interactive water heating", "w": "Your heater as a battery the grid pays you to borrow.", "why": "Utilities move at regulatory speed; hardware startups avoid them.", "closest": "Proprietary utility pilots.", "d": 3, "tags": ["energy", "regulated"]},
            {"t": "Used-cell grading scanner", "w": "A handheld tool that prices a used EV pack, cell by cell, in minutes.", "why": "Unlocks the whole second-life market — which is why it is hard.", "closest": "Lab-grade bench testers.", "d": 4, "tags": ["hardware", "circular"]},
            {"t": "Crop-switching planner", "w": "For farmers whose climate zone just moved: what to plant for the next decade.", "why": "The buyers are rural and the sales cycle is years.", "closest": "Academic papers.", "d": 3, "tags": ["agriculture", "long-cycle"]},
        ],
    },
    {
        "id": "education", "name": "Education & learning",
        "note": "Content became infinite. Retention stayed at zero.",
        "built": [
            ["MOOC platforms", "University lectures with progress bars.", "Completion rates near ten percent say enough.", 5],
            ["Streak language apps", "Gamified vocabulary with an owl holding your self-esteem hostage.", "One winner, forty clones.", 5],
            ["AI flashcard generators", "Paste notes, receive cards.", "A feature, not a product.", 4],
            ["Bootcamp clones", "Twelve weeks from zero to junior, sold with placement percentages.", "The junior job market did the pruning.", 4],
            ["Study-with-me economies", "Cameras pointed at people revising.", "Ambience, not education.", 3],
        ],
        "unbuilt": [
            {"t": "Spaced repetition in real curricula", "w": "The memory schedule embedded in the syllabus itself, not a hobbyist app beside it.", "why": "Schools buy textbooks; nobody sells them memory.", "closest": "Anki — powerful and DIY.", "d": 3, "tags": ["learning science", "schools"]},
            {"t": "Lab-in-a-box", "w": "A $50 kit plus phone camera that grades the experiment your student just ran.", "why": "Needs curriculum fit per country; the hard part is the syllabus, not the sensor.", "closest": "Science toys without assessment.", "d": 4, "tags": ["hardware", "global"]},
            {"t": "Apprenticeship matching", "w": "Welders, electricians, plumbers: matched to mentors by region and capacity.", "why": "No aggregator survives national fragmentation and small fees.", "closest": "Job boards with low fidelity.", "d": 3, "tags": ["trades", "unsexy"]},
            {"t": "Proof-of-work portfolios", "w": "Portable, verifiable evidence you can wire a board or keep books — for jobs that don't commit code.", "why": "Assessing hands-on work resists automation's cheapest tricks.", "closest": "LinkedIn endorsements.", "d": 4, "tags": ["credentials", "under-served"]},
            {"t": "A syllabus-true physics simulator", "w": "Every equation on the national exam, playable, in order, in your textbook's notation.", "why": "Per-country fragmentation makes margins miserable.", "closest": "PhET — generic and US-centric.", "d": 3, "tags": ["education", "global"]},
        ],
    },
    {
        "id": "money", "name": "Money & work",
        "note": "Consumer fintech is a shopping mall. The boring floors are empty.",
        "built": [
            ["Budgeting apps", "Spreadsheets with categories and a subscription.", "Banks give them away now.", 5],
            ["Robo-advisors", "Index funds plus a questionnaire.", "Commoditized down to fees.", 4],
            ["Invoice generators", "A template and a PDF.", "Free tier everywhere.", 5],
            ["Gig platforms", "Uber for anything that moves.", "The economics pruned them all.", 4],
            ["Crypto trading apps", "Charts and hope.", "A full market cycle proved the point.", 4],
        ],
        "unbuilt": [
            {"t": "Benefits that follow the worker", "w": "Retirement, insurance and leave accumulating across every gig platform into one portable account.", "why": "Needs platform cooperation or a regulator's shove.", "closest": "State pilots, nothing portable.", "d": 4, "tags": ["policy", "labour"]},
            {"t": "Micro-pensions for informal workers", "w": "Daily micro-contributions structured for street vendors and day labourers.", "why": "Tiny tickets, heavy compliance — where margins hide from impact.", "closest": "One national scheme in India.", "d": 4, "tags": ["global", "regulated"]},
            {"t": "The medical-bill auditor", "w": "Automatic overcharge detection and negotiation for hospital bills.", "why": "The counterparty owns the pricing data.", "closest": "Human advocates, per case.", "d": 3, "tags": ["consumer", "US"]},
            {"t": "Direct cross-border payroll", "w": "One company pays thirty contractors in twelve countries, compliant, without an employer-of-record markup.", "why": "Compliance is real work; incumbents monetize opacity.", "closest": "EOR platforms with steep fees.", "d": 3, "tags": ["fintech", "unsexy"]},
            {"t": "Insurance for informal economies", "w": "Parametric products priced for a homestead — flood, drought, theft — paid out in days.", "why": "Distribution and trust, not actuarial science, are the blockers.", "closest": "Weather-index pilots.", "d": 4, "tags": ["global", "insurance"]},
        ],
    },
    {
        "id": "food", "name": "Food & farming",
        "note": "The delivery apps feast. The fields wait for tools.",
        "built": [
            ["Delivery platforms", "Restaurants, riders, thirty-percent commissions.", "A three-way squeeze, well documented.", 5],
            ["Recipe websites", "A thousand-word essay before the ingredients.", "SEO sludge the AI summaries are now eating.", 5],
            ["QR menus", "A PDF that loads like dial-up.", "Pandemic muscle memory, now furniture.", 5],
            ["Restaurant POS", "Table maps, tickets, tips.", "Consolidated; switching costs do the rest.", 4],
            ["Macro trackers", "Protein, carbs, photo estimates.", "A feature of every fitness app.", 4],
        ],
        "unbuilt": [
            {"t": "A real fridge inventory", "w": "Camera and weight tracking that survives real households, then cooks from what spoils first.", "why": "Computer vision for crumpled kale is genuinely hard.", "closest": "Barcode-only attempts.", "d": 4, "tags": ["computer vision", "consumer"]},
            {"t": "Smallholder advisory", "w": "Satellite, soil and weather turned into plain-language advice in local languages for five hundred million farms.", "why": "Individually poor customers, collectively enormous value.", "closest": "NGO pilots.", "d": 4, "tags": ["agriculture", "global"]},
            {"t": "The household waste scale", "w": "Weigh, log, learn: the bin as the missing fitness tracker.", "why": "No one wants to weigh garbage — a design problem, not a tech one.", "closest": "Municipal pilot programmes.", "d": 2, "tags": ["behaviour", "climate"]},
            {"t": "Tractor dispatch", "w": "Real rental dispatch for farm equipment across a district, with insurance.", "why": "Seasonality, trust and diesel are uncomfortable bedfellows.", "closest": "WhatsApp groups.", "d": 3, "tags": ["hardware", "marketplaces"]},
            {"t": "Composting that doesn't stink", "w": "An indoor composter under $150 that genuinely works.", "why": "The physics of smell against the price of a bin; engineers chose yachts.", "closest": "$500 countertop dryers.", "d": 3, "tags": ["hardware", "climate"]},
        ],
    },
    {
        "id": "civic", "name": "Cities & civic tech",
        "note": "The report-a-pothole apps shipped. The potholes stayed.",
        "built": [
            ["Issue-reporting apps", "Photograph a problem, send it to a void.", "Reports end at reports.", 4],
            ["Government chatbots", "A phone tree with worse manners.", "Procurement chooses the demo, not the service.", 4],
            ["Open-data portals", "CSV dumps with 2012 aesthetics.", "Ninety percent unused, quietly.", 4],
            ["Transit apps", "Departure boards in your pocket.", "Agencies built the good ones; the rest resell feeds.", 4],
            ["Participation platforms", "Idea walls nobody moderates.", "Engagement theatre, budgeted annually.", 3],
        ],
        "unbuilt": [
            {"t": "The report-to-repair loop", "w": "Civic reports bound to work orders, contractors and published costs — fixable, trackable.", "why": "Requires government plumbing, not another app on top.", "closest": "SeeClickFix, which stops at the report.", "d": 4, "tags": ["govtech", "unsexy"]},
            {"t": "Addresses for the unaddressed", "w": "An open addressing standard, print tool and API for the billions who can't receive a parcel.", "why": "what3words licensed the idea and closed the door.", "closest": "Proprietary geocoding.", "d": 3, "tags": ["infrastructure", "global"]},
            {"t": "The local-law changelog", "w": "Zoning, taxes and rules for your street, versioned and monitored like code.", "why": "Twenty thousand municipalities, hostile formats.", "closest": "State-level legislative scanners.", "d": 3, "tags": ["legal", "govtech"]},
            {"t": "Community broadband kit", "w": "Mesh hardware, billing and an operations playbook a neighbourhood can actually run.", "why": "Telecoms lobby, volunteer burnout, capital costs.", "closest": "Municipal pilots.", "d": 4, "tags": ["infrastructure", "cooperative"]},
            {"t": "Emergency routing beyond one number", "w": "An open dispatch layer for regions where 911 or 112 barely answers.", "why": "The people who need it most can't pay for it.", "closest": "Nothing credible.", "d": 5, "tags": ["safety", "global"]},
        ],
    },
    {
        "id": "robotics", "name": "Robotics & manufacturing",
        "note": "Every demo folds a towel. No product does.",
        "built": [
            ["Robot vacuums", "Discs with opinions about your rug.", "Mature market; features are marketing now.", 5],
            ["Consumer drones", "See the hardware field. Same aisle.", "One maker owns the sky.", 4],
            ["3D printers", "Prototyping for everyone, finally.", "Consolidated around a few ecosystems.", 4],
            ["Demo robot arms", "Six axes of picking up a banana for the camera.", "Great videos; no chassis in sight.", 4],
            ["Warehouse robots", "Shelves that walk to you.", "Genuinely built — but B2B, closed and expensive.", 3],
        ],
        "unbuilt": [
            {"t": "The laundry loop", "w": "Wash-to-fold at a home appliance price, no choreography required.", "why": "Soft, floppy objects remain robotics' honest wall.", "closest": "$4,000 fold-only demo units.", "d": 5, "tags": ["hardware", "home"]},
            {"t": "A $1,000 dexterous hand", "w": "Tactile, tendon-driven, open-source — the missing appendage of general robotics.", "why": "Research budgets tolerate $100k hands; garages don't.", "closest": "LEAP Hand: $2k, research-only.", "d": 4, "tags": ["open-source", "robotics"]},
            {"t": "Kitchen line-work", "w": "Dicing, cleaning and plating at restaurant-shift reliability, not stunt-show reliability.", "why": "Food-grade everything plus speed equals unsolved.", "closest": "Automated fryers pretending.", "d": 5, "tags": ["hardware", "food"]},
            {"t": "The workshop assembly cell", "w": "Pick, place, screw and inspect — programmable by a three-person shop, priced for one.", "why": "Industrial cells cost six figures and demand integrators.", "closest": "Industrial integrators.", "d": 4, "tags": ["manufacturing", "SMB"]},
            {"t": "The micro-recycler sorter", "w": "A machine that identifies and bins waste streams for small recyclers and housing estates.", "why": "Material recovery only pays at municipal scale — so far.", "closest": "Materials-recovery plants.", "d": 4, "tags": ["hardware", "circular"]},
        ],
    },
    {
        "id": "access", "name": "Accessibility",
        "note": "The first budget line cut, the last product built.",
        "built": [
            ["Screen readers", "The web, spoken. Built into every OS.", "Genuinely built — and still treated as optional by most sites.", 3],
            ["Accessibility overlays", "One line of JavaScript promising compliance.", "Widely rejected by the very users they claim to serve.", 4],
            ["Voice assistants", "Timers, weather, shopping lists.", "Peak utility reached a decade ago.", 5],
            ["Live captions", "Speech to text, everywhere, finally good.", "A solved feature, thanks to speech models.", 4],
            ["Contrast modes", "Dark mode and high contrast as afterthoughts.", "Standard-issue settings.", 3],
        ],
        "unbuilt": [
            {"t": "Usable sign-language translation", "w": "Continuous, two-way, on-device signing translation.", "why": "Signing is three-dimensional, fast and regional; demos only do fingerspelling.", "closest": "Research prototypes.", "d": 5, "tags": ["AI", "accessibility"]},
            {"t": "Automatic audio description", "w": "Well-acted scene description generated into the gaps of any video's dialogue.", "why": "Timing and tone are craft; fewer than five percent of video carries description today.", "closest": "Manual studios, expensive.", "d": 4, "tags": ["media", "AI"]},
            {"t": "Wheelchair routing everywhere", "w": "Curb cuts, ramp angles and elevator outages, live, in every map app.", "why": "Crowdsourced coverage dies without a champion who needs it daily.", "closest": "Partial coverage in big cities.", "d": 3, "tags": ["maps", "crowdsourced"]},
            {"t": "A screen-reader-first social network", "w": "Not 'compatible with' — designed in audio and braille from the first commit.", "why": "Nobody has inverted the default and shipped it.", "closest": "Nothing.", "d": 3, "tags": ["social", "accessibility"]},
            {"t": "Memory prosthetics for brain injury", "w": "Task scaffolding and context memory built with patients, not around them.", "why": "Generic apps assume every brain ships with standard firmware.", "closest": "To-do lists that don't know what ABI is.", "d": 3, "tags": ["health", "under-served"]},
        ],
    },
    {
        "id": "media", "name": "Internet & media",
        "note": "Every feed is a slot machine. The plumbing quietly rots.",
        "built": [
            ["Short-video feeds", "Infinite swipes, finite attention.", "Two algorithms now share the world's evenings.", 5],
            ["AI image generators", "Prompt, receive, discard.", "Commoditized into every editor.", 5],
            ["Newsletter tools", "Publish and pray for referrals.", "Consolidated; pricing converges.", 4],
            ["Creator monetization", "Subscriptions, tips, merch shelves.", "Platforms tax creators at both ends.", 4],
            ["Podcast platforms", "An RSS ecosystem wearing a walled garden.", "Distribution solved; discovery still luck.", 4],
        ],
        "unbuilt": [
            {"t": "Visible photo provenance", "w": "The C2PA standard exists; the camera roll that shows it doesn't.", "why": "Standards without consumer surfaces change nothing.", "closest": "Newsroom pilots.", "d": 3, "tags": ["trust", "standards"]},
            {"t": "Archives that outlive platforms", "w": "Your posts, purchases and messages merged into one file no shutdown can delete.", "why": "Every provider prefers your history inside their walls.", "closest": "Per-platform exports in dying formats.", "d": 3, "tags": ["data", "consumer"]},
            {"t": "The consent agent", "w": "Your browser negotiates cookies and trackers once, per your rules, everywhere.", "why": "Sites fight it and laws disagree — the classic blocked gap.", "closest": "Half-kept 'Do Not Track'.", "d": 4, "tags": ["privacy", "browser"]},
            {"t": "Mid-scroll fact-check", "w": "Claim-level context attached to what's passing by, before you share it.", "why": "Platforms monetize speed; a pause is a design insult to them.", "closest": "Post-viral labels.", "d": 3, "tags": ["trust", "media"]},
            {"t": "Modern forum software", "w": "The 2005 stack that runs niche communities, rebuilt to make hosting them sustainable.", "why": "The builders left; the communities stayed.", "closest": "Discourse — better, still heavy.", "d": 2, "tags": ["community", "open-source"]},
        ],
    },
]

# Half-built ideas: something exists, but never finished properly.
# [t, w (what exists), missing (what is missing), why (why it stalled), d (difficulty to finish), tags]
HALF = {
    "software": [
        {"t": "Local-first software", "w": "A movement with real tools — Syncthing, Obsidian, offline design editors — proving software can work without a server.", "missing": "A mainstream app category that treats offline as the default, not a premium feature.", "why": "Subscription economics keeps dragging everything back to the cloud.", "d": 3, "tags": ["infrastructure", "movement"]},
        {"t": "Passkeys everywhere", "w": "The passwordless standard ships in every major operating system and browser.", "missing": "Coverage across banks, governments and the long tail of services — plus recovery when you lose everything.", "why": "Every institution migrates at its own geological pace.", "d": 2, "tags": ["security", "standards"]},
        {"t": "Search for your own life", "w": "OS search finds filenames, photo apps find faces, a few tools find document text.", "missing": "One private, on-device search across everything you have ever seen, typed or photographed.", "why": "Indexing a lifetime of data locally without melting the laptop is genuinely hard.", "d": 4, "tags": ["AI", "privacy"]},
        {"t": "Messaging interop", "w": "Regulators forced the EU gatekeepers to open messaging to other apps under the DMA.", "missing": "Actual interconnection: the big networks barely talk, and third-party clients stayed niche.", "why": "The giants comply in the letter and stall in practice.", "d": 3, "tags": ["regulation", "standards"]},
        {"t": "Package managers for everything", "w": "Code has npm and apt; phones have app stores.", "missing": "The same install-update-trust machinery for datasets, models and design assets.", "why": "Every domain reinvents licensing and trust from scratch.", "d": 3, "tags": ["developer", "standards"]},
    ],
    "ai": [
        {"t": "On-device assistants", "w": "Phones ship small models that summarize and translate offline.", "missing": "A private assistant that actually knows your life and never phones home.", "why": "Memory and battery budgets are real — and vendors prefer your data in their cloud.", "d": 4, "tags": ["privacy", "hardware"]},
        {"t": "AI in peer review", "w": "Journals already use AI to screen plagiarism and pick reviewers.", "missing": "Tools that check a paper's statistics, code and reproducibility before humans spend months.", "why": "Editors fear liability; reviewers have no time.", "d": 3, "tags": ["science", "trust"]},
        {"t": "Conversation that lasts", "w": "Assistants handle timers, weather and smart homes competently.", "missing": "Dialogue that holds context for weeks and acts across every app you use.", "why": "Each vendor walls its assistant inside its own ecosystem.", "d": 4, "tags": ["consumer", "interoperability"]},
        {"t": "Translation for real speech", "w": "Research systems cover thousands of languages on paper.", "missing": "Reliable everyday products for the hundreds of languages billions actually speak at home.", "why": "Per-language data work does not fit venture math.", "d": 3, "tags": ["global", "open-source"]},
        {"t": "AI code review", "w": "Assistants autocomplete and catch obvious bugs inside IDEs.", "missing": "A reviewer that understands architecture, catches security flaws, and earns senior engineers' trust.", "why": "Responsibility for a wrong review still lands on humans.", "d": 4, "tags": ["developer", "trust"]},
    ],
    "hardware": [
        {"t": "E-ink beyond books", "w": "E-ink is cheap, calm and sips power — in dedicated readers.", "missing": "E-ink phones, dashboards and monitors that refresh fast enough for daily use.", "why": "Refresh rate and cost; color e-ink has been almost-ready for a decade.", "d": 4, "tags": ["displays", "hardware"]},
        {"t": "Modular phones", "w": "Fairphone proves repairable phones can ship; Framework did it for laptops.", "missing": "A modular phone at flagship price and performance, sold worldwide.", "why": "Thin margins and carrier deals punish modularity.", "d": 4, "tags": ["circular", "hardware"]},
        {"t": "Health patches", "w": "Continuous glucose monitors changed diabetes care overnight.", "missing": "The same cheap disposable patch for hydration, stress hormones and infection markers.", "why": "Biochemistry resists miniaturization, and regulation adds years.", "d": 5, "tags": ["health", "hardware"]},
        {"t": "A smart home that works", "w": "Matter, the unifying standard, finally shipped across vendors.", "missing": "Setup that works for normal people: no hubs, no app per bulb, no dead devices.", "why": "Every vendor still wants to own the hub.", "d": 3, "tags": ["standards", "consumer"]},
        {"t": "Satellite messaging", "w": "Flagship phones now text satellites in emergencies.", "missing": "Cheap, unlimited two-way data anywhere on Earth, at ordinary prices.", "why": "Spectrum, launch costs and telecom lobbying.", "d": 5, "tags": ["space", "telecom"]},
    ],
    "health": [
        {"t": "Continuous monitors", "w": "Glucose sensors and wrist ECGs moved vitals from clinics to wrists.", "missing": "Blood pressure, hydration and hormones on the same continuous, cheap, wearable rail.", "why": "Every new marker is its own physiological and regulatory battle.", "d": 4, "tags": ["wearables", "regulated"]},
        {"t": "Chronic care over video", "w": "Telemedicine exploded during the pandemic and stayed.", "missing": "Chronic disease management that ties remote monitoring to adjusted prescriptions automatically.", "why": "Prescribing rules lag the technology by a decade.", "d": 3, "tags": ["regulated", "clinical"]},
        {"t": "Genetic risk prediction", "w": "Consumer kits flag variants for a few dozen conditions.", "missing": "Polygenic risk scores that are accurate across ancestries and actionable in clinics.", "why": "The datasets skew heavily to white Europeans.", "d": 4, "tags": ["genomics", "equity"]},
        {"t": "Sleep science in products", "w": "Wearables measure sleep stages with decent accuracy.", "missing": "Interventions that actually fix sleep, instead of scoring it.", "why": "Measurement is easy; behaviour change is not a gadget.", "d": 3, "tags": ["consumer", "behaviour"]},
        {"t": "Antibiotic alternatives", "w": "Phage therapy and CRISPR antimicrobials work in case studies and labs.", "missing": "A pipeline that gets them through trials, into factories and onto pharmacy shelves.", "why": "Pharma economics punish narrow cures that resistance can outdate.", "d": 5, "tags": ["biotech", "regulated"]},
    ],
    "climate": [
        {"t": "Green hydrogen", "w": "Electrolyzers exist, and pilots ship hydrogen-made ammonia and steel.", "missing": "Cost parity with fossil hydrogen at scale, plus the pipelines to move it.", "why": "Cheap solar keeps out-competing it for electrons.", "d": 4, "tags": ["energy", "industrial"]},
        {"t": "Battery swapping", "w": "It works at scale for scooters and rickshaws across Asia.", "missing": "The same standard for cars: one swap network any EV can use.", "why": "Every carmaker builds a different pack.", "d": 4, "tags": ["transport", "standards"]},
        {"t": "Carbon removal", "w": "Direct air capture plants exist; buyers pay around $600 a ton.", "missing": "A route under $100 a ton, measured and guaranteed by someone trustworthy.", "why": "The physics is generous; the economics is brutal.", "d": 5, "tags": ["climate", "market"]},
        {"t": "Cooling without super-pollutants", "w": "The Kigali treaty phases out HFC refrigerants, and alternatives exist.", "missing": "Alternatives as cheap, safe and efficient in tropical heat at mass scale.", "why": "Every substitute trades one problem for another.", "d": 3, "tags": ["climate", "hardware"]},
        {"t": "Vertical farming", "w": "Lettuce grows profitably in warehouses in a few cities.", "missing": "Staple crops at grid-scale economics; most vertical farms still sell garnish.", "why": "Light is an electricity bill, and wheat does not care.", "d": 4, "tags": ["agriculture", "energy"]},
    ],
    "education": [
        {"t": "Classroom laptops, rebooted", "w": "Cheap devices reached hundreds of millions of students.", "missing": "Software and maintenance that survive the classroom; most kit gathers dust within two years.", "why": "Hardware got funded; teachers and repair did not.", "d": 3, "tags": ["global", "schools"]},
        {"t": "AI tutors", "w": "Chatbots explain homework in every subject, for free.", "missing": "A tutor that sequences a real curriculum, remembers your gaps, and proves learning gains.", "why": "Explaining is solved; teaching is not.", "d": 3, "tags": ["AI", "education"]},
        {"t": "Micro-credentials", "w": "Course certificates and digital badges exist by the million.", "missing": "Employers trusting them the way they trust a degree.", "why": "Signal inflation: when everyone issues badges, nobody reads them.", "d": 3, "tags": ["credentials", "labour"]},
        {"t": "Classroom translation", "w": "Auto-captioning and translation work well for major languages.", "missing": "Real-time quality good enough for a refugee kid to follow a physics lesson.", "why": "Accent, jargon and classroom noise defeat current systems.", "d": 3, "tags": ["global", "AI"]},
        {"t": "School data for teachers", "w": "Every school runs an information system.", "missing": "Data that returns to teachers as usable insight instead of compliance paperwork.", "why": "Procurement buys record-keeping, not teaching tools.", "d": 2, "tags": ["schools", "unsexy"]},
    ],
    "money": [
        {"t": "Instant payments", "w": "Pix in Brazil, UPI in India, FedNow in the US: national rails that settle in seconds.", "missing": "Cross-border links, so a worker in Dubai sends home at UPI speed and cost.", "why": "Correspondent banking is a profitable puddle.", "d": 3, "tags": ["payments", "global"]},
        {"t": "Open banking", "w": "Europe and a dozen countries force banks to share your data through APIs.", "missing": "The other 150 countries — and APIs that stay reliable and standardized.", "why": "Banks comply minimally where they must.", "d": 3, "tags": ["fintech", "regulated"]},
        {"t": "Digital identity", "w": "India's Aadhaar and Estonia's e-ID prove state-scale digital identity works.", "missing": "Interoperable, privacy-preserving identity for the billion people without legal ID.", "why": "Trust in the issuer is everything, and nobody trusts everyone.", "d": 5, "tags": ["identity", "global"]},
        {"t": "Lending without collateral", "w": "Fintechs score small merchants from transaction data in a few markets.", "missing": "Underwriting that travels: the same rails for shopkeepers everywhere.", "why": "Local contract enforcement is the hard part, not the model.", "d": 4, "tags": ["credit", "global"]},
        {"t": "Equity for creators", "w": "Patreon and Substack turned audiences into salaries.", "missing": "Fans holding actual equity in the work they make famous.", "why": "Securities law treats every fan as a broker.", "d": 4, "tags": ["creator", "regulated"]},
    ],
    "food": [
        {"t": "Cultivated meat", "w": "Singapore and the US approved the first lab-grown chicken portions.", "missing": "Cost, scale and taste parity; the first plants produce boutique quantities.", "why": "Bioreactors are expensive and cells are delicate.", "d": 5, "tags": ["biotech", "food"]},
        {"t": "Precision-fermented dairy", "w": "Brewed whey and casein proteins already sit in real ice cream.", "missing": "Price parity and the green light across major markets.", "why": "Dairy lobbies move slowly and fermentation tanks move expensively.", "d": 4, "tags": ["biotech", "regulated"]},
        {"t": "Cold chains for smallholders", "w": "Solar cold rooms run in pilot markets across Asia and Africa.", "missing": "Financing and service networks so every market town can run one.", "why": "The gear works; the business model is the gap.", "d": 3, "tags": ["agriculture", "global"]},
        {"t": "Food-waste markets", "w": "Apps sell restaurants' surplus at a discount in big cities.", "missing": "Coverage of groceries, farms and the Global South, where most waste happens.", "why": "Waste is fragmented; every tonne hides in a different supply chain.", "d": 3, "tags": ["climate", "marketplaces"]},
        {"t": "Soil sensing in the field", "w": "Labs read soil samples precisely; kits give rough answers in minutes.", "missing": "Cheap, farmer-grade sensors that read nitrogen and carbon in the field, continuously.", "why": "Chemistry in mud is much harder than chemistry in a vial.", "d": 4, "tags": ["agriculture", "hardware"]},
    ],
    "civic": [
        {"t": "Digital voting", "w": "Estonia votes online; dozens of countries pilot electronic ballots.", "missing": "A system verifiable by ordinary people that survives national politics.", "why": "Security researchers keep showing the prototypes break.", "d": 5, "tags": ["democracy", "security"]},
        {"t": "Digital government", "w": "Estonia, India and others moved most public services online.", "missing": "The long tail: land records, courts and permits digitized without bribes or queues.", "why": "Every reform threatens somebody's rent.", "d": 4, "tags": ["govtech", "corruption"]},
        {"t": "Participatory budgeting", "w": "Thousands of cities let residents vote on small budgets.", "missing": "Real power: the big capital budgets, and evidence the votes change anything.", "why": "The hallways of city hall defend the purse.", "d": 3, "tags": ["democracy", "cities"]},
        {"t": "Disaster early warning", "w": "Cell broadcast reaches millions; the UN aims for global coverage by 2027.", "missing": "Last-mile systems for the poorest regions, in local languages, with somewhere to go.", "why": "A warning without shelter or transport is just a louder disaster.", "d": 3, "tags": ["safety", "global"]},
        {"t": "Public connectivity", "w": "Kiosks like New York's LinkNYC replaced payphones with free Wi-Fi.", "missing": "Free, fast public connectivity as normal as streetlights, in every city.", "why": "No revenue model survives the procurement office.", "d": 2, "tags": ["infrastructure", "cities"]},
    ],
    "robotics": [
        {"t": "Humanoid robots", "w": "Boston Dynamics dances; factories pilot humanoids moving totes.", "missing": "A humanoid that earns its price doing real work for a year without hand-holding.", "why": "Legs are solved; hands, batteries and economics are not.", "d": 5, "tags": ["hardware", "industry"]},
        {"t": "Autonomous trucking", "w": "Driverless trucks run scheduled freight on a few US sunbelt routes.", "missing": "Highway legality everywhere, in weather, with depot economics that beat a driver.", "why": "The long tail of edge cases meets labour politics.", "d": 5, "tags": ["transport", "regulated"]},
        {"t": "Agricultural robots", "w": "Weeders and strawberry pickers work in pilot fields.", "missing": "Machines cheap and versatile enough for small, mixed, messy farms.", "why": "Nature is unstructured and farms are capital-poor.", "d": 4, "tags": ["agriculture", "hardware"]},
        {"t": "Delivery robots", "w": "Sidewalk robots serve a few campuses; drones drop parcels in parts of Africa and Texas.", "missing": "Density and city permits that make them cheaper than a person on a bike.", "why": "Cities tax what they fear, and pedestrians resent wheels.", "d": 4, "tags": ["cities", "regulated"]},
        {"t": "Surgical autonomy", "w": "Assistive systems support millions of operations a year.", "missing": "Autonomy for routine steps, at a price community hospitals can pay.", "why": "Liability concentrates on whoever writes the motion.", "d": 5, "tags": ["medical", "regulated"]},
    ],
    "access": [
        {"t": "Signing avatars", "w": "Avatars and smart gloves translate fingerspelled, isolated signs.", "missing": "Continuous, natural, two-way conversation — the grammar, not the alphabet.", "why": "Signing is a full spatial language; gloves capture none of it.", "d": 5, "tags": ["AI", "accessibility"]},
        {"t": "AI screen readers", "w": "Screen readers read text fast — but hostile pages remain hostile.", "missing": "An assistant that understands page intent and navigates for you, on every site.", "why": "Broken markup never runs out.", "d": 3, "tags": ["AI", "web"]},
        {"t": "Smart navigation canes", "w": "Instrumented canes and apps add obstacle detection.", "missing": "Outdoor-grade, all-weather guidance that beats a trained dog or a white cane.", "why": "Reliability must be near-perfect, or it is dangerous.", "d": 4, "tags": ["hardware", "safety"]},
        {"t": "Inclusive gaming", "w": "Major consoles ship adaptive controllers.", "missing": "Games designed from scratch for blind and motor-limited players, not ported to them.", "why": "Accessibility is a budget line, and it gets cut first.", "d": 3, "tags": ["gaming", "design"]},
        {"t": "Public audio for hearing aids", "w": "Hearing aids stream from phones; loop systems work in some halls.", "missing": "Auracast-style public audio in every station, classroom and theatre.", "why": "Building owners see no paying customer.", "d": 2, "tags": ["audio", "standards"]},
    ],
    "media": [
        {"t": "Universal digital libraries", "w": "The Internet Archive, Project Gutenberg and national libraries scan millions of works.", "missing": "Legal, complete access to the 20th century, still locked by unclear rights.", "why": "A copyright thicket where owners are unknown, so nobody may digitize.", "d": 4, "tags": ["law", "culture"]},
        {"t": "Interoperable social networks", "w": "The fediverse federates, and Threads adopted its protocol.", "missing": "Seamless movement: following anyone from anywhere, with your social graph in your pocket.", "why": "Network effects are the moat, and the protocol drains it.", "d": 4, "tags": ["standards", "social"]},
        {"t": "Interactive news", "w": "Newsrooms ship beautiful interactives for a handful of stories a year.", "missing": "A toolchain where any reporter can build one in an afternoon.", "why": "Every interactive is still a bespoke software project.", "d": 3, "tags": ["journalism", "tools"]},
        {"t": "A creator middle class", "w": "A million people earn from audiences; a few get rich.", "missing": "Economics that let ten million earn a living wage without dancing for an algorithm.", "why": "Platforms pay the top 0.1 percent and harvest the rest.", "d": 4, "tags": ["labour", "platforms"]},
        {"t": "Local news, rebuilt", "w": "Nonprofit newsrooms and newsletters refill some news deserts.", "missing": "A model that covers every county courthouse and city hall, profitably.", "why": "Classified advertising left and never came back.", "d": 4, "tags": ["journalism", "business"]},
    ],
}

TOTAL_BUILT = sum(len(f["built"]) for f in FIELDS)
TOTAL_HALF = sum(len(HALF[f["id"]]) for f in FIELDS)
TOTAL_UNBUILT = sum(len(f["unbuilt"]) for f in FIELDS)
TOTAL = TOTAL_BUILT + TOTAL_HALF + TOTAL_UNBUILT

PICKS = [
    ("software", 0, "Every service you use keeps a copy of you. This one idea asks for the exit."),
    ("hardware", 0, "The clearest hardware gap on the census: huge human value, no volume bet yet."),
    ("money", 0, "Work went portable; the safety net didn't. A regulated, boring, enormous gap."),
]


def esc(s):
    return html.escape(str(s), quote=True)


def nav_links(prefix, active):
    items = [
        ("index.html", "Home"),
        ("fields.html", "Fields"),
        ("search.html", "Search"),
        ("shelves.html", "Shelves"),
        ("about.html", "About"),
    ]
    out = []
    for href, label in items:
        cur = ' aria-current="page"' if label == active else ""
        out.append(f'<a href="{prefix}{href}"{cur}>{label}</a>')
    return "\n          ".join(out)


def head_block(title, desc, prefix, active):
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2032%2032'%3E%3Crect%20x='2'%20y='8'%20width='12'%20height='16'%20fill='%23262A22'/%3E%3Crect%20x='18'%20y='8'%20width='12'%20height='16'%20fill='none'%20stroke='%233A5A94'%20stroke-width='2.5'%20stroke-dasharray='4%203'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,62..125,100..900;1,62..125,100..900&family=Source+Serif+4:ital,opsz,wght@0,8..60,300..700;1,8..60,300..700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/style.css">"""


def site_header(prefix, active):
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap">
    <a class="brand" href="{prefix}index.html">Unbuilt<small>a census of human making</small></a>
    <nav class="site-nav" aria-label="Primary">
          {nav_links(prefix, active)}
    </nav>
  </div>
</header>"""


def site_footer(prefix):
    field_links = " ".join(
        f'<a href="{prefix}fields/{f["id"]}.html">{esc(short_name(f["name"]))}</a>'
        for f in FIELDS
    )
    return f"""<footer>
  <div class="wrap foot-grid">
    <div>
      <p class="brand-f">Unbuilt</p>
      <p>A census of human making: what the world already has on its shelves, and what it is still missing. Read the solid cards to avoid the crowd, the dashed ones to find an empty lane.</p>
    </div>
    <nav aria-label="Footer">
      <h2>Site</h2>
      <div class="foot-nav">
        <a href="{prefix}index.html">Home</a>
        <a href="{prefix}fields.html">All fields</a>
        <a href="{prefix}search.html">Search the census</a>
        <a href="{prefix}shelves.html">Search the shelves</a>
        <a href="{prefix}about.html">Methodology</a>
      </div>
    </nav>
    <div>
      <h2>Fields</h2>
      <div class="foot-fields">{field_links}</div>
    </div>
  </div>
  <div class="colophon">
    <div class="wrap">
      Compiled October 2026 from public reporting and a lot of squinting. Set in Archivo and Source Serif 4. Static pages, no trackers. If you build something from a dashed card, come back and tell the census.
    </div>
  </div>
</footer>"""


def short_name(name):
    return name.split(" & ")[0] if " & " in name else name


SOURCE_DISPLAY = {
    "flathub": "Flathub", "fdroid": "F-Droid", "itunes": "App Store",
    "play": "Google Play", "npm": "npm", "ifixit": "iFixit", "fda": "FDA devices",
    "arduino": "Arduino", "steam": "Steam", "off": "Open Food Facts",
}


def catalog_info():
    """Read assets/catalog.json if the pipeline has run; catalog dict or None."""
    try:
        import json
        with open(os.path.join(OUT, "assets", "catalog.json"), encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def source_names(catalog):
    keys = sorted(catalog.get("sources", {}), key=lambda k: -catalog["sources"].get(k, 0))
    names = [SOURCE_DISPLAY.get(k, k) for k in keys]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def shelves_teaser():
    c = catalog_info()
    if c:
        return (f"Opinion says a space is crowded; a catalog proves it. {c['count']:,} real, "
                f"published apps, devices and products — {source_names(c)} — collected "
                f"{c['generated']}, searchable by name, category and maker.")
    return ("Real, published apps, devices and products from ten catalogs — Flathub, F-Droid, "
            "the App Store, Google Play, npm, iFixit, FDA devices, Arduino, Steam and Open Food "
            "Facts — collected by pipeline/ingest.py and searchable on the shelves page.")


def meter_html(kind, n, label):
    squares = "".join(f'<span class="sq{" on" if i < n else ""}"></span>' for i in range(5))
    return (f'<p class="meter"><span>{kind}</span><span class="squares" aria-hidden="true">{squares}</span>'
            f'<span class="visually-hidden">{esc(label)}</span></p>')


def built_card(f, b, i):
    t, w, v, c = b
    return f"""<article class="card built" id="c-{f['id']}-b{i}">
  <h3>{esc(t)}</h3>
  <p class="what">{esc(w)}</p>
  {meter_html("Crowdedness", c, f"Crowdedness {c} of 5")}
  <p class="verdict">{esc(v)}</p>
</article>"""


def unbuilt_card(f, u, i):
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in u["tags"])
    return f"""<article class="card unbuilt" id="c-{f['id']}-u{i}">
  <h3>{esc(u['t'])}</h3>
  <p class="what">{esc(u['w'])}</p>
  <p class="why">{esc(u['why'])}</p>
  <p class="closest">{esc(u['closest'])}</p>
  {meter_html("Difficulty", u['d'], f"Difficulty {u['d']} of 5")}
  <p class="tags">{tags}</p>
</article>"""


def half_card(f, u, i):
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in u["tags"])
    return f"""<article class="card half" id="c-{f['id']}-h{i}">
  <h3>{esc(u['t'])}</h3>
  <p class="what">{esc(u['w'])}</p>
  <p class="missing">{esc(u['missing'])}</p>
  <p class="why">{esc(u['why'])}</p>
  {meter_html("Difficulty to finish", u['d'], f"Difficulty to finish {u['d']} of 5")}
  <p class="tags">{tags}</p>
</article>"""


def census_strip(prefix):
    cells = []
    for f in FIELDS:
        for i, b in enumerate(f["built"]):
            title = f"{f['name']}: {b[0]} (already built)"
            cells.append(f'<a class="cell" href="{prefix}fields/{f["id"]}.html#c-{f["id"]}-b{i}" title="{esc(title)}" aria-label="{esc(title)}"></a>')
        for i, u in enumerate(HALF[f["id"]]):
            title = f"{f['name']}: {u['t']} (half-built)"
            cells.append(f'<a class="cell h" href="{prefix}fields/{f["id"]}.html#c-{f["id"]}-h{i}" title="{esc(title)}" aria-label="{esc(title)}"></a>')
        for i, u in enumerate(f["unbuilt"]):
            title = f"{f['name']}: {u['t']} (not built yet)"
            cells.append(f'<a class="cell u" href="{prefix}fields/{f["id"]}.html#c-{f["id"]}-u{i}" title="{esc(title)}" aria-label="{esc(title)}"></a>')
    return "\n          ".join(cells)


def tiles(prefix, rich=False):
    out = []
    for f in FIELDS:
        note = f'<p class="t-note">{esc(f["note"])}</p>' if rich else ""
        out.append(f"""<a class="tile" href="{prefix}fields/{f['id']}.html">
  <h3>{esc(f['name'])}</h3>
  <p class="counts">{len(f['built'])} already built, {len(HALF[f['id']])} half-built, {len(f['unbuilt'])} not yet</p>
  {note}
</a>""")
    return "\n".join(out)


def page(title, desc, prefix, active, main_html):
    return f"""<!doctype html>
<html lang="en">
<head>
{head_block(title, desc, prefix, active)}
</head>
<body>
{site_header(prefix, active)}
<main id="main">
{main_html}
</main>
{site_footer(prefix)}
<script src="{prefix}assets/census.js"></script>
<script src="{prefix}assets/app.js"></script>
</body>
</html>
"""


# ---------------------------------------------------------------- home
def build_home():
    picks = []
    for fid, idx, why in PICKS:
        f = next(x for x in FIELDS if x["id"] == fid)
        u = f["unbuilt"][idx]
        picks.append(f"""<article class="card unbuilt pick">
  <p class="pick-field">{esc(f['name'])}</p>
  <h3>{esc(u['t'])}</h3>
  <p class="what">{esc(u['w'])}</p>
  <p class="why">{esc(u['why'])}</p>
  <a class="more" href="fields/{fid}.html#c-{fid}-u{idx}">Read this gap in full</a>
</article>""")
    picks_html = "\n".join(picks)

    main = f"""<section class="hero">
  <div class="wrap">
    <h1>Everyone is building the same ten things.</h1>
    <p class="lede">
      This is a census of what humanity has made and what it hasn't — across software,
      hardware, health, energy, farming, cities, robotics and more. Every field splits in
      three: <em>the solid column is the shelf that's already overloaded</em>;
      <em>the outlined column is what exists but was never finished properly</em>; and
      <em>the dashed column is the empty lane</em>.
    </p>
    <div class="stats">
      <div class="stat"><b>{TOTAL}</b><span>ideas catalogued</span></div>
      <div class="stat"><b>{TOTAL_BUILT}</b><span>already built — stop adding</span></div>
      <div class="stat"><b>{TOTAL_HALF}</b><span>half-built — worth finishing</span></div>
      <div class="stat"><b>{TOTAL_UNBUILT}</b><span>not built yet — open lanes</span></div>
    </div>
    <div class="actions">
      <a class="btn" href="fields.html" data-random-gap>Pull a random gap</a>
      <a class="btn ghost" href="fields.html">Browse the fields</a>
    </div>

    <figure class="census">
      <div class="census-head">
        <h2>The census</h2>
        <div class="legend">
          <span class="k-built"><i></i>already built</span>
          <span class="k-half"><i></i>half-built</span>
          <span class="k-unbuilt"><i></i>not built yet</span>
        </div>
      </div>
      <div class="strip" id="strip">
          {census_strip("")}
      </div>
      <figcaption>One cell per idea. Hover to see it, click to jump straight to it.</figcaption>
    </figure>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <h2>Three gaps to start with</h2>
    <p class="sub">If the census were a reading list, these would be page one — one software gap, one hardware gap, one institutional gap.</p>
    <div class="picks">
      {picks_html}
    </div>
  </div>
</section>

<section class="sec" id="fields">
  <div class="wrap">
    <h2>The twelve fields</h2>
    <p class="sub">Each field page holds the same bargain: five crowded ideas to avoid, five open ones to consider.</p>
    <div class="tiles">
      {tiles("")}
    </div>
  </div>
</section>

<section class="sec" id="shelves">
  <div class="wrap">
    <h2>The shelves</h2>
    <p class="sub">{shelves_teaser()}</p>
    <div class="actions"><a class="btn" href="shelves.html">Search the shelves</a></div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <h2>How to use the census</h2>
    <ol class="howto">
      <li>Pick a field you can actually work in — not the one with the best video.</li>
      <li>Avoid the solid cards. That crowd needs no reinforcements.</li>
      <li>Study the outlined cards: something exists but stalls. Finishing it can beat inventing.</li>
      <li>Take a dashed card and check it against reality: search for products, message the makers of the closest attempt, then decide.</li>
    </ol>
    <p class="howto-more">Judgement calls, definitions and sources are explained in the <a href="about.html">methodology</a>.</p>
  </div>
</section>"""
    return page(
        "Unbuilt — what to build, and what to stop building",
        f"A census of human making: {TOTAL} ideas across {len(FIELDS)} fields, split into what the world already has and what it is still missing.",
        "", "Home", main)


# ---------------------------------------------------------------- fields index
def build_fields_index():
    main = f"""<section class="hero slim">
  <div class="wrap">
    <h1>The fields</h1>
    <p class="lede">Twelve rooms in the house of human making. Each one is split the same way: what is already on the shelf, and what the shelf is still waiting for.</p>
  </div>
</section>
<section>
  <div class="wrap">
    <div class="tiles rich">
      {tiles("", rich=True)}
    </div>
  </div>
</section>"""
    return page(
        "All fields — Unbuilt",
        f"Browse all {len(FIELDS)} fields of the census: software, AI, hardware, health, climate, education, money, food, cities, robotics, accessibility and media.",
        "", "Fields", main)


# ---------------------------------------------------------------- field page
def build_field_page(idx):
    f = FIELDS[idx]
    prev_f = FIELDS[(idx - 1) % len(FIELDS)]
    next_f = FIELDS[(idx + 1) % len(FIELDS)]
    half = HALF[f["id"]]
    built_cards = "\n".join(built_card(f, b, i) for i, b in enumerate(f["built"]))
    half_cards = "\n".join(half_card(f, u, i) for i, u in enumerate(half))
    unbuilt_cards = "\n".join(unbuilt_card(f, u, i) for i, u in enumerate(f["unbuilt"]))
    main = f"""<div class="wrap">
  <nav class="crumb" aria-label="Breadcrumb">
    <a href="../index.html">Home</a><span class="sep">/</span><a href="../fields.html">Fields</a><span class="sep">/</span><span aria-current="page">{esc(f['name'])}</span>
  </nav>

  <header class="field-head page-head">
    <h1>{esc(f['name'])}</h1>
    <p class="note">{esc(f['note'])}</p>
  </header>

  <div class="cols">
    <div class="col col-built">
      <div class="col-head"><span class="swatch" aria-hidden="true"></span>Already built<span class="count">{len(f['built'])}</span></div>
      {built_cards}
    </div>
    <div class="col col-half">
      <div class="col-head"><span class="swatch half" aria-hidden="true"></span>Half-built<span class="count">{len(half)}</span></div>
      {half_cards}
    </div>
    <div class="col col-unbuilt">
      <div class="col-head"><span class="swatch" aria-hidden="true"></span>Not built yet<span class="count">{len(f['unbuilt'])}</span></div>
      {unbuilt_cards}
    </div>
  </div>

  <nav class="pager" aria-label="More fields">
    <a href="{prev_f['id']}.html"><span class="dir">Previous field</span><span class="name">{esc(prev_f['name'])}</span></a>
    <a class="all" href="../fields.html">All fields</a>
    <a class="next" href="{next_f['id']}.html"><span class="dir">Next field</span><span class="name">{esc(next_f['name'])}</span></a>
  </nav>
</div>"""
    return page(
        f"{f['name']} — Unbuilt",
        f"{f['note']} Five already-built ideas to avoid and five open gaps in {f['name'].lower()}.",
        "../", None, main)


# ---------------------------------------------------------------- search page
def build_search():
    main = """<section class="hero slim">
  <div class="wrap">
    <h1>Search the census</h1>
    <p class="lede">All {TOTAL} ideas in one box. Try “braille”, “farm”, “pension”, “battery” — or the thing you were about to build, to check whether the shelf already bends under its weight.</p>
  </div>
</section>
<section>
  <div class="wrap">
    <p class="howto-more">This page searches the census of ideas — editorial calls. To search real, published apps, use the <a href="shelves.html">shelves</a>.</p>
    <div class="toolbar-page">
      <input id="q" type="search" placeholder="Search {TOTAL} ideas…" aria-label="Search ideas">
      <span class="shown" id="shown" aria-live="polite"></span>
    </div>
    <div class="results" id="results" aria-label="Search results"></div>
  </div>
</section>"""
    return page(
        "Search — Unbuilt",
        "Search all 120 ideas in the census of human making, across software, hardware, health, climate and nine more fields.",
        "", "Search", main)


# ---------------------------------------------------------------- shelves page
def build_shelves():
    c = catalog_info()
    if c:
        lede = (f"Opinion says a space is crowded; a catalog proves it. These are real, published "
                f"apps, devices and products — {c['count']:,} of them, collected {c['generated']} "
                f"from {source_names(c)}. Search before you build.")
    else:
        lede = ("A catalog of real, published apps, devices and products — evidence for what "
                "already exists. Build it with pipeline/ingest.py and pipeline/build_site_index.py.")
    main = f"""<section class="hero slim">
  <div class="wrap">
    <h1>The shelves</h1>
    <p class="lede">{lede}</p>
  </div>
</section>
<section>
  <div class="wrap">
    <p class="shelves-status" id="loadstate" aria-live="polite">Loading the catalog…</p>
    <div class="srcchips" id="srcchips" aria-label="Filter by source"></div>
    <div class="toolbar-page">
      <input id="q" type="search" placeholder="Search real apps, devices, products — try “hearing aid”, “tractor”, “notes”…" aria-label="Search published products" disabled>
      <span class="shown" id="shown" aria-live="polite"></span>
    </div>
    <div class="results" id="results" aria-label="Catalog results"></div>
  </div>
</section>
<script>
{SHELVES_JS}</script>"""
    return page(
        "The shelves — Unbuilt",
        "Search real, published apps and packages from Flathub, F-Droid, the App Store, Google Play and npm — evidence of what is already built.",
        "", "Shelves", main)


# ---------------------------------------------------------------- about page
def build_about():
    main = """<section class="hero slim">
  <div class="wrap">
    <h1>About the census</h1>
    <p class="lede">What this is, how it was put together, and where it will be wrong.</p>
  </div>
</section>
<section class="prose wrap">
  <h2>What this is</h2>
  <p>
    Unbuilt is a census of human making. It lists ideas in twelve fields and splits each
    field three ways: things the world already has plenty of, things that exist but were
    never finished properly, and things it is still missing. The premise is simple — in
    every field, most people build the same ten things, because those ten things are
    visible. The interesting work hides in the outlined and dashed cards, which are
    invisible precisely because nobody has made them yet — or nobody has made them whole.
  </p>

  <h2>What the three columns mean</h2>
  <p>
    <strong>Already built</strong> means the shelf is full: mature products, many funded
    competitors, no unsolved problem left worth your years. The crowdedness marks are
    judgement, not measurement — five squares means you would be entering the most crowded
    room in the field.
  </p>
  <p>
    <strong>Half-built</strong> means it exists, but not properly: too expensive, locked to
    one country or vendor, painful to use, or stuck at pilot scale. These are often the
    best openings on the census — the riskiest question, "does anyone actually want this?",
    is already answered by whatever exists, and the assignment is to finish what stalled.
    Each card says what is missing and why it stalled.
  </p>
  <p>
    <strong>Not built yet</strong> means not built well enough, cheaply enough, or
    available where most people live. It is not a claim that nobody ever tried. Many of
    these gaps are open for good reasons — regulation, thin margins, missing data — and
    the page says which reason blocks each one. A gap with a blocker is an assignment, not
    a warning.
  </p>

  <h2>How it was compiled</h2>
  <p>
    The census was written in October 2026, combining public reporting with judgement.
    Saturation claims were cross-checked against 2026 sources, including
    preuve.ai's ranked list of AI startup ideas, a long Hacker News debate on why founders
    avoid novel problems, and the Lemelson Foundation's work on hardware invention for
    underserved markets. Everything else — the crowdedness marks, the difficulty marks, the
    "closest attempt" attributions — is editorial opinion and should be treated as such.
  </p>
  <ul>
    <li><a href="https://preuve.ai/blog/startup-ideas-2026">preuve.ai — AI startup ideas 2026, ranked</a></li>
    <li><a href="https://news.ycombinator.com/item?id=37431950">Hacker News — why most startups don't solve novel problems</a></li>
    <li><a href="https://www.lemelson.org/unlocking-the-potential-of-hardware-based-invention-to-solve-global-development-challenges">Lemelson Foundation — hardware invention for global development</a></li>
  </ul>

  <h2>The shelves, and where they come from</h2>
  <p>
    The Shelves page backs "already built" with real catalogs rather than memory:
    Flathub and F-Droid in full from their open metadata dumps, the Apple App Store through
    its official Search API, popular npm packages through the registry API, Steam's games
    catalog, and — for hardware — iFixit's complete device-repair tree, openFDA's regulated
    medical-device database, Arduino's embedded-library registry and Open Food Facts'
    product database. Google Play contributes capped, popularity-ranked searches: Play has
    no bulk API, and scraping all of it would violate its terms, so the pipeline stops at
    capped results. The raw snapshots live in <code>data/raw/</code>, the full merged
    catalog in <code>data/catalog.db</code>, and the site ships a capped index at
    <code>assets/catalog.json</code>. Rerun <code>pipeline/ingest.py</code> and
    <code>pipeline/build_site_index.py</code> to refresh it — the census of ideas is
    editorial, but the shelves are measured.
  </p>

  <h2>Limits, stated plainly</h2>
  <p>
    This census goes stale the moment you read it. Someone may have started on a dashed
    card last week; two people may have finished one this morning. Before committing years
    to anything here, search for products, message the makers of the closest attempt, and
    assume the world moved since this was written. Being second with a real difference
    still beats being first into a crowd — but both beat building number four thousand and
    one.
  </p>

  <h2>Colophon</h2>
  <p>
    The whole site is static HTML generated by one Python script, set in Archivo and
    Source Serif 4, with no trackers and no cookies. The generator lives in
    <code>build.py</code>; edit the census data there and rebuild.
  </p>
</section>"""
    return page(
        "About — Unbuilt",
        "What the Unbuilt census is, how it was compiled, what the columns mean, and where it will be wrong.",
        "", "About", main)


# ---------------------------------------------------------------- 404
def build_404():
    main = """<section class="hero slim">
  <div class="wrap">
    <h1>This shelf is empty.</h1>
    <p class="lede">The page you asked for isn't in the census. The census itself, however, is full of empty shelves.</p>
    <div class="actions">
      <a class="btn" href="index.html">Back to the census</a>
      <a class="btn ghost" href="fields.html">Browse the fields</a>
    </div>
  </div>
</section>"""
    return page(
        "Page not found — Unbuilt",
        "The page you asked for isn't in the census.",
        "", None, main)


# ---------------------------------------------------------------- assets
STYLE_CSS = """:root{
  --paper:#E9E7DE;
  --card:#F4F2EA;
  --ink:#262A22;
  --built-text:#EDEBE0;
  --built-dim:rgba(237,235,224,.78);
  --muted:#6C7060;
  --line:#C6C4B4;
  --blue:#3A5A94;
  --blue-deep:#2E4C82;
  --red:#A63B24;
  --red-bright:#E4754F;
  --footer-text:#C9C7B8;
  --footer-dim:#95937F;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  background:var(--paper);
  color:var(--ink);
  font-family:"Archivo",system-ui,sans-serif;
  font-size:16px;
  line-height:1.55;
  -webkit-font-smoothing:antialiased;
}
::selection{background:var(--blue);color:var(--paper)}
a{color:inherit}
:focus-visible{outline:3px solid var(--blue);outline-offset:2px}
.visually-hidden{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.skip{
  position:absolute;left:-9999px;top:0;background:var(--ink);color:var(--paper);
  padding:.6rem 1rem;z-index:99;font-weight:600;text-decoration:none;
}
.skip:focus{left:0}
.wrap{max-width:1180px;margin:0 auto;padding:0 clamp(1rem,4vw,2.5rem)}

/* ---------- top bar ---------- */
.site-head{border-bottom:2px solid var(--ink)}
.site-head .wrap{display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap;padding-top:.9rem;padding-bottom:.9rem}
.brand{font-weight:900;font-stretch:118%;font-size:1.25rem;letter-spacing:.01em;text-decoration:none}
.brand small{font-weight:500;font-stretch:100%;color:var(--muted);margin-left:.75rem;font-size:.85rem}
.site-nav{display:flex;gap:1.3rem;flex-wrap:wrap}
.site-nav a{
  font-weight:600;font-size:.95rem;text-decoration:none;color:var(--ink);
  padding-bottom:.1rem;border-bottom:2px solid transparent;
}
.site-nav a:hover{border-bottom-color:var(--ink)}
.site-nav a[aria-current="page"]{border-bottom-color:var(--red)}

/* ---------- hero ---------- */
.hero{padding:clamp(3rem,8vw,5.5rem) 0 clamp(2rem,5vw,3.5rem)}
.hero.slim{padding-top:clamp(2.2rem,5vw,3.4rem)}
.hero h1{
  font-weight:900;font-stretch:120%;
  font-size:clamp(2.4rem,6.2vw,4.4rem);
  line-height:1.02;letter-spacing:-.015em;
  max-width:16ch;
}
.hero.slim h1{font-size:clamp(2rem,4.5vw,3.2rem)}
.lede{
  margin-top:1.4rem;max-width:62ch;font-size:clamp(1rem,1.6vw,1.15rem);color:var(--ink);
}
.lede em{font-family:"Source Serif 4",Georgia,serif;font-style:italic}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border:1px solid var(--line);margin-top:2.4rem}
.stat{background:var(--paper);padding:.9rem 1.1rem .8rem}
.stat b{display:block;font-size:clamp(1.7rem,3vw,2.3rem);font-weight:900;font-stretch:112%;font-variant-numeric:tabular-nums;line-height:1.1}
.stat span{font-size:.82rem;color:var(--muted)}
.actions{margin-top:1.8rem;display:flex;gap:.8rem;flex-wrap:wrap}
.btn{
  display:inline-block;font:inherit;font-weight:700;font-size:.95rem;
  padding:.75rem 1.4rem;border:2px solid var(--ink);cursor:pointer;
  background:var(--ink);color:var(--paper);text-decoration:none;
}
.btn:hover{background:var(--blue-deep);border-color:var(--blue-deep)}
.btn.ghost{background:transparent;color:var(--ink)}
.btn.ghost:hover{background:var(--ink);color:var(--paper)}

/* ---------- census strip ---------- */
.census{margin:2.6rem 0 0;border-top:2px solid var(--ink);border-bottom:2px solid var(--ink);padding:1.1rem 0 1.3rem}
.census-head{display:flex;justify-content:space-between;align-items:baseline;gap:1rem;flex-wrap:wrap;margin-bottom:.8rem}
.census-head h2{font-size:1rem;font-weight:800;font-stretch:110%}
.legend{display:flex;gap:1.4rem;font-size:.82rem;color:var(--muted)}
.legend i{display:inline-block;width:.8em;height:.8em;margin-right:.45em;vertical-align:baseline}
.legend .k-built i{background:var(--ink)}
.legend .k-half i{background:linear-gradient(90deg,var(--ink) 50%,transparent 50%);border:1.5px solid var(--ink)}
.legend .k-unbuilt i{border:1.5px dashed var(--blue)}
.strip{display:grid;grid-template-columns:repeat(auto-fill,minmax(15px,1fr));gap:4px}
.cell{
  aspect-ratio:1;width:100%;min-width:0;display:block;
  background:var(--ink);transition:transform .12s ease;
}
.cell.u{background:transparent;border:1.5px dashed var(--blue)}
.cell.h{background:linear-gradient(90deg,var(--ink) 50%,transparent 50%)}
.cell:hover,.cell:focus-visible{transform:scale(1.5);position:relative;z-index:2}
.census figcaption{margin-top:.7rem;font-size:.8rem;color:var(--muted)}

/* ---------- home sections ---------- */
.sec{margin-top:clamp(2.5rem,6vw,4rem)}
.sec > .wrap > h2, .sec > h2{font-weight:900;font-stretch:115%;font-size:clamp(1.4rem,2.6vw,1.9rem);border-top:2px solid var(--ink);padding-top:1rem}
.sec .sub{color:var(--muted);margin-top:.5rem;max-width:60ch}
.howto{margin:1.4rem 0 0 1.3rem;display:grid;gap:.55rem;max-width:64ch}
.howto-more{margin-top:1.2rem;color:var(--muted);font-size:.95rem}
.howto-more a{color:var(--ink)}

/* ---------- picks & tiles ---------- */
.picks{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:1.6rem}
.pick{margin-bottom:0}
.pick-field{font-size:.75rem;font-weight:700;color:var(--blue-deep);margin-bottom:.4rem}
.pick .more{
  display:inline-block;margin-top:.7rem;font-size:.85rem;font-weight:700;
  color:var(--ink);text-decoration:underline;text-underline-offset:3px;
}
.pick .more:hover{color:var(--blue-deep)}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:1.6rem}
.tile{
  display:block;background:var(--card);border:1px solid var(--line);
  padding:1.1rem 1.2rem 1.2rem;text-decoration:none;transition:border-color .15s ease;
}
.tile:hover{border-color:var(--ink)}
.tile h3{font-size:1.05rem;font-weight:800;line-height:1.25}
.tile .counts{font-size:.8rem;color:var(--muted);margin-top:.35rem}
.tile .t-note{
  font-family:"Source Serif 4",Georgia,serif;font-style:italic;
  font-size:.9rem;color:var(--muted);margin-top:.55rem;
}

/* ---------- search page ---------- */
.toolbar-page{display:flex;gap:.9rem;align-items:baseline;flex-wrap:wrap;margin-top:1.8rem}
.toolbar-page input{
  flex:1 1 320px;min-width:0;font:inherit;font-size:1rem;padding:.65rem .9rem;
  border:1.5px solid var(--ink);background:var(--card);color:var(--ink);
}
.toolbar-page input::placeholder{color:var(--muted)}
.shown{font-size:.85rem;color:var(--muted);white-space:nowrap}
.results{margin-top:1.4rem;border-top:2px solid var(--ink);min-height:6rem}
.result{
  display:grid;grid-template-columns:auto 1fr auto;gap:.15rem .8rem;
  padding:.95rem .2rem;border-bottom:1px solid var(--line);
  text-decoration:none;color:var(--ink);
}
.result:hover{background:var(--card)}
.r-side{grid-row:1/3;font-size:.7rem;font-weight:700;padding:.18rem .5rem;border:1.5px solid currentColor;align-self:start;white-space:nowrap}
.r-side.b{color:var(--red)}
.r-side.h{color:var(--ink)}
.r-side.u{color:var(--blue-deep)}
.result .src{color:var(--ink)}
.shelves-status{margin-top:1.6rem;color:var(--muted);font-size:.9rem;min-height:1.3em}
.srcchips{display:flex;flex-wrap:wrap;gap:.4rem;margin-top:.6rem}
.chip{
  font:inherit;font-size:.78rem;font-weight:600;color:var(--muted);
  background:var(--card);border:1px solid var(--line);padding:.15rem .6rem;cursor:pointer;
}
.chip:hover{border-color:var(--ink);color:var(--ink)}
.chip.on{color:var(--ink);border-color:var(--ink);font-weight:700}
.r-title{font-weight:800}
.r-field{font-size:.78rem;color:var(--muted)}
.r-what{grid-column:2/4;font-size:.9rem;color:#454B3C;max-width:75ch}
.shown-more{padding:1rem .2rem;color:var(--muted);font-size:.85rem}

/* ---------- breadcrumb & pager ---------- */
.crumb{font-size:.82rem;color:var(--muted);padding-top:1.4rem}
.crumb a{color:var(--muted);text-decoration:none}
.crumb a:hover{color:var(--ink);text-decoration:underline}
.crumb .sep{margin:0 .45rem}
.crumb [aria-current]{color:var(--ink)}
.pager{
  display:flex;justify-content:space-between;align-items:baseline;gap:1rem;flex-wrap:wrap;
  border-top:2px solid var(--ink);margin-top:clamp(2.5rem,6vw,4rem);padding:1.2rem 0 0;
}
.pager a{text-decoration:none}
.pager .dir{display:block;font-size:.75rem;color:var(--muted)}
.pager .name{font-weight:800;font-stretch:108%}
.pager a:hover .name{color:var(--blue-deep)}
.pager .next{text-align:right;margin-left:auto}
.pager .all{font-size:.85rem;font-weight:700;color:var(--muted);text-decoration:underline;text-underline-offset:3px}
.pager .all:hover{color:var(--ink)}

/* ---------- field pages ---------- */
.page-head{display:flex;justify-content:space-between;align-items:baseline;gap:1.5rem;flex-wrap:wrap;margin-top:1.2rem}
.page-head h1{font-weight:900;font-stretch:115%;font-size:clamp(1.9rem,4vw,2.8rem);line-height:1.05;letter-spacing:-.01em}
.page-head .note{
  font-family:"Source Serif 4",Georgia,serif;font-style:italic;font-size:1.02rem;
  color:var(--muted);max-width:44ch;text-align:right;
}
.cols{display:grid;grid-template-columns:1fr 1fr 1fr;margin-top:1.6rem}
.cols > .col + .col{border-left:1px solid var(--line);padding-left:clamp(1.1rem,2.5vw,2.2rem)}
.col-built{padding-right:clamp(1.1rem,2.5vw,2.2rem)}
.col-head{
  display:flex;align-items:baseline;gap:.6rem;margin-bottom:1.1rem;
  font-weight:800;font-size:1rem;font-stretch:108%;
}
.col-head .count{
  font-weight:600;font-size:.78rem;color:var(--muted);border:1px solid var(--line);
  padding:.05rem .45rem;
}
.swatch{width:.85em;height:.85em;align-self:center;flex:none}
.col-built .swatch{background:var(--ink)}
.swatch.half{background:linear-gradient(90deg,var(--ink) 50%,transparent 50%);border:1.5px solid var(--ink)}
.col-unbuilt .swatch{border:1.5px dashed var(--blue)}

/* ---------- cards ---------- */
.card{padding:1.1rem 1.2rem 1.15rem;margin-bottom:1rem}
.card h3{font-size:1.06rem;font-weight:800;letter-spacing:-.005em;line-height:1.25}
.card .what{margin-top:.35rem;font-size:.92rem}
.card.built{background:var(--ink);color:var(--built-text)}
.card.built .what{color:var(--built-dim)}
.card.built .verdict{margin-top:.55rem;font-size:.9rem;color:var(--red-bright)}
.card.unbuilt{background:var(--card);border:1.5px dashed var(--blue)}
.card.unbuilt .what{color:var(--ink)}
.card.unbuilt .why{
  margin-top:.55rem;font-family:"Source Serif 4",Georgia,serif;font-style:italic;
  font-size:.95rem;color:#454B3C;
}
.card.unbuilt .why::before{
  content:"Why it is still open: ";
  font-family:"Archivo",system-ui,sans-serif;font-style:normal;font-weight:700;
  font-size:.78rem;color:var(--blue-deep);
}
.card.unbuilt .closest{margin-top:.45rem;font-size:.83rem;color:var(--muted)}
.card.unbuilt .closest::before{
  content:"Closest attempt: ";font-weight:700;color:var(--ink);
}
.card.half{background:var(--card);border:1.5px solid var(--ink)}
.card.half .what{color:var(--ink)}
.card.half .missing{margin-top:.55rem;font-size:.92rem}
.card.half .missing::before{content:"What is missing: ";font-weight:700}
.card.half .why{
  margin-top:.45rem;font-family:"Source Serif 4",Georgia,serif;font-style:italic;
  font-size:.95rem;color:#454B3C;
}
.card.half .why::before{
  content:"Why it stalled: ";
  font-family:"Archivo",system-ui,sans-serif;font-style:normal;font-weight:700;
  font-size:.78rem;color:var(--muted);
}
.card.half .meter{color:var(--ink)}
.meter{margin-top:.7rem;display:flex;align-items:center;gap:.6rem;font-size:.76rem}
.meter .squares{display:inline-flex;gap:3px}
.sq{width:10px;height:10px;border:1.5px solid currentColor;display:inline-block}
.sq.on{background:currentColor}
.card.built .meter{color:var(--built-dim)}
.card.unbuilt .meter{color:var(--blue-deep)}
.tags{display:flex;flex-wrap:wrap;gap:.4rem;margin-top:.7rem}
.tag{
  font-size:.72rem;font-weight:600;letter-spacing:.02em;color:var(--blue-deep);
  border:1px solid var(--blue);padding:.1rem .5rem;
}
.card:target{animation:flash 1.1s ease 2}
@keyframes flash{
  0%,100%{box-shadow:none}
  50%{box-shadow:0 0 0 4px var(--blue)}
}

/* ---------- prose (about) ---------- */
.prose{padding-bottom:1rem;max-width:none}
.prose > *{max-width:70ch}
.prose h2{font-weight:900;font-stretch:112%;font-size:1.3rem;margin-top:2.4rem;padding-top:0;border:0}
.prose p{margin-top:1rem}
.prose ul{margin:1rem 0 0 1.3rem;display:grid;gap:.45rem}
.prose code{font-size:.9em;background:var(--card);border:1px solid var(--line);padding:.05rem .35rem}

/* ---------- footer ---------- */
footer{margin-top:clamp(3rem,7vw,5rem);background:var(--ink);color:var(--footer-text)}
.foot-grid{display:grid;grid-template-columns:1.2fr .8fr 1.6fr;gap:2.5rem;padding-top:clamp(2.5rem,6vw,4rem);padding-bottom:2.5rem}
footer h2{color:var(--built-text);font-size:.95rem;font-weight:800;font-stretch:110%;margin-bottom:.8rem}
footer p{font-size:.92rem;max-width:44ch}
.brand-f{font-weight:900;font-stretch:118%;font-size:1.2rem;color:var(--built-text);margin-bottom:.6rem}
.foot-nav{display:grid;gap:.4rem}
.foot-nav a, .foot-fields a{
  color:var(--footer-text);text-decoration:none;font-size:.9rem;
}
.foot-nav a:hover, .foot-fields a:hover{color:var(--red-bright);text-decoration:underline}
.foot-fields{display:flex;flex-wrap:wrap;gap:.4rem .9rem}
.colophon{border-top:1px solid #4A4E42}
.colophon .wrap{padding-top:1.2rem;padding-bottom:1.6rem;font-size:.8rem;color:var(--footer-dim)}

/* ---------- responsive ---------- */
@media (max-width:880px){
  .cols{grid-template-columns:1fr}
  .cols > .col + .col{border-left:none;padding-left:0;margin-top:2rem}
  .col-built{padding-right:0}
  .page-head .note{text-align:left}
  .stats{grid-template-columns:repeat(2,1fr)}
  .picks,.tiles{grid-template-columns:1fr}
  .foot-grid{grid-template-columns:1fr;gap:1.8rem}
}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  .cell{transition:none}
  .card:target{animation:none;outline:3px solid var(--blue);outline-offset:2px}
}
"""

APP_JS = """(function () {
  "use strict";

  /* "Pull a random gap" links navigate to a random not-built idea */
  document.querySelectorAll("[data-random-gap]").forEach(function (el) {
    el.addEventListener("click", function (e) {
      var C = window.CENSUS;
      if (!C) return;
      var pool = [];
      C.fields.forEach(function (f) {
        for (var i = 0; i < f.unbuilt.length; i++) pool.push(f.id + "|" + i);
      });
      if (!pool.length) return;
      e.preventDefault();
      var pick = pool[Math.floor(Math.random() * pool.length)].split("|");
      window.location.href = "fields/" + pick[0] + ".html#c-" + pick[0] + "-u" + pick[1];
    });
  });

  /* Search page */
  var input = document.getElementById("q");
  var list = document.getElementById("results");
  var shown = document.getElementById("shown");
  if (!input || !list || !window.CENSUS) return;

  var ITEMS = [];
  CENSUS.fields.forEach(function (f) {
    f.built.forEach(function (b, i) {
      ITEMS.push({ f: f, side: "built", i: i, t: b.t, w: b.w });
    });
    f.half.forEach(function (u, i) {
      ITEMS.push({ f: f, side: "half", i: i, t: u.t, w: u.w, why: u.why });
    });
    f.unbuilt.forEach(function (u, i) {
      ITEMS.push({ f: f, side: "unbuilt", i: i, t: u.t, w: u.w, why: u.why });
    });
  });

  var SIDE_LABEL = { built: "crowded", half: "half-built", unbuilt: "not built" };
  var SIDE_CODE = { built: "b", half: "h", unbuilt: "u" };

  function render() {
    var qy = input.value.trim().toLowerCase();
    var hits = ITEMS.filter(function (it) {
      if (!qy) return true;
      return (it.f.name + " " + it.t + " " + it.w + " " + (it.why || "")).toLowerCase().indexOf(qy) !== -1;
    });
    shown.textContent = hits.length + " of " + ITEMS.length + " ideas";
    list.innerHTML = "";
    if (!hits.length) {
      var empty = document.createElement("p");
      empty.className = "shown-more";
      empty.textContent = "Nothing matches — which might itself be a good sign.";
      list.appendChild(empty);
      return;
    }
    hits.slice(0, 60).forEach(function (it) {
      var a = document.createElement("a");
      a.className = "result";
      a.href = "fields/" + it.f.id + ".html#c-" + it.f.id + "-" + SIDE_CODE[it.side] + it.i;
      var side = document.createElement("span");
      side.className = "r-side " + SIDE_CODE[it.side];
      side.textContent = SIDE_LABEL[it.side];
      var title = document.createElement("span");
      title.className = "r-title";
      title.textContent = it.t;
      var fld = document.createElement("span");
      fld.className = "r-field";
      fld.textContent = it.f.name;
      var what = document.createElement("span");
      what.className = "r-what";
      what.textContent = it.w;
      a.appendChild(side); a.appendChild(title); a.appendChild(fld); a.appendChild(what);
      list.appendChild(a);
    });
    if (hits.length > 60) {
      var more = document.createElement("p");
      more.className = "shown-more";
      more.textContent = "First 60 shown — refine the search to narrow further.";
      list.appendChild(more);
    }
  }
  input.addEventListener("input", render);
  render();
})();
"""

SHELVES_JS = """(function () {
  "use strict";
  var DISPLAY = {flathub: "Flathub", fdroid: "F-Droid", itunes: "App Store", play: "Google Play",
    npm: "npm", ifixit: "iFixit", fda: "FDA devices", arduino: "Arduino",
    steam: "Steam", off: "Open Food Facts"};
  var input = document.getElementById("q");
  var list = document.getElementById("results");
  var shown = document.getElementById("shown");
  var status = document.getElementById("loadstate");
  var chips = document.getElementById("srcchips");
  var CAT = null, INDEX = null, active = {}, timer = null;

  fetch("assets/catalog.json").then(function (r) {
    if (!r.ok) throw new Error("HTTP " + r.status);
    return r.json();
  }).then(function (c) {
    CAT = c;
    INDEX = c.apps.map(function (a) {
      return [a[0].toLowerCase(), (a[0] + " " + a[1] + " " + a[3] + " " + a[5]).toLowerCase(), a];
    });
    var keys = Object.keys(CAT.sources).sort(function (a, b) {
      return CAT.sources[b] - CAT.sources[a];
    });
    keys.forEach(function (k) {
      active[k] = true;
      var b = document.createElement("button");
      b.type = "button";
      b.className = "chip on";
      b.setAttribute("aria-pressed", "true");
      b.textContent = (DISPLAY[k] || k) + " " + CAT.sources[k].toLocaleString();
      b.addEventListener("click", function () {
        active[k] = !active[k];
        b.classList.toggle("on", active[k]);
        b.setAttribute("aria-pressed", String(!!active[k]));
        render();
      });
      chips.appendChild(b);
    });
    status.textContent = CAT.count.toLocaleString() + " apps, devices and products on the " +
      "shelves, collected " + CAT.generated + " from " + keys.length + " catalogs";
    input.disabled = false;
    render();
  }).catch(function () {
    status.textContent = "The catalog could not be loaded. Build it with pipeline/ingest.py and " +
      "pipeline/build_site_index.py, then serve this folder over HTTP.";
  });

  function render() {
    if (!CAT) return;
    var qy = input.value.trim().toLowerCase();
    var hits = [];
    if (qy.length >= 2) {
      for (var i = 0; i < INDEX.length; i++) {
        var it = INDEX[i];
        if (!active[it[2][2]]) continue;
        var s = 0;
        if (it[0].indexOf(qy) === 0) s = 4;
        else if (it[0].indexOf(qy) !== -1) s = 3;
        else if (it[1].indexOf(qy) !== -1) s = 1;
        if (s) hits.push([s, it[2]]);
      }
      hits.sort(function (a, b) { return b[0] - a[0] || a[1][0].length - b[1][0].length; });
      shown.textContent = hits.length.toLocaleString() + " of " + CAT.count.toLocaleString() + " entries";
    } else {
      shown.textContent = CAT.count.toLocaleString() + " entries";
    }
    list.innerHTML = "";
    if (qy.length < 2) {
      var hint = document.createElement("p");
      hint.className = "shown-more";
      hint.textContent = "Type at least two letters — app names, device models, categories, makers. " +
        "This is the evidence shelf for what already exists, not opinion.";
      list.appendChild(hint);
      return;
    }
    if (!hits.length) {
      var empty = document.createElement("p");
      empty.className = "shown-more";
      empty.textContent = "No listing matches. It may live outside these catalogs — " +
        "or it may genuinely not exist yet, which is what the dashed columns are for.";
      list.appendChild(empty);
      return;
    }
    hits.slice(0, 50).forEach(function (pair) {
      var a0 = pair[1];
      var a = document.createElement("a");
      a.className = "result";
      if (a0[4]) { a.href = a0[4]; a.target = "_blank"; a.rel = "noopener"; }
      var src = document.createElement("span");
      src.className = "r-side src";
      src.textContent = DISPLAY[a0[2]] || a0[2];
      var title = document.createElement("span");
      title.className = "r-title";
      title.textContent = a0[0];
      var fld = document.createElement("span");
      fld.className = "r-field";
      fld.textContent = a0[3];
      var what = document.createElement("span");
      what.className = "r-what";
      what.textContent = a0[1] + (a0[5] ? " (" + a0[5] + ")" : "");
      a.appendChild(src); a.appendChild(title); a.appendChild(fld); a.appendChild(what);
      list.appendChild(a);
    });
    if (hits.length > 50) {
      var more = document.createElement("p");
      more.className = "shown-more";
      more.textContent = "First 50 shown — narrow the search to see the rest.";
      list.appendChild(more);
    }
  }
  input.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(render, 150);
  });
})();
"""


def census_js():
    fields = []
    for f in FIELDS:
        fields.append({
            "id": f["id"],
            "name": f["name"],
            "built": [{"t": b[0], "w": b[1]} for b in f["built"]],
            "half": [{"t": u["t"], "w": u["w"], "why": u["why"]} for u in HALF[f["id"]]],
            "unbuilt": [{"t": u["t"], "w": u["w"], "why": u["why"]} for u in f["unbuilt"]],
        })
    import json
    return "window.CENSUS = " + json.dumps({"fields": fields}, ensure_ascii=False) + ";\n"


def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True) if os.path.dirname(path) else None
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"  wrote {path}")


def main():
    os.makedirs(os.path.join(OUT, "fields"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    print("Building Unbuilt:")
    write("index.html", build_home())
    write("fields.html", build_fields_index())
    write("search.html", build_search())
    write("shelves.html", build_shelves())
    write("about.html", build_about())
    write("404.html", build_404())
    for i, f in enumerate(FIELDS):
        write(f"fields/{f['id']}.html", build_field_page(i))
    write("assets/style.css", STYLE_CSS)
    write("assets/app.js", APP_JS)
    write("assets/census.js", census_js())
    print(f"Done: {TOTAL} ideas, {TOTAL_BUILT} built, {TOTAL_HALF} half-built, {TOTAL_UNBUILT} unbuilt, {len(FIELDS)} fields.")


if __name__ == "__main__":
    main()
