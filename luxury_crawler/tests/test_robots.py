"""Basic tests for robots handler behavior."""
import urllib.robotparser

from luxury_crawler.src.robots_handler import RobotsHandler


def test_domain_parsing():
    handler = RobotsHandler(user_agent="test-agent")
    assert handler._domain_from_url("https://example.com/page") == "https://example.com"
    assert handler._domain_from_url("http://example.com/foo/bar") == "http://example.com"


def test_fail_closed_on_missing_file(monkeypatch):
    handler = RobotsHandler(user_agent="test-agent")

    # Force download failure so parser is populated with a disallow-all policy.
    monkeypatch.setattr(handler, "_download_robots", lambda url: None)

    # Trigger fetch and ensure it fails closed.
    assert handler.can_fetch("https://example.com/private") is False

    parser: urllib.robotparser.RobotFileParser = handler._parsers["https://example.com"]
    assert parser.can_fetch("test-agent", "https://example.com/public") is False
