"""Parser de referências bíblicas em texto livre (pt-BR).

Resolve entradas como "jo 3:16", "salmos 23", "1 co 13:4-7" ou
"apocalipse 21" para o(s) livro(s) candidato(s) + capítulo + versículo(s),
usando os códigos de BibleBook.abbrev como já cadastrados em populate_bible.py.
"""
import re
import unicodedata

# abbrev canônico (BibleBook.abbrev) -> nome completo, só para referência/debug
BOOK_NAMES = {
    'Gn': 'Gênesis', 'Ex': 'Êxodo', 'Lv': 'Levítico', 'Nm': 'Números', 'Dt': 'Deuteronômio',
    'Js': 'Josué', 'Jz': 'Juízes', 'Rt': 'Rute', '1Sm': '1 Samuel', '2Sm': '2 Samuel',
    '1Rs': '1 Reis', '2Rs': '2 Reis', '1Cr': '1 Crônicas', '2Cr': '2 Crônicas',
    'Ed': 'Esdras', 'Ne': 'Neemias', 'Et': 'Ester', 'Jó': 'Jó', 'Sl': 'Salmos',
    'Pv': 'Provérbios', 'Ec': 'Eclesiastes', 'Ct': 'Cânticos', 'Is': 'Isaías',
    'Jr': 'Jeremias', 'Lm': 'Lamentações', 'Ez': 'Ezequiel', 'Dn': 'Daniel',
    'Os': 'Oséias', 'Jl': 'Joel', 'Am': 'Amós', 'Ob': 'Obadias', 'Jn': 'Jonas',
    'Mq': 'Miquéias', 'Na': 'Naum', 'Hc': 'Habacuque', 'Sf': 'Sofonias', 'Ag': 'Ageu',
    'Zc': 'Zacarias', 'Ml': 'Malaquias', 'Mt': 'Mateus', 'Mc': 'Marcos', 'Lc': 'Lucas',
    'Jo': 'João', 'At': 'Atos', 'Rm': 'Romanos', '1Co': '1 Coríntios', '2Co': '2 Coríntios',
    'Gl': 'Gálatas', 'Ef': 'Efésios', 'Fp': 'Filipenses', 'Cl': 'Colossenses',
    '1Ts': '1 Tessalonicenses', '2Ts': '2 Tessalonicenses', '1Tm': '1 Timóteo',
    '2Tm': '2 Timóteo', 'Tt': 'Tito', 'Fm': 'Filemom', 'Hb': 'Hebreus', 'Tg': 'Tiago',
    '1Pe': '1 Pedro', '2Pe': '2 Pedro', '1Jo': '1 João', '2Jo': '2 João', '3Jo': '3 João',
    'Jd': 'Judas', 'Ap': 'Apocalipse',
}

