# Changelog

**Author:** Christos Bouronikos  
**Email:** chrisbouronikos@gmail.com  
**GitHub:** https://github.com/ChristosBouronikos  
**Donations:** [PayPal](https://paypal.me/christosbouronikos)

---

**Language:** [English](#english) | [Ελληνικά](#ελληνικά)

---

# English

## [1.3.0] - 2026-07-22

### Added
- English/Greek coverage for the complete existing inventory (at least 116 buttons, 22 columns, 18 panes, all 11 managers and all 11 tabs), plus ATLAS.ti 26 manager segment panes and filters, context-menu commands, Welcome screen controls, Quotation Reader controls, and import/search/query/report/confirmation dialog controls
- Self-contained English/Greek role labels for add-on-generated speech: buttons, menu items, check boxes, radio buttons and columns are identified by control type as well as name (for example, `Κουμπί Αποθήκευση Έργου`, `Στήλη Έναρξη`, and `Καρτέλα Αρχική`)
- Five dialog-specific NVDA overlays for import, search, query, report and confirmation pop-ups
- Disabled-by-default privacy-filtered UI-tree capture command (NVDA+Ctrl+Alt+Shift+U) for gathering real ATLAS.ti 26 control names, roles, automation IDs and window classes on Windows; list/table/tree/editable/document branches and their descendants are pruned to exclude research content
- Documentation-derived semantic UI tree for official manual 26.1.1+34607 and a generated JSON catalogue containing every English/Greek label, expected role, aliases, contexts, identifiers and source pages
- Capture reconciliation tool that reports unknown controls, role mismatches, changed AutomationIds, duplicate observations and documented controls not yet seen; release audit tool for translations, references and collision safety
- Manager, manager-filter, manager-context-menu, Welcome screen and Quotation Reader overlay families in addition to the five dialog-specific overlays
- English/Greek announcements for checked, partially checked, selected, expanded, collapsed, unavailable and pressed states, plus a configurable translated-state setting
- Keyboard-focus recovery that tries the first enabled interactive descendant before moving only NVDA's navigator object
- Privacy regression corpus and complete Windows ATLAS.ti 26 validation checklist
- "Describe the current chart or diagram" command (NVDA+Ctrl+Alt+Shift+V): finds the nearest chart/diagram/visual-only view at or above focus, first tries to read any real accessible content Atlas.ti exposes for it (some diagramming controls do register per-shape UI Automation elements), and only falls back to an explanation of what the visual normally shows plus a pointer to its accessible alternative when Atlas.ti truly exposes nothing
- "Jump to the accessible data view of the current chart" command (NVDA+Ctrl+Alt+Shift+J): moves focus straight to the nearest table/list equivalent of the current chart (e.g. Word Cloud → Word List, Code Co-Occurrence Explorer → Code Co-Occurrence Table, Network Editor → Link Manager)
- View-mode warnings: jumping to the Code Manager or Document Manager while it is showing a Cloud, Bar chart or Treemap view (instead of the normal, fully accessible List view) now says so immediately, in English or Greek, instead of leaving the researcher to discover an apparently empty manager on their own
- `visualOnly`/`companion`/`concept` metadata added to `_atlastiUI.py` for every chart-like element (Network Editor, Diagram pane, Word Cloud, Sankey diagram, Treemap, Bar chart, Code Co-Occurrence Explorer, and the Cloud/Bar chart/Treemap view-mode toggles), each with an English and Greek description of what it normally shows
- Data-integrity tests ensuring every `companion` reference points at a real element and every visual-only element has a concept description, plus behavioural tests for content-found vs. content-absent chart reading, the data-view jump, and view-mode warnings

### Changed
- UI resolution is now role- and container-aware, allowing repeated labels such as Comment, Color, Preview and Project Search to resolve to the correct control in each manager or dialog
- Reading commands and the shortcut list document that Atlas.ti's rendered charts and diagrams (Network Editor, Sankey diagrams, Treemaps, Word Cloud, the Code Manager's Cloud/Bar-chart views) are graphics without per-element accessible content in Atlas.ti today, and point to the nearest accessible table or list wherever one exists, rather than staying silent about the gap

### Fixed
- The `Start` manager column no longer collides with the German `Start` label for the Home tab; row reading now resolves and announces it explicitly as `Column Start` / `Στήλη Έναρξη`
- Automatic Greek control translation now applies only to genuine controls with exact known labels or identifiers, so project content containing words such as "codes" or "documents" is never replaced with a generic translated UI label
- Executable variants now use NVDA's supported `registerExecutableWithAppModule` API, are unregistered cleanly when the global plugin unloads, and include underscore-form alias modules for dotted executable names such as `atlas.ti26`

---

## [1.2.0] - 2026-07-22

### Added
- Full-coverage recognition of Atlas.ti's interface: all six ribbon tabs, all entity managers (Documents, Quotations, Codes, Memos, Networks, Links, Relations, plus their group managers), the Quotation Reader, Network Editor, Query Tool, coding dialogue, Welcome screen, Options dialog and Project Search window, the Project Navigator and per-entity browsers, the margin area, working area, comment/preview pane, status bar, side panel, ribbon and Quick Access toolbar, well over a hundred ribbon buttons and commands across every tab, list columns (ID, Name, Grounded, Density, Created by, etc.), view options, and query operators (AND/OR/ONE OF/NOT/WITHIN/ENCLOSING/OVERLAPPING/CO-OCCUR/FOLLOWS) — sourced from the official Atlas.ti Windows user manual (v22–v26)
- Recognition of Atlas.ti's own interface labels in every language Atlas.ti ships in (English, German, Spanish, Portuguese, Simplified Chinese) via `_atlastiUI.py`, a pure, NVDA-free knowledge base module with its own test suite
- Bilingual English/Greek announcements for every recognised control, independent of Atlas.ti's own display language, since Atlas.ti has no Greek interface of its own
- New panel navigation commands: Network Manager, Link Manager, ribbon, margin area, working area, comment pane, side panel, plus next/previous panel cycling
- New reading commands: describe the focused control in detail (name, role, value, containing panel, hint, Atlas.ti shortcut), read every column of the current row with headers, report item count and status bar, list every control on the current ribbon tab, read the margin area, read the comment/preview pane
- Built-in bilingual glossary of Atlas.ti terms (NVDA+Ctrl+Alt+Shift+G), browsable in an NVDA window
- Speech language toggle (NVDA+Ctrl+Alt+Shift+L) cycling between "follow NVDA", English and Greek
- Diagnostics command (NVDA+Ctrl+Alt+Shift+I) that logs structural information about the focused control without ever logging research data
- NVDA Settings panel ("Atlas.ti" category) to configure speech language, bilingual labels, automatic translation, button labelling, and panel/ribbon change announcements without editing any file
- Alias app module for Atlas.ti 26 (`atlasti26.py`)

### Changed
- Unicode-aware text normalisation: matching now folds case, accents and the Greek final sigma instead of stripping every non-ASCII character, so Greek and other non-English text is no longer reduced to an empty string during matching (this was silently breaking recognition of any Greek-only label in 1.1.0)
- Panel navigation now verifies that focus actually moved before announcing success; when a panel refuses focus, NVDA's navigator object is moved there instead and the announcement says so explicitly, rather than always claiming success
- "Read code" and "read quotation" now check that focus is genuinely inside the relevant manager before speaking, and say so plainly when it is not, instead of describing an unrelated focused control as if it were a code or quotation
- Reading commands renamed and reworded to describe what they actually do
- Manager matching prefers automation IDs and window class names (language-independent) before falling back to display names, so a button whose name happens to mention a manager can no longer be matched ahead of the manager itself
- `README.md`/`CHANGELOG.md` are now copied into the packaged docs with the correct case, fixing a build that silently failed to update bundled documentation on case-sensitive (Linux) build environments while appearing to work on macOS/Windows
- Bumped `lastTestedNVDAVersion` and Atlas.ti compatibility range to include Atlas.ti 26

### Fixed
- Greek panel/control names could never be matched during recognition because the previous normaliser stripped all non-ASCII characters to an empty string
- Navigation and reading commands could report success or describe content without verifying it was true

---

## [1.1.0] - 2026-02-01

### Added
- Compatibility aliases for common Atlas.ti executable names
- More robust panel detection with normalized UIA matching and caching
- Safer default shortcuts to reduce conflicts

### Changed
- Panel navigation shortcuts now use NVDA+Ctrl+Alt+...
- Reading shortcuts now use NVDA+Ctrl+Alt+Shift+...
- Bumped `lastTestedNVDAVersion` to 2026.1.1 (NVDA 2026.1 reset add-on API compatibility; the previous 2025.3.0 value marked this add-on incompatible and hidden by default in the Add-on Store)

### Fixed
- Panel navigation cache is now cleared on foreground window change, so a stale cached panel reference from a previous Atlas.ti window/project can no longer be reused

---

## [1.0.0] - 2026-01-31

### Added
- Initial release
- Panel navigation shortcuts (NVDA+Alt+D/C/Q/M/P)
- Reading helpers (NVDA+Shift+C/Q/D/P/H)
- Improved control labeling for unlabeled buttons
- Greek and English localization
- User documentation in both languages

### Features
- Jump to Documents panel (NVDA+Alt+D)
- Jump to Codes panel (NVDA+Alt+C)
- Jump to Quotations panel (NVDA+Alt+Q)
- Jump to Memos panel (NVDA+Alt+M)
- Jump to Project Navigator (NVDA+Alt+P)
- Read code details (NVDA+Shift+C)
- Read quotation text (NVDA+Shift+Q)
- Read document info (NVDA+Shift+D)
- Announce current panel (NVDA+Shift+P)
- List all shortcuts (NVDA+Shift+H)

---

## Future Plans

- Quotation navigation (next/previous quotation keys)
- Code hierarchy navigation in the Code Manager tree
- Quick coding mode
- Audio feedback (earcons)
- Live NVDA + Atlas.ti integration testing across all supported versions and interface languages

---

# Ελληνικά

## [1.3.0] - 2026-07-22

### Προστέθηκαν
- Πλήρης αγγλική/ελληνική κάλυψη για το σύνολο του υπάρχοντος καταλόγου στοιχείων (τουλάχιστον 116 κουμπιά, 22 στήλες, 18 πλαίσια, όλοι οι 11 διαχειριστές και όλες οι 11 καρτέλες), καθώς και τα τμηματοποιημένα πλαίσια και φίλτρα διαχειριστών του ATLAS.ti 26, εντολές μενού περιβάλλοντος, στοιχεία της οθόνης υποδοχής, στοιχεία του Αναγνώστη Αποσπασμάτων, και στοιχεία παραθύρων διαλόγου εισαγωγής/αναζήτησης/ερωτήματος/αναφοράς/επιβεβαίωσης
- Αυτοτελείς αγγλικές/ελληνικές ετικέτες ρόλου για την ομιλία που παράγει το πρόσθετο: κουμπιά, στοιχεία μενού, πλαίσια ελέγχου, κουμπιά επιλογής και στήλες αναγνωρίζονται τόσο από τον τύπο ελέγχου όσο και από το όνομά τους (για παράδειγμα, `Κουμπί Αποθήκευση Έργου`, `Στήλη Έναρξη`, και `Καρτέλα Αρχική`)
- Πέντε εξειδικευμένες επικαλύψεις NVDA για παράθυρα διαλόγου εισαγωγής, αναζήτησης, ερωτήματος, αναφοράς και επιβεβαίωσης
- Απενεργοποιημένη από προεπιλογή εντολή καταγραφής δέντρου διεπαφής με φίλτρο απορρήτου (NVDA+Ctrl+Alt+Shift+U) για τη συλλογή πραγματικών ονομάτων, ρόλων, αναγνωριστικών αυτοματισμού και κλάσεων παραθύρων στοιχείων ελέγχου του ATLAS.ti 26 σε Windows· οι κλάδοι λιστών/πινάκων/δέντρων/επεξεργάσιμου κειμένου/εγγράφων και οι απόγονοί τους περικόπτονται ώστε να αποκλείεται το ερευνητικό περιεχόμενο
- Σημασιολογικό δέντρο διεπαφής βασισμένο στην τεκμηρίωση, για το επίσημο εγχειρίδιο έκδοσης 26.1.1+34607, και ένας παραγόμενος κατάλογος JSON που περιέχει κάθε αγγλική/ελληνική ετικέτα, αναμενόμενο ρόλο, ψευδώνυμα, πλαίσια, αναγνωριστικά και σελίδες πηγής
- Εργαλείο συμφωνίας καταγραφών που αναφέρει άγνωστα στοιχεία ελέγχου, αναντιστοιχίες ρόλου, αλλαγμένα AutomationId, διπλές παρατηρήσεις και τεκμηριωμένα στοιχεία ελέγχου που δεν έχουν ακόμη παρατηρηθεί· εργαλείο ελέγχου έκδοσης για μεταφράσεις, αναφορές και ασφάλεια συγκρούσεων
- Οικογένειες επικαλύψεων για διαχειριστές, φίλτρα διαχειριστών, μενού περιβάλλοντος διαχειριστών, την οθόνη υποδοχής και τον Αναγνώστη Αποσπασμάτων, επιπλέον των πέντε εξειδικευμένων επικαλύψεων παραθύρων διαλόγου
- Αγγλικές/ελληνικές ανακοινώσεις για τις καταστάσεις επιλεγμένο, μερικώς επιλεγμένο, επισημασμένο, αναπτυγμένο, συμπτυγμένο, μη διαθέσιμο και πατημένο, καθώς και ρυθμιζόμενη επιλογή μεταφρασμένων καταστάσεων
- Ανάκτηση εστίασης πληκτρολογίου που δοκιμάζει πρώτα τον πρώτο ενεργοποιημένο διαδραστικό απόγονο, πριν μετακινήσει μόνο το αντικείμενο πλοήγησης του NVDA
- Σώμα δοκιμών οπισθοδρόμησης απορρήτου και πλήρης λίστα ελέγχου επικύρωσης ATLAS.ti 26 για Windows
- Εντολή «Περιγραφή του τρέχοντος γραφήματος ή διαγράμματος» (NVDA+Ctrl+Alt+Shift+V): εντοπίζει το πλησιέστερο γράφημα/διάγραμμα/προβολή μόνο-οπτικού περιεχομένου στην εστίαση ή πάνω από αυτήν, προσπαθεί πρώτα να διαβάσει οποιοδήποτε πραγματικό προσβάσιμο περιεχόμενο εκθέτει το Atlas.ti για αυτό (ορισμένα στοιχεία ελέγχου διαγραμμάτων καταχωρούν όντως στοιχεία UI Automation ανά σχήμα), και καταφεύγει σε εξήγηση του τι δείχνει κανονικά το οπτικό στοιχείο, μαζί με υπόδειξη της προσβάσιμης εναλλακτικής του, μόνο όταν το Atlas.ti πραγματικά δεν εκθέτει τίποτα
- Εντολή «Μετάβαση στην προσβάσιμη προβολή δεδομένων του τρέχοντος γραφήματος» (NVDA+Ctrl+Alt+Shift+J): μετακινεί την εστίαση απευθείας στο πλησιέστερο ισοδύναμο πίνακα/λίστας του τρέχοντος γραφήματος (π.χ. Νέφος Λέξεων → Λίστα Λέξεων, Εξερευνητής Συνεμφάνισης Κωδικών → Πίνακας Συνεμφάνισης Κωδικών, Επεξεργαστής Δικτύου → Διαχειριστής Συνδέσεων)
- Προειδοποιήσεις λειτουργίας προβολής: η μετάβαση στον Διαχειριστή Κωδικών ή Εγγράφων ενώ βρίσκεται σε προβολή Νέφους, Ραβδογράμματος ή Δενδροχάρτη (αντί για την κανονική, πλήρως προσβάσιμη Προβολή λίστας) το αναφέρει πλέον αμέσως, στα Αγγλικά ή στα Ελληνικά, αντί να αφήνει τον ερευνητή να ανακαλύψει μόνος του έναν φαινομενικά άδειο διαχειριστή
- Προστέθηκαν μεταδεδομένα `visualOnly`/`companion`/`concept` στο `_atlastiUI.py` για κάθε στοιχείο τύπου γραφήματος (Επεξεργαστής Δικτύου, Πλαίσιο διαγράμματος, Νέφος Λέξεων, διάγραμμα Sankey, Δενδροχάρτης, Ραβδόγραμμα, Εξερευνητής Συνεμφάνισης Κωδικών, και οι εναλλαγές προβολής Νέφους/Ραβδογράμματος/Δενδροχάρτη), καθένα με αγγλική και ελληνική περιγραφή του τι δείχνει κανονικά
- Δοκιμές ακεραιότητας δεδομένων που διασφαλίζουν ότι κάθε αναφορά `companion` δείχνει σε πραγματικό στοιχείο και ότι κάθε στοιχείο μόνο-οπτικού περιεχομένου διαθέτει περιγραφή έννοιας, καθώς και δοκιμές συμπεριφοράς για την ανάγνωση γραφήματος με ή χωρίς περιεχόμενο, τη μετάβαση στην προβολή δεδομένων, και τις προειδοποιήσεις λειτουργίας προβολής

### Άλλαξαν
- Η ανάλυση στοιχείων διεπαφής είναι πλέον ευαίσθητη ως προς τον ρόλο και τον περιέκτη, επιτρέποντας σε επαναλαμβανόμενες ετικέτες όπως Σχόλιο, Χρώμα, Προεπισκόπηση και Αναζήτηση Έργου να αντιστοιχίζονται στο σωστό στοιχείο ελέγχου σε κάθε διαχειριστή ή παράθυρο διαλόγου
- Οι εντολές ανάγνωσης και η λίστα συντομεύσεων τεκμηριώνουν ότι τα γραφήματα και διαγράμματα που σχεδιάζει το Atlas.ti (Επεξεργαστής Δικτύου, διαγράμματα Sankey, Δενδροχάρτες, Νέφος Λέξεων, οι προβολές Νέφους/Ραβδογράμματος του Διαχειριστή Κωδικών) είναι σήμερα στο Atlas.ti γραφικά χωρίς προσβάσιμο περιεχόμενο ανά στοιχείο, και υποδεικνύουν τον πλησιέστερο προσβάσιμο πίνακα ή λίστα όπου υπάρχει, αντί να αποσιωπούν το κενό

### Διορθώθηκαν
- Η στήλη διαχειριστή `Start` δεν συγκρούεται πλέον με τη γερμανική ετικέτα `Start` της καρτέλας Αρχική· η ανάγνωση γραμμών πλέον την αναλύει και την ανακοινώνει ρητά ως `Column Start` / `Στήλη Έναρξη`
- Η αυτόματη ελληνική μετάφραση στοιχείων ελέγχου εφαρμόζεται πλέον μόνο σε γνήσια στοιχεία ελέγχου με ακριβώς γνωστές ετικέτες ή αναγνωριστικά, ώστε το περιεχόμενο του έργου που περιέχει λέξεις όπως «codes» ή «documents» να μην αντικαθίσταται ποτέ από μια γενική μεταφρασμένη ετικέτα διεπαφής
- Οι παραλλαγές εκτελέσιμων χρησιμοποιούν πλέον το υποστηριζόμενο API `registerExecutableWithAppModule` του NVDA, καταργούν την καταχώρισή τους καθαρά όταν αποφορτώνεται το γενικό πρόσθετο, και περιλαμβάνουν ψευδώνυμα αρθρώματα με μορφή κάτω παύλας για εκτελέσιμα ονόματα με τελεία, όπως `atlas.ti26`

---

## [1.2.0] - 2026-07-22

### Προστέθηκαν
- Πλήρης αναγνώριση της διεπαφής του Atlas.ti: και οι έξι καρτέλες της κορδέλας, όλοι οι διαχειριστές οντοτήτων (Έγγραφα, Αποσπάσματα, Κωδικοί, Σημειώματα, Δίκτυα, Συνδέσεις, Σχέσεις, καθώς και οι διαχειριστές ομάδων τους), ο Αναγνώστης Αποσπασμάτων, ο Επεξεργαστής Δικτύου, το Εργαλείο Ερωτημάτων, το παράθυρο κωδικοποίησης, η οθόνη υποδοχής, το παράθυρο Επιλογών και το παράθυρο Αναζήτησης Έργου, ο Πλοηγός Έργου και οι περιηγητές ανά οντότητα, η περιοχή περιθωρίου, η περιοχή εργασίας, το πλαίσιο σχολίου/προεπισκόπησης, η γραμμή κατάστασης, το πλαϊνό πλαίσιο, η κορδέλα και η γραμμή γρήγορης πρόσβασης, πάνω από εκατό κουμπιά και εντολές της κορδέλας σε κάθε καρτέλα, στήλες λιστών (ID, Όνομα, Θεμελίωση, Πυκνότητα, Δημιουργήθηκε από, κ.λπ.), επιλογές προβολής, και τελεστές ερωτημάτων (AND/OR/ONE OF/NOT/WITHIN/ENCLOSING/OVERLAPPING/CO-OCCUR/FOLLOWS) — βάσει του επίσημου εγχειριδίου χρήσης Atlas.ti για Windows (εκδόσεις 22–26)
- Αναγνώριση των δικών του ετικετών διεπαφής του Atlas.ti σε κάθε γλώσσα που διαθέτει το Atlas.ti (Αγγλικά, Γερμανικά, Ισπανικά, Πορτογαλικά, Απλοποιημένα Κινεζικά) μέσω του `_atlastiUI.py`, ενός αμιγούς αρθρώματος βάσης γνώσης χωρίς εξάρτηση από το NVDA, με τη δική του σουίτα δοκιμών
- Δίγλωσσες αγγλικές/ελληνικές ανακοινώσεις για κάθε αναγνωρισμένο στοιχείο ελέγχου, ανεξάρτητα από τη γλώσσα εμφάνισης του ίδιου του Atlas.ti, καθώς το Atlas.ti δεν διαθέτει δική του ελληνική διεπαφή
- Νέες εντολές πλοήγησης πινάκων: Διαχειριστής Δικτύων, Διαχειριστής Συνδέσεων, κορδέλα, περιοχή περιθωρίου, περιοχή εργασίας, πλαίσιο σχολίου, πλαϊνό πλαίσιο, καθώς και εναλλαγή στον επόμενο/προηγούμενο πίνακα
- Νέες εντολές ανάγνωσης: λεπτομερής περιγραφή του εστιασμένου στοιχείου ελέγχου (όνομα, ρόλος, τιμή, πίνακας που το περιέχει, υπόδειξη, συντόμευση Atlas.ti), ανάγνωση όλων των στηλών της τρέχουσας γραμμής με τις επικεφαλίδες τους, αναφορά αριθμού στοιχείων και γραμμής κατάστασης, λίστα όλων των στοιχείων της τρέχουσας καρτέλας κορδέλας, ανάγνωση της περιοχής περιθωρίου, ανάγνωση του πλαισίου σχολίου/προεπισκόπησης
- Ενσωματωμένο δίγλωσσο γλωσσάρι όρων Atlas.ti (NVDA+Ctrl+Alt+Shift+G), με δυνατότητα περιήγησης σε παράθυρο του NVDA
- Εναλλαγή γλώσσας ομιλίας (NVDA+Ctrl+Alt+Shift+L) που κυκλώνει μεταξύ «ακολούθηση NVDA», Αγγλικών και Ελληνικών
- Εντολή διαγνωστικών (NVDA+Ctrl+Alt+Shift+I) που καταγράφει διαρθρωτικές πληροφορίες για το εστιασμένο στοιχείο ελέγχου, χωρίς ποτέ να καταγράφει ερευνητικά δεδομένα
- Πίνακας Ρυθμίσεων NVDA (κατηγορία «Atlas.ti») για τη διαμόρφωση της γλώσσας ομιλίας, των δίγλωσσων ετικετών, της αυτόματης μετάφρασης, της ονοματοδοσίας κουμπιών, και των ανακοινώσεων αλλαγής πίνακα/κορδέλας, χωρίς επεξεργασία κανενός αρχείου
- Άρθρωμα ψευδωνύμου εφαρμογής για το Atlas.ti 26 (`atlasti26.py`)

### Άλλαξαν
- Κανονικοποίηση κειμένου με επίγνωση Unicode: η αντιστοίχιση πλέον ενοποιεί πεζά/κεφαλαία, τόνους και το ελληνικό τελικό σίγμα, αντί να αφαιρεί κάθε μη-ASCII χαρακτήρα, ώστε τα ελληνικά και άλλα μη αγγλικά κείμενα να μην ανάγονται πλέον σε κενή συμβολοσειρά κατά την αντιστοίχιση (αυτό υπονόμευε σιωπηλά την αναγνώριση κάθε αμιγώς ελληνικής ετικέτας στην έκδοση 1.1.0)
- Η πλοήγηση πινάκων επαληθεύει πλέον ότι η εστίαση όντως μετακινήθηκε πριν ανακοινώσει επιτυχία· όταν ένας πίνακας αρνείται την εστίαση, το αντικείμενο πλοήγησης του NVDA μετακινείται εκεί αντ' αυτού και η ανακοίνωση το δηλώνει ρητά, αντί να διεκδικεί πάντα επιτυχία
- Οι εντολές «ανάγνωση κωδικού» και «ανάγνωση αποσπάσματος» ελέγχουν πλέον ότι η εστίαση βρίσκεται πράγματι μέσα στον σχετικό διαχειριστή πριν εκφωνήσουν, και το δηλώνουν ξεκάθαρα όταν δεν ισχύει, αντί να περιγράφουν ένα άσχετο εστιασμένο στοιχείο ελέγχου σαν να ήταν κωδικός ή απόσπασμα
- Οι εντολές ανάγνωσης μετονομάστηκαν και επαναδιατυπώθηκαν ώστε να περιγράφουν αυτό που πράγματι κάνουν
- Η αντιστοίχιση διαχειριστών προτιμά τα αναγνωριστικά αυτοματισμού και τα ονόματα κλάσεων παραθύρων (ανεξάρτητα γλώσσας) πριν καταφύγει σε ονόματα εμφάνισης, ώστε ένα κουμπί του οποίου το όνομα τυχαίνει να αναφέρει έναν διαχειριστή να μην μπορεί πλέον να αντιστοιχιστεί πριν από τον ίδιο τον διαχειριστή
- Τα `README.md`/`CHANGELOG.md` αντιγράφονται πλέον στα πακεταρισμένα έγγραφα με το σωστό πεζά/κεφαλαία, διορθώνοντας μια κατασκευή που απέτυχε σιωπηλά να ενημερώσει τα ενσωματωμένα έγγραφα σε περιβάλλοντα κατασκευής με διάκριση πεζών-κεφαλαίων (Linux), ενώ φαινομενικά λειτουργούσε σε macOS/Windows
- Αυξήθηκε το `lastTestedNVDAVersion` και το εύρος συμβατότητας με το Atlas.ti ώστε να περιλαμβάνει το Atlas.ti 26

### Διορθώθηκαν
- Τα ελληνικά ονόματα πινάκων/στοιχείων ελέγχου δεν μπορούσαν ποτέ να αντιστοιχιστούν κατά την αναγνώριση, επειδή ο προηγούμενος κανονικοποιητής αφαιρούσε όλους τους μη-ASCII χαρακτήρες μέχρι να απομείνει κενή συμβολοσειρά
- Οι εντολές πλοήγησης και ανάγνωσης μπορούσαν να αναφέρουν επιτυχία ή να περιγράφουν περιεχόμενο χωρίς να επαληθεύουν ότι ίσχυε

---

## [1.1.0] - 2026-02-01

### Προστέθηκαν
- Ψευδώνυμα συμβατότητας για κοινά ονόματα εκτελέσιμων του Atlas.ti
- Πιο ανθεκτική ανίχνευση πινάκων με κανονικοποιημένη αντιστοίχιση UIA και προσωρινή αποθήκευση
- Ασφαλέστερες προεπιλεγμένες συντομεύσεις για τη μείωση συγκρούσεων

### Άλλαξαν
- Οι συντομεύσεις πλοήγησης πινάκων χρησιμοποιούν πλέον NVDA+Ctrl+Alt+...
- Οι συντομεύσεις ανάγνωσης χρησιμοποιούν πλέον NVDA+Ctrl+Alt+Shift+...
- Αυξήθηκε το `lastTestedNVDAVersion` σε 2026.1.1 (το NVDA 2026.1 επαναφέρει τη συμβατότητα API προσθέτων· η προηγούμενη τιμή 2025.3.0 σήμαινε ότι αυτό το πρόσθετο θεωρούνταν ασύμβατο και κρυβόταν από προεπιλογή στο Κατάστημα Προσθέτων)

### Διορθώθηκαν
- Η προσωρινή μνήμη πλοήγησης πινάκων καθαρίζεται πλέον όταν αλλάζει το παράθυρο πρώτου πλάνου, ώστε μια παρωχημένη αποθηκευμένη αναφορά πίνακα από προηγούμενο παράθυρο/έργο του Atlas.ti να μην μπορεί πλέον να επαναχρησιμοποιηθεί

---

## [1.0.0] - 2026-01-31

### Προστέθηκαν
- Αρχική έκδοση
- Συντομεύσεις πλοήγησης πινάκων (NVDA+Alt+D/C/Q/M/P)
- Βοηθοί ανάγνωσης (NVDA+Shift+C/Q/D/P/H)
- Βελτιωμένη ονοματοδοσία στοιχείων ελέγχου για κουμπιά χωρίς ετικέτα
- Ελληνικός και αγγλικός τοπικισμός
- Τεκμηρίωση χρήστη και στις δύο γλώσσες

### Χαρακτηριστικά
- Μετάβαση στον πίνακα Εγγράφων (NVDA+Alt+D)
- Μετάβαση στον πίνακα Κωδικών (NVDA+Alt+C)
- Μετάβαση στον πίνακα Αποσπασμάτων (NVDA+Alt+Q)
- Μετάβαση στον πίνακα Σημειωμάτων (NVDA+Alt+M)
- Μετάβαση στον Πλοηγό Έργου (NVDA+Alt+P)
- Ανάγνωση λεπτομερειών κωδικού (NVDA+Shift+C)
- Ανάγνωση κειμένου αποσπάσματος (NVDA+Shift+Q)
- Ανάγνωση πληροφοριών εγγράφου (NVDA+Shift+D)
- Ανακοίνωση τρέχοντος πίνακα (NVDA+Shift+P)
- Λίστα όλων των συντομεύσεων (NVDA+Shift+H)

---

## Μελλοντικά Σχέδια

- Πλοήγηση αποσπασμάτων (πλήκτρα επόμενου/προηγούμενου αποσπάσματος)
- Πλοήγηση ιεραρχίας κωδικών στο δέντρο του Διαχειριστή Κωδικών
- Λειτουργία γρήγορης κωδικοποίησης
- Ηχητική ανατροφοδότηση (earcons)
- Δοκιμές ζωντανής ενσωμάτωσης NVDA + Atlas.ti σε όλες τις υποστηριζόμενες εκδόσεις και γλώσσες διεπαφής
