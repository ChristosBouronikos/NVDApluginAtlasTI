# -*- coding: utf-8 -*-
# =============================================================================
# ATLAS.ti user interface knowledge base
# Version: 1.3.0
# =============================================================================
#
# Author: Christos Bouronikos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donations: https://paypal.me/christosbouronikos
#
# Copyright (C) 2026 Christos Bouronikos
# This file is covered by the GNU General Public License v2.
# See the file LICENSE for more details.
# =============================================================================

"""Knowledge base of the ATLAS.ti Windows user interface.

This module deliberately imports nothing from NVDA so it can be unit tested
on plain CPython. It answers three questions for the app module:

1. "What is this control?" -- given an accessible name, an automation id or a
   window class name, resolve it to a canonical ATLAS.ti UI element.
2. "How do I say it?" -- render that element in English or Greek.
3. "Which language is ATLAS.ti itself running in?" -- inferred from the
   labels we have observed so far.

Why the localised aliases matter
--------------------------------
ATLAS.ti ships its interface in English, German, Spanish, Portuguese and
Simplified Chinese (File > Options > Application Preferences > Display
Language). There is no Greek interface, so a Greek researcher always sees a
foreign-language ATLAS.ti. Recognising the foreign label and speaking the
Greek one is the whole point of this table: the add-on reads the interface
in Greek no matter which language ATLAS.ti is displaying.

Sources: ATLAS.ti Windows user manual (v22 through v26),
https://manuals.atlasti.com/Win/en/manual/ -- interface, entity manager,
margin area, tools, querying and appendix chapters.
"""

import unicodedata

# =============================================================================
# TEXT NORMALISATION
# =============================================================================

# Substring matching on very short tokens produces nonsense ("id" matches
# "Hide"), so a token must be at least this long to be matched loosely.
MIN_LOOSE_TOKEN_LENGTH = 4


def normalize(value):
    """Fold a UI string down to a comparable key.

    Unicode aware on purpose: version 1.1.0 stripped everything outside
    ``[a-z0-9]``, which reduced every Greek and Chinese label to an empty
    string and made non-English matching impossible.

    Case, accents, Greek tonos and the final sigma are all folded away, so
    "Κωδικών", "ΚΩΔΙΚΩΝ" and "κωδικων" compare equal.
    """
    text = unicodedata.normalize("NFKD", str(value)).casefold()
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("ς", "σ")
    return "".join(ch for ch in text if ch.isalnum())


# =============================================================================
# UI ELEMENT TABLE
# =============================================================================

ELEMENTS = {}
"""Canonical key -> element dict.

Each element carries:
    kind      What sort of control it is ("tab", "manager", "button", ...).
    en / el   The spoken label in English and Greek.
    ids       Language independent tokens: UIA automation ids and window
              class names ATLAS.ti is known or likely to expose.
    loc       Recognition aliases for the other ATLAS.ti interface
              languages, keyed by language code.
    hint      Optional one-line explanation, spoken by the "describe
              element" command.
    shortcut  Optional ATLAS.ti keyboard shortcut, where the manual
              documents one.
"""


def _e(key, kind, en, el, ids=(), de=(), es=(), pt=(), zh=(), hint=None, shortcut=None,
       visualOnly=False, companion=None, concept=None, contexts=(), controlType=None):
    """Register one UI element.

    ``visualOnly``, ``companion`` and ``concept`` describe elements that are
    rendered graphics rather than accessible controls (charts, diagrams,
    word clouds, canvas-drawn networks):

    visualOnly  True when Atlas.ti is likely to expose this element as a
                single opaque graphic with no readable child content --
                either a dedicated visualisation window/pane, or a view
                mode that turns an otherwise-accessible list into one.
    companion   The element key of the nearest accessible alternative that
                shows the same underlying data as text -- a table, a list,
                or the same manager's default List view. None when no
                alternative is known.
    concept     (english, greek) explanation of what the visual normally
                shows, spoken when the add-on cannot read its contents, so
                the researcher at least knows what they are missing rather
                than hearing silence or a bare name.
    contexts    Optional canonical container keys that make an otherwise
                ambiguous label specific (for example, a ``Start`` column
                versus the German label of the Home tab).
    controlType Semantic role used when an announcement must include the
                type as words (button, menu item, column, and so on).
    """
    loc = {}
    for code, values in (("de", de), ("es", es), ("pt", pt), ("zh", zh)):
        if values:
            loc[code] = list(values)
    ELEMENTS[key] = {
        "key": key,
        "kind": kind,
        "en": en,
        "el": el,
        "ids": list(ids),
        "loc": loc,
        "hint": hint,
        "shortcut": shortcut,
        "visualOnly": visualOnly,
        "companion": companion,
        "concept": concept,
        "contexts": tuple(contexts),
        "controlType": controlType,
    }


# -----------------------------------------------------------------------------
# Entity types -- the six main ATLAS.ti objects
# -----------------------------------------------------------------------------
_e("documents", "entity", "Documents", "Έγγραφα",
   ids=("Documents", "DocumentList", "DocumentTree"),
   de=("Dokumente",), es=("Documentos",), pt=("Documentos",), zh=("文档",),
   hint="The data files you added to the project.")
_e("quotations", "entity", "Quotations", "Αποσπάσματα",
   ids=("Quotations", "QuotationList"),
   de=("Zitate",), es=("Citas",), pt=("Citações",), zh=("引文",),
   hint="Selected segments of your data.")
_e("codes", "entity", "Codes", "Κωδικοί",
   ids=("Codes", "CodeList", "CodeTree"),
   de=("Kodes", "Codes"), es=("Códigos",), pt=("Códigos",), zh=("代码", "编码"),
   hint="Labels applied to quotations.")
_e("memos", "entity", "Memos", "Σημειώματα",
   ids=("Memos", "MemoList"),
   de=("Memos",), es=("Memos", "Memorandos"), pt=("Memorandos", "Memos"), zh=("备忘录",),
   hint="Your own research notes stored in the project.")
_e("networks", "entity", "Networks", "Δίκτυα",
   ids=("Networks", "NetworkList"),
   de=("Netzwerke",), es=("Redes",), pt=("Redes",), zh=("网络",),
   hint="Visual maps of linked entities.")
_e("links", "entity", "Links", "Συνδέσεις",
   ids=("Links", "LinkList"),
   de=("Links", "Verknüpfungen"), es=("Vínculos", "Enlaces"), pt=("Ligações", "Vínculos"),
   zh=("链接",),
   hint="Code to code links and hyperlinks between quotations.")
_e("relations", "entity", "Relations", "Σχέσεις",
   ids=("Relations", "RelationList"),
   de=("Relationen",), es=("Relaciones",), pt=("Relações",), zh=("关系",),
   hint="The named relationships used on links.")
_e("groups", "entity", "Groups", "Ομάδες",
   ids=("Groups", "GroupList"),
   de=("Gruppen",), es=("Grupos",), pt=("Grupos",), zh=("组", "群组"),
   hint="Collections of documents, codes, memos or networks.")
_e("comments", "entity", "Comments", "Σχόλια",
   ids=("Comments",),
   de=("Kommentare",), es=("Comentarios",), pt=("Comentários",), zh=("注释", "评论"))

# -----------------------------------------------------------------------------
# Ribbon tabs
# -----------------------------------------------------------------------------
_e("tabFile", "tab", "File menu", "Μενού Αρχείο",
   ids=("File", "FileTab", "Backstage", "BackstageButton"),
   de=("Datei",), es=("Archivo",), pt=("Arquivo", "Ficheiro"), zh=("文件",),
   hint="Project level actions: new, open, save, export, merge, options.")
_e("tabHome", "tab", "Home tab", "Καρτέλα Αρχική",
   ids=("Home", "HomeTab", "RibbonHome"),
   de=("Start",), es=("Inicio",), pt=("Início",), zh=("主页", "开始"),
   hint="Add documents, create entities, open navigators and managers.")
_e("tabSearchCode", "tab", "Search and Code tab", "Καρτέλα Αναζήτηση και Κωδικοποίηση",
   ids=("SearchAndCode", "SearchCodeTab"),
   de=("Suchen & Kodieren", "Suchen und Kodieren"),
   es=("Buscar y Codificar",), pt=("Pesquisar e Codificar",), zh=("搜索与编码",),
   hint="Text search, regex, entity recognition, sentiment, AI coding.")
_e("tabAnalyze", "tab", "Analyze tab", "Καρτέλα Ανάλυση",
   ids=("Analyze", "AnalyzeTab", "Analysis"),
   de=("Analysieren", "Analyse"), es=("Analizar",), pt=("Analisar",), zh=("分析",),
   hint="Query tool, tables, co-occurrence, filters, inter-coder agreement.")
_e("tabImportExport", "tab", "Import and Export tab", "Καρτέλα Εισαγωγή και Εξαγωγή",
   ids=("ImportExport", "ImportAndExport"),
   de=("Import & Export", "Import und Export"),
   es=("Importar y Exportar",), pt=("Importar e Exportar",), zh=("导入与导出",),
   hint="Survey data, reference managers, code books, statistics export.")
_e("tabTools", "tab", "Tools tab", "Καρτέλα Εργαλεία",
   ids=("Tools", "ToolsTab"),
   de=("Werkzeuge", "Extras"), es=("Herramientas",), pt=("Ferramentas",), zh=("工具",),
   hint="User management, project search, redundant codings.")
_e("tabHelp", "tab", "Help tab", "Καρτέλα Βοήθεια",
   ids=("Help", "HelpTab"),
   de=("Hilfe",), es=("Ayuda",), pt=("Ajuda",), zh=("帮助",))
_e("tabSearchFilter", "tab", "Search and Filter tab", "Καρτέλα Αναζήτηση και Φίλτρο",
   ids=("SearchFilter", "SearchAndFilter"),
   de=("Suchen & Filtern",), es=("Buscar y Filtrar",), pt=("Pesquisar e Filtrar",),
   hint="Manager tab holding search, local filters and global filters.")
_e("tabView", "tab", "View tab", "Καρτέλα Προβολή",
   ids=("View", "ViewTab"),
   de=("Ansicht",), es=("Vista", "Ver"), pt=("Ver", "Vista"), zh=("视图",))
_e("tabDocument", "tab", "Document tab", "Καρτέλα Έγγραφο",
   ids=("DocumentTab",),
   de=("Dokument",), es=("Documento",), pt=("Documento",))
_e("tabNetwork", "tab", "Network tab", "Καρτέλα Δίκτυο",
   ids=("NetworkTab",),
   de=("Netzwerk",), es=("Red",), pt=("Rede",))

# -----------------------------------------------------------------------------
# Entity managers and other main windows
# -----------------------------------------------------------------------------
_e("managerDocuments", "manager", "Document Manager", "Διαχειριστής Εγγράφων",
   ids=("DocumentManager", "DocumentsManager", "DocManager"),
   de=("Dokument-Manager", "Dokumentenmanager"), es=("Administrador de Documentos",),
   pt=("Gerenciador de Documentos",), zh=("文档管理器",),
   hint="Lists every document with its ID, name and location.")
_e("managerQuotations", "manager", "Quotation Manager", "Διαχειριστής Αποσπασμάτων",
   ids=("QuotationManager", "QuotationsManager"),
   de=("Zitat-Manager", "Zitatmanager"), es=("Administrador de Citas",),
   pt=("Gerenciador de Citações",), zh=("引文管理器",),
   hint="Lists every quotation with its reference and codes.")
_e("managerCodes", "manager", "Code Manager", "Διαχειριστής Κωδικών",
   ids=("CodeManager", "CodesManager"),
   de=("Kode-Manager", "Code-Manager"), es=("Administrador de Códigos",),
   pt=("Gerenciador de Códigos",), zh=("代码管理器",),
   hint="Create, colour, group, merge and split codes.")
_e("managerMemos", "manager", "Memo Manager", "Διαχειριστής Σημειωμάτων",
   ids=("MemoManager", "MemosManager"),
   de=("Memo-Manager",), es=("Administrador de Memos",),
   pt=("Gerenciador de Memorandos",), zh=("备忘录管理器",),
   hint="Create, read, group and export memos.")
