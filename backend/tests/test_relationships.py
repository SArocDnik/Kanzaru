from unittest.mock import patch, MagicMock
import pytest
from src.services.analyzer import map_relationships, Relationship, CharacterInfo


MOCK_RELATIONSHIP_RESPONSE = """{
  "relationships": [
    {"character_a": "Taro", "character_b": "Sora", "rel_type": "friendship", "description": "Childhood friends"},
    {"character_a": "Taro", "character_b": "Kuro", "rel_type": "rivalry", "description": "Competitors"}
  ]
}"""


def test_map_relationships_success():
    mock_client = MagicMock()
    mock_client.chat.return_value = MOCK_RELATIONSHIP_RESPONSE

    characters = [
        CharacterInfo(name="Taro", role="protagonist"),
        CharacterInfo(name="Sora", role="supporting"),
        CharacterInfo(name="Kuro", role="antagonist"),
    ]
    result = map_relationships(characters, "Some chapter text", client=mock_client)

    assert len(result) == 2
    assert result[0].character_a == "Taro"
    assert result[0].character_b == "Sora"
    assert result[0].rel_type == "friendship"
    assert result[1].rel_type == "rivalry"


def test_map_relationships_empty_characters():
    mock_client = MagicMock()
    result = map_relationships([], "text", client=mock_client)
    assert result == []
    mock_client.chat.assert_not_called()


def test_map_relationships_empty_text():
    mock_client = MagicMock()
    chars = [CharacterInfo(name="A")]
    result = map_relationships(chars, "", client=mock_client)
    assert result == []


def test_map_relationships_invalid_json():
    mock_client = MagicMock()
    mock_client.chat.return_value = "not json"
    chars = [CharacterInfo(name="A")]
    result = map_relationships(chars, "text", client=mock_client)
    assert result == []