# alias normalizado (minúsculo, sem acento) -> lista de abbrevs candidatos.
# Entradas com número (1/2/3) já são específicas de um único livro; entradas
# genéricas ("cor", "sm", "reis"...) ficam ambíguas de propósito e a view
# resolve consultando todos os candidatos.
_RAW_ALIASES = {
    'Gn': ['gn', 'gen', 'genesis'],
    'Ex': ['ex', 'exo', 'exodo'],
    'Lv': ['lv', 'lev', 'levitico'],
    'Nm': ['nm', 'num', 'numeros'],
    'Dt': ['dt', 'deut', 'deuteronomio'],
    'Js': ['js', 'jos', 'josue'],
    'Jz': ['jz', 'juizes'],
    'Rt': ['rt', 'rute'],
    '1Sm': ['1sm', '1 sm', '1samuel', '1 samuel'],
    '2Sm': ['2sm', '2 sm', '2samuel', '2 samuel'],
    '1Rs': ['1rs', '1 rs', '1reis', '1 reis'],
    '2Rs': ['2rs', '2 rs', '2reis', '2 reis'],
    '1Cr': ['1cr', '1 cr', '1cronicas', '1 cronicas'],
    '2Cr': ['2cr', '2 cr', '2cronicas', '2 cronicas'],
    'Ed': ['ed', 'esdras'],
    'Ne': ['ne', 'neemias'],
    'Et': ['et', 'ester'],
    'Jó': ['job'],  # "jó" acentuado é tratado à parte, antes de remover acentos
    'Sl': ['sl', 'salmo', 'salmos', 'sal'],
    'Pv': ['pv', 'prov', 'proverbios'],
    'Ec': ['ec', 'eclesiastes'],
    'Ct': ['ct', 'cantares', 'canticos', 'cantico dos canticos'],
    'Is': ['is', 'isaias'],
    'Jr': ['jr', 'jer', 'jeremias'],
    'Lm': ['lm', 'lamentacoes'],
    'Ez': ['ez', 'eze', 'ezequiel'],
    'Dn': ['dn', 'dan', 'daniel'],
    'Os': ['os', 'oseias'],
    'Jl': ['jl', 'joel'],
    'Am': ['am', 'amos'],
    'Ob': ['ob', 'obadias'],
    'Jn': ['jn', 'jonas'],
    'Mq': ['mq', 'miqueias'],
    'Na': ['na', 'naum'],
    'Hc': ['hc', 'habacuque'],
    'Sf': ['sf', 'sofonias'],
    'Ag': ['ag', 'ageu'],
    'Zc': ['zc', 'zac', 'zacarias'],
    'Ml': ['ml', 'malaquias'],
    'Mt': ['mt', 'mat', 'mateus'],
    'Mc': ['mc', 'mar', 'marcos'],
    'Lc': ['lc', 'luc', 'lucas'],
    'Jo': ['jo', 'joao'],  # ambíguo com "jó" só quando digitado sem acento
    'At': ['at', 'atos'],
    'Rm': ['rm', 'rom', 'romanos'],
    '1Co': ['1co', '1 co', '1cor', '1 cor', '1corintios', '1 corintios'],
    '2Co': ['2co', '2 co', '2cor', '2 cor', '2corintios', '2 corintios'],
    'Gl': ['gl', 'gal', 'galatas'],
    'Ef': ['ef', 'efe', 'efesios'],
    'Fp': ['fp', 'fil', 'filipenses'],
    'Cl': ['cl', 'col', 'colossenses'],
    '1Ts': ['1ts', '1 ts', '1tessalonicenses', '1 tessalonicenses'],
    '2Ts': ['2ts', '2 ts', '2tessalonicenses', '2 tessalonicenses'],
    '1Tm': ['1tm', '1 tm', '1timoteo', '1 timoteo'],
    '2Tm': ['2tm', '2 tm', '2timoteo', '2 timoteo'],
    'Tt': ['tt', 'tito'],
    'Fm': ['fm', 'filemom'],
    'Hb': ['hb', 'heb', 'hebreus'],
    'Tg': ['tg', 'tia', 'tiago'],
    '1Pe': ['1pe', '1 pe', '1pedro', '1 pedro'],
    '2Pe': ['2pe', '2 pe', '2pedro', '2 pedro'],
    '1Jo': ['1jo', '1 jo', '1joao', '1 joao'],
    '2Jo': ['2jo', '2 jo', '2joao', '2 joao'],
    '3Jo': ['3jo', '3 jo', '3joao', '3 joao'],
    'Jd': ['jd', 'judas'],
    'Ap': ['ap', 'apo', 'apocalipse'],
}


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize('NFKD', text)
    return ''.join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize(text: str) -> str:
    return _strip_accents(text).lower().strip()


# índice alias normalizado -> [abbrevs]; construído uma vez no import
_ALIAS_INDEX: dict[str, list[str]] = {}
for _abbrev, _aliases in _RAW_ALIASES.items():
    for _alias in _aliases:
        _key = normalize(_alias)
        _ALIAS_INDEX.setdefault(_key, [])
        if _abbrev not in _ALIAS_INDEX[_key]:
            _ALIAS_INDEX[_key].append(_abbrev)