_e("managerNetworks", "manager", "Network Manager", "Διαχειριστής Δικτύων",
   ids=("NetworkManager", "NetworksManager"),
   de=("Netzwerk-Manager",), es=("Administrador de Redes",),
   pt=("Gerenciador de Redes",), zh=("网络管理器",),
   hint="Create and open networks.")
_e("managerLinks", "manager", "Link Manager", "Διαχειριστής Συνδέσεων",
   ids=("LinkManager", "LinksManager"),
   de=("Link-Manager",), es=("Administrador de Vínculos",),
   pt=("Gerenciador de Ligações",),
   hint="Lists code to code links and hyperlinks.")
_e("managerRelations", "manager", "Relation Manager", "Διαχειριστής Σχέσεων",
   ids=("RelationManager", "RelationsManager"),
   de=("Relationen-Manager",), es=("Administrador de Relaciones",),
   pt=("Gerenciador de Relações",),
   hint="Review, edit and create relations used on links.")
_e("managerDocumentGroups", "manager", "Document Group Manager", "Διαχειριστής Ομάδων Εγγράφων",
   ids=("DocumentGroupManager",))
_e("managerCodeGroups", "manager", "Code Group Manager", "Διαχειριστής Ομάδων Κωδικών",
   ids=("CodeGroupManager",))
_e("managerMemoGroups", "manager", "Memo Group Manager", "Διαχειριστής Ομάδων Σημειωμάτων",
   ids=("MemoGroupManager",))
_e("managerNetworkGroups", "manager", "Network Group Manager", "Διαχειριστής Ομάδων Δικτύων",
   ids=("NetworkGroupManager",))

_e("quotationReader", "window", "Quotation Reader", "Αναγνώστης Αποσπασμάτων",
   ids=("QuotationReader",),
   de=("Zitat-Leser",), es=("Lector de Citas",), pt=("Leitor de Citações",),
   hint="Reads all quotations coded with a code or returned by a query.")
_e("networkEditor", "window", "Network Editor", "Επεξεργαστής Δικτύου",
   ids=("NetworkEditor",),
   de=("Netzwerk-Editor",), es=("Editor de Redes",), pt=("Editor de Redes",),
   hint="Canvas where network nodes and links are edited.",
   visualOnly=True, companion="managerLinks",
   concept=(
       "A diagram of codes, quotations, memos, documents and groups drawn as "
       "boxes, connected by lines that represent links and relations between "
       "them. The layout, box positions and line routing are not available "
       "as text.",
       "Ένα διάγραμμα κωδικών, αποσπασμάτων, σημειωμάτων, εγγράφων και "
       "ομάδων, σχεδιασμένο ως πλαίσια συνδεδεμένα με γραμμές που "
       "αναπαριστούν συνδέσεις και σχέσεις μεταξύ τους. Η διάταξη, οι "
       "θέσεις των πλαισίων και η δρομολόγηση των γραμμών δεν είναι "
       "διαθέσιμες ως κείμενο.",
   ))
_e("queryTool", "window", "Query Tool", "Εργαλείο Ερωτημάτων",
   ids=("QueryTool",),
   de=("Abfrage-Tool", "Abfragewerkzeug"), es=("Herramienta de Consultas",),
   pt=("Ferramenta de Consulta",), zh=("查询工具",),
   hint="Retrieves quotations using Boolean and proximity operators.")
_e("codingDialogue", "dialog", "Coding dialogue", "Παράθυρο κωδικοποίησης",
   ids=("CodingDialog", "ApplyCodesDialog"),
   hint="Where you type a new code name or pick existing codes.")
_e("welcomeScreen", "window", "Welcome screen", "Οθόνη υποδοχής",
   ids=("WelcomeScreen", "StartScreen"),
   de=("Startbildschirm",), es=("Pantalla de bienvenida",),
   hint="Project list shown when no project is open.")
_e("optionsDialog", "dialog", "Options", "Επιλογές",
   ids=("Options", "Preferences", "ApplicationPreferences"),
   de=("Optionen", "Einstellungen"), es=("Opciones",), pt=("Opções",), zh=("选项",))
_e("projectSearchWindow", "window", "Project Search", "Αναζήτηση Έργου",
   ids=("ProjectSearch", "SearchProject"),
   de=("Projektsuche",), es=("Búsqueda de proyecto",), pt=("Pesquisa de projeto",),
   hint="Searches names, comments and content across the whole project.")

# -----------------------------------------------------------------------------
# Panes, areas and navigators
# -----------------------------------------------------------------------------
_e("projectNavigator", "panel", "Project Navigator", "Πλοηγός Έργου",
   ids=("ProjectNavigator", "ProjectExplorer", "Navigator", "NavigationPane"),
   de=("Projekt-Navigator", "Projekt-Explorer"), es=("Navegador del proyecto",),
   pt=("Navegador do projeto",), zh=("项目导航器",),
   hint="Tree of all project entities on the left-hand side.")
_e("documentBrowser", "panel", "Document Browser", "Περιηγητής Εγγράφων",
   ids=("DocumentBrowser",), de=("Dokument-Browser",))
_e("codeBrowser", "panel", "Code Browser", "Περιηγητής Κωδικών",
   ids=("CodeBrowser",), de=("Kode-Browser", "Code-Browser"))
_e("quotationBrowser", "panel", "Quotation Browser", "Περιηγητής Αποσπασμάτων",
   ids=("QuotationBrowser",), de=("Zitat-Browser",))
_e("memoBrowser", "panel", "Memo Browser", "Περιηγητής Σημειωμάτων",
   ids=("MemoBrowser",), de=("Memo-Browser",))
_e("networkBrowser", "panel", "Network Browser", "Περιηγητής Δικτύων",
   ids=("NetworkBrowser",), de=("Netzwerk-Browser",))
_e("marginArea", "panel", "Margin area", "Περιοχή περιθωρίου",
   ids=("MarginArea", "Margin"),
   de=("Randbereich", "Marginalienbereich"), es=("Área de margen",),
   pt=("Área de margem",), zh=("边距区",),
   hint="Strip beside a document showing the codes, memos and hyperlinks "
        "attached to each quotation.")
_e("workArea", "panel", "Working area", "Περιοχή εργασίας",
   ids=("WorkArea", "WorkingArea", "MainWorkspace", "DocumentArea"),
   de=("Arbeitsbereich",), es=("Área de trabajo",), pt=("Área de trabalho",),
   hint="Central area where documents, managers and networks open in tabs.")
_e("commentPane", "panel", "Comment pane", "Πλαίσιο σχολίου",
   ids=("CommentPane", "CommentField", "CommentEditor"),
   de=("Kommentarfeld",), es=("Panel de comentarios",), pt=("Painel de comentários",),
   hint="Editable comment for the item selected in the list above.")
_e("previewPane", "panel", "Preview pane", "Πλαίσιο προεπισκόπησης",
   ids=("PreviewPane", "Preview"),
   de=("Vorschau",), es=("Vista previa",), pt=("Pré-visualização",), zh=("预览",))
_e("diagramPane", "panel", "Diagram pane", "Πλαίσιο διαγράμματος",
   ids=("DiagramPane",),
   hint="Bar chart of code distribution across documents.",
   visualOnly=True, companion="codeDocumentTable",
   concept=(
       "A small bar chart showing how the selected code's quotations are "
       "distributed across the project's documents. Switch this pane to "
       "Comment or Preview view for the same code's text content instead.",
       "Ένα μικρό ραβδόγραμμα που δείχνει πώς κατανέμονται τα αποσπάσματα "
       "του επιλεγμένου κωδικού στα έγγραφα του έργου. Αλλάξτε αυτό το "
       "πλαίσιο σε προβολή Σχολίου ή Προεπισκόπησης για το κείμενο του "
       "ίδιου κωδικού.",
   ))
_e("sidePanel", "panel", "Side panel", "Πλαϊνό πλαίσιο",
   ids=("SidePanel", "FilterArea", "GroupPanel"),
   de=("Seitenbereich",), es=("Panel lateral",), pt=("Painel lateral",),
   hint="Filter area listing groups, codes or relations.")
_e("statusBar", "panel", "Status bar", "Γραμμή κατάστασης",
   ids=("StatusBar",),
   de=("Statusleiste",), es=("Barra de estado",), pt=("Barra de estado",),
   zh=("状态栏",),
   hint="Shows how many items the current manager lists.")
_e("titleBar", "panel", "Title bar", "Γραμμή τίτλου",
   ids=("TitleBar",), de=("Titelleiste",), es=("Barra de título",))
_e("quickAccessToolbar", "panel", "Quick Access toolbar", "Γραμμή γρήγορης πρόσβασης",
   ids=("QuickAccessToolbar", "QAT"),
   de=("Symbolleiste für den Schnellzugriff",),
   hint="Save, undo, redo, cut, copy and paste, left of the title.")
_e("ribbon", "panel", "Ribbon", "Κορδέλα",
   ids=("Ribbon", "RibbonControl", "RibbonTabs"),
   de=("Menüband",), es=("Cinta de opciones",), pt=("Faixa de opções",),
   zh=("功能区",),
   hint="Tabbed toolbar at the top of the ATLAS.ti window.")
_e("searchField", "field", "Search field", "Πεδίο αναζήτησης",
   ids=("SearchField", "SearchBox", "txtSearch"),
   de=("Suchfeld",), es=("Campo de búsqueda",), pt=("Campo de pesquisa",),
   hint="Incremental search; clear it to see all items again.")
_e("globalFilterBar", "panel", "Global filter bar", "Γραμμή καθολικού φίλτρου",
   ids=("GlobalFilterBar",),
   hint="Coloured row shown above filtered lists; the check box "
        "deactivates the filter, the x removes it.")
_e("tabGroup", "panel", "Tab group", "Ομάδα καρτελών",
   ids=("TabGroup", "DocumentTabs"),
   hint="Documents, managers and networks open side by side in tab groups.")

# -----------------------------------------------------------------------------
# File menu / backstage
# -----------------------------------------------------------------------------
_e("newProject", "button", "New Project", "Νέο Έργο",
   ids=("NewProject", "ProjectNew"),
   de=("Neues Projekt",), es=("Nuevo proyecto",), pt=("Novo projeto",), zh=("新建项目",))
_e("openProject", "button", "Open Project", "Άνοιγμα Έργου",
   ids=("OpenProject", "ProjectOpen"),
   de=("Projekt öffnen",), es=("Abrir proyecto",), pt=("Abrir projeto",), zh=("打开项目",))
_e("saveProject", "button", "Save Project", "Αποθήκευση Έργου",
   ids=("SaveProject", "Save", "ProjectSave"),
   de=("Speichern",), es=("Guardar",), pt=("Guardar", "Salvar"), zh=("保存",),
   shortcut="Ctrl+S")
_e("projectInfo", "button", "Project info", "Πληροφορίες έργου",
   ids=("ProjectInfo", "Info"), de=("Info",), es=("Información",),
   hint="Project properties, including Set Password.")
_e("setPassword", "button", "Set Password", "Ορισμός κωδικού πρόσβασης",
   ids=("SetPassword",),
   hint="ATLAS.ti cannot recover a lost project password.")
_e("importProject", "button", "Import Project", "Εισαγωγή Έργου",
   ids=("ImportProject",), de=("Projekt importieren",), es=("Importar proyecto",))
_e("exportProject", "button", "Export Project", "Εξαγωγή Έργου",
   ids=("ExportProject", "ProjectExport"),
   de=("Projekt exportieren",), es=("Exportar proyecto",),
   hint="Writes a project bundle for backup or transfer.")
_e("mergeProjects", "button", "Merge Projects", "Συγχώνευση Έργων",
   ids=("MergeProjects", "Merge"),
   de=("Projekte zusammenführen",), es=("Fusionar proyectos",),
   pt=("Mesclar projetos",),
   hint="Combines team members' projects into one.")
_e("createSnapshotProject", "button", "Create Snapshot", "Δημιουργία Στιγμιότυπου",
   ids=("CreateSnapshot", "Snapshot"),
   de=("Schnappschuss erstellen",), es=("Crear instantánea",))
_e("deleteProject", "button", "Delete Project", "Διαγραφή Έργου", ids=("DeleteProject",))
_e("renameProject", "button", "Rename Project", "Μετονομασία Έργου", ids=("RenameProject",))
_e("printProject", "button", "Print", "Εκτύπωση",
   ids=("Print", "PrintWithMargin"),
   de=("Drucken",), es=("Imprimir",), pt=("Imprimir",), zh=("打印",))
