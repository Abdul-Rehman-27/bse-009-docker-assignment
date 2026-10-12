"""
Unit tests for app.py using Python's built-in unittest framework.

Run with:
    python -m unittest testing.py
"""

import unittest
from unittest.mock import patch, MagicMock

from app import allowed_file, transcribe_audio, load_model


class TestAllowedFile(unittest.TestCase):
    """Tests for the allowed_file() validation function."""

    def test_valid_wav_extension(self):
        self.assertTrue(allowed_file("recording.wav"))

    def test_valid_mp3_extension(self):
        self.assertTrue(allowed_file("voice_note.MP3"))  # case-insensitive

    def test_invalid_extension(self):
        self.assertFalse(allowed_file("document.pdf"))

    def test_no_extension(self):
        self.assertFalse(allowed_file("noextension"))


class TestLoadModel(unittest.TestCase):
    """Tests for the thread-safe singleton model loader."""

    @patch("app.whisper.load_model")
    def test_model_loaded_only_once(self, mock_load):
        mock_load.return_value = MagicMock()

        # Reset the module-level singleton before testing
        import app
        app.model = None

        first = load_model()
        second = load_model()

        # whisper.load_model should only be called once, even though
        # load_model() was called twice (singleton behaviour).
        mock_load.assert_called_once()
        self.assertIs(first, second)


class TestTranscribeAudio(unittest.TestCase):
    """Tests for transcribe_audio(), mocking the actual Whisper model."""

    @patch("app.load_model")
    def test_transcribe_returns_stripped_text(self, mock_load_model):
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "  hello world  "}
        mock_load_model.return_value = mock_model

        result = transcribe_audio("fake_path.wav")

        self.assertEqual(result, "hello world")
        mock_model.transcribe.assert_called_once_with("fake_path.wav")

    @patch("app.load_model")
    def test_transcribe_handles_empty_result(self, mock_load_model):
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {}
        mock_load_model.return_value = mock_model

        result = transcribe_audio("fake_path.wav")

        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
