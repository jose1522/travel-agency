from core.security.sanitizer import Sanitizer


def test_sanitize():
    badString = "$where:{1==1}"
    cleanString = Sanitizer.sanitize(badString)
    assert cleanString != badString