_e("displayLanguage", "button", "Display Language", "Γλώσσα εμφάνισης",
   ids=("DisplayLanguage",),
   de=("Anzeigesprache",), es=("Idioma de la interfaz",),
   hint="File, Options, Application Preferences, Display Language.")

# -----------------------------------------------------------------------------
# Quick Access toolbar / editing
# -----------------------------------------------------------------------------
_e("undo", "button", "Undo", "Αναίρεση", ids=("Undo",),
   de=("Rückgängig",), es=("Deshacer",), pt=("Desfazer",), zh=("撤销",))
_e("redo", "button", "Redo", "Επανάληψη", ids=("Redo",),
   de=("Wiederholen",), es=("Rehacer",), pt=("Refazer",), zh=("重做",))
_e("cut", "button", "Cut", "Αποκοπή", ids=("Cut",),
   de=("Ausschneiden",), es=("Cortar",), pt=("Cortar",), zh=("剪切",))
_e("copy", "button", "Copy", "Αντιγραφή", ids=("Copy",),
   de=("Kopieren",), es=("Copiar",), pt=("Copiar",), zh=("复制",))
_e("paste", "button", "Paste", "Επικόλληση", ids=("Paste",),
   de=("Einfügen",), es=("Pegar",), pt=("Colar",), zh=("粘贴",))
_e("selectAll", "button", "Select All", "Επιλογή όλων", ids=("SelectAll",),
   de=("Alles auswählen",), es=("Seleccionar todo",))

# -----------------------------------------------------------------------------
# Home tab
# -----------------------------------------------------------------------------
_e("addDocuments", "button", "Add Documents", "Προσθήκη Εγγράφων",
   ids=("AddDocuments", "AddDocument", "ImportDocuments"),
   de=("Dokumente hinzufügen",), es=("Agregar documentos",),
   pt=("Adicionar documentos",), zh=("添加文档",),
   hint="Import files, folder contents, transcripts or geo documents.")
_e("newEntities", "button", "New Entities", "Νέες Οντότητες",
   ids=("NewEntities", "NewEntity"),
   de=("Neue Entitäten",), es=("Nuevas entidades",),
   hint="Drop-down for creating codes, memos, networks and groups.")
_e("newCode", "button", "New Codes", "Νέοι Κωδικοί",
   ids=("NewCode", "NewCodes", "CreateCode"),
   de=("Neuer Kode", "Neue Kodes"), es=("Nuevo código",), pt=("Novo código",),
   zh=("新建代码",),
   hint="Creates free codes that are not yet applied to data.",
   shortcut="Ctrl+K")
_e("newMemo", "button", "New Memo", "Νέο Σημείωμα",
   ids=("NewMemo", "CreateMemo"),
   de=("Neues Memo",), es=("Nuevo memo",), pt=("Novo memorando",), zh=("新建备忘录",))
_e("newNetwork", "button", "New Network", "Νέο Δίκτυο",
   ids=("NewNetwork", "CreateNetwork"),
   de=("Neues Netzwerk",), es=("Nueva red",), pt=("Nova rede",))
_e("newDocument", "button", "New Document", "Νέο Έγγραφο",
   ids=("NewDocument", "CreateTextDocument"),
   de=("Neues Dokument",), es=("Nuevo documento",))
_e("newFolder", "button", "New Folder", "Νέος Φάκελος",
   ids=("NewFolder", "Folder"),
   de=("Neuer Ordner",), es=("Nueva carpeta",), pt=("Nova pasta",), zh=("新建文件夹",))
_e("newFolderFromSelection", "button", "New Folder from Selection",
   "Νέος Φάκελος από την Επιλογή",
   ids=("NewFolderFromSelection",))
_e("newGroup", "button", "New Group", "Νέα Ομάδα",
   ids=("NewGroup", "CreateGroup"),
   de=("Neue Gruppe",), es=("Nuevo grupo",), pt=("Novo grupo",))
_e("smartGroup", "button", "Smart Group", "Έξυπνη Ομάδα",
   ids=("SmartGroup",),
   de=("Smarte Gruppe",), es=("Grupo inteligente",),
   hint="Combines existing groups with Boolean operators.")
_e("smartCode", "button", "Smart Code", "Έξυπνος Κωδικός",
   ids=("SmartCode",),
   de=("Smarter Kode",), es=("Código inteligente",),
   hint="Stored query that behaves like a code.")
_e("createSnapshotCode", "button", "Create Snapshot", "Δημιουργία Στιγμιότυπου Κωδικού",
   ids=("CreateSnapshotCode", "SnapshotCode"),
   contexts=("managerCodes", "queryTool"),
   hint="Freezes a smart code into a normal code.")
_e("createSnapshotGroup", "button", "Create Snapshot", "Δημιουργία στιγμιότυπου ομάδας",
   ids=("CreateSnapshotGroup", "SnapshotGroup"), contexts=("managerDocumentGroups",
   "managerCodeGroups", "managerMemoGroups", "managerNetworkGroups"),
   hint="Freezes a smart group into a normal group.")
_e("applyCodes", "button", "Apply Codes", "Εφαρμογή Κωδικών",
   ids=("ApplyCodes", "ApplyCoding", "Coding"),
   de=("Kodes anwenden", "Kodieren"), es=("Aplicar códigos",),
   pt=("Aplicar códigos",), zh=("应用代码",),
   hint="Codes the selected data segment with a new or existing code.",
   shortcut="Ctrl+J")
_e("codeInVivo", "button", "Code In Vivo", "Κωδικοποίηση In Vivo",
   ids=("CodeInVivo", "InVivo"),
   de=("In-Vivo kodieren",), es=("Codificar in vivo",),
   hint="Uses the selected text itself as the code name.")
_e("quickCoding", "button", "Quick Coding", "Γρήγορη Κωδικοποίηση",
   ids=("QuickCoding",),
   de=("Schnellkodierung",), es=("Codificación rápida",),
   hint="Applies the last used code.")
_e("editComment", "button", "Edit Comment", "Επεξεργασία Σχολίου",
   ids=("EditComment", "Comment"),
   de=("Kommentar bearbeiten",), es=("Editar comentario",),
   pt=("Editar comentário",), zh=("编辑注释",))
_e("edit", "button", "Edit", "Επεξεργασία", ids=("Edit",),
   de=("Bearbeiten",), es=("Editar",), pt=("Editar",), zh=("编辑",))
_e("rename", "button", "Rename", "Μετονομασία", ids=("Rename",),
   de=("Umbenennen",), es=("Renombrar",), pt=("Renomear",), zh=("重命名",))
_e("delete", "button", "Delete", "Διαγραφή", ids=("Delete", "Remove"),
   de=("Löschen",), es=("Eliminar", "Borrar"), pt=("Excluir", "Eliminar"), zh=("删除",))
_e("duplicate", "button", "Duplicate", "Δημιουργία αντιγράφου", ids=("Duplicate",),
   de=("Duplizieren",), es=("Duplicar",), pt=("Duplicar",))
_e("color", "button", "Color", "Χρώμα", ids=("Color", "Colour", "SetColor"),
   de=("Farbe",), es=("Color",), pt=("Cor",), zh=("颜色",))
_e("openNetwork", "button", "Open Network", "Άνοιγμα Δικτύου",
   ids=("OpenNetwork", "ShowInNetwork", "Network"),
   de=("Netzwerk öffnen",), es=("Abrir red",), pt=("Abrir rede",),
   hint="Opens an ad-hoc network on the selection.")
_e("groupButton", "button", "Group", "Ομάδα", ids=("GroupButton", "ShowGroups"),
   hint="Shows or hides the group side panel.")

# -----------------------------------------------------------------------------
# Search & Code tab
# -----------------------------------------------------------------------------
_e("textSearch", "button", "Text Search", "Αναζήτηση Κειμένου",
   ids=("TextSearch", "SearchText"),
   de=("Textsuche",), es=("Búsqueda de texto",), pt=("Pesquisa de texto",),
   zh=("文本搜索",),
   hint="Finds text and can auto-code the hits.")
_e("regexSearch", "button", "Regular Expression Search", "Αναζήτηση με Κανονική Έκφραση",
   ids=("RegexSearch", "RegularExpressionSearch", "Regex", "GREP"),
   de=("Regex-Suche",), es=("Búsqueda con expresiones regulares",),
   hint="Expert search using GREP patterns.")
_e("namedEntityRecognition", "button", "Named Entity Recognition",
   "Αναγνώριση Ονομαστικών Οντοτήτων",
   ids=("NamedEntityRecognition", "NER"),
   de=("Named Entity Recognition",), es=("Reconocimiento de entidades nombradas",),
   hint="Finds people, organisations and places automatically.")
_e("sentimentAnalysis", "button", "Sentiment Analysis", "Ανάλυση Συναισθήματος",
   ids=("SentimentAnalysis", "Sentiment"),
   de=("Sentiment-Analyse",), es=("Análisis de sentimiento",),
   pt=("Análise de sentimento",), zh=("情感分析",),
   hint="Codes positive, negative and neutral passages.")
_e("findConcepts", "button", "Find Concepts", "Εύρεση Εννοιών",
   ids=("FindConcepts", "Concepts", "Concept"),
   de=("Konzepte finden",), es=("Encontrar conceptos",))
_e("opinionMining", "button", "Opinion Mining", "Εξόρυξη Απόψεων",
   ids=("OpinionMining",),
   de=("Opinion Mining",), es=("Minería de opiniones",))
_e("aiCoding", "button", "AI Coding", "Κωδικοποίηση με Τεχνητή Νοημοσύνη",
   ids=("AICoding",),
   de=("KI-Kodierung",), es=("Codificación con IA",), zh=("AI 编码",),
   hint="Suggests codings automatically.")
_e("intentionalAICoding", "button", "Intentional AI Coding",
   "Στοχευμένη Κωδικοποίηση με Τεχνητή Νοημοσύνη",
   ids=("IntentionalAICoding",),
   hint="AI coding guided by your own research question.")
_e("aiSummaries", "button", "AI Summaries", "Περιλήψεις με Τεχνητή Νοημοσύνη",
   ids=("AISummaries", "AISummary"),
   de=("KI-Zusammenfassungen",), es=("Resúmenes con IA",))
_e("conversationalAI", "button", "Conversational AI", "Συνομιλιακή Τεχνητή Νοημοσύνη",
   ids=("ConversationalAI",),
   hint="Natural-language questions about your documents.")
_e("autoCode", "button", "Auto Code", "Αυτόματη Κωδικοποίηση",
   ids=("AutoCode", "AutoCoding"),
   de=("Auto-Kodierung",), es=("Autocodificación",))
_e("focusGroupCoding", "button", "Focus Group Coding", "Κωδικοποίηση Ομάδας Εστίασης",
   ids=("FocusGroupCoding", "FocusGroup"),
   hint="Auto-codes speaker units in focus group transcripts.")
_e("wordCloud", "button", "Word Cloud", "Νέφος Λέξεων",
   ids=("WordCloud", "Cloud"),
   de=("Wortwolke",), es=("Nube de palabras",), pt=("Nuvem de palavras",),
   zh=("词云",),
   visualOnly=True, companion="wordList",
   concept=(
       "The same words shown in the Word List, drawn so that more frequent "
       "words appear larger, in an arbitrary layout with no reading order.",
       "Οι ίδιες λέξεις που εμφανίζονται στη Λίστα Λέξεων, σχεδιασμένες "
       "έτσι ώστε οι πιο συχνές λέξεις να εμφανίζονται μεγαλύτερες, σε "
       "τυχαία διάταξη χωρίς σειρά ανάγνωσης.",
   ))
_e("wordList", "button", "Word List", "Λίστα Λέξεων",
   ids=("WordList", "WordFrequencies", "Words"),
   de=("Wortliste",), es=("Lista de palabras",), pt=("Lista de palavras",))
_e("stopList", "button", "Stop list", "Λίστα αποκλεισμού λέξεων", ids=("StopList",))
_e("goList", "button", "Go list", "Λίστα επιτρεπόμενων λέξεων", ids=("GoList",))
_e("typeTokenRatio", "button", "Type-Token Ratio", "Λόγος Τύπων προς Λεκτικές Μονάδες",
   ids=("TypeTokenRatio",))

