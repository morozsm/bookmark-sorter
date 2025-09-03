ТЗ: «chrome-bookmarks-cleaner»
1) Цель проекта

Создать кроссплатформенный CLI-инструмент на Python для автоматической очистки и организации закладок Chrome:

Импорт закладок из профилей Chrome или из export-HTML.

Резервное копирование.

Нормализация URL (удаление мусорных параметров, приведение к канонической форме).

Проверка «живости» ссылок (alive/temp_down/auth_required/gone/invalid).

Дедупликация жёстких и мягких дублей.

Категоризация ссылок (три режима: rules → embeddings → LLM).

Генерация плана изменений с объяснениями.

Экспорт «чистых» закладок в стандартный HTML для импорта в Chrome.

Подробный отчёт (HTML/Markdown), dry-run по умолчанию. Никакой записи в файлы Chrome.

2) Нефункциональные требования

Python 3.11+.

ОС: Linux/macOS/Windows (без платформозависимых библиотек).

Быстрый запуск, понятный CLI, детальные логи.

Работа офлайн (без LLM/интернета), кроме опций fetch/wayback/LLM.

Производительность: асинхронные сетевые проверки, кэш в sqlite.

Повторяемость: все решения детерминированы при одинаковой конфигурации и кэше.

Кодстайл: black, ruff, mypy (strict на core-модулях), pre-commit.

Тесты: pytest с покрытием ключевых модулей.

3) Технологический стек

CLI: Typer (или Click) + Rich (прогресс/лог).

HTTP: aiohttp.

HTML: BeautifulSoup4 / selectolax.

Fuzzy: rapidfuzz.

Embeddings (опционально офлайн): sentence-transformers (например, all-MiniLM-L6-v2).

Кластеризация: hdbscan или scikit-learn (KMeans) — по конфигу.

БД: sqlite3 (через встроенный модуль), слой access в storage.py.

Конфиги: ruamel.yaml или pydantic-settings.

Отчёты: Jinja2 шаблоны → report.html + report.md.

Линтеры: ruff, mypy. Форматер: black.

4) Структура репозитория
chrome-bookmarks-cleaner/
  README.md
  LICENSE
  pyproject.toml
  .gitignore
  .pre-commit-config.yaml
  src/cbclean/
    __init__.py
    cli.py
    config.py
    chrome_reader.py
    backup.py
    normalize.py
    fetch.py
    dedup.py
    classify_rules.py
    classify_embed.py
    classify_llm.py
    cluster.py
    propose.py
    apply.py
    storage.py
    report.py
    utils.py
  configs/
    config.example.yaml
    rules.example.yaml
  data/
    samples/*.json
  templates/
    report.html.j2
    report.md.j2
  tests/
    test_normalize.py
    test_dedup.py
    test_fetch.py
    test_classify_rules.py
    test_apply_export.py
  .github/workflows/ci.yml

5) Конфигурация (configs/config.example.yaml)

Реализовать валидируемую модель (pydantic). Значения по умолчанию внутри кода.

Секции и ключи:

input:
  bookmarks_path: "~/.config/google-chrome/Default/Bookmarks"
  profile_glob: "~/.config/google-chrome/*/Bookmarks"
  import_html: ""     # путь к экспортированному bookmarks.html (если не читаем JSON Chrome)

output:
  export_dir: "./out"
  plan_name: "plan-{timestamp}"
  report_formats: ["html","md"]

network:
  enabled: true       # включает fetch
  timeout_sec: 8
  retries: 2
  concurrent: 16
  user_agent: "cbclean/0.1"

normalize:
  strip_query_params: ["utm_*","gclid","yclid","fbclid","ref","ref_src"]
  strip_fragments: true
  strip_www: true

dedup:
  title_similarity_threshold: 0.90
  content_similarity_threshold: 0.92
  prefer_shorter_url: true

liveness:
  enabled: true
  treat_401_403_as_alive: true
  soft404_patterns:
    - "not found"
    - "страница не найдена"
    - "page removed"
    - "404"

dead_links:
  on_gone: "move_to/_Trash"   # drop | replace_with_archive | move_to/_Trash
  wayback_lookup: false

categorize:
  mode: "rules"               # rules | embeddings | llm
  rules_file: "./configs/rules.example.yaml"
  embeddings:
    model: "all-MiniLM-L6-v2"
    cluster_algo: "hdbscan"   # hdbscan | kmeans
    min_cluster_size: 4
  llm:
    provider: "openai"
    model: "gpt-4o-mini"      # placeholder, не вызывать без флага
    batch_size: 30
    only_uncertain: true

