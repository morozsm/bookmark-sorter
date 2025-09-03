from __future__ import annotations

from typing import List
from pydantic import BaseModel


class InputCfg(BaseModel):
    bookmarks_path: str = "~/.config/google-chrome/Default/Bookmarks"
    profile_glob: str = "~/.config/google-chrome/*/Bookmarks"
    import_html: str = ""


class OutputCfg(BaseModel):
    export_dir: str = "./out"
    plan_name: str = "plan-{timestamp}"
    report_formats: List[str] = ["html", "md"]


class NetworkCfg(BaseModel):
    enabled: bool = True
    timeout_sec: int = 8
    retries: int = 2
    concurrent: int = 16
    user_agent: str = "cbclean/0.1"
    fetch_content: bool = False
    max_content_chars: int = 2000


class NormalizeCfg(BaseModel):
    strip_query_params: List[str] = ["utm_*", "gclid", "yclid", "fbclid", "ref", "ref_src"]
    strip_fragments: bool = True
    strip_www: bool = True


class DedupCfg(BaseModel):
    title_similarity_threshold: float = 0.90
    content_similarity_threshold: float = 0.92
    prefer_shorter_url: bool = True


class LivenessCfg(BaseModel):
    enabled: bool = True
    treat_401_403_as_alive: bool = True
    soft404_patterns: List[str] = ["not found", "страница не найдена", "page removed", "404"]


class DeadLinksCfg(BaseModel):
    on_gone: str = "move_to/_Trash"  # drop | replace_with_archive | move_to/_Trash
    wayback_lookup: bool = False


class EmbeddingsCfg(BaseModel):
    model: str = "all-MiniLM-L6-v2"
    cluster_algo: str = "hdbscan"  # hdbscan | kmeans
    min_cluster_size: int = 4
    top_k: int = 2
    score_threshold: float = 0.35
    labels: List[str] | None = None


class LlmCfg(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    batch_size: int = 30
    only_uncertain: bool = True
    api_key_env: str = "OPENAI_API_KEY"
    api_base: str | None = None
    temperature: float = 0.0
    labels: List[str] | None = None
    allow_new_labels: bool = True
    max_new_labels_per_batch: int = 10


class CategorizeCfg(BaseModel):
    mode: str = "rules"  # rules | embeddings | llm
    rules_file: str = "./configs/rules.example.yaml"
    embeddings: EmbeddingsCfg = EmbeddingsCfg()
    llm: LlmCfg = LlmCfg()


class ThresholdsCfg(BaseModel):
    tag_confidence_move: float = 0.75
    tag_confidence_ask: float = 0.55


class ApplyCfg(BaseModel):
    mode: str = "export_html"  # export_html | dry_run
    group_by: str = "folder"  # folder | tag


class AppConfig(BaseModel):
    input: InputCfg = InputCfg()
    output: OutputCfg = OutputCfg()
    network: NetworkCfg = NetworkCfg()
    normalize: NormalizeCfg = NormalizeCfg()
    dedup: DedupCfg = DedupCfg()
    liveness: LivenessCfg = LivenessCfg()
    dead_links: DeadLinksCfg = DeadLinksCfg()
    categorize: CategorizeCfg = CategorizeCfg()
    thresholds: ThresholdsCfg = ThresholdsCfg()
    apply: ApplyCfg = ApplyCfg()