# -----------------------------------------------------------------------------
# Analyze tab
# -----------------------------------------------------------------------------
_e("codeDocumentTable", "button", "Code-Document Table", "Πίνακας Κωδικών-Εγγράφων",
   ids=("CodeDocumentTable", "CodeDocumentAnalysis"),
   de=("Kode-Dokument-Tabelle",), es=("Tabla de códigos y documentos",),
   hint="Cross-tabulates code frequencies by document.")
_e("codeCooccurrenceTable", "button", "Code Co-Occurrence Table",
   "Πίνακας Συνεμφάνισης Κωδικών",
   ids=("CodeCooccurrenceTable", "CoOccurrenceTable", "ShowCooccurrences"),
   de=("Kode-Kookkurrenz-Tabelle",), es=("Tabla de co-ocurrencia de códigos",),
   hint="Shows which codes are applied to the same data.")
_e("codeCooccurrenceExplorer", "button", "Code Co-Occurrence Explorer",
   "Εξερευνητής Συνεμφάνισης Κωδικών",
   ids=("CodeCooccurrenceExplorer",),
   visualOnly=True, companion="codeCooccurrenceTable",
   concept=(
       "A visual map of which codes tend to occur together, drawn as "
       "connected shapes rather than a list.",
       "Ένας οπτικός χάρτης του ποιοι κωδικοί τείνουν να συνεμφανίζονται, "
       "σχεδιασμένος ως συνδεδεμένα σχήματα αντί για λίστα.",
   ))
_e("codeDistribution", "button", "Code Distribution", "Κατανομή Κωδικών",
   ids=("CodeDistribution",))
_e("globalFilter", "button", "Global Filter", "Καθολικό Φίλτρο",
   ids=("GlobalFilter", "SetGlobalFilter"),
   de=("Globaler Filter",), es=("Filtro global",), pt=("Filtro global",),
   hint="Filters the whole project, not just the current list.")
_e("clearGlobalFilter", "button", "Clear Global Filter", "Καθαρισμός Καθολικού Φίλτρου",
   ids=("ClearGlobalFilter", "RemoveGlobalFilter"))
_e("localFilter", "button", "Filter", "Φίλτρο",
   ids=("Filter", "LocalFilter"),
   de=("Filter",), es=("Filtro",), pt=("Filtro",), zh=("筛选", "过滤"))
_e("interCoderAgreement", "button", "Inter-Coder Agreement", "Συμφωνία Μεταξύ Κωδικοποιητών",
   ids=("InterCoderAgreement", "ICA"),
   de=("Intercoder-Übereinstimmung",), es=("Acuerdo entre codificadores",),
   hint="Measures how consistently coders applied the same codes.")
_e("sankeyDiagram", "button", "Sankey diagram", "Διάγραμμα Sankey", ids=("Sankey",),
   visualOnly=True, companion="codeCooccurrenceTable",
   concept=(
       "A flow diagram where the width of each ribbon between two entities "
       "shows how much coded data flows between them. No text alternative "
       "exists in Atlas.ti for this specific view; the Code Co-Occurrence "
       "Table covers similar ground in table form.",
       "Ένα διάγραμμα ροής όπου το πλάτος κάθε κορδέλας μεταξύ δύο "
       "οντοτήτων δείχνει πόσα κωδικοποιημένα δεδομένα ρέουν μεταξύ τους. "
       "Δεν υπάρχει ισοδύναμο κειμένου σε αυτή τη συγκεκριμένη προβολή στο "
       "Atlas.ti· ο Πίνακας Συνεμφάνισης Κωδικών καλύπτει παρόμοιο έδαφος "
       "σε μορφή πίνακα.",
   ))
_e("treemap", "button", "Treemap", "Δενδροχάρτης", ids=("Treemap",),
   visualOnly=True, companion="codeDocumentTable",
   concept=(
       "Nested rectangles sized by frequency or groundedness, with no "
       "reading order and no text labels exposed outside the shapes "
       "themselves.",
       "Εμφωλευμένα ορθογώνια με μέγεθος ανάλογο της συχνότητας ή της "
       "θεμελίωσης, χωρίς σειρά ανάγνωσης και χωρίς ετικέτες κειμένου "
       "εκτός από τα ίδια τα σχήματα.",
   ))
_e("barChart", "button", "Bar chart", "Ραβδόγραμμα", ids=("BarChart",),
   de=("Balkendiagramm",), es=("Gráfico de barras",),
   visualOnly=True, companion="codeDocumentTable",
   concept=(
       "Code frequencies drawn as bars of varying height rather than a "
       "list of numbers.",
       "Συχνότητες κωδικών σχεδιασμένες ως ράβδοι διαφορετικού ύψους αντί "
       "για λίστα αριθμών.",
   ))

# -----------------------------------------------------------------------------
# Import & Export tab
# -----------------------------------------------------------------------------
_e("importSurveyData", "button", "Import Survey Data", "Εισαγωγή Δεδομένων Έρευνας",
   ids=("ImportSurveyData", "SurveyImport"),
   de=("Umfragedaten importieren",), es=("Importar datos de encuesta",))
_e("importReferenceManager", "button", "Import Reference Manager Data",
   "Εισαγωγή Δεδομένων Διαχειριστή Βιβλιογραφίας",
   ids=("ImportReferenceManager", "EndNote", "BibTex", "Mendeley"),
   hint="Supports EndNote XML and BibTeX.")
_e("importSocialNetwork", "button", "Import Social Network Comments",
   "Εισαγωγή Σχολίων Κοινωνικών Δικτύων",
   ids=("ImportSocialNetworkComments",))
_e("importEvernote", "button", "Import from Evernote", "Εισαγωγή από Evernote",
   ids=("ImportEvernote",))
_e("importTranscripts", "button", "Import Transcripts", "Εισαγωγή Απομαγνητοφωνήσεων",
   ids=("ImportTranscripts",),
   de=("Transkripte importieren",), es=("Importar transcripciones",))
_e("importCodeList", "button", "Import Code List", "Εισαγωγή Λίστας Κωδικών",
   ids=("ImportCodeList", "ImportCodebook"),
   de=("Kodeliste importieren",), es=("Importar lista de códigos",))
_e("exportCodeList", "button", "Export Code List", "Εξαγωγή Λίστας Κωδικών",
   ids=("ExportCodeList", "ExportCodebook"))
_e("codebook", "button", "Code Book", "Βιβλίο Κωδικών", ids=("Codebook", "CodeBook"))
_e("importDocumentGroups", "button", "Import Document Groups", "Εισαγωγή Ομάδων Εγγράφων",
   ids=("ImportDocumentGroups",))
_e("exportDocumentGroups", "button", "Export Document Groups", "Εξαγωγή Ομάδων Εγγράφων",
   ids=("ExportDocumentGroups",))
_e("spssExport", "button", "SPSS Syntax Export", "Εξαγωγή Σύνταξης SPSS",
   ids=("SPSSExport", "SPSS"))
_e("genericExport", "button", "Generic Export", "Γενική Εξαγωγή",
   ids=("GenericExport",),
   hint="Spreadsheet export for R, SAS or STATA.")
_e("qdpxExport", "button", "QDPX Export", "Εξαγωγή QDPX",
   ids=("QDPX", "QDPXExport", "UniversalDataExchange"),
   hint="Universal exchange format for other QDA software.")
_e("exportDocuments", "button", "Export Documents", "Εξαγωγή Εγγράφων",
   ids=("ExportDocuments",))
_e("excelExport", "button", "Excel Export", "Εξαγωγή σε Excel",
   ids=("ExcelExport", "Excel"),
   de=("Excel-Export",), es=("Exportar a Excel",), pt=("Exportar para Excel",))
_e("report", "button", "Report", "Αναφορά",
   ids=("Report", "CreateReport"),
   de=("Bericht",), es=("Informe",), pt=("Relatório",), zh=("报告",),
   hint="Word, PDF or spreadsheet output of the current list.")
_e("export", "button", "Export", "Εξαγωγή",
   ids=("Export",),
   de=("Exportieren",), es=("Exportar",), pt=("Exportar",), zh=("导出",))
_e("importButton", "button", "Import", "Εισαγωγή",
   ids=("Import",),
   de=("Importieren",), es=("Importar",), pt=("Importar",), zh=("导入",))

# -----------------------------------------------------------------------------
# Tools tab
# -----------------------------------------------------------------------------
_e("userManagement", "button", "User Management", "Διαχείριση Χρηστών",
   ids=("UserManagement", "Users"),
   de=("Benutzerverwaltung",), es=("Gestión de usuarios",),
   pt=("Gestão de utilizadores",))
_e("projectSearchButton", "button", "Project Search", "Αναζήτηση Έργου",
   ids=("ProjectSearchButton", "SearchProjectButton"),
   hint="Searches names, comments and content of all entities; supports GREP.")
_e("redundantCodings", "button", "Find Redundant Codings", "Εύρεση Πλεοναζουσών Κωδικοποιήσεων",
   ids=("RedundantCodings", "RedundantCodingAnalyzer"),
   de=("Redundante Kodierungen finden",), es=("Buscar codificaciones redundantes",),
   hint="Finds overlapping quotations coded with the same code.")
_e("renumberDocuments", "button", "Renumber Documents", "Επαναρίθμηση Εγγράφων",
   ids=("RenumberDocuments",))
_e("renumberQuotations", "button", "Renumber Quotations", "Επαναρίθμηση Αποσπασμάτων",
   ids=("RenumberQuotations",))
_e("repairLink", "button", "Repair Link", "Επιδιόρθωση Σύνδεσης", ids=("RepairLink",))
_e("removeCodings", "button", "Remove Codings", "Αφαίρεση Κωδικοποιήσεων",
   ids=("RemoveCodings",))
_e("mergeQuotations", "button", "Merge Quotations", "Συγχώνευση Αποσπασμάτων",
   ids=("MergeQuotations",))
_e("mergeCodes", "button", "Merge Codes", "Συγχώνευση Κωδικών",
   ids=("MergeCodes",), de=("Kodes zusammenführen",), es=("Fusionar códigos",))
_e("splitCode", "button", "Split Code", "Διαχωρισμός Κωδικού",
   ids=("SplitCode",), de=("Kode aufteilen",), es=("Dividir código",))
_e("convertToDocument", "button", "Convert to Document", "Μετατροπή σε Έγγραφο",
   ids=("ConvertToDocument",),
   hint="Turns a memo into a codable project document.")
_e("browseGeoLocation", "button", "Browse Geo Location", "Περιήγηση Γεωγραφικής Θέσης",
   ids=("BrowseGeoLocation",))

# -----------------------------------------------------------------------------
# Links, relations and hyperlinks
# -----------------------------------------------------------------------------
_e("cutLink", "button", "Cut Link", "Κοπή Σύνδεσης", ids=("CutLink",))
_e("flipLink", "button", "Flip Link", "Αντιστροφή Σύνδεσης", ids=("FlipLink",))
_e("changeRelation", "button", "Change Relation", "Αλλαγή Σχέσης", ids=("ChangeRelation",))
_e("hyperlinkSource", "button", "Source", "Πηγή", ids=("Source",),
   de=("Quelle",), es=("Origen", "Fuente"), pt=("Origem",),
   hint="Start anchor of a hyperlink.")
_e("hyperlinkTarget", "button", "Target", "Στόχος", ids=("Target",),
   de=("Ziel",), es=("Destino",), pt=("Destino",),
   hint="End anchor of a hyperlink.")
_e("hyperlinks", "entity", "Hyperlinks", "Υπερσύνδεσμοι", ids=("Hyperlinks", "Hyperlink"),
   de=("Hyperlinks",), es=("Hipervínculos",), pt=("Hiperligações",))
_e("codeCodeLinks", "entity", "Code-Code Links", "Συνδέσεις Κωδικού-Κωδικού",
   ids=("CodeCodeLinks",))

# -----------------------------------------------------------------------------
# View options
# -----------------------------------------------------------------------------
_e("viewDetails", "view", "Details view", "Προβολή λεπτομερειών", ids=("Details",),
   de=("Details",), es=("Detalles",))