thresholds:
  tag_confidence_move: 0.75
  tag_confidence_ask: 0.55

apply:
  mode: "export_html"         # export_html | dry_run

6) Формат правил (configs/rules.example.yaml)
domains:
  "github.com":      ["Dev","Code"]
  "docs.python.org": ["Dev","Python","Docs"]
  "habr.com":        ["Dev","RU"]
  "raindrop.io":     ["Tools","Bookmarks"]
keywords:
  "docker":          ["Dev","Containers"]
  "haproxy":         ["Dev","Networking"]
  "recipe|рецепт":   ["Cooking"]
  "ft8|wsjt":        ["Ham Radio","Digital"]
lang:
  "ru": ["RU"]

7) Данные и БД (sqlite)
Таблица bookmarks

id INTEGER PK

parent_id INTEGER NULL

profile TEXT

title TEXT

url TEXT

normalized_url TEXT

folder_path TEXT (например: "Bookmarks Bar/Work")

created_at DATETIME NULL

last_visited DATETIME NULL

Индексы: normalized_url, url.

Таблица pages (кэш fetch)

url TEXT PK

final_url TEXT

http_status INT

state TEXT ('alive'|'temp_down'|'gone'|'auth_required'|'invalid')

title TEXT

canonical_url TEXT

lang TEXT

hash_body_64k TEXT

fetched_at DATETIME

tries INT

error TEXT

Таблица tags

bookmark_id INT

tag TEXT

PK(bookmark_id,tag)

Таблица clusters

bookmark_id INT

cluster_id INT

Таблица actions (план)

id INTEGER PK

bookmark_id INT

action TEXT ('merge_duplicates','move','rename','drop','replace_with_archive')

reason TEXT

confidence REAL

payload_json TEXT

decided INT (0/1)

Таблица meta

key TEXT PK

value TEXT

8) CLI (Typer)

Команды и поведение:

cbclean scan [--config CONFIG]

Найти все профили по profile_glob и/или взять bookmarks_path/import_html.

