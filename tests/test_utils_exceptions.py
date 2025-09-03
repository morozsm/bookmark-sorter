from cbclean.utils import domain_of, normalize_url


def test_domain_of_exception_returns_none():
    class X:  # not a URL
        pass

    assert domain_of(X()) is None


def test_normalize_url_exception_returns_original():
    class X:
        pass

    x = X()
    out = normalize_url(x, strip_params=[], strip_fragments=True, strip_www_flag=True)  # type: ignore[arg-type]
    assert out is x