_e("viewSingleColumn", "view", "Single column view", "Προβολή μίας στήλης",
   ids=("SingleColumn",))
_e("viewList", "view", "List view", "Προβολή λίστας", ids=("ListView",),
   hint="The fully accessible view: a normal, readable list.")
_e("viewCloud", "view", "Cloud view", "Προβολή νέφους", ids=("ViewCloud", "CloudView"),
   visualOnly=True, companion="viewList",
   concept=(
       "The Code Manager's code list redrawn as a word-cloud-style graphic "
       "instead of a readable list. Switch back to List view (View button) "
       "to read the same codes as text.",
       "Η λίστα κωδικών του Διαχειριστή Κωδικών, σχεδιασμένη ξανά ως "
       "γραφικό τύπου νέφους λέξεων αντί για αναγνώσιμη λίστα. Επιστρέψτε "
       "στην Προβολή λίστας (κουμπί Προβολή) για να διαβάσετε τους ίδιους "
       "κωδικούς ως κείμενο.",
   ))
_e("viewCodeBarChart", "view", "Bar chart view", "Προβολή ραβδογράμματος",
   ids=("ViewBarChart", "BarChartView"),
   visualOnly=True, companion="viewList",
   concept=(
       "The Code Manager's code list redrawn as bars sized by frequency "
       "instead of a readable list. Switch back to List view (View button) "
       "to read the same codes as text.",
       "Η λίστα κωδικών του Διαχειριστή Κωδικών, σχεδιασμένη ξανά ως ράβδοι "
       "ανάλογες της συχνότητας αντί για αναγνώσιμη λίστα. Επιστρέψτε στην "
       "Προβολή λίστας (κουμπί Προβολή) για να διαβάσετε τους ίδιους "
       "κωδικούς ως κείμενο.",
   ))
_e("viewTreemapMode", "view", "Treemap view", "Προβολή δενδροχάρτη",
   ids=("ViewTreemap", "TreemapView"),
   visualOnly=True, companion="viewList",
   concept=(
       "The Document Manager's document list redrawn as nested rectangles "
       "instead of a readable list. Switch back to List view (View button) "
       "to read the same documents as text.",
       "Η λίστα εγγράφων του Διαχειριστή Εγγράφων, σχεδιασμένη ξανά ως "
       "εμφωλευμένα ορθογώνια αντί για αναγνώσιμη λίστα. Επιστρέψτε στην "
       "Προβολή λίστας (κουμπί Προβολή) για να διαβάσετε τα ίδια έγγραφα "
       "ως κείμενο.",
   ))
_e("dock", "button", "Dock", "Αγκύρωση", ids=("Dock",),
   de=("Andocken",), es=("Acoplar",),
   hint="Attaches a floating window to the main window.")
_e("float", "button", "Float", "Αποσύνδεση παραθύρου", ids=("Float",),
   de=("Schweben",), es=("Flotante",))
_e("alwaysOnTop", "button", "Always On Top", "Πάντα σε πρώτο πλάνο", ids=("AlwaysOnTop",),
   de=("Immer im Vordergrund",))
_e("goToContext", "button", "Go to Context", "Μετάβαση στο περιβάλλον",
   ids=("GoToContext", "ViewInContext"),
   hint="Shows the quotation inside its original document.")
_e("newTabGroup", "button", "New Tab Group", "Νέα Ομάδα Καρτελών", ids=("NewTabGroup",))

# -----------------------------------------------------------------------------
# ATLAS.ti 26 manager panes, filters and context-menu commands
# -----------------------------------------------------------------------------
_MANAGER_CONTEXTS = (
    "managerDocuments", "managerQuotations", "managerCodes", "managerMemos",
    "managerNetworks", "managerLinks", "managerRelations",
    "managerDocumentGroups", "managerCodeGroups", "managerMemoGroups",
    "managerNetworkGroups",
)

_e("managerDiagramView", "button", "Diagram", "Διάγραμμα",
   ids=("ManagerDiagramView", "SegmentDiagram"), contexts=_MANAGER_CONTEXTS,
   controlType="radioButton")
_e("managerPreviewView", "button", "Preview", "Προεπισκόπηση",
   ids=("ManagerPreviewView", "SegmentPreview"), contexts=_MANAGER_CONTEXTS,
   controlType="radioButton")
_e("managerCommentView", "button", "Comment", "Σχόλιο",
   ids=("ManagerCommentView", "SegmentComment"), contexts=_MANAGER_CONTEXTS,
   controlType="radioButton")
_e("managerCommentEditor", "field", "Comment field", "Πεδίο σχολίου",
   ids=("ManagerCommentEditorField", "EntityCommentEditor"), contexts=_MANAGER_CONTEXTS)
_e("memoContentPane", "panel", "Memo content pane", "Πλαίσιο περιεχομένου σημειώματος",
   ids=("MemoContentPane", "MemoEditorPane"), contexts=("managerMemos",))
_e("managerSplitBar", "panel", "Split bar", "Διαχωριστική γραμμή",
   ids=("ManagerSplitBar", "ManagerSplitter"), contexts=_MANAGER_CONTEXTS)
_e("managerGroupPanel", "panel", "Group panel", "Πλαίσιο ομάδων",
   ids=("ManagerGroupPanel", "EntityGroupPanel"), contexts=_MANAGER_CONTEXTS)
_e("managerListPane", "panel", "Manager list pane", "Πλαίσιο λίστας διαχειριστή",
   ids=("ManagerListPane", "EntityListPane"), contexts=_MANAGER_CONTEXTS)

_e("filterToday", "button", "Today", "Σήμερα", ids=("FilterToday",),
   contexts=_MANAGER_CONTEXTS, controlType="checkBox")
_e("filterThisWeek", "button", "This week", "Αυτή την εβδομάδα",
   ids=("FilterThisWeek",), contexts=_MANAGER_CONTEXTS, controlType="checkBox")
_e("filterOnlyMine", "button", "Only mine", "Μόνο τα δικά μου",
   ids=("FilterOnlyMine",), contexts=_MANAGER_CONTEXTS, controlType="checkBox")
_e("filterCommented", "button", "Commented", "Με σχόλιο",
   ids=("FilterCommented",), contexts=_MANAGER_CONTEXTS, controlType="checkBox")
_e("clearFilter", "button", "Clear filter", "Εκκαθάριση φίλτρου",
   ids=("ClearManagerFilter",), contexts=_MANAGER_CONTEXTS)

_e("menuUnlink", "button", "Unlink", "Αποσύνδεση", ids=("ContextUnlink",),
   contexts=_MANAGER_CONTEXTS, controlType="menuItem")
_e("menuChangeColor", "button", "Change Color", "Αλλαγή χρώματος",
   ids=("ContextChangeColor",), contexts=_MANAGER_CONTEXTS, controlType="menuItem")
_e("menuRemoveColor", "button", "Remove Color", "Αφαίρεση χρώματος",
   ids=("ContextRemoveColor",), contexts=_MANAGER_CONTEXTS, controlType="menuItem")
_e("menuAppliedCodes", "button", "Applied Codes", "Εφαρμοσμένοι κωδικοί",
   ids=("ContextAppliedCodes",), contexts=("managerQuotations",), controlType="menuItem")
_e("menuRemoveAppliedCodes", "button", "Remove Applied Codes",
   "Αφαίρεση εφαρμοσμένων κωδικών", ids=("ContextRemoveAppliedCodes",),
   contexts=("managerQuotations",), controlType="menuItem")
_e("menuShowHideGroups", "button", "Show/Hide Groups", "Εμφάνιση/Απόκρυψη ομάδων",
   ids=("ContextShowHideGroups",), contexts=_MANAGER_CONTEXTS, controlType="menuItem")
_e("menuDuplicateMemos", "button", "Duplicate Memo(s)",
   "Δημιουργία αντιγράφου σημειώματος ή σημειωμάτων",
   ids=("ContextDuplicateMemos",), contexts=("managerMemos",), controlType="menuItem")
_e("menuConvertMemoToDocument", "button", "Convert to Document",
   "Μετατροπή σε έγγραφο", ids=("ContextConvertMemoToDocument",),
   contexts=("managerMemos",), controlType="menuItem")
_e("menuMemoExport", "button", "Memo Export", "Εξαγωγή σημειώματος",
   ids=("ContextMemoExport",), contexts=("managerMemos",), controlType="menuItem")
_e("menuNetworkExcelExport", "button", "Network Export to Excel",
   "Εξαγωγή δικτύων σε Excel", ids=("ContextNetworkExcelExport",),
   contexts=("managerNetworks",), controlType="menuItem")
_e("showCodeCodeLinks", "button", "Code-Code Links", "Συνδέσεις κωδικού προς κωδικό",
   ids=("ShowCodeCodeLinks",), contexts=("managerLinks",), controlType="radioButton")
_e("showHyperlinks", "button", "Hyperlinks", "Υπερσυνδέσεις",
   ids=("ShowHyperlinks",), contexts=("managerLinks",), controlType="radioButton")
_e("relationCategory", "button", "Category", "Κατηγορία",
   ids=("RelationCategory",), contexts=("managerRelations",))
_e("showCodeRelations", "button", "Code-Code Relations", "Σχέσεις κωδικού προς κωδικό",
   ids=("ShowCodeRelations",), contexts=("managerRelations",), controlType="radioButton")
_e("showHyperlinkRelations", "button", "Hyperlink Relations", "Σχέσεις υπερσυνδέσεων",
   ids=("ShowHyperlinkRelations",), contexts=("managerRelations",), controlType="radioButton")
_e("newRelation", "button", "New Relation", "Νέα σχέση", ids=("NewRelation",),
   contexts=("managerRelations",))
_e("relationStyle", "button", "Style", "Στυλ", ids=("RelationStyleButton",),
   contexts=("managerRelations",))
_e("relationProperty", "button", "Property", "Ιδιότητα",
   ids=("RelationPropertyButton",), contexts=("managerRelations",))
_e("groupMembersPane", "panel", "Items in group", "Στοιχεία στην ομάδα",
   ids=("GroupMembersPane",), contexts=("managerDocumentGroups", "managerCodeGroups",
                                         "managerMemoGroups", "managerNetworkGroups"))
_e("groupNonMembersPane", "panel", "Items not in group", "Στοιχεία εκτός ομάδας",
   ids=("GroupNonMembersPane",), contexts=("managerDocumentGroups", "managerCodeGroups",
                                            "managerMemoGroups", "managerNetworkGroups"))
_e("addToGroup", "button", "Add to group", "Προσθήκη στην ομάδα",
   ids=("AddToGroup", "MoveLeftIntoGroup"), contexts=("managerDocumentGroups",
   "managerCodeGroups", "managerMemoGroups", "managerNetworkGroups"))
_e("removeFromGroup", "button", "Remove from group", "Αφαίρεση από την ομάδα",
   ids=("RemoveFromGroup", "MoveRightOutOfGroup"), contexts=("managerDocumentGroups",
   "managerCodeGroups", "managerMemoGroups", "managerNetworkGroups"))
_e("exitEditMode", "button", "Exit Edit Mode", "Έξοδος από τη λειτουργία επεξεργασίας",
   ids=("ExitEditMode",), contexts=("managerDocuments", "managerMemos"))
_e("importFiles", "button", "Import Files", "Εισαγωγή αρχείων",
   ids=("ImportFiles",), contexts=("managerDocuments",))
_e("importFolderContents", "button", "Import Folder Contents",
   "Εισαγωγή περιεχομένων φακέλου", ids=("ImportFolderContents",),
   contexts=("managerDocuments",))
_e("referenceExternalMultimedia", "button", "Reference External Multimedia Documents",
   "Αναφορά εξωτερικών εγγράφων πολυμέσων", ids=("ReferenceExternalMultimedia",),
   contexts=("managerDocuments",))
_e("addGeoDocuments", "button", "Add Geo Documents", "Προσθήκη γεωγραφικών εγγράφων",
   ids=("AddGeoDocuments",), contexts=("managerDocuments",))

# -----------------------------------------------------------------------------
# Welcome screen and Quotation Reader
# -----------------------------------------------------------------------------
_e("welcomeLicensePane", "panel", "License information pane", "Πλαίσιο πληροφοριών άδειας",
   ids=("WelcomeLicensePane",), contexts=("welcomeScreen",))
