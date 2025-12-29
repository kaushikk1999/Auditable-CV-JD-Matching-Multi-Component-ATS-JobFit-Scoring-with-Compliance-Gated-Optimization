import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.parsers import CVParser

def test_txt_parser():
    sample = b"John Doe\nSoftware Engineer\n5 years experience"
    result = CVParser.parse_txt(sample)
    assert "John Doe" in result
    assert "Software Engineer" in result
    print("✅ TXT parser test passed")

def test_parse_dispatcher():
    sample = b"Test CV content"
    result = CVParser.parse(sample, ".txt")
    assert len(result) > 0
    print("✅ Parse dispatcher test passed")

if __name__ == "__main__":
    test_txt_parser()
    test_parse_dispatcher()
    print("\n✅ All parser tests passed!")