Сохранить «сырой» снимок в out/raw/*.json.

Сделать backup в out/backup/bookmarks-backup-{timestamp}.html.

Вставить дерево в bookmarks (sqlite), не дублируя уже существующие id (использовать транзакции).

cbclean analyze [--config CONFIG] [--no-fetch] [--refresh]

Нормализовать URL (обновить normalized_url).

Если fetch включён: асинхронно проверить liveness, записать в pages.

Определить дубликаты:

Жёсткие: одинаковый normalized_url.

Мягкие: совп. canonical_url, либо rapidfuzz по title ≥ threshold, либо (если есть) hash_body_64k/эмбеддинги.

Категоризация: режим согласно categorize.mode.

Результат — обновить tags, clusters, вспомогательные поля.

cbclean plan [--config CONFIG] [--drop-broken]

Сформировать план:

merge_duplicates: выбрать «лучший» URL (alive>dead, короче>длиннее, есть title>нет).

move: предложить папку по тегам/кластерам.

rename: сократить названия, убрать «- SiteName», опционально добавить понятный префикс.

drop/replace_with_archive: для gone/invalid по политике.

Записать в actions, посчитать confidence.

Сгенерировать out/{plan_name}/report.(html|md).

cbclean apply [--config CONFIG] [--mode export_html|dry_run]

Применить план в памяти и сгенерировать bookmarks-cleaned-{timestamp}.html.

Записать JSON-план и итоговую статистику.

cbclean report [--config CONFIG]

Перегенерация отчётов из БД.

cbclean restore

Инструкция пользователю: импортировать последний backup HTML через UI Chrome.

Код — только ищет и пишет путь на консоль.

Каждая команда — с прогресс-барами, понятными логами, кодом возврата (0/≠0).

9) Алгоритмы (детально)
9.1 Нормализация URL (normalize.py)

Разобрать через urllib.parse.

Нижний регистр хоста, при strip_www: true — удалить префикс www..

Удалить fragment при strip_fragments: true.

Удалить query-параметры по маскам (glob-pattern utm_* и список из конфигурации).

Отсортировать оставшиеся параметры по ключу.

Собрать обратно.

Юнит-тесты: десяток кейсов (utm, fbclid, порядок параметров, www, фрагменты).

9.2 Fetch/Liveness (fetch.py)

asyncio + aiohttp, семафор на concurrent.

Сначала HEAD (если 405/403 и т. п. → GET c ограничением 128КБ).

Таймауты, ретраи (экспоненциальный backoff).

Парсить финальный URL, статус, <title>, <meta name="description">, <link rel="canonical">, язык.

Определять состояния:

2xx → alive, но проверить soft-404 (эвристики по контенту/титулу, размеру).

404/410 → gone.

401/403 → auth_required (если в конфиге не считать мёртвыми).

429/5xx (после ретраев) → temp_down.

Ошибки DNS/TLS/timeout (после ретраев) → invalid.

Кэширование в sqlite, повторный fetch только с --refresh или при устаревшем fetched_at.

9.3 Дедупликация (dedup.py)

Жёсткие: группировка по normalized_url.

Мягкие:

canonical_url совпадает.

rapidfuzz.fuzz.token_sort_ratio(title_a, title_b) >= threshold.

При наличии hash_body_64k — совпадение.

Выбор «мастера» в группе: alive > temp_down > auth_required > gone/invalid; короче URL; есть title; более новый last_visited.

Сформировать действия merge_duplicates.

9.4 Категоризация
A) Rules (classify_rules.py)

Загрузить rules.yml.

Для каждой закладки вычислить счёт по домену, ключевым словам, языку.

Вернуть список тегов + confidence (0..1).

Юнит-тесты: домены и ключевые слова.

B) Embeddings (classify_embed.py + cluster.py)

Сформировать текст признаков: title + meta + url_tokens.

Закодировать эмбеддингами (локальная модель).

Кластеризация (HDBSCAN или KMeans).

Название кластера: топ-термины tf-idf + частые домены.

Теги = 1–3 топ-термина. confidence = внутрикластерная близость.

Кэш эмбеддингов в sqlite.

C) LLM (classify_llm.py)

Не вызывать без флага.

Батчить по batch_size, отдавать только «неуверенные» кейсы из Rules/Embeddings.

Промпт формировать строго (см. §12).

Кэш ответов (url → теги/папка).

9.5 Предложение структуры (propose.py)

На основе тегов/кластеров предложить верхние папки (топ-темы).

Внутри — разнести по доменам/подтемам.

Сливать «мелкие» папки в близкие.

Формировать actions:

move (new_folder_path)

rename (new_title)

drop/replace_with_archive

merge_duplicates

9.6 Экспорт HTML (apply.py)

Генерация стандартного bookmarks.html (структура <DL><DT> и <A HREF="...">).

Кодировка UTF-8.

Сохранить в out/bookmarks-cleaned-{timestamp}.html.

9.7 Отчёт (report.py)

Jinja2-шаблоны: report.html.j2, report.md.j2.

Разделы: статистика, топ-темы, список удалённых (с причинами), список «сомнительных» (confidence ниже порога) для ручной проверки.

10) Логи, ошибки, UX

Логи: INFO в консоль, DEBUG в файл out/{plan}/cbclean.log.

Падать с кодом ≠0 при фатальных ошибках.

Всегда печатать путь к отчёту и экспортному HTML.

11) Безопасность и приватность

По умолчанию не отправлять данные во внешние API.

Включение LLM/Wayback — только флагом в конфиге/CLI, с явным предупреждением.

Логировать только агрегаты, URL в логе по желанию (флаг --log-urls).

12) Промпты для LLM (если включено)

Инструкция:

«Тебе дан список ссылок. Для каждой верни 1–3 тематических тега и короткое имя папки. Используй только предоставленный список тем, если он задан. Формат ответа — строгий JSON-массив объектов {url, tags:[], folder, confidence}. Не добавляй комментарии.»

Вход: title, meta, url, (опционально краткий сниппет).

Выход: JSON. Валидация и retry при невалидном JSON.

13) Критерии приёмки (Acceptance Criteria)

Резервное копирование: команда scan создаёт bookmarks-backup-*.html, пригодный для импорта в Chrome.

Нормализация: модуль normalize проходит тест-набор из 20 кейсов (utm, fbclid, www, фрагменты, порядок query).

Fetch/Liveness: для списка из 100 URL с искусственными кейсами правильно расставляет состояния (≥95% точности на тест-наборе).

Дедуп: объединяет группы дублей (жёсткие и мягкие) по заданным порогам; выбирает «мастера» по правилам.

Категоризация (rules): работает офлайн, присваивает теги/папки согласно rules; тесты покрывают домены/keywords/lang.

План: команда plan генерирует actions с понятной причиной и confidence.

Экспорт: команда apply создаёт bookmarks-cleaned-*.html, который успешно импортируется в Chrome без ошибок.

Отчёт: report.html отображает статистику, список удалённых/перемещённых/сомнительных.

Производительность: анализ 10k закладок с включённым fetch и concurrency=16 завершается без падений, fetch кэшируется.

Документация: README содержит инструкции установки, примеры CLI, и предупреждение «Chrome должен быть закрыт».

14) CI/CD

GitHub Actions: линтеры (ruff/black), mypy, pytest.

Матричное тестирование (Linux/macOS). Windows — опционально (но код совместимый).

15) Roadmap (инкременты релизов)

v0.1: scan/backup, normalize, dedup по URL, export, базовый отчёт.

v0.2: fetch/liveness + soft-404, temp_down.

v0.3: rules-категоризация, улучшенный отчёт.

v0.4: embeddings + кластеризация, автолэйблы.

v0.5: LLM-ассист только для «неуверенных», кэш, контроль стоимости.

v0.6: wayback-замена, поддержка Firefox/Edge HTML.

16) Чёткие задачи для Codex (разбить по PR)

Задача A: каркас проекта

Сгенерировать pyproject.toml с зависимостями: typer, rich, aiohttp, beautifulsoup4, rapidfuzz, jinja2, pydantic, hdbscan/scikit-learn (под флагом), sentence-transformers (под флагом), langid.

Создать структуру директорий, __init__.py, заготовки модулей, README.md, .pre-commit-config.yaml, ci.yml.

Задача B: chrome_reader + backup

Реализовать парсер JSON-файла Chrome Bookmarks и/или импорт bookmarks.html.

Экспорт backup в out/backup/bookmarks-backup-{timestamp}.html.

Сохранение дерева в sqlite (bookmarks), аккуратно с null-датами.

Задача C: normalize

Реализовать функцию нормализации, конфиг-маски query-параметров.

Юнит-тесты (минимум 20 кейсов).

Задача D: fetch/liveness

Реализовать асинхронный fetch с HEAD→GET, ограничением по размеру, парсингом <title>, <meta>, <link rel="canonical">.

Эвристики soft-404.

Кэш sqlite.

Флаги --no-fetch/--refresh.

Задача E: dedup

Жёсткие и мягкие дубли; выбор «мастера».

Юнит-тесты на наборах.

Задача F: categorize (rules)

Правила из YAML, скоринг, теги, confidence.

Тесты.

Задача G: embeddings + cluster (опционально за флагом)

Векторизация, кластеризация, автолейблинг.

Задача H: propose + apply + экспорт HTML

Генерация плана с причинами и confidence.

Экспорт bookmarks.html.

Задача I: report

Jinja2 HTML/MD отчёты, прогресс/лог.

Задача J: упаковка и UX

Полные help-тексты CLI, обработка ошибок, коды возврата.

17) Примерные сигнатуры функций (минимум)
# normalize.py
def normalize_url(url: str, cfg: NormalizeConfig) -> str: ...

# fetch.py
@dataclass
class PageMeta:
    final_url: str
    http_status: int | None
    state: Literal['alive','temp_down','gone','auth_required','invalid']
    title: str | None
    canonical_url: str | None
    lang: str | None
    hash_body_64k: str | None
    error: str | None

async def fetch_meta(urls: list[str], cfg: NetworkConfig, db: Storage) -> dict[str, PageMeta]: ...

# dedup.py
@dataclass
class DuplicateDecision:
    keep_id: int
    drop_ids: list[int]
    reason: str

def detect_duplicates(bm: list[Bookmark], pages: dict[str, PageMeta], cfg: DedupConfig) -> list[DuplicateDecision]: ...

# classify_rules.py
@dataclass
class Classification:
    tags: list[str]
    folder: str | None
    confidence: float
    reason: str

def classify_by_rules(item: BookmarkFeatures, rules: Rules) -> Classification: ...

# propose.py
@dataclass
class Action:
    bookmark_id: int
    action: Literal['merge_duplicates','move','rename','drop','replace_with_archive']
    reason: str
    confidence: float
    payload: dict[str, Any]

def build_plan(... ) -> list[Action]: ...

# apply.py
def export_bookmarks_html(tree: BookmarkTree, path: Path) -> None: ...

18) Пример промпта для Codex (генерация модуля)

«Сгенерируй модуль normalize.py для проекта из ТЗ. Требования: Python 3.11, функция normalize_url(url: str, cfg: NormalizeConfig) -> str. Используй urllib.parse. Реализуй маски для query-ключей (fnmatchcase). Удали фрагмент при cfg.strip_fragments. Приведи host к нижнему регистру, при cfg.strip_www — убери префикс www.. Отсортируй query-пары по ключу. Напиши 10 юнит-тестов в tests/test_normalize.py (pytest).»

Аналогично — по каждому модулю из задач A–J.