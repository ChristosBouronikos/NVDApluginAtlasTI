# Πρόσθετο Προσβασιμότητας Atlas.ti για NVDA
# Atlas.ti Accessibility NVDA Add-on

**Δημιουργός / Author:** Christos Bouronikos  
**Email:** chrisbouronikos@gmail.com  
**Δωρεές / Donations:** [PayPal](https://paypal.me/christosbouronikos)

---

> 💝 **Αν αυτό το πρόσθετο σας βοήθησε, παρακαλώ σκεφτείτε να κάνετε μια δωρεά!**  
> 💝 **If this plugin helped you, please consider making a donation!**  
> 👉 [https://paypal.me/christosbouronikos](https://paypal.me/christosbouronikos)

---

## ℹ️ Τι είναι το πλήκτρο NVDA; / What is the NVDA key?

Το **πλήκτρο NVDA** είναι ένα πλήκτρο τροποποίησης που χρησιμοποιείται για τις εντολές του NVDA.

**Προεπιλεγμένα πλήκτρα NVDA / Default NVDA keys:**
- **Insert** (κύριο πληκτρολόγιο)
- **Numpad Insert** (αριθμητικό πληκτρολόγιο)
- **Caps Lock** (μπορεί να ενεργοποιηθεί στις ρυθμίσεις)

Για παράδειγμα, `NVDA+Alt+D` σημαίνει:
- Κρατήστε πατημένο το **Insert** (ή Caps Lock)
- Κρατήστε πατημένο το **Alt**
- Πατήστε μια φορά το πλήκτρο **D**

---

# 🇬🇷 Ελληνικά

## Επισκόπηση

Ένα πρόσθετο αναγνώστη οθόνης NVDA που βελτιώνει την προσβασιμότητα του λογισμικού ποιοτικής ανάλυσης δεδομένων [Atlas.ti](https://atlasti.com/), καθιστώντας το χρησιμοποιήσιμο για τυφλούς ερευνητές.

## 🎯 Χαρακτηριστικά

- **Γρήγορη Πλοήγηση Πινάκων** - Μετάβαση μεταξύ Εγγράφων, Κωδικών, Αποσπασμάτων, Σημειώσεων
- **Βοηθοί Ανάγνωσης** - Πληροφορίες για κωδικούς, αποσπάσματα και έγγραφα
- **Βελτιωμένες Ετικέτες** - Ουσιαστικά ονόματα για κουμπιά χωρίς ετικέτα
- **Υποστήριξη Ελληνικών/Αγγλικών**

## ⌨️ Συντομεύσεις Πληκτρολογίου

### Πλοήγηση Πινάκων
| Συντόμευση | Ενέργεια |
|------------|----------|
| `NVDA+Alt+D` | Πίνακας Εγγράφων |
| `NVDA+Alt+C` | Πίνακας Κωδικών |
| `NVDA+Alt+Q` | Πίνακας Αποσπασμάτων |
| `NVDA+Alt+M` | Πίνακας Σημειώσεων |
| `NVDA+Alt+P` | Περιήγηση Έργου |

### Ανάγνωση
| Συντόμευση | Ενέργεια |
|------------|----------|
| `NVDA+Shift+C` | Λεπτομέρειες κωδικού |
| `NVDA+Shift+Q` | Κείμενο αποσπάσματος |
| `NVDA+Shift+D` | Πληροφορίες εγγράφου |
| `NVDA+Shift+P` | Τρέχων πίνακας |
| `NVDA+Shift+H` | Λίστα συντομεύσεων |

## 📦 Εγκατάσταση

### Μέθοδος 1: Από Εκδόσεις (Συνιστάται)
1. Κατεβάστε το αρχείο `.nvda-addon` από τις [Εκδόσεις](../../releases)
2. Κάντε διπλό κλικ στο αρχείο για αυτόματη εγκατάσταση
   - **Ή** χρησιμοποιήστε: NVDA Μενού → Εργαλεία → Κατάστημα Πρόσθετων → Εγκατάσταση από εξωτερική πηγή
3. Επανεκκινήστε το NVDA όταν σας ζητηθεί

### Μέθοδος 2: Χτίσιμο από τον Κώδικα
**Για Mac/Linux:**
```bash
./build.sh
```

**Για Windows (PowerShell):**
```powershell
.\build.ps1
```

Μετά το χτίσιμο, το αρχείο `atlastiAccessibility-1.0.0.nvda-addon` θα δημιουργηθεί στον φάκελο του έργου.

### Μέθοδος 3: Από το Κατάστημα NVDA (Σύντομα)
Το πρόσθετο θα υποβληθεί στο επίσημο κατάστημα πρόσθετων του NVDA σύντομα.

## 🧪 Δοκιμές

Για να δοκιμάσετε το πρόσθετο:
1. Εγκαταστήστε το NVDA στα Windows 10/11
2. Εγκαταστήστε το πρόσθετο
3. Ανοίξτε το Atlas.ti
4. Δοκιμάστε τις συντομεύσεις

## ❓ Αντιμετώπιση Προβλημάτων

- **Δεν φορτώνει:** `NVDA+N` → Εργαλεία → Αρχείο Καταγραφής
- **Συντομεύσεις:** Ελέγξτε ότι το Atlas.ti έχει την εστίαση

## 📄 Άδεια

GNU GPL v2.0 - Απαιτείται αναφορά στον δημιουργό Christos Bouronikos

---

# 🇬🇧 English

## Overview

A NVDA screen reader add-on that enhances accessibility for [Atlas.ti](https://atlasti.com/) qualitative data analysis software, making it usable for blind researchers.

## 🎯 Features

- **Quick Panel Navigation** - Jump between Documents, Codes, Quotations, Memos
- **Reading Helpers** - Get information about codes, quotations, and documents
- **Improved Labels** - Meaningful names for unlabeled buttons
- **Greek/English Support**

## ⌨️ Keyboard Shortcuts

### Panel Navigation
| Shortcut | Action |
|----------|--------|
| `NVDA+Alt+D` | Documents Panel |
| `NVDA+Alt+C` | Codes Panel |
| `NVDA+Alt+Q` | Quotations Panel |
| `NVDA+Alt+M` | Memos Panel |
| `NVDA+Alt+P` | Project Navigator |

### Reading
| Shortcut | Action |
|----------|--------|
| `NVDA+Shift+C` | Code details |
| `NVDA+Shift+Q` | Quotation text |
| `NVDA+Shift+D` | Document info |
| `NVDA+Shift+P` | Current panel |
| `NVDA+Shift+H` | List shortcuts |

## 📦 Installation

### Method 1: From Releases (Recommended)
1. Download the `.nvda-addon` file from [Releases](../../releases)
2. Double-click the file to install automatically
   - **Or** use: NVDA Menu → Tools → Add-on Store → Install from external source
3. Restart NVDA when prompted

### Method 2: Build from Source
**For Mac/Linux:**
```bash
./build.sh
```

**For Windows (PowerShell):**
```powershell
.\build.ps1
```

After building, the `atlastiAccessibility-1.0.0.nvda-addon` file will be created in the project folder.

### Method 3: From NVDA Add-on Store (Coming Soon)
This add-on will be submitted to the official NVDA add-on store soon.

**For developers wanting to submit:**
1. Create a GitHub Release with the `.nvda-addon` file
2. Open an issue at [nvaccess/addon-datastore](https://github.com/nvaccess/addon-datastore)
3. Provide the HTTPS download URL, repository URL, and metadata
4. Wait for initial approval (automated security checks)
5. Future updates will be published automatically

## 🧪 Testing Instructions

### Requirements
- Windows 10 or Windows 11
- NVDA 2023.1 or newer
- Atlas.ti (any version from 9 to 24)

### Steps to Test
1. Install NVDA on Windows
2. Download and install the `.nvda-addon` file
3. Restart NVDA when prompted
4. Open Atlas.ti
5. Test each shortcut:
   - Press `NVDA+Alt+D` - should announce "Documents panel"
   - Press `NVDA+Alt+C` - should announce "Codes panel"
   - Press `NVDA+Shift+H` - should list all shortcuts
6. Check NVDA log for any errors: `NVDA+N` → Tools → View Log

### Reporting Issues
If something doesn't work:
1. Note your NVDA version
2. Note your Atlas.ti version
3. Note your Windows version
4. Describe what happened vs what you expected
5. Open an issue on GitHub

## ❓ Troubleshooting

- **Not loading:** `NVDA+N` → Tools → View Log
- **Shortcuts not working:** Ensure Atlas.ti has focus

## 📄 License

GNU GPL v2.0 - Attribution to original creator Christos Bouronikos required

---

## 🙏 Support the Project

If you find this addon helpful, please consider:
- ⭐ Starring this repository
- 🐛 Reporting bugs or suggesting features
- � Making a donation: [https://paypal.me/christosbouronikos](https://paypal.me/christosbouronikos)

Thank you! / Ευχαριστώ!
