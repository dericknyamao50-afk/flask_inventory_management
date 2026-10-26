
from unittest.mock import Mock, patch

import cli


@patch("cli.requests.get")
def test_display_inventory(mock_get, capsys):
    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "id": 1,
            "name": "Mango Juice",
            "price": 120.0,
            "stock": 10,
        }
    ]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    cli.display_inventory()

    output = capsys.readouterr().out
    assert "Mango Juice" in output
    assert "120.0" in output


@patch("cli.requests.post")
@patch("builtins.input", side_effect=["Mango Juice", "120", "10"])
def test_add_item(mock_input, mock_post, capsys):
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": 3,
        "name": "Mango Juice",
    }
    mock_post.return_value = mock_response

    cli.add_item()

    mock_post.assert_called_once()
    assert "201" in capsys.readouterr().out


@patch("builtins.input", return_value="0")
def test_main_exits(mock_input, capsys):
    cli.main()

    assert "Goodbye!" in capsys.readouterr().out