# formas sem número que são genuinamente ambíguas entre 1º/2º/3º livro
# (ex: "cor" sozinho não indica se é 1 ou 2 Coríntios) — a view resolve
# consultando os dois e devolvendo um candidato por livro que tiver o
# capítulo/versículo pedido.
_AMBIGUOUS_BARE_ALIASES = {
    'cor': ['1Co', '2Co'],
    'corintios': ['1Co', '2Co'],
    'samuel': ['1Sm', '2Sm'],
    'reis': ['1Rs', '2Rs'],
    'cronicas': ['1Cr', '2Cr'],
    'tessalonicenses': ['1Ts', '2Ts'],
    'timoteo': ['1Tm', '2Tm'],
    'pedro': ['1Pe', '2Pe'],
}
for _key, _abbrevs in _AMBIGUOUS_BARE_ALIASES.items():
    _ALIAS_INDEX.setdefault(_key, [])
    for _abbrev in _abbrevs:
        if _abbrev not in _ALIAS_INDEX[_key]:
            _ALIAS_INDEX[_key].append(_abbrev)

# "jó" com acento é inequívoco: cadastra antes de normalizar o resto
_JO_ACCENT_KEY = 'jó'.lower()

# regex: [número opcional] + nome do livro (não-numérico) + capítulo + [:versículo[-versículo]]
_REFERENCE_RE = re.compile(
    r'^\s*(?P<book>\d?\s*[^\d]+?)\s*(?P<chapter>\d+)'
    r'(?:\s*[:.]\s*(?P<verse_start>\d+)(?:\s*-\s*(?P<verse_end>\d+))?)?\s*$'
)


class ParsedReference:
    def __init__(self, book_abbrevs, chapter, verse_start=None, verse_end=None):
        self.book_abbrevs = book_abbrevs
        self.chapter = chapter
        self.verse_start = verse_start
        self.verse_end = verse_end


def resolve_book_abbrevs(raw_book_text: str) -> list[str]:
    """Resolve um trecho de texto (ex: 'jo', '1 cor', 'salmos') para uma
    lista de BibleBook.abbrev candidatos. Lista vazia = nenhum livro reconhecido."""
    if raw_book_text.strip().lower() == _JO_ACCENT_KEY:
        return ['Jó']

    key = normalize(raw_book_text)
    if key in _ALIAS_INDEX:
        return list(_ALIAS_INDEX[key])

    # fallback: prefixo (ex: "apoca" -> "apocalipse") pra digitação incompleta
    prefix_matches: list[str] = []
    for alias_key, abbrevs in _ALIAS_INDEX.items():
        if len(key) >= 2 and alias_key.startswith(key):
            for abbrev in abbrevs:
                if abbrev not in prefix_matches:
                    prefix_matches.append(abbrev)
    return prefix_matches


def parse_reference(query: str) -> ParsedReference | None:
    """Interpreta a query digitada após o '@'. Retorna None se não achar
    nem um capítulo válido (ex: usuário ainda está digitando o nome do livro)."""
    if not query or not query.strip():
        return None

    match = _REFERENCE_RE.match(query)
    if not match:
        return None

    book_abbrevs = resolve_book_abbrevs(match.group('book'))
    if not book_abbrevs:
        return None

    chapter = int(match.group('chapter'))
    verse_start = match.group('verse_start')
    verse_end = match.group('verse_end')

    return ParsedReference(
        book_abbrevs=book_abbrevs,
        chapter=chapter,
        verse_start=int(verse_start) if verse_start else None,
        verse_end=int(verse_end) if verse_end else (int(verse_start) if verse_start else None),
    )


def suggest_books(raw_query: str, limit: int = 8) -> list[str]:
    """Quando ainda não há capítulo digitado (ex: '@sal'), sugere livros
    cujo alias bate por prefixo, na ordem canônica da Bíblia."""
    abbrevs = resolve_book_abbrevs(raw_query)
    return abbrevs[:limit]


def format_reference(book_name: str, chapter: int, verse_start: int | None, verse_end: int | None) -> str:
    if verse_start is None:
        return f'{book_name} {chapter}'
    if verse_end and verse_end != verse_start:
        return f'{book_name} {chapter}:{verse_start}-{verse_end}'
    return f'{book_name} {chapter}:{verse_start}'
