# ATLAS.ti 26 Windows accessibility capture and validation

**Author:** Christos Bouronikos  
**Email:** chrisbouronikos@gmail.com  
**GitHub:** https://github.com/ChristosBouronikos  
**Donations:** [PayPal](https://paypal.me/christosbouronikos)

---

**Language:** [English](#english) | [Ελληνικά](#ελληνικά)

---

# English

Use this checklist to validate the real Windows UI Automation tree against the
documentation-derived catalogue. Work in a disposable sample project containing
no confidential research material.

## Preparation

1. Install `atlastiAccessibility-1.3.0.nvda-addon` and restart NVDA.
2. Confirm the Atlas.ti category appears under NVDA Settings.
3. Set the speech language to English for the first pass.
4. Enable **privacy-filtered ATLAS.ti UI tree capture**.
5. Set the NVDA log level to Info and clear the log.
6. Open the ATLAS.ti Sustainability sample project or another non-sensitive test project.
7. On every surface below press `NVDA+Ctrl+Alt+Shift+U`, then save the complete
   block from `safe UI tree capture begin` through `end` as UTF-8 text.

The capture prunes list, table, tree, data-grid, editable-text and document
branches and redacts unknown structural window/pane titles. Before sharing a
capture, confirm that it contains no document, quotation, code, memo, project or
participant text.

## Core window and ribbon

- [ ] Title bar and Quick Access toolbar
- [ ] File menu / Μενού Αρχείο
- [ ] Home tab / Καρτέλα Αρχική
- [ ] Search and Code tab / Καρτέλα Αναζήτηση και Κωδικοποίηση
- [ ] Analyze tab / Καρτέλα Ανάλυση
- [ ] Import and Export tab / Καρτέλα Εισαγωγή και Εξαγωγή
- [ ] Tools tab / Καρτέλα Εργαλεία
- [ ] Help tab / Καρτέλα Βοήθεια
- [ ] Search and Filter contextual tab / Καρτέλα Αναζήτηση και Φίλτρο
- [ ] View contextual tab / Καρτέλα Προβολή
- [ ] Document contextual tab / Καρτέλα Έγγραφο
- [ ] Network contextual tab / Καρτέλα Δίκτυο
- [ ] Project Navigator, working area, margin area and status bar

Traverse every tab with Tab and Shift+Tab. Verify the visible English label and
role. Repeat in Greek mode and verify the Greek label and role, for example
`Κουμπί Αποθήκευση Έργου` and `Καρτέλα Αρχική`.

## Welcome screen

- [ ] Licence-information pane
- [ ] New Project, Import Project and Options
- [ ] Project-list pane, search field and sortable columns
- [ ] Project context menu: show/hide, open, pin/unpin, rename and delete
- [ ] News/resources pane, manual, sample projects and video tutorials
- [ ] Expand/collapse resource controls and state announcements

## Entity managers

Capture each manager once floating and, where practical, once docked:

- [ ] Document Manager
- [ ] Quotation Manager
- [ ] Code Manager
- [ ] Memo Manager
- [ ] Network Manager
- [ ] Link Manager
- [ ] Relation Manager
- [ ] Document Group Manager
- [ ] Code Group Manager
- [ ] Memo Group Manager
- [ ] Network Group Manager

For every manager verify:

- [ ] Manager list, group/filter pane, segmented bottom pane and split bars
- [ ] Diagram, Preview and Comment choices where present
- [ ] Search field and Today, This week, Only mine and Commented filters
- [ ] Checked/selected/expanded/collapsed/unavailable/pressed state feedback
- [ ] Column reading includes `Column` / `Στήλη`; specifically `Start` must be
      `Στήλη Έναρξη`, never the Home tab
- [ ] Status-bar item count
- [ ] Context items include `Menu item` / `Στοιχείο μενού`
- [ ] Dock, Float and Always On Top
- [ ] Navigation focuses the manager or an enabled child when its container refuses focus

## Quotation Reader

- [ ] Single Line / Μία γραμμή
- [ ] Small Preview / Μικρή προεπισκόπηση
- [ ] Large Preview / Μεγάλη προεπισκόπηση
- [ ] Quotation name and comment controls
- [ ] Apply Codes and Remove Codes
- [ ] View/Go to Context
- [ ] Rename, Delete, Open Network and Select All

## Pop-ups and specialised tools

- [ ] Codebook import: headers, update existing codes, Import, Cancel
- [ ] Search and Project Search: entities, user restriction, Use GREP,
      Case Sensitive, Show None and results
- [ ] Query Tool: operands, operators, expression, results and report
- [ ] Query Scope: Edit Scope, expression, results and close/delete
- [ ] Query report: List, List with Comments, Full Content, Content plus Comments
- [ ] Confirmation pop-ups: Yes, No, OK, Continue and Cancel
- [ ] Options/Application Preferences
- [ ] Coding dialogue

## Visual-only views

- [ ] Network Editor
- [ ] Word Cloud
- [ ] Code Manager cloud and bar-chart views
- [ ] Document Manager treemap view
- [ ] Sankey, treemap and bar-chart outputs

Run `NVDA+Ctrl+Alt+Shift+V` on each. If ATLAS.ti exposes child shapes, verify
they are listed. Otherwise verify that the add-on identifies the limitation and
offers the nearest accessible table/list alternative.

## Capture reconciliation

```text
python scripts/compare_ui_capture.py atlasti26-capture.log \
  --json-output atlasti26-comparison.json \
  --markdown-output atlasti26-comparison.md
```

Investigate every unknown control, role mismatch and changed AutomationId.
Update the catalogue only after confirming the result in two captures or with
Microsoft Accessibility Insights/Inspect.exe.

## Acceptance criteria

- [ ] No research content appears in any safe capture
- [ ] No unresolved catalogue collisions
- [ ] No known control lacks English or Greek
- [ ] Every observed role mismatch has been investigated
- [ ] Every changed AutomationId has been confirmed on Windows
- [ ] Keyboard focus reaches every control or a documented fallback
- [ ] English mode speaks English names and roles
- [ ] Greek mode speaks Greek names, roles and states
- [ ] All automated tests and package-integrity checks pass

---

# Ελληνικά

Χρησιμοποιήστε αυτή τη λίστα ελέγχου για να επαληθεύσετε το πραγματικό δέντρο UI
Automation των Windows σε σύγκριση με τον κατάλογο που προέκυψε από την
τεκμηρίωση. Εργαστείτε σε ένα αναλώσιμο δείγμα έργου που δεν περιέχει
εμπιστευτικό ερευνητικό υλικό.

## Προετοιμασία

1. Εγκαταστήστε το `atlastiAccessibility-1.3.0.nvda-addon` και επανεκκινήστε το NVDA.
2. Επιβεβαιώστε ότι η κατηγορία Atlas.ti εμφανίζεται στις Ρυθμίσεις του NVDA.
3. Ορίστε τη γλώσσα ομιλίας στα Αγγλικά για το πρώτο πέρασμα.
4. Ενεργοποιήστε την **καταγραφή δέντρου διεπαφής ATLAS.ti με φίλτρο απορρήτου**.
5. Ορίστε το επίπεδο καταγραφής του NVDA σε Info και καθαρίστε το αρχείο καταγραφής.
6. Ανοίξτε το δείγμα έργου Sustainability του ATLAS.ti ή άλλο μη ευαίσθητο δοκιμαστικό έργο.
7. Σε κάθε επιφάνεια παρακάτω πατήστε `NVDA+Ctrl+Alt+Shift+U` και έπειτα
   αποθηκεύστε ολόκληρο το μπλοκ από το `safe UI tree capture begin` έως το
   `end` ως κείμενο UTF-8.

Η καταγραφή περικόπτει κλάδους λιστών, πινάκων, δέντρων, πλεγμάτων δεδομένων,
επεξεργάσιμου κειμένου και εγγράφων, και αποκρύπτει άγνωστους δομικούς τίτλους
παραθύρων/πλαισίων. Πριν μοιραστείτε μια καταγραφή, επιβεβαιώστε ότι δεν
περιέχει κείμενο εγγράφου, αποσπάσματος, κωδικού, σημειώματος, έργου ή
συμμετέχοντα.

## Κύριο παράθυρο και κορδέλα

- [ ] Γραμμή τίτλου και Γραμμή γρήγορης πρόσβασης
- [ ] File menu / Μενού Αρχείο
- [ ] Home tab / Καρτέλα Αρχική
- [ ] Search and Code tab / Καρτέλα Αναζήτηση και Κωδικοποίηση
- [ ] Analyze tab / Καρτέλα Ανάλυση
- [ ] Import and Export tab / Καρτέλα Εισαγωγή και Εξαγωγή
- [ ] Tools tab / Καρτέλα Εργαλεία
- [ ] Help tab / Καρτέλα Βοήθεια
- [ ] Search and Filter contextual tab / Καρτέλα Αναζήτηση και Φίλτρο
- [ ] View contextual tab / Καρτέλα Προβολή
- [ ] Document contextual tab / Καρτέλα Έγγραφο
- [ ] Network contextual tab / Καρτέλα Δίκτυο
- [ ] Πλοηγός Έργου, περιοχή εργασίας, περιοχή περιθωρίου και γραμμή κατάστασης

Διατρέξτε κάθε καρτέλα με Tab και Shift+Tab. Επαληθεύστε την ορατή αγγλική
ετικέτα και τον ρόλο. Επαναλάβετε σε ελληνική λειτουργία και επαληθεύστε την
ελληνική ετικέτα και τον ρόλο, για παράδειγμα `Κουμπί Αποθήκευση Έργου` και
`Καρτέλα Αρχική`.

## Οθόνη υποδοχής

- [ ] Πλαίσιο πληροφοριών άδειας χρήσης
- [ ] Νέο Έργο, Εισαγωγή Έργου και Επιλογές
- [ ] Πλαίσιο λίστας έργων, πεδίο αναζήτησης και ταξινομήσιμες στήλες
- [ ] Μενού περιβάλλοντος έργου: εμφάνιση/απόκρυψη, άνοιγμα, καρφίτσωμα/ξεκαρφίτσωμα, μετονομασία και διαγραφή
- [ ] Πλαίσιο νέων/πόρων, εγχειρίδιο, δείγματα έργων και βίντεο οδηγοί
- [ ] Στοιχεία ανάπτυξης/σύμπτυξης πόρων και ανακοινώσεις κατάστασης

## Διαχειριστές οντοτήτων

Καταγράψτε κάθε διαχειριστή μία φορά σε αποσυνδεδεμένο (floating) παράθυρο και,
όπου είναι πρακτικό, μία φορά αγκυρωμένο (docked):

- [ ] Διαχειριστής Εγγράφων
- [ ] Διαχειριστής Αποσπασμάτων
- [ ] Διαχειριστής Κωδικών
- [ ] Διαχειριστής Σημειωμάτων
- [ ] Διαχειριστής Δικτύων
- [ ] Διαχειριστής Συνδέσεων
- [ ] Διαχειριστής Σχέσεων
- [ ] Διαχειριστής Ομάδων Εγγράφων
- [ ] Διαχειριστής Ομάδων Κωδικών
- [ ] Διαχειριστής Ομάδων Σημειωμάτων
- [ ] Διαχειριστής Ομάδων Δικτύων

Για κάθε διαχειριστή επαληθεύστε:

- [ ] Λίστα διαχειριστή, πλαίσιο ομάδων/φίλτρων, τμηματοποιημένο κάτω πλαίσιο και μπάρες διαχωρισμού
- [ ] Επιλογές Διάγραμμα, Προεπισκόπηση και Σχόλιο όπου υπάρχουν
- [ ] Πεδίο αναζήτησης και φίλτρα Σήμερα, Αυτή την εβδομάδα, Μόνο δικά μου και Με σχόλιο
- [ ] Ανατροφοδότηση καταστάσεων επιλεγμένο/επισημασμένο/αναπτυγμένο/συμπτυγμένο/μη διαθέσιμο/πατημένο
- [ ] Η ανάγνωση στηλών περιλαμβάνει `Column` / `Στήλη`· ειδικά το `Start` πρέπει να
      είναι `Στήλη Έναρξη`, ποτέ η καρτέλα Αρχική
- [ ] Αριθμός στοιχείων στη γραμμή κατάστασης
- [ ] Τα στοιχεία μενού περιβάλλοντος περιλαμβάνουν `Menu item` / `Στοιχείο μενού`
- [ ] Αγκύρωση, Αποσύνδεση παραθύρου και Πάντα σε πρώτο πλάνο
- [ ] Η πλοήγηση εστιάζει στον διαχειριστή ή σε ενεργοποιημένο θυγατρικό στοιχείο όταν ο περιέκτης του αρνείται την εστίαση

## Αναγνώστης Αποσπασμάτων

- [ ] Single Line / Μία γραμμή
- [ ] Small Preview / Μικρή προεπισκόπηση
- [ ] Large Preview / Μεγάλη προεπισκόπηση
- [ ] Στοιχεία ονόματος και σχολίου αποσπάσματος
- [ ] Εφαρμογή Κωδικών και Αφαίρεση Κωδικών
- [ ] Προβολή/Μετάβαση στο Πλαίσιο
- [ ] Μετονομασία, Διαγραφή, Άνοιγμα Δικτύου και Επιλογή όλων

## Αναδυόμενα παράθυρα και εξειδικευμένα εργαλεία

- [ ] Εισαγωγή βιβλίου κωδικών: επικεφαλίδες, ενημέρωση υπαρχόντων κωδικών, Εισαγωγή, Άκυρο
- [ ] Αναζήτηση και Αναζήτηση Έργου: οντότητες, περιορισμός χρήστη, Χρήση GREP,
      Διάκριση πεζών-κεφαλαίων, Εμφάνιση κανενός και αποτελέσματα
- [ ] Εργαλείο Ερωτημάτων: τελεστέοι, τελεστές, έκφραση, αποτελέσματα και αναφορά
- [ ] Εμβέλεια ερωτήματος: Επεξεργασία Εμβέλειας, έκφραση, αποτελέσματα και κλείσιμο/διαγραφή
- [ ] Αναφορά ερωτήματος: Λίστα, Λίστα με Σχόλια, Πλήρες Περιεχόμενο, Περιεχόμενο και Σχόλια
- [ ] Αναδυόμενα παράθυρα επιβεβαίωσης: Ναι, Όχι, ΟΚ, Συνέχεια και Άκυρο
- [ ] Επιλογές/Προτιμήσεις εφαρμογής
- [ ] Παράθυρο κωδικοποίησης

## Προβολές μόνο-οπτικού περιεχομένου

- [ ] Επεξεργαστής Δικτύου
- [ ] Νέφος Λέξεων
- [ ] Προβολές νέφους και ραβδογράμματος του Διαχειριστή Κωδικών
- [ ] Προβολή δενδροχάρτη του Διαχειριστή Εγγράφων
- [ ] Έξοδοι Sankey, δενδροχάρτη και ραβδογράμματος

Εκτελέστε `NVDA+Ctrl+Alt+Shift+V` σε κάθε μία. Αν το ATLAS.ti εκθέτει θυγατρικά
σχήματα, επαληθεύστε ότι εμφανίζονται στη λίστα. Διαφορετικά, επαληθεύστε ότι το
πρόσθετο αναγνωρίζει τον περιορισμό και προσφέρει την πλησιέστερη προσβάσιμη
εναλλακτική πίνακα/λίστας.

## Συμφωνία καταγραφής

```text
python scripts/compare_ui_capture.py atlasti26-capture.log \
  --json-output atlasti26-comparison.json \
  --markdown-output atlasti26-comparison.md
```

Διερευνήστε κάθε άγνωστο στοιχείο ελέγχου, αναντιστοιχία ρόλου και αλλαγμένο
AutomationId. Ενημερώστε τον κατάλογο μόνο αφού επιβεβαιώσετε το αποτέλεσμα σε
δύο καταγραφές ή με το Microsoft Accessibility Insights/Inspect.exe.

## Κριτήρια αποδοχής

- [ ] Δεν εμφανίζεται ερευνητικό περιεχόμενο σε καμία ασφαλή καταγραφή
- [ ] Δεν υπάρχουν ανεπίλυτες συγκρούσεις καταλόγου
- [ ] Κανένα γνωστό στοιχείο ελέγχου δεν στερείται αγγλικής ή ελληνικής απόδοσης
- [ ] Κάθε παρατηρούμενη αναντιστοιχία ρόλου έχει διερευνηθεί
- [ ] Κάθε αλλαγμένο AutomationId έχει επιβεβαιωθεί στα Windows
- [ ] Η εστίαση πληκτρολογίου φτάνει σε κάθε στοιχείο ελέγχου ή σε τεκμηριωμένη εναλλακτική
- [ ] Η αγγλική λειτουργία εκφωνεί αγγλικά ονόματα και ρόλους
- [ ] Η ελληνική λειτουργία εκφωνεί ελληνικά ονόματα, ρόλους και καταστάσεις
- [ ] Όλες οι αυτοματοποιημένες δοκιμές και οι έλεγχοι ακεραιότητας πακέτου περνούν
