from cbclean.config import AppConfig


def test_app_config_defaults_and_override():
    cfg = AppConfig()
    assert cfg.normalize.strip_www is True
    # override a few fields
    cfg2 = AppConfig.model_validate({"output": {"export_dir": "./o", "report_formats": ["md"]}})
    assert cfg2.output.export_dir == "./o"
    assert cfg2.output.report_formats == ["md"]