_e("welcomeProjectListPane", "panel", "Project list pane", "Πλαίσιο λίστας έργων",
   ids=("WelcomeProjectListPane",), contexts=("welcomeScreen",))
_e("welcomeResourcesPane", "panel", "Resources pane", "Πλαίσιο πόρων",
   ids=("WelcomeResourcesPane",), contexts=("welcomeScreen",))
_e("welcomeNews", "button", "News", "Νέα", ids=("WelcomeNews",),
   contexts=("welcomeScreen",))
_e("welcomeResources", "button", "Resources", "Πόροι", ids=("WelcomeResources",),
   contexts=("welcomeScreen",))
_e("sampleProjects", "button", "Sample Projects", "Δείγματα έργων",
   ids=("SampleProjects",), contexts=("welcomeScreen",))
_e("showAllProjects", "button", "Show All Projects", "Εμφάνιση όλων των έργων",
   ids=("ShowAllProjects",), contexts=("welcomeScreen",), controlType="menuItem")
_e("hideProject", "button", "Hide Project", "Απόκρυψη έργου",
   ids=("HideWelcomeProject",), contexts=("welcomeScreen",), controlType="menuItem")
_e("pinToFavorites", "button", "Pin to Favorites", "Καρφίτσωμα στα αγαπημένα",
   ids=("PinProjectToFavorites",), contexts=("welcomeScreen",), controlType="menuItem")
_e("unpinFromFavorites", "button", "Unpin from Favorites",
   "Ξεκαρφίτσωμα από τα αγαπημένα", ids=("UnpinProjectFromFavorites",),
   contexts=("welcomeScreen",), controlType="menuItem")
_e("collapseResources", "button", "Collapse resources", "Σύμπτυξη πόρων",
   ids=("CollapseWelcomeResources",), contexts=("welcomeScreen",))
_e("expandResources", "button", "Expand resources", "Ανάπτυξη πόρων",
   ids=("ExpandWelcomeResources",), contexts=("welcomeScreen",))

_e("quotationReaderView", "panel", "Quotation Reader content pane",
   "Πλαίσιο περιεχομένου Αναγνώστη Αποσπασμάτων", ids=("QuotationReaderContentPane",),
   contexts=("quotationReader",))
_e("quotationSingleLine", "button", "Single Line", "Μία γραμμή",
   ids=("QuotationReaderSingleLine",), contexts=("quotationReader",),
   controlType="radioButton")
_e("quotationSmallPreview", "button", "Small Preview", "Μικρή προεπισκόπηση",
   ids=("QuotationReaderSmallPreview",), contexts=("quotationReader",),
   controlType="radioButton")
_e("quotationLargePreview", "button", "Large Preview", "Μεγάλη προεπισκόπηση",
   ids=("QuotationReaderLargePreview",), contexts=("quotationReader",),
   controlType="radioButton")
_e("quotationNameField", "field", "Quotation Name", "Όνομα αποσπάσματος",
   ids=("QuotationReaderName",), contexts=("quotationReader",))
_e("quotationCommentField", "field", "Quotation Comment", "Σχόλιο αποσπάσματος",
   ids=("QuotationReaderComment",), contexts=("quotationReader",))
_e("removeCodes", "button", "Remove Codes", "Αφαίρεση κωδικών",
   ids=("QuotationReaderRemoveCodes",), contexts=("quotationReader",))
_e("quotationReaderContextButton", "button", "View in Context", "Προβολή στο περιβάλλον",
   ids=("QuotationReaderViewInContext",), contexts=("quotationReader",))

# -----------------------------------------------------------------------------
# Search, query, report, import and confirmation dialogs
# -----------------------------------------------------------------------------
_e("importDialog", "dialog", "Import dialog", "Παράθυρο διαλόγου εισαγωγής",
   ids=("ImportDialog", "ImportCodebookDialog"))
_e("searchDialog", "dialog", "Search dialog", "Παράθυρο διαλόγου αναζήτησης",
   ids=("SearchDialog", "TextSearchDialog"))
_e("queryDialog", "dialog", "Query dialog", "Παράθυρο διαλόγου ερωτήματος",
   ids=("QueryDialog", "QueryBuilderDialog"))
_e("reportDialog", "dialog", "Report dialog", "Παράθυρο διαλόγου αναφοράς",
   ids=("ReportDialog", "QueryReportDialog"))
_e("confirmationDialog", "dialog", "Confirmation dialog", "Παράθυρο διαλόγου επιβεβαίωσης",
   ids=("ConfirmationDialog", "ConfirmDialog", "MessageBoxDialog"))
_e("searchResultsPane", "panel", "Search results pane", "Πλαίσιο αποτελεσμάτων αναζήτησης",
   ids=("SearchResultsPane",), contexts=("searchDialog", "projectSearchWindow"))
_e("queryOperandsPane", "panel", "Query operands pane", "Πλαίσιο τελεστών ερωτήματος",
   ids=("QueryOperandsPane",), contexts=("queryTool", "queryDialog"))
_e("queryExpressionPane", "panel", "Query expression pane", "Πλαίσιο έκφρασης ερωτήματος",
   ids=("QueryExpressionPane",), contexts=("queryTool", "queryDialog"))
_e("queryResultsPane", "panel", "Query results pane", "Πλαίσιο αποτελεσμάτων ερωτήματος",
   ids=("QueryResultsPane",), contexts=("queryTool", "queryDialog"))
_e("queryScopePane", "panel", "Scope pane", "Πλαίσιο πεδίου εφαρμογής",
   ids=("QueryScopePane",), contexts=("queryTool", "queryDialog"))
_e("useGrep", "button", "Use GREP", "Χρήση GREP", ids=("UseGrep",),
   contexts=("searchDialog", "projectSearchWindow"), controlType="checkBox")
_e("caseSensitive", "button", "Case Sensitive", "Διάκριση πεζών και κεφαλαίων",
   ids=("CaseSensitive",), contexts=("searchDialog", "projectSearchWindow"),
   controlType="checkBox")
_e("showNone", "button", "Show None", "Αποεπιλογή όλων", ids=("ShowNone",),
   contexts=("searchDialog", "projectSearchWindow"))
_e("editScope", "button", "Edit Scope", "Επεξεργασία πεδίου εφαρμογής",
   ids=("EditQueryScope",), contexts=("queryTool", "queryDialog"))
_e("saveSmartCode", "button", "Save Smart Code", "Αποθήκευση έξυπνου κωδικού",
   ids=("SaveSmartCode",), contexts=("queryTool", "queryDialog"))
_e("reportList", "button", "List", "Λίστα", ids=("ReportList",),
   contexts=("reportDialog",), controlType="radioButton")
_e("reportListComments", "button", "List with Comments", "Λίστα με σχόλια",
   ids=("ReportListComments",), contexts=("reportDialog",), controlType="radioButton")
_e("reportFullContent", "button", "Full Content", "Πλήρες περιεχόμενο",
   ids=("ReportFullContent",), contexts=("reportDialog",), controlType="radioButton")
_e("reportContentComments", "button", "Content plus Comments", "Περιεχόμενο και σχόλια",
   ids=("ReportContentComments",), contexts=("reportDialog",), controlType="radioButton")
_e("dataContainsHeaders", "button", "My Data Contains Headers",
   "Τα δεδομένα μου περιέχουν επικεφαλίδες", ids=("DataContainsHeaders",),
   contexts=("importDialog",), controlType="checkBox")
_e("updateExistingCodes", "button", "Update Existing Codes",
   "Ενημέρωση υπαρχόντων κωδικών", ids=("UpdateExistingCodes",),
   contexts=("importDialog",), controlType="checkBox")
_e("dialogContinue", "button", "Continue", "Συνέχεια", ids=("DialogContinue",),
   contexts=("importDialog", "searchDialog", "queryDialog", "reportDialog",
             "confirmationDialog"))
_e("dialogCreate", "button", "Create", "Δημιουργία", ids=("DialogCreate",),
   contexts=("importDialog", "queryDialog"))
_e("dialogImport", "button", "Import", "Εισαγωγή", ids=("DialogImport",),
   contexts=("importDialog",))
_e("dialogCancel", "button", "Cancel", "Ακύρωση", ids=("DialogCancel",),
   contexts=("importDialog", "searchDialog", "queryDialog", "reportDialog",
             "confirmationDialog"))
_e("dialogYes", "button", "Yes", "Ναι", ids=("DialogYes",),
   contexts=("confirmationDialog",))
_e("dialogNo", "button", "No", "Όχι", ids=("DialogNo",),
   contexts=("confirmationDialog",))
_e("dialogOk", "button", "OK", "Εντάξει", ids=("DialogOK",),
   contexts=("importDialog", "searchDialog", "queryDialog", "reportDialog",
             "confirmationDialog"))

_e("colLastModified", "column", "Last Modified", "Τελευταία τροποποίηση",
   ids=("WelcomeLastModifiedColumn",), contexts=("welcomeScreen",))
_e("colLastUsed", "column", "Last Used", "Τελευταία χρήση",
   ids=("WelcomeLastUsedColumn",), contexts=("welcomeScreen",))
_e("colCloudStatus", "column", "Cloud Status", "Κατάσταση νέφους",
   ids=("WelcomeCloudStatusColumn",), contexts=("welcomeScreen",))

# -----------------------------------------------------------------------------
# Manager list columns
# -----------------------------------------------------------------------------
_e("colId", "column", "ID", "Αναγνωριστικό", ids=("ID", "Id"),
   hint="For quotations, document number colon quotation number.")
_e("colName", "column", "Name", "Όνομα", ids=("Name",),
   de=("Name",), es=("Nombre",), pt=("Nome",), zh=("名称",))
_e("colLocation", "column", "Location", "Τοποθεσία", ids=("Location",),
   de=("Speicherort",), es=("Ubicación",), pt=("Localização",))
_e("colGrounded", "column", "Grounded", "Θεμελίωση", ids=("Grounded", "Groundedness"),
   de=("Verankerung",), es=("Fundamentación",),
   hint="How many quotations are linked to this code.")
_e("colDensity", "column", "Density", "Πυκνότητα", ids=("Density",),
   de=("Dichte",), es=("Densidad",), pt=("Densidade",),
   hint="How many links this entity has to other entities.")
_e("colDegree", "column", "Degree", "Βαθμός", ids=("Degree",),
   hint="Number of nodes in a network.")
_e("colAuthor", "column", "Created by", "Δημιουργήθηκε από",
   ids=("CreatedBy", "Author"),
   de=("Erstellt von", "Autor"), es=("Creado por",), pt=("Criado por",))
_e("colModifiedBy", "column", "Modified by", "Τροποποιήθηκε από", ids=("ModifiedBy",),
   de=("Geändert von",), es=("Modificado por",))
_e("colCreated", "column", "Created", "Δημιουργήθηκε", ids=("Created",),
   de=("Erstellt",), es=("Creado",), pt=("Criado",))
_e("colModified", "column", "Modified", "Τροποποιήθηκε", ids=("Modified",),
   de=("Geändert",), es=("Modificado",), pt=("Modificado",))
_e("colComment", "column", "Comment", "Σχόλιο", ids=("CommentColumn",),
   de=("Kommentar",), es=("Comentario",), pt=("Comentário",), zh=("注释",))
_e("colType", "column", "Type", "Τύπος", ids=("Type",),
   de=("Typ",), es=("Tipo",), pt=("Tipo",), zh=("类型",))
_e("colReference", "column", "Reference", "Αναφορά", ids=("Reference",),
   de=("Referenz",), es=("Referencia",),
   hint="Where the quotation sits in its document.")
_e("colStart", "column", "Start", "Έναρξη", ids=("Start",), de=("Anfang",), es=("Inicio",))
_e("colEnd", "column", "End", "Λήξη", ids=("End",), de=("Ende",), es=("Fin",))
_e("colExtent", "column", "Extent", "Έκταση", ids=("Extent",),
   de=("Umfang",), es=("Extensión",))
_e("colUsage", "column", "Usage", "Χρήση", ids=("Usage",))
_e("colStyle", "column", "Style", "Στυλ", ids=("Style",), de=("Stil",), es=("Estilo",))
_e("colFormalProperty", "column", "Formal Property", "Τυπική Ιδιότητα",
   ids=("FormalProperty", "Property"),
   hint="Symmetric or asymmetric relation.")
