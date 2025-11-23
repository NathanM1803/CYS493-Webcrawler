"""Example parser tests using minimal HTML fixtures."""
from luxury_crawler.src.parser import parse_inventory_page


HTML = """
<html><body>
  <div class="listing">
    <span class="brand">BrandX</span>
    <span class="model">ModelY</span>
    <span class="year">2024</span>
    <span class="price">$100,000</span>
  </div>
  <a href="/inventory/page2">Next</a>
</body></html>
"""


def test_parse_inventory_page_extracts_car_and_link():
    cars, urls = parse_inventory_page(HTML, base_url="https://example-luxurycars.com/inventory", source="example")
    assert len(cars) == 1
    assert cars[0].brand == "BrandX"
    assert urls == ["https://example-luxurycars.com/inventory/page2"]