_e("colRelation", "column", "Relation", "Σχέση", ids=("Relation",),
   de=("Relation",), es=("Relación",), pt=("Relação",))
_e("colColor", "column", "Color", "Χρώμα", ids=("ColorColumn",))
_e("colMediaType", "column", "Media type", "Τύπος πολυμέσων", ids=("MediaType",))
_e("colSource", "column", "Source", "Πηγή", ids=("SourceColumn",),
   contexts=("managerLinks",))
_e("colTarget", "column", "Target", "Στόχος", ids=("TargetColumn",),
   contexts=("managerLinks",))

# -----------------------------------------------------------------------------
# Query operators
# -----------------------------------------------------------------------------
_e("opAnd", "operator", "AND", "ΚΑΙ", ids=("AND",), hint="All conditions are true.")
_e("opOr", "operator", "OR", "Ή", ids=("OR",), hint="At least one condition is true.")
_e("opOneOf", "operator", "ONE OF", "ΕΝΑ ΑΠΟ", ids=("ONEOF",),
   hint="Exactly one condition is true.")
_e("opNot", "operator", "NOT", "ΟΧΙ", ids=("NOT",), hint="None of the conditions is true.")
_e("opWithin", "operator", "WITHIN", "ΕΝΤΟΣ", ids=("WITHIN",))
_e("opEnclosing", "operator", "ENCLOSING", "ΠΕΡΙΚΛΕΙΕΙ", ids=("ENCLOSING",))
_e("opOverlapping", "operator", "OVERLAPPING", "ΕΠΙΚΑΛΥΠΤΕΤΑΙ", ids=("OVERLAPPING",))
_e("opCooccur", "operator", "CO-OCCUR", "ΣΥΝΕΜΦΑΝΙΖΕΤΑΙ", ids=("COOCCUR",))
_e("opFollows", "operator", "FOLLOWS", "ΑΚΟΛΟΥΘΕΙ", ids=("FOLLOWS",))

# -----------------------------------------------------------------------------
# Help tab
# -----------------------------------------------------------------------------
_e("userManual", "button", "User Manual", "Εγχειρίδιο Χρήσης", ids=("UserManual", "Manual"),
   de=("Handbuch",), es=("Manual del usuario",))
_e("quickTour", "button", "Quick Tour", "Γρήγορη Ξενάγηση", ids=("QuickTour",))
_e("videoTutorials", "button", "Video Tutorials", "Βίντεο Οδηγοί", ids=("VideoTutorials",))
_e("support", "button", "Support", "Υποστήριξη", ids=("Support",),
   de=("Support",), es=("Soporte",))
_e("about", "button", "About", "Σχετικά", ids=("About",),
   de=("Über",), es=("Acerca de",), pt=("Sobre",))
_e("checkForUpdates", "button", "Check for Updates", "Έλεγχος για ενημερώσεις",
   ids=("CheckForUpdates", "LiveUpdate"))


# =============================================================================
# DOCUMENTATION-DERIVED ATLAS.TI 26 SURFACE TREE
# =============================================================================

MANUAL_VERSION = "26.1.1+34607"
MANUAL_ROOT = "https://manuals.atlasti.com/Win/en/manual/"

# This is a semantic tree reconstructed from the official manual. It is not
# presented as the Windows UI Automation tree: roles, AutomationIds, class
# names and exact child order still require a live Windows capture. The keys
# point into ELEMENTS so the same bilingual catalogue drives documentation,
# resolution, capture comparison and tests.
DOCUMENTED_SURFACES = {
    "mainWindow": {
        "label": {"en": "ATLAS.ti project window", "el": "Παράθυρο έργου ATLAS.ti"},
        "source": MANUAL_ROOT + "Intro/IntroductionInterface.html",
        "children": (
            "titleBar", "quickAccessToolbar", "ribbon", "tabFile", "tabHome",
            "tabSearchCode", "tabAnalyze", "tabImportExport", "tabTools",
            "tabHelp", "projectNavigator", "workArea", "marginArea", "statusBar",
        ),
    },
    "welcome": {
        "label": {"en": "Welcome screen", "el": "Οθόνη υποδοχής"},
        "source": MANUAL_ROOT + "Intro/IntroductionStartingATLAS.tiWelcomeScreen.html",
        "root": "welcomeScreen",
        "children": (
            "welcomeLicensePane", "newProject", "importProject", "optionsDialog",
            "welcomeProjectListPane", "searchField", "colName", "colCreated",
            "colLastModified", "colLastUsed", "colCloudStatus", "showAllProjects",
            "hideProject", "openProject", "pinToFavorites", "unpinFromFavorites",
            "renameProject", "deleteProject", "welcomeResourcesPane", "welcomeNews",
            "welcomeResources", "userManual", "sampleProjects", "videoTutorials",
            "collapseResources", "expandResources",
        ),
    },
    "entityManagerCommon": {
        "label": {"en": "Common entity-manager structure", "el": "Κοινή δομή διαχειριστών οντοτήτων"},
        "source": MANUAL_ROOT + "Managers/EntityManagers.html",
        "children": (
            "tabSearchFilter", "tabView", "managerGroupPanel", "managerListPane",
            "managerCommentEditor", "managerPreviewView", "managerCommentView",
            "managerSplitBar", "statusBar", "searchField", "groupButton",
            "filterToday", "filterThisWeek", "filterOnlyMine", "filterCommented",
            "clearFilter", "globalFilterBar", "viewDetails", "viewSingleColumn",
            "viewList", "dock", "float", "alwaysOnTop",
        ),
    },
    "documentManager": {
        "label": {"en": "Document Manager", "el": "Διαχειριστής Εγγράφων"},
        "source": MANUAL_ROOT + "Managers/ManagersForDocuments.html",
        "root": "managerDocuments",
        "children": (
            "documents", "managerGroupPanel", "managerListPane", "previewPane",
            "managerCommentEditor", "importFiles", "importFolderContents", "newFolder",
            "newDocument", "importTranscripts", "referenceExternalMultimedia",
            "addGeoDocuments", "newGroup", "smartGroup", "editComment", "openNetwork",
            "rename", "delete", "codeDocumentTable", "report", "excelExport",
        ),
    },
    "quotationManager": {
        "label": {"en": "Quotation Manager", "el": "Διαχειριστής Αποσπασμάτων"},
        "source": MANUAL_ROOT + "Managers/ManagerForQuotations.html",
        "root": "managerQuotations",
        "children": (
            "quotations", "managerGroupPanel", "managerListPane", "managerPreviewView",
            "managerCommentView", "previewPane", "managerCommentEditor", "newFolder",
            "newFolderFromSelection", "newCode", "smartCode", "applyCodes", "codeInVivo",
            "quickCoding", "menuAppliedCodes", "menuRemoveAppliedCodes", "goToContext",
            "openNetwork", "rename", "delete", "report", "excelExport",
        ),
    },
    "codeManager": {
        "label": {"en": "Code Manager", "el": "Διαχειριστής Κωδικών"},
        "source": MANUAL_ROOT + "Managers/ManagerForCodes.html",
        "root": "managerCodes",
        "children": (
            "codes", "managerGroupPanel", "managerListPane", "managerDiagramView",
            "managerPreviewView", "managerCommentView", "diagramPane", "previewPane",
            "managerCommentEditor", "newCode", "newFolder", "newGroup", "smartGroup",
            "color", "mergeCodes", "splitCode", "openNetwork", "report", "excelExport",
            "viewList", "viewCloud", "viewCodeBarChart", "treemap",
        ),
    },
    "memoManager": {
        "label": {"en": "Memo Manager", "el": "Διαχειριστής Σημειωμάτων"},
        "source": MANUAL_ROOT + "Managers/ManagerForMemos.html",
        "root": "managerMemos",
        "children": (
            "memos", "managerGroupPanel", "managerListPane", "memoContentPane",
            "managerCommentEditor", "newMemo", "newFolder", "newGroup", "smartGroup",
            "edit", "editComment", "openNetwork", "rename", "delete",
            "menuDuplicateMemos", "menuConvertMemoToDocument", "report", "excelExport",
            "menuMemoExport", "managerMemoGroups",
        ),
    },
    "networkManager": {
        "label": {"en": "Network Manager", "el": "Διαχειριστής Δικτύων"},
        "source": MANUAL_ROOT + "Managers/ManagerForNetworks.html",
        "root": "managerNetworks",
        "children": (
            "networks", "managerGroupPanel", "managerListPane", "managerCommentEditor",
            "newNetwork", "newFolder", "newGroup", "smartGroup", "editComment",
            "openNetwork", "rename", "delete", "duplicate", "menuNetworkExcelExport",
            "managerNetworkGroups",
        ),
    },
    "linkManager": {
        "label": {"en": "Link Manager", "el": "Διαχειριστής Συνδέσεων"},
        "source": MANUAL_ROOT + "Managers/ManagerForLinks.html",
        "root": "managerLinks",
        "children": (
            "showCodeCodeLinks", "showHyperlinks", "managerGroupPanel", "managerListPane",
            "managerCommentEditor", "colSource", "colRelation", "colTarget", "colAuthor",
            "colModifiedBy", "colCreated", "colModified", "cutLink", "flipLink",
            "changeRelation", "editComment", "managerRelations", "localFilter",
            "filterToday", "filterThisWeek", "filterOnlyMine", "filterCommented",
            "openNetwork", "excelExport",
        ),
    },
    "relationManager": {
        "label": {"en": "Relation Manager", "el": "Διαχειριστής Σχέσεων"},
        "source": MANUAL_ROOT + "Managers/ManagerForRelations.html",
        "root": "managerRelations",
        "children": (
            "relationCategory", "showCodeRelations", "showHyperlinkRelations",
            "managerListPane", "managerCommentEditor", "colUsage", "colStyle",
            "colFormalProperty", "newRelation", "duplicate", "rename", "delete",
            "color", "relationStyle", "relationProperty", "excelExport", "viewDetails",
            "viewSingleColumn",
        ),
    },
    "groupManagers": {
        "label": {"en": "Entity Group Managers", "el": "Διαχειριστές ομάδων οντοτήτων"},
        "source": MANUAL_ROOT + "Groups/GroupsCreatingAndRenaming.html",
        "children": (
            "managerDocumentGroups", "managerCodeGroups", "managerMemoGroups",
            "managerNetworkGroups", "newGroup", "createSnapshotGroup", "rename", "delete",
            "groupMembersPane", "groupNonMembersPane", "addToGroup", "removeFromGroup",
        ),
    },
    "quotationReader": {
        "label": {"en": "Quotation Reader", "el": "Αναγνώστης Αποσπασμάτων"},
        "source": MANUAL_ROOT + "Quotations/QuotationReader.html",
        "root": "quotationReader",
        "children": (
            "quotationReaderView", "quotationSingleLine", "quotationSmallPreview",
            "quotationLargePreview", "quotationNameField", "quotationCommentField",
            "applyCodes", "removeCodes", "quotationReaderContextButton", "delete",
            "rename", "openNetwork", "selectAll",
        ),
    },
    "projectSearch": {
        "label": {"en": "Project Search", "el": "Αναζήτηση Έργου"},
        "source": MANUAL_ROOT + "Tools/ToolsProjectSearch.html",
        "root": "projectSearchWindow",
        "children": (
            "documents", "quotations", "codes", "memos", "comments", "searchField",
            "useGrep", "caseSensitive", "showNone", "searchResultsPane",
        ),
    },
    "queryTool": {
        "label": {"en": "Query Tool", "el": "Εργαλείο Ερωτημάτων"},
        "source": MANUAL_ROOT + "Querying/QueryTool.html",
        "root": "queryTool",
        "children": (
            "queryOperandsPane", "queryExpressionPane", "queryResultsPane", "opAnd",
            "opOr", "opOneOf", "opNot", "opWithin", "opEnclosing", "opOverlapping",
            "opCooccur", "opFollows", "editScope", "saveSmartCode", "report",
        ),
    },
    "queryScope": {
        "label": {"en": "Query scope region", "el": "Περιοχή πεδίου εφαρμογής ερωτήματος"},
        "source": MANUAL_ROOT + "Querying/QueryToolRestrictingAQuery.html",
        "root": "queryScopePane",
        "children": (
            "documents", "groups", "queryExpressionPane", "queryResultsPane", "delete",
            "editScope",
        ),
    },
    "queryReport": {
        "label": {"en": "Query report dialog", "el": "Παράθυρο αναφοράς ερωτήματος"},
        "source": MANUAL_ROOT + "Querying/QueryToolReports.html",
        "root": "reportDialog",
        "children": (
            "reportList", "reportListComments", "reportFullContent",
            "reportContentComments", "excelExport", "dialogOk", "dialogCancel",
        ),
    },
    "codebookImport": {
        "label": {"en": "Codebook import dialog", "el": "Παράθυρο εισαγωγής βιβλίου κωδικών"},
        "source": MANUAL_ROOT + "Codes/CodeImportExportCodeList.html",
        "root": "importDialog",
        "children": (
            "dataContainsHeaders", "updateExistingCodes", "dialogImport", "dialogCancel",
        ),
    },
    "confirmation": {
        "label": {"en": "Confirmation pop-up", "el": "Αναδυόμενο παράθυρο επιβεβαίωσης"},
        "source": MANUAL_ROOT + "Intro/IntroductionInterfaceSoftwareNavigation.html",
        "root": "confirmationDialog",
        "children": ("dialogYes", "dialogNo", "dialogOk", "dialogCancel", "dialogContinue"),
    },
}


def documentationSources(elementKey):
    """Official manual pages that document an element or its surface."""
    sources = []
    for surface in DOCUMENTED_SURFACES.values():
        if elementKey == surface.get("root") or elementKey in surface.get("children", ()):
            source = surface.get("source")
            if source and source not in sources:
                sources.append(source)
    return sources


def catalogueRecords():
    """Serializable bilingual catalogue used by capture reconciliation."""
    records = []
    for element in ELEMENTS.values():
        aliases = {"en": [element["en"]], "el": [element["el"]]}
        for language, values in element["loc"].items():
            aliases[language] = list(values)
        records.append({
            "key": element["key"],
            "kind": element["kind"],
            "controlType": controlType(element),
            "en": element["en"],
            "el": element["el"],
            "automationIds": list(element["ids"]),
            "aliases": aliases,
            "contexts": list(element.get("contexts") or ()),
            "documentation": documentationSources(element["key"]),
            "shortcut": element.get("shortcut"),
            "visualOnly": bool(element.get("visualOnly")),
        })
    return records


# =============================================================================
# LOOKUP INDEXES
# =============================================================================

_EXACT = {}          # normalised string -> [element keys], insertion ordered
_LOOSE = []          # (normalised token, element key), longest first
_LANG_TOKENS = {}    # language code -> {normalised token: element key}


def _addIndexEntry(text, key, language=None):
    normalized = normalize(text)
    if not normalized:
        return
    keys = _EXACT.setdefault(normalized, [])
    if key not in keys:
        keys.append(key)
    _LOOSE.append((normalized, key))
    if language:
        _LANG_TOKENS.setdefault(language, {}).setdefault(normalized, key)


def _buildIndexes():
    for key, element in ELEMENTS.items():
        _addIndexEntry(key, key)
        _addIndexEntry(element["en"], key, "en")
        _addIndexEntry(element["el"], key, "el")
        for identifier in element["ids"]:
            _addIndexEntry(identifier, key)
        for language, values in element["loc"].items():
            for value in values:
                _addIndexEntry(value, key, language)
    _LOOSE.sort(key=lambda item: len(item[0]), reverse=True)


_buildIndexes()


def exactCollisions():
    """All exact aliases shared by more than one canonical element."""
    return {
        token: list(keys)
        for token, keys in sorted(_EXACT.items())
        if len(keys) > 1
    }


def unresolvedCollisions():
    """Collision candidates that kind/context criteria cannot select.

    An empty result means every duplicate label has a deterministic route
    when the caller supplies the object's role and containing surface.
    """
    issues = []
    for token, keys in exactCollisions().items():
        for key in keys:
            element = ELEMENTS[key]
            selected = _select(
                keys,
                kind=element["kind"],
                context=element.get("contexts"),
            )
            if selected is None or selected["key"] != key:
                issues.append({
                    "normalisedLabel": token,
                    "key": key,
                    "selected": selected["key"] if selected else None,
                    "kind": element["kind"],
                    "contexts": list(element.get("contexts") or ()),
                })
    return issues


# =============================================================================
# PUBLIC API
# =============================================================================

def _contextKeys(context):
    """Normalise a caller's context into canonical element keys."""
    if not context:
        return set()
    if isinstance(context, dict):
        return {context.get("key")} if context.get("key") else set()
    if isinstance(context, str):
        return {context}
    keys = set()
    for item in context:
        if isinstance(item, dict):
            item = item.get("key")
        if item:
            keys.add(item)
    return keys


def _select(keys, kind=None, context=None):
    """Choose the best element from an ambiguous index entry."""
    elements = [ELEMENTS[key] for key in keys]
    if kind:
        kinds = {kind} if isinstance(kind, str) else set(kind)
        matching = [element for element in elements if element["kind"] in kinds]
        if matching:
            elements = matching
        else:
            return None

    contexts = _contextKeys(context)
    if contexts:
        contextual = [
            element for element in elements
            if contexts.intersection(element.get("contexts") or ())
        ]
        if contextual:
            return contextual[0]
        generic = [element for element in elements if not element.get("contexts")]
        if generic:
            return generic[0]
    return elements[0] if elements else None


def resolve(*values, **criteria):
    """Resolve the first recognisable UI string to an element dict.

    Values are tried in the order given, which lets callers state their
    preference: an automation id is stable across ATLAS.ti's interface
    languages, so it should be passed before a display name.

    Exact matches win over substring matches, and every value gets its
    exact-match chance before any value is matched loosely -- otherwise a
    container named "Codes and Memos" could beat an exact "MemoManager".
    """
    kind = criteria.get("kind")
    context = criteria.get("context")
    candidates = [normalize(value) for value in values if value]
    candidates = [candidate for candidate in candidates if candidate]

    for candidate in candidates:
        keys = _EXACT.get(candidate)
        if keys:
            element = _select(keys, kind=kind, context=context)
            if element:
                return element

    for candidate in candidates:
        for token, key in _LOOSE:
            if len(token) >= MIN_LOOSE_TOKEN_LENGTH and token in candidate:
                element = _select((key,), kind=kind, context=context)
                if element:
                    return element
    return None


def resolveExact(*values, **criteria):
    """Resolve only an exact UI string, without substring matching.

    Use this when the caller intends to mutate an NVDA object's accessible
    name.  Loose matching is useful for finding controls in imperfect UIA
    trees, but it is unsafe for renaming: project content such as
    ``"Interview about codes"`` must never become the generic ``Codes``
    label merely because it contains a known UI word.
    """
    for value in values:
        if not value:
            continue
        keys = _EXACT.get(normalize(value))
        if keys:
            element = _select(
                keys,
                kind=criteria.get("kind"),
                context=criteria.get("context"),
            )
            if element:
                return element
    return None


def label(element, language="en", bilingual=False):
    """Render an element's name in the requested language.

    With ``bilingual`` the English original follows the Greek label, which
    helps users who follow the English ATLAS.ti manual while listening to
    Greek speech.
    """
    if not element:
        return None
    primary = element.get(language) or element["en"]
    if bilingual and language != "en" and element["en"] != primary:
        return "{primary} ({original})".format(primary=primary, original=element["en"])
    return primary


CONTROL_TYPE_LABELS = {
    "button": {"en": "Button", "el": "Κουμπί"},
    "menuItem": {"en": "Menu item", "el": "Στοιχείο μενού"},
    "checkBox": {"en": "Check box", "el": "Πλαίσιο ελέγχου"},
    "radioButton": {"en": "Radio button", "el": "Κουμπί επιλογής"},
    "column": {"en": "Column", "el": "Στήλη"},
}

STATE_LABELS = {
    "CHECKED": {"en": "Checked", "el": "Τσεκαρισμένο"},
    "HALFCHECKED": {"en": "Partially checked", "el": "Μερικώς τσεκαρισμένο"},
    "SELECTED": {"en": "Selected", "el": "Επιλεγμένο"},
    "EXPANDED": {"en": "Expanded", "el": "Αναπτυγμένο"},
    "COLLAPSED": {"en": "Collapsed", "el": "Συμπτυγμένο"},
    "UNAVAILABLE": {"en": "Unavailable", "el": "Μη διαθέσιμο"},
    "PRESSED": {"en": "Pressed", "el": "Πατημένο"},
}

STATE_ORDER = (
    "UNAVAILABLE", "PRESSED", "CHECKED", "HALFCHECKED", "SELECTED",
    "EXPANDED", "COLLAPSED",
)

KIND_CONTROL_TYPES = {
    "button": "button",
    "operator": "button",
    "column": "column",
}


def controlType(element):
    """Return the semantic control type used by self-contained speech."""
    if not element:
        return None
    return element.get("controlType") or KIND_CONTROL_TYPES.get(element.get("kind"))


def spokenLabel(element, language="en", bilingual=False, controlTypeOverride=None):
    """Render a self-contained label that includes a translatable role.

    Normal NVDA focus speech already appends its localised role.  This
    helper is for add-on generated messages (row summaries, diagnostics and
    descriptions), where the role would otherwise be lost.
    """
    base = label(element, language=language, bilingual=bilingual)
    semanticType = controlTypeOverride or controlType(element)
    roleLabels = CONTROL_TYPE_LABELS.get(semanticType)
    if not base or not roleLabels:
        return base
    roleLabel = roleLabels.get(language) or roleLabels["en"]
    return "{role} {label}".format(role=roleLabel, label=base)


def stateLabels(states, language="en"):
    """Translate relevant NVDA/UIA state names in a stable speech order."""
    present = set()
    for state in states or ():
        name = getattr(state, "name", None) or str(state)
        normalized = normalize(name).upper()
        for candidate in sorted(STATE_LABELS, key=lambda item: len(normalize(item)), reverse=True):
            if normalize(candidate).upper() in normalized:
                present.add(candidate)
                break
    return [
        STATE_LABELS[name].get(language) or STATE_LABELS[name]["en"]
        for name in STATE_ORDER if name in present
    ]


def hint(element):
    """Return the element's explanatory hint, if it has one."""
    if not element:
        return None
    return element.get("hint")


def shortcut(element):
    """Return the documented ATLAS.ti keyboard shortcut, if any."""
    if not element:
        return None
    return element.get("shortcut")


def isVisualOnly(element):
    """Is this element likely a rendered graphic with no readable content?"""
    return bool(element) and bool(element.get("visualOnly"))


def companion(element):
    """The element key of the nearest accessible alternative, if known."""
    if not element:
        return None
    key = element.get("companion")
    return ELEMENTS.get(key) if key else None


def concept(element, language="en"):
    """What a visual-only element normally shows, in the given language.

    Spoken when the add-on cannot read the element's actual contents, so
    the researcher learns what they are missing instead of hearing silence
    or a bare control name.
    """
    if not element:
        return None
    pair = element.get("concept")
    if not pair:
        return None
    english, greek = pair
    return greek if language == "el" and greek else english


def guessInterfaceLanguage(names):
    """Guess which language ATLAS.ti's interface is displaying.

    ``names`` is any iterable of accessible names harvested from the
    ATLAS.ti window. Tokens shared by several languages (for example
    "Memos", "Filter") are ignored, so only distinguishing evidence counts.
    Returns a language code, or None when there is not enough evidence.
    """
    scores = {}
    for name in names:
        normalized = normalize(name)
        if not normalized:
            continue
        matches = [
            language
            for language, tokens in _LANG_TOKENS.items()
            if normalized in tokens
        ]
        if len(matches) == 1:
            scores[matches[0]] = scores.get(matches[0], 0) + 1
    if not scores:
        return None
    return max(scores, key=scores.get)


def elementsOfKind(kind):
    """All elements of a given kind, sorted by English name."""
    return sorted(
        (element for element in ELEMENTS.values() if element["kind"] == kind),
        key=lambda element: element["en"],
    )
