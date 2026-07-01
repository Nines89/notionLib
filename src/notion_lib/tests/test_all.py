"""
tests/test_all.py
=================
Suite completa di test per notion_lib.

Struttura
---------
Ogni TestCase copre un modulo o una classe.
I test che richiedono chiamate HTTP usano unittest.mock per simulare
le risposte dell'API senza una connessione reale.

Esecuzione
----------
    # dalla root del progetto:
    python -m pytest tests/test_all.py -v
    # oppure senza pytest:
    python tests/test_all.py

Legenda output
--------------
  OK   — test superato
  FAIL — asserzione fallita
  ERROR — eccezione inattesa
"""

import json
import sys
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

sys.path.insert(0, "")

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _fake_response(data: dict, status: int = 200):
    """Costruisce un oggetto response finto compatibile con requests."""
    r = MagicMock()
    r.status_code = status
    r.ok = status < 400
    r.text = json.dumps(data)
    r.json.return_value = data
    r.headers = {}
    return r


# ─────────────────────────────────────────────────────────────────────────────
# 1. utils
# ─────────────────────────────────────────────────────────────────────────────

class TestCheckUrlOrId(unittest.TestCase):

    def test_plain_32_hex(self):
        from notion_lib.utils.utils import check_url_or_id
        self.assertEqual(check_url_or_id("2a7b7a8f729480b3b420f8736c4116d7"),
                         "2a7b7a8f729480b3b420f8736c4116d7")

    def test_hyphenated_uuid(self):
        from notion_lib.utils.utils import check_url_or_id
        self.assertEqual(check_url_or_id("2a7b7a8f-7294-80b3-b420-f8736c4116d7"),
                         "2a7b7a8f729480b3b420f8736c4116d7")

    def test_url_with_slug(self):
        from notion_lib.utils.utils import check_url_or_id
        url = "https://www.notion.so/My-Page-2a7b7a8f729480b3b420f8736c4116d7"
        self.assertEqual(check_url_or_id(url), "2a7b7a8f729480b3b420f8736c4116d7")

    def test_url_with_fragment(self):
        from notion_lib.utils.utils import check_url_or_id
        url = ("https://www.notion.so/Page-2a7b7a8f729480b3b420f8736c4116d7"
               "?source=copy_link#2a7b7a8f7294814297b9cc59924601e3")
        result = check_url_or_id(url)
        self.assertEqual(len(result), 32)

    def test_invalid_raises(self):
        from notion_lib.utils.utils import check_url_or_id
        with self.assertRaises(ValueError):
            check_url_or_id("not-an-id")

    def test_wrong_length_raises(self):
        from notion_lib.utils.utils import check_url_or_id
        with self.assertRaises(ValueError):
            check_url_or_id("2a7b7a8f729480b3b420")


class TestResolveResponse(unittest.TestCase):

    def test_dict_passthrough(self):
        from notion_lib.utils.utils import resolve_response
        d = {"a": 1, "b": 2}
        self.assertIs(resolve_response(d), d)

    def test_nget_like_object(self):
        from notion_lib.utils.utils import resolve_response
        class FakeSession:
            response = {"object": "page", "id": "abc"}
        self.assertEqual(resolve_response(FakeSession()), {"object": "page", "id": "abc"})

    def test_invalid_type_raises(self):
        from notion_lib.utils.utils import resolve_response
        with self.assertRaises(TypeError):
            resolve_response(42)


# ─────────────────────────────────────────────────────────────────────────────
# 2. client/auth
# ─────────────────────────────────────────────────────────────────────────────

class TestNotionApiClient(unittest.TestCase):

    def setUp(self):
        from notion_lib.client.auth import NotionApiClient
        self.api = NotionApiClient(key="test_key_abc123", version="2025-09-03")

    def test_key_stored(self):
        self.assertEqual(self.api.key, "test_key_abc123")

    def test_version_stored(self):
        self.assertEqual(self.api.version, "2025-09-03")

    def test_headers_built(self):
        h = self.api.headers
        self.assertEqual(h["Authorization"], "Bearer test_key_abc123")
        self.assertEqual(h["Notion-Version"], "2025-09-03")
        self.assertEqual(h["Content-Type"], "application/json")

    def test_key_immutable(self):
        with self.assertRaises(AttributeError):
            self.api.key = "changed"

    def test_version_immutable(self):
        with self.assertRaises(AttributeError):
            self.api.version = "changed"

    def test_other_attrs_mutable(self):
        self.api.custom_field = "ok"
        self.assertEqual(self.api.custom_field, "ok")

    def test_default_version(self):
        from notion_lib.client.auth import NotionApiClient
        api = NotionApiClient(key="k")
        self.assertEqual(api.version, "2025-09-03")


# ─────────────────────────────────────────────────────────────────────────────
# 3. client/https  (HTTP mockato)
# ─────────────────────────────────────────────────────────────────────────────

class TestHttpsLayer(unittest.TestCase):

    def setUp(self):
        from notion_lib.client.https import invalidate_cache
        invalidate_cache()

    @patch("requests.request")
    def test_nget_returns_json(self, mock_req):
        from notion_lib.client.https import NGET, invalidate_cache
        invalidate_cache()
        mock_req.return_value = _fake_response({"object": "page", "id": "abc"})
        r = NGET(url="https://api.notion.com/v1/pages/abc",
                 header={"Authorization": "Bearer x"})
        self.assertEqual(r.response["object"], "page")

    @patch("requests.request")
    def test_npost_returns_json(self, mock_req):
        from notion_lib.client.https import NPOST
        mock_req.return_value = _fake_response({"object": "block"})
        r = NPOST(url="https://api.notion.com/v1/pages",
                  header={"Authorization": "Bearer x"},
                  data={"parent": {}})
        self.assertEqual(r.response["object"], "block")

    @patch("requests.request")
    def test_npatch_returns_json(self, mock_req):
        from notion_lib.client.https import NPATCH
        mock_req.return_value = _fake_response({"id": "xyz"})
        r = NPATCH(url="https://api.notion.com/v1/pages/xyz",
                   header={"Authorization": "Bearer x"},
                   data={"archived": True})
        self.assertEqual(r["id"], "xyz")

    @patch("requests.request")
    def test_error_raises_mapped_exception(self, mock_req):
        from notion_lib.client.https import NGET, invalidate_cache
        from notion_lib.client.errors import ObjectNotFound
        invalidate_cache()
        mock_req.return_value = _fake_response(
            {"code": "object_not_found", "message": "not found"}, status=404)
        with self.assertRaises(ObjectNotFound):
            NGET(url="https://api.notion.com/v1/pages/missing",
                 header={"Authorization": "Bearer x"})

    @patch("requests.request")
    def test_invalidate_cache_called_on_post(self, mock_req):
        from notion_lib.client.https import NPOST, _cached_get, invalidate_cache
        invalidate_cache()
        mock_req.return_value = _fake_response({"id": "new"})
        NPOST(url="https://api.notion.com/v1/pages",
              header={"Authorization": "Bearer x"}, data={})
        # Dopo NPOST la cache deve essere vuota
        info = _cached_get.cache_info()
        self.assertEqual(info.currsize, 0)


# ─────────────────────────────────────────────────────────────────────────────
# 4. nTypes/primitives
# ─────────────────────────────────────────────────────────────────────────────

class TestNDate(unittest.TestCase):

    def test_from_iso_string(self):
        from notion_lib.nTypes.primitives import NDate
        d = NDate("2025-01-15T10:00:00.000Z")
        self.assertIsInstance(d.data, datetime)

    def test_from_datetime(self):
        from notion_lib.nTypes.primitives import NDate
        dt = datetime(2025, 6, 1, tzinfo=timezone.utc)
        d = NDate(dt)
        self.assertEqual(d.data, dt)

    def test_to_dict_format(self):
        from notion_lib.nTypes.primitives import NDate
        d = NDate("2025-01-15T10:00:00.000Z")
        s = d.to_dict()
        self.assertIn("2025-01-15", s)

    def test_repr(self):
        from notion_lib.nTypes.primitives import NDate
        d = NDate("2025-01-01T00:00:00.000Z")
        self.assertIn("2025", repr(d))


class TestNText(unittest.TestCase):

    def _make(self, content="hello", link=None):
        from notion_lib.nTypes.primitives import NText
        return NText({"text": {"content": content, "link": {"url": link} if link else None}})

    def test_content_read(self):
        t = self._make("world")
        self.assertEqual(t.content, "world")

    def test_content_write(self):
        t = self._make("old")
        t.content = "new"
        self.assertEqual(t.content, "new")

    def test_link_none(self):
        t = self._make()
        self.assertIsNone(t.link)

    def test_link_read(self):
        t = self._make(link="https://example.com")
        self.assertEqual(t.link, "https://example.com")

    def test_link_write_existing(self):
        t = self._make(link="https://old.com")
        t.link = "https://new.com"
        self.assertEqual(t.link, "https://new.com")

    def test_link_write_new(self):
        t = self._make()
        t.link = "https://added.com"
        self.assertEqual(t.link, "https://added.com")

    def test_to_dict(self):
        t = self._make("hi")
        d = t.to_dict()
        self.assertEqual(d["content"], "hi")


class TestNEquation(unittest.TestCase):

    def test_read(self):
        from notion_lib.nTypes.primitives import NEquation
        e = NEquation({"equation": {"expression": "E=mc^2"}})
        self.assertEqual(e.equation, "E=mc^2")

    def test_write(self):
        from notion_lib.nTypes.primitives import NEquation
        e = NEquation({"equation": {"expression": "x"}})
        e.equation = "y=f(x)"
        self.assertEqual(e.equation, "y=f(x)")


# ─────────────────────────────────────────────────────────────────────────────
# 5. nTypes/rich_text
# ─────────────────────────────────────────────────────────────────────────────

class TestNRichText(unittest.TestCase):

    def _make_text_item(self, content="test"):
        return {
            "type": "text",
            "text": {"content": content, "link": None},
            "annotations": {
                "bold": False, "italic": False, "strikethrough": False,
                "underline": False, "code": False, "color": "default"
            },
            "plain_text": content,
            "href": None,
        }

    def test_type(self):
        from notion_lib.nTypes.rich_text import NRichText
        rt = NRichText(self._make_text_item())
        self.assertEqual(rt.type, "text")

    def test_plain_text(self):
        from notion_lib.nTypes.rich_text import NRichText
        rt = NRichText(self._make_text_item("hello"))
        self.assertEqual(rt.plain_text, "hello")

    def test_schema_error_on_missing_key(self):
        from notion_lib.nTypes.rich_text import NRichText, RichTextSchemaError
        bad = {"type": "text", "text": {"content": "x", "link": None}}
        with self.assertRaises(RichTextSchemaError):
            NRichText(bad)


class TestNRichList(unittest.TestCase):

    def test_append_valid(self):
        from notion_lib.nTypes.rich_text import NRichList, NRichText
        rl = NRichList()
        item = {
            "type": "text",
            "text": {"content": "x", "link": None},
            "annotations": {"bold": False, "italic": False, "strikethrough": False,
                             "underline": False, "code": False, "color": "default"},
            "plain_text": "x", "href": None,
        }
        rl.append(NRichText(item))
        self.assertEqual(len(rl), 1)

    def test_append_invalid_raises(self):
        from notion_lib.nTypes.rich_text import NRichList
        rl = NRichList()
        with self.assertRaises(ValueError):
            rl.append("not a NRichText")

    def test_text_property(self):
        from notion_lib.nTypes.rich_text import simple_rich_text_list
        rl = simple_rich_text_list("hello world")
        self.assertEqual(rl.text, "hello world")

    def test_to_dict_structure(self):
        from notion_lib.nTypes.rich_text import simple_rich_text_list
        rl = simple_rich_text_list("abc")
        d = rl.to_dict()
        self.assertIsInstance(d, list)
        self.assertEqual(len(d), 1)
        self.assertIn("type", d[0])


class TestSimpleRichTextList(unittest.TestCase):

    def test_text_type(self):
        from notion_lib.nTypes.rich_text import simple_rich_text_list
        rl = simple_rich_text_list("hi")
        self.assertEqual(rl[0].type, "text")

    def test_equation_type(self):
        from notion_lib.nTypes.rich_text import simple_rich_text_list
        rl = simple_rich_text_list("E=mc^2", "equation")
        self.assertEqual(rl[0].type, "equation")

    def test_invalid_type_raises(self):
        from notion_lib.nTypes.rich_text import simple_rich_text_list
        with self.assertRaises(ValueError):
            simple_rich_text_list("x", "mention")


class TestCreateRichList(unittest.TestCase):

    def test_empty_list(self):
        from notion_lib.nTypes.rich_text import create_rich_list
        self.assertEqual(len(create_rich_list([])), 0)

    def test_single_item(self):
        from notion_lib.nTypes.rich_text import create_rich_list
        item = {
            "type": "text",
            "text": {"content": "hello", "link": None},
            "annotations": {"bold": False, "italic": False, "strikethrough": False,
                             "underline": False, "code": False, "color": "default"},
            "plain_text": "hello", "href": None,
        }
        rl = create_rich_list([item])
        self.assertEqual(rl.text, "hello")


# ─────────────────────────────────────────────────────────────────────────────
# 6. nTypes/files
# ─────────────────────────────────────────────────────────────────────────────

class TestFiles(unittest.TestCase):

    def test_external_type(self):
        from notion_lib.nTypes.files import FileTypeExternal
        f = FileTypeExternal("https://example.com/img.png")
        self.assertEqual(f.type, "external")
        self.assertEqual(f.url, "https://example.com/img.png")

    def test_external_to_dict(self):
        from notion_lib.nTypes.files import FileTypeExternal
        d = FileTypeExternal("https://x.com").to_dict()
        self.assertEqual(d["type"], "external")
        self.assertEqual(d["external"]["url"], "https://x.com")

    def test_uploaded_type(self):
        from notion_lib.nTypes.files import FileTypeUploaded
        f = FileTypeUploaded("upload-id-123")
        self.assertEqual(f.type, "file_upload")
        self.assertEqual(f.id, "upload-id-123")

    def test_file_type(self):
        from notion_lib.nTypes.files import FileTypeFile
        f = FileTypeFile("https://s3.amazonaws.com/file.pdf", "2025-01-01T00:00:00Z")
        self.assertEqual(f.type, "file")
        self.assertEqual(f.expiry_time, "2025-01-01T00:00:00Z")

    def test_n_file_external(self):
        from notion_lib.nTypes.files import n_file, FileTypeExternal
        f = n_file({"type": "external", "external": {"url": "https://x.com"}})
        self.assertIsInstance(f, FileTypeExternal)

    def test_n_file_file(self):
        from notion_lib.nTypes.files import n_file, FileTypeFile
        f = n_file({"type": "file", "file": {"url": "https://s3.com/f", "expiry_time": None}})
        self.assertIsInstance(f, FileTypeFile)

    def test_n_file_uploaded(self):
        from notion_lib.nTypes.files import n_file, FileTypeUploaded
        f = n_file({"type": "file_upload", "file_upload": {"id": "abc"}})
        self.assertIsInstance(f, FileTypeUploaded)

    def test_n_file_empty_raises(self):
        from notion_lib.nTypes.files import n_file
        with self.assertRaises(ValueError):
            n_file({})

    def test_n_file_unknown_raises(self):
        from notion_lib.nTypes.files import n_file
        with self.assertRaises(ValueError):
            n_file({"type": "unknown_type"})


# ─────────────────────────────────────────────────────────────────────────────
# 7. nTypes/icons
# ─────────────────────────────────────────────────────────────────────────────

class TestIcons(unittest.TestCase):

    def test_nemoji_read(self):
        from notion_lib.nTypes.icons import NEmoji
        e = NEmoji({"type": "emoji", "emoji": "🥑"})
        self.assertEqual(e.emoji, "🥑")

    def test_nemoji_write(self):
        from notion_lib.nTypes.icons import NEmoji
        e = NEmoji({"type": "emoji", "emoji": "🥑"})
        e.emoji = "🚀"
        self.assertEqual(e.emoji, "🚀")

    def test_nemoji_to_payload(self):
        from notion_lib.nTypes.icons import NEmoji
        e = NEmoji({"type": "emoji", "emoji": "🎯"})
        p = e.to_payload()
        self.assertEqual(p["type"], "emoji")
        self.assertEqual(p["emoji"], "🎯")

    def test_ncustom_emoji(self):
        from notion_lib.nTypes.icons import NCustomEmoji
        data = {"type": "custom_emoji", "custom_emoji": {
            "id": "abc", "name": "bufo", "url": "https://x.com/bufo.png"
        }}
        e = NCustomEmoji(data)
        self.assertEqual(e.id_, "abc")
        self.assertEqual(e.name, "bufo")

    def test_nemoji_factory_emoji(self):
        from notion_lib.nTypes.icons import NEmojiFactory, NEmoji
        e = NEmojiFactory.find({"type": "emoji", "emoji": "🔥"})
        self.assertIsInstance(e, NEmoji)

    def test_nemoji_factory_custom(self):
        from notion_lib.nTypes.icons import NEmojiFactory, NCustomEmoji
        e = NEmojiFactory.find({"type": "custom_emoji", "custom_emoji": {
            "id": "x", "name": "y", "url": "z"
        }})
        self.assertIsInstance(e, NCustomEmoji)

    def test_nemoji_factory_unknown_raises(self):
        from notion_lib.nTypes.icons import NEmojiFactory, EmojiError
        with self.assertRaises(EmojiError):
            NEmojiFactory.find({"type": "unknown"})

    def test_icon_factory_emoji(self):
        from notion_lib.nTypes.icons import IconFactory, NEmoji
        r = IconFactory.find({"type": "emoji", "emoji": "⭐"})
        self.assertIsInstance(r, NEmoji)

    def test_icon_factory_none(self):
        from notion_lib.nTypes.icons import IconFactory
        self.assertIsNone(IconFactory.find(None))

    def test_icon_factory_external_file(self):
        from notion_lib.nTypes.icons import IconFactory
        from notion_lib.nTypes.files import FileTypeExternal
        r = IconFactory.find({"type": "external", "external": {"url": "https://x.com/i.png"}})
        self.assertIsInstance(r, FileTypeExternal)


# ─────────────────────────────────────────────────────────────────────────────
# 8. nTypes/ds_filters
# ─────────────────────────────────────────────────────────────────────────────

class TestFiltersF(unittest.TestCase):

    def test_checkbox_equals(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.checkbox("Done").equals(True)
        self.assertEqual(f["property"], "Done")
        self.assertEqual(f["checkbox"]["equals"], True)

    def test_checkbox_does_not_equal(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.checkbox("Done").does_not_equal(False)
        self.assertIn("does_not_equal", f["checkbox"])

    def test_number_equals(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.number("Score").equals_number(42.0)
        self.assertEqual(f["number"]["equals"], 42.0)

    def test_number_greater_than(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.number("Score").greater_than(10)
        self.assertEqual(f["number"]["greater_than"], 10)

    def test_number_less_than_or_equal(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.number("Score").less_than_or_equal_to(100)
        self.assertIn("less_than_or_equal_to", f["number"])

    def test_number_is_empty(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.number("Score").is_empty()
        self.assertTrue(f["number"]["is_empty"])

    def test_date_after(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.date("Due").after("2025-01-01")
        self.assertEqual(f["date"]["after"], "2025-01-01")

    def test_date_next_week(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.date("Due").next_week()
        self.assertEqual(f["date"]["next_week"], {})

    def test_date_this_week(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.date("Due").this_week()
        self.assertIn("this_week", f["date"])

    def test_text_contains(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.rich_text("Desc").contains("urgent")
        self.assertEqual(f["rich_text"]["contains"], "urgent")

    def test_text_starts_with(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.rich_text("Name").starts_with("A")
        self.assertIn("starts_with", f["rich_text"])

    def test_text_is_empty(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.rich_text("Name").is_empty()
        self.assertTrue(f["rich_text"]["is_empty"])

    def test_select_equals(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.select("Priority").equals("High")
        self.assertEqual(f["select"]["equals"], "High")

    def test_multi_select_contains(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.multi_select("Tags").contains("urgent")
        self.assertEqual(f["multi_select"]["contains"], "urgent")

    def test_status_equals(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.status("Progress").equals("Done")
        self.assertEqual(f["status"]["equals"], "Done")

    def test_people_is_not_empty(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.people("Assignee").is_not_empty()
        self.assertTrue(f["people"]["is_not_empty"])

    def test_relation_contains(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.relation("Project").contains("Alpha")
        self.assertEqual(f["relation"]["contains"], "Alpha")

    def test_files_is_empty(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.files("Attachments").is_empty()
        self.assertTrue(f["files"]["is_empty"])

    def test_notion_id_greater_than(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.notion_id("ID").greater_than(42)
        self.assertEqual(f["ID"]["greater_than"], 42)

    def test_timestamp_created_on_or_before(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.timestamp("created_time").on_or_before("2025-12-01")
        self.assertEqual(f["timestamp"], "created_time")
        self.assertIn("on_or_before", f["created_time"])

    def test_timestamp_last_edited_after(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.timestamp("last_edited_time").after("2025-06-01")
        self.assertIn("after", f["last_edited_time"])

    def test_verification_status(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.verification("Ver").status("verified")
        self.assertEqual(f["verification"]["status"], "verified")

    def test_and_compound(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.and_(
            F.checkbox("Done").equals(True),
            F.select("Priority").equals("High"),
        )
        self.assertIn("and", f)
        self.assertEqual(len(f["and"]), 2)

    def test_or_compound(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.or_(
            F.select("Status").equals("Open"),
            F.select("Status").equals("Pending"),
        )
        self.assertIn("or", f)
        self.assertEqual(len(f["or"]), 2)

    def test_and_or_nested(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.and_(
            F.checkbox("Done").equals(True),
            F.or_(
                F.multi_select("Tags").contains("A"),
                F.multi_select("Tags").contains("B"),
            )
        )
        self.assertIn("or", f["and"][1])

    def test_rollup_any(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.rollup("Tasks").any("Complete")
        self.assertIn("any", f["rollup"])
        self.assertEqual(f["rollup"]["any"]["rich_text"]["contains"], "Complete")

    def test_rollup_every(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.rollup("Tasks").every("Done")
        self.assertIn("every", f["rollup"])

    def test_rollup_none(self):
        from notion_lib.nTypes.ds_filters import F
        f = F.rollup("Tasks").none("Blocked")
        self.assertIn("none", f["rollup"])

    def test_rollup_state_isolation(self):
        """_RollupFilter non deve condividere stato tra istanze diverse."""
        from notion_lib.nTypes.ds_filters import F
        r1 = F.rollup("A")
        r2 = F.rollup("B")
        p1 = r1.any("foo")
        p2 = r2.any("bar")
        self.assertEqual(p1["rollup"]["any"]["rich_text"]["contains"], "foo")
        self.assertEqual(p2["rollup"]["any"]["rich_text"]["contains"], "bar")
        # Verifica che p1 non sia stato contaminato
        self.assertEqual(p1["rollup"]["any"]["rich_text"]["contains"], "foo")


class TestSortS(unittest.TestCase):

    def test_single_ascending(self):
        from notion_lib.nTypes.ds_filters import S
        s = S().get(("Name", True))
        self.assertEqual(len(s["sorts"]), 1)
        self.assertEqual(s["sorts"][0]["direction"], "ascending")

    def test_single_descending(self):
        from notion_lib.nTypes.ds_filters import S
        s = S().get(("Name", False))
        self.assertEqual(s["sorts"][0]["direction"], "descending")

    def test_property_key(self):
        from notion_lib.nTypes.ds_filters import S
        s = S().get(("Name", True))
        self.assertEqual(s["sorts"][0]["property"], "Name")

    def test_timestamp_key(self):
        from notion_lib.nTypes.ds_filters import S
        s = S().get(("created_time", True))
        self.assertEqual(s["sorts"][0]["timestamp"], "created_time")
        self.assertNotIn("property", s["sorts"][0])

    def test_last_edited_time_uses_timestamp(self):
        from notion_lib.nTypes.ds_filters import S
        s = S().get(("last_edited_time", False))
        self.assertEqual(s["sorts"][0]["timestamp"], "last_edited_time")

    def test_multiple_sorts(self):
        from notion_lib.nTypes.ds_filters import S
        s = S().get(("Name", True), ("created_time", False), ("Score", True))
        self.assertEqual(len(s["sorts"]), 3)


# ─────────────────────────────────────────────────────────────────────────────
# 9. nTypes/page_properties
# ─────────────────────────────────────────────────────────────────────────────

class TestPropertyFactory(unittest.TestCase):

    def _prop(self, t, extra=None):
        base = {"type": t, "id": "abc"}
        if extra:
            base.update(extra)
        return base

    def test_title(self):
        from notion_lib.nTypes.page_properties import PropertyFactory, TitleProperty
        p = PropertyFactory.from_data("Name", self._prop("title", {"title": []}))
        self.assertIsInstance(p, TitleProperty)

    def test_rich_text(self):
        from notion_lib.nTypes.page_properties import PropertyFactory, RichTextProperty
        p = PropertyFactory.from_data("Desc", self._prop("rich_text", {"rich_text": []}))
        self.assertIsInstance(p, RichTextProperty)

    def test_number(self):
        from notion_lib.nTypes.page_properties import PropertyFactory, NumberProperty
        p = PropertyFactory.from_data("N", self._prop("number", {"number": 42}))
        self.assertIsInstance(p, NumberProperty)
        self.assertEqual(p.value, 42)

    def test_checkbox(self):
        from notion_lib.nTypes.page_properties import PropertyFactory, CheckboxProperty
        p = PropertyFactory.from_data("Done", self._prop("checkbox", {"checkbox": True}))
        self.assertIsInstance(p, CheckboxProperty)
        self.assertTrue(p.value)

    def test_select(self):
        from notion_lib.nTypes.page_properties import PropertyFactory
        p = PropertyFactory.from_data("P", self._prop("select", {"select": {"name": "High"}}))
        self.assertEqual(p.value, "High")

    def test_multi_select(self):
        from notion_lib.nTypes.page_properties import PropertyFactory
        p = PropertyFactory.from_data("T", self._prop("multi_select", {
            "multi_select": [{"name": "A"}, {"name": "B"}]
        }))
        self.assertEqual(p.value, ["A", "B"])

    def test_status(self):
        from notion_lib.nTypes.page_properties import PropertyFactory
        p = PropertyFactory.from_data("S", self._prop("status", {"status": {"name": "In Progress"}}))
        self.assertEqual(p.value, "In Progress")

    def test_date_with_start(self):
        from notion_lib.nTypes.page_properties import PropertyFactory, DateProperty
        p = PropertyFactory.from_data("D", self._prop("date", {
            "date": {"start": "2025-01-01", "end": None, "time_zone": None}
        }))
        self.assertIsInstance(p, DateProperty)
        self.assertIsNotNone(p.start)

    def test_date_none(self):
        from notion_lib.nTypes.page_properties import PropertyFactory
        p = PropertyFactory.from_data("D", self._prop("date", {"date": None}))
        self.assertIsNone(p.value)

    def test_url(self):
        from notion_lib.nTypes.page_properties import PropertyFactory
        p = PropertyFactory.from_data("U", self._prop("url", {"url": "https://x.com"}))
        self.assertEqual(p.value, "https://x.com")

    def test_email(self):
        from notion_lib.nTypes.page_properties import PropertyFactory
        p = PropertyFactory.from_data("E", self._prop("email", {"email": "a@b.com"}))
        self.assertEqual(p.value, "a@b.com")

    def test_phone_number(self):
        from notion_lib.nTypes.page_properties import PropertyFactory
        p = PropertyFactory.from_data("P", self._prop("phone_number", {"phone_number": "+39123"}))
        self.assertEqual(p.value, "+39123")

    def test_relation(self):
        from notion_lib.nTypes.page_properties import PropertyFactory
        p = PropertyFactory.from_data("R", self._prop("relation", {
            "relation": [{"id": "id1"}, {"id": "id2"}]
        }))
        self.assertEqual(p.value, ["id1", "id2"])

    def test_people(self):
        from notion_lib.nTypes.page_properties import PropertyFactory
        p = PropertyFactory.from_data("P", self._prop("people", {
            "people": [{"id": "u1"}]
        }))
        self.assertEqual(p.value, ["u1"])

    def test_formula_number(self):
        from notion_lib.nTypes.page_properties import PropertyFactory, FormulaProperty
        p = PropertyFactory.from_data("F", self._prop("formula", {
            "formula": {"type": "number", "number": 99.0}
        }))
        self.assertIsInstance(p, FormulaProperty)
        self.assertEqual(p.value, 99.0)

    def test_rollup(self):
        from notion_lib.nTypes.page_properties import PropertyFactory, RollupProperty
        p = PropertyFactory.from_data("R", self._prop("rollup", {
            "rollup": {"type": "number", "number": 5.0}
        }))
        self.assertIsInstance(p, RollupProperty)

    def test_unique_id(self):
        from notion_lib.nTypes.page_properties import PropertyFactory, UniqueIDProperty
        p = PropertyFactory.from_data("ID", self._prop("unique_id", {
            "unique_id": {"number": 42, "prefix": "PRJ"}
        }))
        self.assertIsInstance(p, UniqueIDProperty)
        self.assertEqual(p.value, 42)
        self.assertEqual(p.prefix, "PRJ")

    def test_created_time(self):
        from notion_lib.nTypes.page_properties import PropertyFactory, CreatedTimeProperty
        p = PropertyFactory.from_data("CT", self._prop("created_time", {
            "created_time": "2025-01-01T00:00:00Z"
        }))
        self.assertIsInstance(p, CreatedTimeProperty)

    def test_last_edited_time(self):
        from notion_lib.nTypes.page_properties import PropertyFactory, LastEditedTimeProperty
        p = PropertyFactory.from_data("LT", self._prop("last_edited_time", {
            "last_edited_time": "2025-06-01T00:00:00Z"
        }))
        self.assertIsInstance(p, LastEditedTimeProperty)

    def test_created_by(self):
        from notion_lib.nTypes.page_properties import PropertyFactory, CreatedByProperty
        p = PropertyFactory.from_data("CB", self._prop("created_by", {
            "created_by": {"id": "user-123"}
        }))
        self.assertIsInstance(p, CreatedByProperty)
        self.assertEqual(p.value, "user-123")

    def test_last_edited_by(self):
        from notion_lib.nTypes.page_properties import PropertyFactory
        p = PropertyFactory.from_data("LB", self._prop("last_edited_by", {
            "last_edited_by": {"id": "user-456"}
        }))
        self.assertEqual(p.value, "user-456")

    def test_files_readonly(self):
        from notion_lib.nTypes.page_properties import PropertyFactory, FilesProperty
        p = PropertyFactory.from_data("F", self._prop("files", {"files": []}))
        self.assertIsInstance(p, FilesProperty)
        with self.assertRaises(AttributeError):
            p.to_payload()

    # --- Tipi nuovi (precedentemente mancanti) ---

    def test_verification(self):
        from notion_lib.nTypes.page_properties import PropertyFactory, VerificationProperty
        p = PropertyFactory.from_data("V", self._prop("verification", {
            "verification": {"state": "verified", "verified_by": None, "date": None}
        }))
        self.assertIsInstance(p, VerificationProperty)
        self.assertEqual(p.value, "verified")

    def test_button(self):
        from notion_lib.nTypes.page_properties import PropertyFactory, ButtonProperty
        p = PropertyFactory.from_data("B", self._prop("button", {"button": {}}))
        self.assertIsInstance(p, ButtonProperty)
        self.assertIsNone(p.value)

    def test_location(self):
        from notion_lib.nTypes.page_properties import PropertyFactory, LocationProperty
        p = PropertyFactory.from_data("L", self._prop("location", {
            "location": {"latitude": 45.46, "longitude": 9.19}
        }))
        self.assertIsInstance(p, LocationProperty)
        self.assertAlmostEqual(p.latitude, 45.46)

    def test_place(self):
        from notion_lib.nTypes.page_properties import PropertyFactory, PlaceProperty
        p = PropertyFactory.from_data("P", self._prop("place", {"place": {"name": "Milan"}}))
        self.assertIsInstance(p, PlaceProperty)

    def test_last_visited_time(self):
        from notion_lib.nTypes.page_properties import PropertyFactory, LastVisitedTimeProperty
        p = PropertyFactory.from_data("LV", self._prop("last_visited_time", {
            "last_visited_time": "2025-03-01T12:00:00Z"
        }))
        self.assertIsInstance(p, LastVisitedTimeProperty)
        self.assertIsNotNone(p.value)

    def test_unknown_raises(self):
        from notion_lib.nTypes.page_properties import PropertyFactory
        with self.assertRaises(ValueError):
            PropertyFactory.from_data("X", {"type": "definitely_unknown", "id": "x"})

    # --- Payload writable ---

    def test_title_payload(self):
        from notion_lib.nTypes.page_properties import TitleProperty
        p = TitleProperty.from_data("Name", "id", {"title": []})
        p.value = "New Title"
        payload = p.to_payload()
        self.assertIn("Name", payload)
        self.assertIn("title", payload["Name"])

    def test_number_payload(self):
        from notion_lib.nTypes.page_properties import NumberProperty
        p = NumberProperty.from_data("Score", "id", {"number": 10})
        p.value = 99
        self.assertEqual(p.to_payload()["Score"]["number"], 99)

    def test_checkbox_payload(self):
        from notion_lib.nTypes.page_properties import CheckboxProperty
        p = CheckboxProperty.from_data("Done", "id", {"checkbox": False})
        p.value = True
        self.assertTrue(p.to_payload()["Done"]["checkbox"])

    def test_select_payload_none(self):
        from notion_lib.nTypes.page_properties import SelectProperty
        p = SelectProperty.from_data("P", "id", {"select": None})
        p.value = None
        self.assertIsNone(p.to_payload()["P"]["select"])

    def test_multi_select_payload(self):
        from notion_lib.nTypes.page_properties import MultiSelectProperty
        p = MultiSelectProperty.from_data("T", "id", {"multi_select": []})
        p.value = ["X", "Y"]
        names = [x["name"] for x in p.to_payload()["T"]["multi_select"]]
        self.assertEqual(names, ["X", "Y"])

    def test_date_payload_with_end(self):
        from notion_lib.nTypes.page_properties import DateProperty
        p = DateProperty.from_data("D", "id", {
            "date": {"start": "2025-01-01", "end": "2025-01-31", "time_zone": None}
        })
        payload = p.to_payload()
        self.assertIn("end", payload["D"]["date"])

    def test_date_payload_none(self):
        from notion_lib.nTypes.page_properties import DateProperty
        p = DateProperty.from_data("D", "id", {"date": None})
        self.assertIsNone(p.to_payload()["D"]["date"])

    def test_relation_payload(self):
        from notion_lib.nTypes.page_properties import RelationProperty
        p = RelationProperty.from_data("R", "id", {"relation": []})
        p.value = ["id-a", "id-b"]
        ids = [x["id"] for x in p.to_payload()["R"]["relation"]]
        self.assertEqual(ids, ["id-a", "id-b"])

    def test_people_payload(self):
        from notion_lib.nTypes.page_properties import PeopleProperty
        p = PeopleProperty.from_data("P", "id", {"people": []})
        p.value = ["u1"]
        objs = p.to_payload()["P"]["people"]
        self.assertEqual(objs[0]["object"], "user")
        self.assertEqual(objs[0]["id"], "u1")


# ─────────────────────────────────────────────────────────────────────────────
# 10. nModels/blocks — registry e tutti i tipi
# ─────────────────────────────────────────────────────────────────────────────

class TestBlockRegistry(unittest.TestCase):

    def test_all_expected_types_registered(self):
        from notion_lib.nModels.blocks.base_block import _ensure_registry_populated, _BLOCK_REGISTRY
        _ensure_registry_populated()
        required = [
            "paragraph",
            "heading_1", "heading_2", "heading_3",
            "to_do", "toggle", "bulleted_list_item", "numbered_list_item",
            "image", "video", "audio", "file", "pdf", "embed",
            "table", "table_row",
            "callout", "code", "synced_block", "breadcrumb",
            "child_page", "child_database", "equation", "bookmark",
            "link_to_page", "column_list", "column", "divider",
            "quote", "table_of_contents", "link_preview",
            "meeting_notes", "transcription",
        ]
        missing = [b for b in required if b not in _BLOCK_REGISTRY]
        self.assertEqual(missing, [], f"Blocchi non registrati: {missing}")

    def test_unsupported_block_fallback(self):
        from notion_lib.nModels.blocks.base_block import BlockFactory, UnsupportedBlock
        data = {"type": "completely_unknown_block_xyz", "completely_unknown_block_xyz": {}}
        blk = BlockFactory.from_data(headers=None, data=data, block_id="fake")
        self.assertIsInstance(blk, UnsupportedBlock)


class TestParagraphBlock(unittest.TestCase):

    def test_create_payload(self):
        from notion_lib.nModels.blocks.paragraph import ParagraphBlock
        b = ParagraphBlock.create("Hello")
        p = b.to_payload()
        self.assertIn("paragraph", p)
        self.assertEqual(p["paragraph"]["color"], "default")

    def test_rich_text_setter(self):
        from notion_lib.nModels.blocks.paragraph import ParagraphBlock
        b = ParagraphBlock.create("old")
        b.rich_text = "new"
        self.assertEqual(b._rich_text.text, "new")

    def test_color_setter(self):
        from notion_lib.nModels.blocks.paragraph import ParagraphBlock
        from notion_lib.utils.constants import NColors
        b = ParagraphBlock.create("x")
        b.color = NColors.BLUE_BACKGROUND
        self.assertEqual(b._color, "blue_background")

    def test_supports_children(self):
        from notion_lib.nModels.blocks.paragraph import ParagraphBlock
        self.assertTrue(ParagraphBlock.supports_children)

    def test_from_data(self):
        from notion_lib.nModels.blocks.paragraph import ParagraphBlock
        data = {
            "type": "paragraph",
            "paragraph": {
                "rich_text": [],
                "color": "red"
            }
        }
        b = ParagraphBlock.from_data(headers=None, data=data, block_id="fake-id")
        self.assertEqual(b._color, "red")


class TestHeadingBlocks(unittest.TestCase):

    def test_heading1_create(self):
        from notion_lib.nModels.blocks.heading import Heading1
        b = Heading1.create("Title")
        p = b.to_payload()
        self.assertIn("heading_1", p)

    def test_heading2_create(self):
        from notion_lib.nModels.blocks.heading import Heading2
        b = Heading2.create("H2")
        self.assertIn("heading_2", b.to_payload())

    def test_heading3_create(self):
        from notion_lib.nModels.blocks.heading import Heading3
        b = Heading3.create("H3")
        self.assertIn("heading_3", b.to_payload())

    def test_is_toggleable_false_no_children(self):
        from notion_lib.nModels.blocks.heading import Heading1
        b = Heading1.create("T", is_toggleable=False)
        self.assertFalse(b.supports_children)

    def test_is_toggleable_true_enables_children(self):
        from notion_lib.nModels.blocks.heading import Heading2
        b = Heading2.create("T", is_toggleable=True)
        self.assertTrue(b.supports_children)

    def test_is_toggleable_setter(self):
        from notion_lib.nModels.blocks.heading import Heading3
        b = Heading3.create("T")
        b.is_toggleable = True
        self.assertTrue(b.supports_children)
        b.is_toggleable = False
        self.assertFalse(b.supports_children)

    def test_from_data(self):
        from notion_lib.nModels.blocks.heading import Heading2
        data = {"type": "heading_2", "heading_2": {
            "rich_text": [], "color": "blue", "is_toggleable": True
        }}
        b = Heading2.from_data(None, data, "id")
        self.assertTrue(b._is_toggleable)
        self.assertTrue(b.supports_children)


class TestListBlocks(unittest.TestCase):

    def test_todo_create_unchecked(self):
        from notion_lib.nModels.blocks.list_blocks import ToDo
        b = ToDo.create("task")
        self.assertFalse(b._checked)
        self.assertIn("to_do", b.to_payload())

    def test_todo_create_checked(self):
        from notion_lib.nModels.blocks.list_blocks import ToDo
        b = ToDo.create("task", checked=True)
        self.assertTrue(b.to_payload()["to_do"]["checked"])

    def test_todo_checked_setter(self):
        from notion_lib.nModels.blocks.list_blocks import ToDo
        b = ToDo.create("task")
        b.checked = True
        self.assertTrue(b._checked)

    def test_toggle_create(self):
        from notion_lib.nModels.blocks.list_blocks import Toggle
        b = Toggle.create("toggle me")
        self.assertIn("toggle", b.to_payload())
        self.assertTrue(b.supports_children)

    def test_bulleted_list_item(self):
        from notion_lib.nModels.blocks.list_blocks import BulletedListItem
        b = BulletedListItem.create("bullet")
        self.assertIn("bulleted_list_item", b.to_payload())

    def test_numbered_list_item(self):
        from notion_lib.nModels.blocks.list_blocks import NumberedListItem
        b = NumberedListItem.create("1.")
        self.assertIn("numbered_list_item", b.to_payload())


class TestMediaBlocks(unittest.TestCase):

    def test_image_create(self):
        from notion_lib.nModels.blocks.media import Image
        from notion_lib.nTypes.files import FileTypeExternal
        fo = FileTypeExternal("https://x.com/img.png")
        b = Image.create("caption", fo)
        p = b.to_payload()
        self.assertIn("image", p)
        self.assertNotIn("type", p["image"])  # "type" rimosso nel payload

    def test_image_caption_setter(self):
        from notion_lib.nModels.blocks.media import Image
        from notion_lib.nTypes.files import FileTypeExternal
        b = Image.create("old", FileTypeExternal("https://x.com/a.png"))
        b.caption = "new caption"
        self.assertEqual(b._caption.text, "new caption")

    def test_video_create(self):
        from notion_lib.nModels.blocks.media import Video
        b = Video.create("https://youtube.com/watch?v=test", caption="yt video")
        p = b.to_payload()
        self.assertIn("video", p)

    def test_video_url_property(self):
        from notion_lib.nModels.blocks.media import Video
        b = Video.create("https://youtube.com/watch?v=test")
        self.assertEqual(b.url, "https://youtube.com/watch?v=test")

    def test_audio_create_raises(self):
        from notion_lib.nModels.blocks.media import Audio
        with self.assertRaises(NotImplementedError):
            Audio.create()

    def test_audio_to_payload_raises(self):
        from notion_lib.nModels.blocks.media import Audio
        b = Audio.__new__(Audio)
        b._file_object = None
        b._caption = None
        with self.assertRaises(NotImplementedError):
            b.to_payload()

    def test_embed_create(self):
        from notion_lib.nModels.blocks.media import Embed
        b = Embed.create("https://airtable.com/embed/123")
        self.assertEqual(b.to_payload()["embed"]["url"], "https://airtable.com/embed/123")

    def test_file_create(self):
        from notion_lib.nModels.blocks.media import File
        from notion_lib.nTypes.files import FileTypeExternal
        b = File.create("my file", FileTypeExternal("https://x.com/f.pdf"))
        self.assertIn("file", b.to_payload())

    def test_from_data_image(self):
        from notion_lib.nModels.blocks.media import Image
        data = {"type": "image", "image": {
            "type": "external",
            "external": {"url": "https://x.com/img.jpg"},
            "caption": []
        }}
        b = Image.from_data(None, data, "id")
        self.assertEqual(b._file_object.url, "https://x.com/img.jpg")


class TestTableBlocks(unittest.TestCase):

    def _make_row(self, *texts):
        from notion_lib.nModels.blocks.table import TableRowBlock
        from notion_lib.nTypes.rich_text import simple_rich_text_list
        return TableRowBlock.create([simple_rich_text_list(t) for t in texts])

    def test_table_row_create(self):
        row = self._make_row("A", "B", "C")
        self.assertEqual(len(row), 3)
        self.assertEqual(row.cell(1), "A")
        self.assertEqual(row.cell(3), "C")

    def test_table_row_payload(self):
        row = self._make_row("X", "Y")
        p = row.to_payload()
        self.assertIn("table_row", p)
        self.assertEqual(len(p["table_row"]["cells"]), 2)

    def test_table_create(self):
        from notion_lib.nModels.blocks.table import TableBlock
        rows = [self._make_row("H1", "H2"), self._make_row("V1", "V2")]
        t = TableBlock.create(2, True, False, cells=rows)
        p = t.to_payload()
        self.assertIn("table", p)
        self.assertTrue(p["table"]["has_column_header"])
        self.assertEqual(p["table"]["table_width"], 2)

    def test_table_create_wrong_width_raises(self):
        from notion_lib.nModels.blocks.table import TableBlock
        rows = [self._make_row("A", "B", "C")]  # 3 colonne invece di 2
        with self.assertRaises(ArithmeticError):
            TableBlock.create(2, False, False, cells=rows)

    def test_table_cell_access(self):
        from notion_lib.nModels.blocks.table import TableBlock
        rows = [self._make_row("R1C1", "R1C2"), self._make_row("R2C1", "R2C2")]
        t = TableBlock.create(2, False, False, cells=rows)
        self.assertEqual(t.cell(1, 1), "R1C1")
        self.assertEqual(t.cell(2, 2), "R2C2")

    def test_table_setitem(self):
        from notion_lib.nModels.blocks.table import TableBlock
        rows = [self._make_row("old", "x")]
        t = TableBlock.create(2, False, False, cells=rows)
        t[1, 1] = "new"
        self.assertEqual(t.cell(1, 1), "new")

    def test_table_getitem_tuple(self):
        from notion_lib.nModels.blocks.table import TableBlock
        rows = [self._make_row("val", "x")]
        t = TableBlock.create(2, False, False, cells=rows)
        self.assertEqual(t[1, 1], "val")

    def test_table_has_row_header_setter(self):
        from notion_lib.nModels.blocks.table import TableBlock
        t = TableBlock.create(1, False, False, cells=[self._make_row("x")])
        t.has_row_header = True
        self.assertTrue(t._has_row_header)


class TestSpecialBlocks(unittest.TestCase):

    def test_callout_create(self):
        from notion_lib.nModels.blocks.special_blocks import CalloutBlock
        from notion_lib.nTypes.icons import NEmoji
        from notion_lib.utils.constants import NColors
        icon = NEmoji({"type": "emoji", "emoji": "⚡"})
        b = CalloutBlock.create("note", icon, NColors.YELLOW_BACKGROUND)
        p = b.to_payload()
        self.assertIn("callout", p)
        self.assertEqual(p["callout"]["icon"]["emoji"], "⚡")

    def test_code_create(self):
        from notion_lib.nModels.blocks.special_blocks import CodeBlock
        from notion_lib.utils.constants import NLanguage
        b = CodeBlock.create("print('hi')", NLanguage.PYTHON, "example")
        p = b.to_payload()
        self.assertEqual(p["code"]["language"], "python")

    def test_code_language_setter(self):
        from notion_lib.nModels.blocks.special_blocks import CodeBlock
        from notion_lib.utils.constants import NLanguage
        b = CodeBlock.create("x = 1", NLanguage.PYTHON)
        b.language = NLanguage.JAVASCRIPT
        self.assertEqual(b._language, "javascript")

    def test_equation_create(self):
        from notion_lib.nModels.blocks.special_blocks import EquationBlock
        b = EquationBlock.create("e=mc^2")
        self.assertEqual(b.to_payload()["equation"]["expression"], "e=mc^2")

    def test_bookmark_create(self):
        from notion_lib.nModels.blocks.special_blocks import BookmarkBlock
        b = BookmarkBlock.create(url="https://notion.so", caption="Notion")
        p = b.to_payload()
        self.assertEqual(p["bookmark"]["url"], "https://notion.so")

    def test_breadcrumb_create(self):
        from notion_lib.nModels.blocks.special_blocks import BreadcrumbBlock
        b = BreadcrumbBlock.create()
        self.assertEqual(b.to_payload(), {"breadcrumb": {}})

    def test_divider_create(self):
        from notion_lib.nModels.blocks.special_blocks import DividerBlock
        b = DividerBlock.create()
        self.assertEqual(b.to_payload(), {"divider": {}})

    def test_child_page_create(self):
        from notion_lib.nModels.blocks.special_blocks import ChildPageBlock
        b = ChildPageBlock.create("My Child Page")
        self.assertEqual(b.to_payload()["child_page"]["title"], "My Child Page")

    def test_child_page_title_setter(self):
        from notion_lib.nModels.blocks.special_blocks import ChildPageBlock
        b = ChildPageBlock.create("Old")
        b.title = "New"
        self.assertEqual(b._title, "New")

    def test_child_database_create(self):
        from notion_lib.nModels.blocks.special_blocks import ChildDatabaseBlock
        b = ChildDatabaseBlock.create("DB Title")
        self.assertEqual(b.to_payload()["child_database"]["title"], "DB Title")

    def test_synced_block_no_source(self):
        from notion_lib.nModels.blocks.special_blocks import SyncedBlock
        b = SyncedBlock.create(synced_from=None)
        p = b.to_payload()
        self.assertIsNone(p["synced_block"]["synced_from"])

    def test_synced_block_with_source(self):
        from notion_lib.nModels.blocks.special_blocks import SyncedBlock
        b = SyncedBlock.create(synced_from={"block_id": "abc"})
        p = b.to_payload()
        self.assertNotIn("children", p["synced_block"])

    def test_link_to_page_readonly(self):
        from notion_lib.nModels.blocks.special_blocks import LinkToPageBlock
        with self.assertRaises(NotImplementedError):
            LinkToPageBlock.create()

    def test_link_to_page_from_data(self):
        from notion_lib.nModels.blocks.special_blocks import LinkToPageBlock
        data = {"type": "link_to_page", "link_to_page": {
            "type": "page_id", "page_id": "abc123def456abc123def456abc123de"
        }}
        b = LinkToPageBlock.from_data(None, data, "id")
        self.assertEqual(b.target_type, "page_id")
        self.assertEqual(b.target_id, "abc123def456abc123def456abc123de")

    def test_link_to_page_to_payload_raises(self):
        from notion_lib.nModels.blocks.special_blocks import LinkToPageBlock
        data = {"type": "link_to_page", "link_to_page": {"type": "page_id", "page_id": "x" * 32}}
        b = LinkToPageBlock.from_data(None, data, "id")
        with self.assertRaises(NotImplementedError):
            b.to_payload()

    def test_link_preview_readonly(self):
        from notion_lib.nModels.blocks.special_blocks import LinkPreviewBlock
        with self.assertRaises(NotImplementedError):
            LinkPreviewBlock.create()

    def test_quote_create(self):
        from notion_lib.nModels.blocks.special_blocks import QuoteBlock
        from notion_lib.utils.constants import NColors
        b = QuoteBlock.create("quote text", NColors.BLUE)
        p = b.to_payload()
        self.assertIn("quote", p)
        self.assertEqual(p["quote"]["color"], "blue")

    def test_quote_children_in_payload_when_no_block_id(self):
        from notion_lib.nModels.blocks.special_blocks import QuoteBlock
        from notion_lib.nModels.blocks.paragraph import ParagraphBlock
        from notion_lib.utils.constants import NColors
        child = ParagraphBlock.create("child")
        b = QuoteBlock.create("parent", NColors.DEFAULT, children=[child])
        p = b.to_payload()
        self.assertIn("children", p["quote"])

    def test_toc_create(self):
        from notion_lib.nModels.blocks.special_blocks import TableOfContentsBlock
        from notion_lib.utils.constants import NColors
        b = TableOfContentsBlock.create(NColors.GRAY)
        self.assertEqual(b.to_payload()["table_of_contents"]["color"], "gray")

    def test_column_list_create(self):
        from notion_lib.nModels.blocks.special_blocks import ColumnListBlock
        b = ColumnListBlock.create()
        self.assertIsInstance(b, ColumnListBlock)

    def test_column_create(self):
        from notion_lib.nModels.blocks.special_blocks import ColumnBlock
        b = ColumnBlock.create(ratio=0.5)
        self.assertEqual(b._ratio, 0.5)

    def test_column_payload_includes_ratio(self):
        from notion_lib.nModels.blocks.special_blocks import ColumnBlock
        b = ColumnBlock.create(ratio=0.33)
        p = b.to_payload()
        self.assertIn("width_ratio", p["column"])
        self.assertEqual(p["column"]["width_ratio"], 0.33)

    def test_append_children_isinstance_filter(self):
        """Verifica che ChildPageBlock e ChildDatabaseBlock siano esclusi correttamente."""
        from notion_lib.nModels.blocks.special_blocks import ChildPageBlock, ChildDatabaseBlock
        from notion_lib.nModels.blocks.paragraph import ParagraphBlock

        children = [
            ParagraphBlock.create("para1"),
            ChildPageBlock.create("page"),
            ParagraphBlock.create("para2"),
            ChildDatabaseBlock.create("db"),
        ]
        filtered = [
            c.to_payload()
            for c in children
            if not isinstance(c, (ChildDatabaseBlock, ChildPageBlock))
        ]
        self.assertEqual(len(filtered), 2)


class TestMeetingNotesBlock(unittest.TestCase):

    def _make_data(self, status="notes_ready"):
        return {
            "type": "meeting_notes",
            "meeting_notes": {
                "title": [],
                "status": status,
                "children": {
                    "summary_block_id": "sum-id-" + "0" * 26,
                    "notes_block_id": "note-id" + "0" * 25,
                    "transcript_block_id": "trans-i" + "0" * 25,
                },
                "calendar_event": {
                    "start_time": "2025-03-01T10:00:00Z",
                    "end_time": "2025-03-01T11:00:00Z",
                    "attendees": [{"email": "a@b.com"}],
                },
                "recording": {
                    "start_time": "2025-03-01T10:01:00Z",
                    "end_time": "2025-03-01T10:59:00Z",
                }
            }
        }

    def test_from_data_ready(self):
        from notion_lib.nModels.blocks.meeting_notes import MeetingNotesBlock, MeetingNotesStatus
        b = MeetingNotesBlock.from_data(None, self._make_data(), "block-id" + "0" * 24)
        self.assertTrue(b.is_ready)
        self.assertEqual(b.status, MeetingNotesStatus.NOTES_READY)

    def test_from_data_in_progress(self):
        from notion_lib.nModels.blocks.meeting_notes import MeetingNotesBlock
        b = MeetingNotesBlock.from_data(None, self._make_data("transcription_in_progress"), "id" + "0" * 30)
        self.assertFalse(b.is_ready)

    def test_attendees(self):
        from notion_lib.nModels.blocks.meeting_notes import MeetingNotesBlock
        b = MeetingNotesBlock.from_data(None, self._make_data(), "id" + "0" * 30)
        self.assertEqual(len(b.attendees), 1)

    def test_recording_dates(self):
        from notion_lib.nModels.blocks.meeting_notes import MeetingNotesBlock
        from notion_lib.nTypes.primitives import NDate
        b = MeetingNotesBlock.from_data(None, self._make_data(), "id" + "0" * 30)
        self.assertIsInstance(b.recording_start, NDate)
        self.assertIsInstance(b.recording_end, NDate)

    def test_create_raises(self):
        from notion_lib.nModels.blocks.meeting_notes import MeetingNotesBlock
        with self.assertRaises(NotImplementedError):
            MeetingNotesBlock.create()

    def test_to_payload_raises(self):
        from notion_lib.nModels.blocks.meeting_notes import MeetingNotesBlock
        b = MeetingNotesBlock.from_data(None, self._make_data(), "id" + "0" * 30)
        with self.assertRaises(NotImplementedError):
            b.to_payload()

    def test_supports_children(self):
        from notion_lib.nModels.blocks.meeting_notes import MeetingNotesBlock
        self.assertTrue(MeetingNotesBlock.supports_children)

    def test_not_updatable(self):
        from notion_lib.nModels.blocks.meeting_notes import MeetingNotesBlock
        self.assertFalse(MeetingNotesBlock.updatable)


# ─────────────────────────────────────────────────────────────────────────────
# 11. nModels/pages  (_apply, PageFactory routing)
# ─────────────────────────────────────────────────────────────────────────────

class TestSimplePage(unittest.TestCase):

    def _make_raw(self, title_text="My Page"):
        return {
            "object": "page",
            "id": "2a7b7a8f729480b3b420f8736c4116d7",
            "parent": {"type": "page_id", "page_id": "parent-id" + "0" * 23},
            "archived": False,
            "in_trash": False,
            "url": "https://notion.so/My-Page-abc",
            "icon": None,
            "cover": None,
            "properties": {
                "title": {
                    "id": "title", "type": "title",
                    "title": [{"plain_text": title_text, "type": "text",
                               "text": {"content": title_text, "link": None},
                               "annotations": {"bold": False, "italic": False,
                                               "strikethrough": False, "underline": False,
                                               "code": False, "color": "default"},
                               "href": None}]
                }
            }
        }

    def test_apply_sets_title(self):
        from notion_lib.nModels.pages import SimplePage
        p = SimplePage(headers={}, page_id="2a7b7a8f729480b3b420f8736c4116d7")
        p._apply(self._make_raw("Test Title"))
        self.assertEqual(p.title, "Test Title")

    def test_title_setter(self):
        from notion_lib.nModels.pages import SimplePage
        p = SimplePage(headers={}, page_id="2a7b7a8f729480b3b420f8736c4116d7")
        p._apply(self._make_raw())
        p.title = "Renamed"
        self.assertEqual(p.title, "Renamed")

    def test_url_property(self):
        from notion_lib.nModels.pages import SimplePage
        p = SimplePage(headers={}, page_id="2a7b7a8f729480b3b420f8736c4116d7")
        p._apply(self._make_raw())
        self.assertIn("notion.so", p.url)

    def test_to_payload_structure(self):
        from notion_lib.nModels.pages import SimplePage
        p = SimplePage(headers={}, page_id="2a7b7a8f729480b3b420f8736c4116d7")
        p._apply(self._make_raw("Hello"))
        payload = p.to_payload()
        self.assertIn("properties", payload)
        self.assertIn("title", payload["properties"])

    def test_icon_none(self):
        from notion_lib.nModels.pages import SimplePage
        p = SimplePage(headers={}, page_id="2a7b7a8f729480b3b420f8736c4116d7")
        p._apply(self._make_raw())
        self.assertIsNone(p.icon)

    def test_icon_emoji(self):
        from notion_lib.nModels.pages import SimplePage
        from notion_lib.nTypes.icons import NEmoji
        raw = self._make_raw()
        raw["icon"] = {"type": "emoji", "emoji": "🚀"}
        p = SimplePage(headers={}, page_id="2a7b7a8f729480b3b420f8736c4116d7")
        p._apply(raw)
        self.assertIsInstance(p.icon, NEmoji)


class TestDatabasePage(unittest.TestCase):

    def _make_raw(self):
        return {
            "object": "page",
            "id": "2a7b7a8f729480b3b420f8736c4116d7",
            "parent": {"type": "database_id", "database_id": "db-id" + "0" * 27},
            "archived": False,
            "in_trash": False,
            "url": "https://notion.so/entry-abc",
            "icon": None,
            "cover": None,
            "properties": {
                "Name": {"id": "title", "type": "title",
                         "title": [{"plain_text": "Entry 1", "type": "text",
                                    "text": {"content": "Entry 1", "link": None},
                                    "annotations": {"bold": False, "italic": False,
                                                    "strikethrough": False, "underline": False,
                                                    "code": False, "color": "default"},
                                    "href": None}]},
                "Score": {"id": "sc", "type": "number", "number": 77},
                "Done": {"id": "dn", "type": "checkbox", "checkbox": True},
            }
        }

    def test_apply_loads_properties(self):
        from notion_lib.nModels.pages import DatabasePage
        p = DatabasePage(headers={}, page_id="2a7b7a8f729480b3b420f8736c4116d7")
        p._apply(self._make_raw())
        self.assertIn("Name", p.properties)
        self.assertIn("Score", p.properties)

    def test_prop_access(self):
        from notion_lib.nModels.pages import DatabasePage
        p = DatabasePage(headers={}, page_id="2a7b7a8f729480b3b420f8736c4116d7")
        p._apply(self._make_raw())
        self.assertEqual(p.prop("Score").value, 77)

    def test_set_prop(self):
        from notion_lib.nModels.pages import DatabasePage
        p = DatabasePage(headers={}, page_id="2a7b7a8f729480b3b420f8736c4116d7")
        p._apply(self._make_raw())
        p.set_prop("Score", 99)
        self.assertEqual(p.prop("Score").value, 99)

    def test_set_prop_chaining(self):
        from notion_lib.nModels.pages import DatabasePage
        p = DatabasePage(headers={}, page_id="2a7b7a8f729480b3b420f8736c4116d7")
        p._apply(self._make_raw())
        result = p.set_prop("Score", 10).set_prop("Done", False)
        self.assertIs(result, p)

    def test_prop_not_found_raises(self):
        from notion_lib.nModels.pages import DatabasePage
        p = DatabasePage(headers={}, page_id="2a7b7a8f729480b3b420f8736c4116d7")
        p._apply(self._make_raw())
        with self.assertRaises(KeyError):
            p.prop("NonExistent")

    def test_title_method(self):
        from notion_lib.nModels.pages import DatabasePage
        p = DatabasePage(headers={}, page_id="2a7b7a8f729480b3b420f8736c4116d7")
        p._apply(self._make_raw())
        self.assertEqual(p.title(), "Entry 1")

    def test_to_payload_excludes_readonly(self):
        from notion_lib.nModels.pages import DatabasePage
        p = DatabasePage(headers={}, page_id="2a7b7a8f729480b3b420f8736c4116d7")
        p._apply(self._make_raw())
        payload = p.to_payload()
        # formula/rollup/files non presenti = nessun errore
        self.assertIn("properties", payload)


class TestPageFactory(unittest.TestCase):

    @patch("requests.request")
    def test_routes_page_parent_to_simple(self, mock_req):
        from notion_lib.nModels.pages import PageFactory, SimplePage
        from notion_lib.client.https import invalidate_cache
        invalidate_cache()
        raw = {
            "object": "page", "id": "2a7b7a8f729480b3b420f8736c4116d7",
            "parent": {"type": "page_id", "page_id": "parent" + "0" * 26},
            "archived": False, "in_trash": False, "url": "https://notion.so/x",
            "icon": None, "cover": None,
            "properties": {"title": {"id": "title", "type": "title", "title": []}}
        }
        mock_req.return_value = _fake_response(raw)
        page = PageFactory.find({}, "2a7b7a8f729480b3b420f8736c4116d7")
        self.assertIsInstance(page, SimplePage)

    @patch("requests.request")
    def test_routes_database_parent_to_database_page(self, mock_req):
        from notion_lib.nModels.pages import PageFactory, DatabasePage
        from notion_lib.client.https import invalidate_cache
        invalidate_cache()
        raw = {
            "object": "page", "id": "2a7b7a8f729480b3b420f8736c4116d7",
            "parent": {"type": "database_id", "database_id": "db" + "0" * 30},
            "archived": False, "in_trash": False, "url": "https://notion.so/x",
            "icon": None, "cover": None,
            "properties": {}
        }
        mock_req.return_value = _fake_response(raw)
        page = PageFactory.find({}, "2a7b7a8f729480b3b420f8736c4116d7")
        # FIX verificato: database_id → DatabasePage
        self.assertIsInstance(page, DatabasePage)

    @patch("requests.request")
    def test_routes_data_source_to_database_page(self, mock_req):
        from notion_lib.nModels.pages import PageFactory, DatabasePage
        from notion_lib.client.https import invalidate_cache
        invalidate_cache()
        raw = {
            "object": "page", "id": "2a7b7a8f729480b3b420f8736c4116d7",
            "parent": {"type": "data_source_id", "data_source_id": "ds" + "0" * 30},
            "archived": False, "in_trash": False, "url": "https://notion.so/x",
            "icon": None, "cover": None,
            "properties": {}
        }
        mock_req.return_value = _fake_response(raw)
        page = PageFactory.find({}, "2a7b7a8f729480b3b420f8736c4116d7")
        self.assertIsInstance(page, DatabasePage)

    @patch("requests.request")
    def test_routes_workspace_to_simple(self, mock_req):
        from notion_lib.nModels.pages import PageFactory, SimplePage
        from notion_lib.client.https import invalidate_cache
        invalidate_cache()
        raw = {
            "object": "page", "id": "2a7b7a8f729480b3b420f8736c4116d7",
            "parent": {"type": "workspace", "workspace": True},
            "archived": False, "in_trash": False, "url": "https://notion.so/x",
            "icon": None, "cover": None,
            "properties": {"title": {"id": "title", "type": "title", "title": []}}
        }
        mock_req.return_value = _fake_response(raw)
        page = PageFactory.find({}, "2a7b7a8f729480b3b420f8736c4116d7")
        self.assertIsInstance(page, SimplePage)


# ─────────────────────────────────────────────────────────────────────────────
# 12. nModels/databases
# ─────────────────────────────────────────────────────────────────────────────

class TestNDatabase(unittest.TestCase):

    def _make_raw(self, title="Test DB"):
        return {
            "object": "database",
            "id": "2a7b7a8f7294801ab914e1f063fab45a",
            "parent": {"type": "page_id", "page_id": "p" + "0" * 31},
            "title": [{"plain_text": title, "type": "text",
                       "text": {"content": title, "link": None},
                       "annotations": {"bold": False, "italic": False,
                                       "strikethrough": False, "underline": False,
                                       "code": False, "color": "default"},
                       "href": None}],
            "is_inline": True,
            "is_locked": False,
            "archived": False,
            "in_trash": False,
            "data_sources": [
                {"id": "ds-id" + "0" * 27, "name": "DS 1"},
                {"id": "ds-id" + "1" * 27, "name": "DS 2"},
            ],
            "properties": {},
            "url": "https://notion.so/db-abc",
        }

    def test_apply_title(self):
        from notion_lib.nModels.databases import NDatabase
        db = NDatabase({}, "2a7b7a8f7294801ab914e1f063fab45a")
        db._apply(self._make_raw("My DB"))
        self.assertEqual(db.title, "My DB")

    def test_apply_is_inline(self):
        from notion_lib.nModels.databases import NDatabase
        db = NDatabase({}, "2a7b7a8f7294801ab914e1f063fab45a")
        db._apply(self._make_raw())
        self.assertTrue(db.is_inline)

    def test_apply_is_locked(self):
        from notion_lib.nModels.databases import NDatabase
        db = NDatabase({}, "2a7b7a8f7294801ab914e1f063fab45a")
        db._apply(self._make_raw())
        self.assertFalse(db.is_locked)

    def test_datasources_count(self):
        from notion_lib.nModels.databases import NDatabase
        db = NDatabase({}, "2a7b7a8f7294801ab914e1f063fab45a")
        db._apply(self._make_raw())
        self.assertEqual(len(db._raw_datasources), 2)

    def test_title_setter(self):
        from notion_lib.nModels.databases import NDatabase
        db = NDatabase({}, "2a7b7a8f7294801ab914e1f063fab45a")
        db._apply(self._make_raw())
        db.title = "Renamed DB"
        self.assertEqual(db.title, "Renamed DB")

    def test_to_payload_contains_title(self):
        from notion_lib.nModels.databases import NDatabase
        db = NDatabase({}, "2a7b7a8f7294801ab914e1f063fab45a")
        db._apply(self._make_raw("DB Payload"))
        p = db.to_payload()
        self.assertIn("title", p)

    def test_repr(self):
        from notion_lib.nModels.databases import NDatabase
        db = NDatabase({}, "2a7b7a8f7294801ab914e1f063fab45a")
        db._apply(self._make_raw("Repr DB"))
        self.assertIn("Repr DB", repr(db))


# ─────────────────────────────────────────────────────────────────────────────
# 13. nModels/datasources
# ─────────────────────────────────────────────────────────────────────────────

class TestNDataSource(unittest.TestCase):

    def _make_raw(self, title="Test DS"):
        return {
            "object": "data_source",
            "id": "ds-id-" + "0" * 26,
            "title": [{"plain_text": title, "type": "text",
                       "text": {"content": title, "link": None},
                       "annotations": {"bold": False, "italic": False,
                                       "strikethrough": False, "underline": False,
                                       "code": False, "color": "default"},
                       "href": None}],
            "parent": {"type": "database_id", "database_id": "db" + "0" * 30},
            "properties": {
                "Name": {"id": "title", "type": "title", "title": {}},
                "Score": {"id": "sc", "type": "number", "number": {}},
            },
            "archived": False,
            "in_trash": False,
        }

    def test_apply_title(self):
        from notion_lib.nModels.datasources import NDataSource
        ds = NDataSource({}, "ds-id-" + "0" * 26)
        ds._apply(self._make_raw("My DS"))
        self.assertEqual(ds.title, "My DS")

    def test_apply_schema(self):
        from notion_lib.nModels.datasources import NDataSource
        ds = NDataSource({}, "ds-id-" + "0" * 26)
        ds._apply(self._make_raw())
        self.assertIn("Name", ds.schema)
        self.assertIn("Score", ds.schema)

    def test_apply_parent_db_id(self):
        from notion_lib.nModels.datasources import NDataSource
        ds = NDataSource({}, "ds-id-" + "0" * 26)
        ds._apply(self._make_raw())
        self.assertIsNotNone(ds.parent_db_id)

    def test_title_setter(self):
        from notion_lib.nModels.datasources import NDataSource
        ds = NDataSource({}, "ds-id-" + "0" * 26)
        ds._apply(self._make_raw())
        ds.title = "Renamed DS"
        self.assertEqual(ds.title, "Renamed DS")

    def test_templates_cache_invalidated_on_apply(self):
        from notion_lib.nModels.datasources import NDataSource
        ds = NDataSource({}, "ds-id-" + "0" * 26)
        ds._apply(self._make_raw())
        self.assertIsNone(ds._templates)

    def test_repr(self):
        from notion_lib.nModels.datasources import NDataSource
        ds = NDataSource({}, "ds-id-" + "0" * 26)
        ds._apply(self._make_raw("Repr DS"))
        self.assertIn("Repr DS", repr(ds))


class TestDataSourceTemplate(unittest.TestCase):

    def test_properties(self):
        from notion_lib.nModels.datasources import DataSourceTemplate
        t = DataSourceTemplate({"id": "t-id", "name": "Template A", "is_default": True})
        self.assertEqual(t.id, "t-id")
        self.assertEqual(t.name, "Template A")
        self.assertTrue(t.is_default)

    def test_not_default(self):
        from notion_lib.nModels.datasources import DataSourceTemplate
        t = DataSourceTemplate({"id": "x", "name": "B", "is_default": False})
        self.assertFalse(t.is_default)

    def test_repr_default_tag(self):
        from notion_lib.nModels.datasources import DataSourceTemplate
        t = DataSourceTemplate({"id": "x", "name": "Default", "is_default": True})
        self.assertIn("[default]", repr(t))


# ─────────────────────────────────────────────────────────────────────────────
# 14. nModels/user
# ─────────────────────────────────────────────────────────────────────────────

class TestNUser(unittest.TestCase):

    def _person_raw(self):
        return {
            "object": "user",
            "id": "aaaa0001" * 4,
            "type": "person",
            "name": "Alice",
            "avatar_url": "https://x.com/avatar.png",
            "person": {"email": "alice@example.com"},
        }

    def _bot_user_raw(self):
        return {
            "object": "user",
            "id": "bbbb0002" * 4,
            "type": "bot",
            "name": "My Bot",
            "avatar_url": None,
            "bot": {},
            "owner": {"type": "user", "user": {"id": "cccc0003" * 4}},
        }

    def _bot_workspace_raw(self):
        return {
            "object": "user",
            "id": "dddd0004" * 4,
            "type": "bot",
            "name": "Workspace Bot",
            "avatar_url": None,
            "bot": {},
            "owner": {"type": "workspace"},
            "workspace_name": "My Workspace",
        }

    @patch("requests.request")
    def test_person_name(self, mock_req):
        from notion_lib.nModels.user import UserFactory
        from notion_lib.client.https import invalidate_cache
        invalidate_cache()
        mock_req.return_value = _fake_response(self._person_raw())
        u = UserFactory.create({}, "aaaa0001" * 4)
        self.assertEqual(u.name, "Alice")

    @patch("requests.request")
    def test_person_email(self, mock_req):
        from notion_lib.nModels.user import UserFactory, NPerson
        from notion_lib.client.https import invalidate_cache
        invalidate_cache()
        mock_req.return_value = _fake_response(self._person_raw())
        u = UserFactory.create({}, "aaaa0001" * 4)
        self.assertIsInstance(u, NPerson)
        self.assertEqual(u.email, "alice@example.com")

    @patch("requests.request")
    def test_bot_user(self, mock_req):
        from notion_lib.nModels.user import UserFactory, NBotUser
        from notion_lib.client.https import invalidate_cache
        invalidate_cache()
        mock_req.return_value = _fake_response(self._bot_user_raw())
        u = UserFactory.create({}, "bbbb0002" * 4)
        self.assertIsInstance(u, NBotUser)
        self.assertEqual(u.owner_type, "user")

    @patch("requests.request")
    def test_bot_workspace(self, mock_req):
        from notion_lib.nModels.user import UserFactory, NBotWorkspace
        from notion_lib.client.https import invalidate_cache
        invalidate_cache()
        mock_req.return_value = _fake_response(self._bot_workspace_raw())
        u = UserFactory.create({}, "dddd0004" * 4)
        self.assertIsInstance(u, NBotWorkspace)
        self.assertEqual(u.owner_type, "workspace")

    @patch("requests.request")
    def test_user_avatar(self, mock_req):
        from notion_lib.nModels.user import UserFactory
        from notion_lib.client.https import invalidate_cache
        invalidate_cache()
        mock_req.return_value = _fake_response(self._person_raw())
        u = UserFactory.create({}, "aaaa0001" * 4)
        self.assertEqual(u.avatar, "https://x.com/avatar.png")

    @patch("requests.request")
    def test_user_type_property(self, mock_req):
        from notion_lib.nModels.user import UserFactory
        from notion_lib.client.https import invalidate_cache
        invalidate_cache()
        mock_req.return_value = _fake_response(self._person_raw())
        u = UserFactory.create({}, "aaaa0001" * 4)
        self.assertEqual(u.type, "person")

    @patch("requests.request")
    def test_unknown_type_raises(self, mock_req):
        from notion_lib.nModels.user import UserFactory, UserError
        from notion_lib.client.https import invalidate_cache
        invalidate_cache()
        mock_req.return_value = _fake_response({
            "object": "user", "id": "eeee0005" * 4, "type": "alien", "name": "ET"
        })
        with self.assertRaises(UserError):
            UserFactory.create({}, "eeee0005" * 4)


# ─────────────────────────────────────────────────────────────────────────────
# 15. nModels/blocks/base_block  (NObjBlock, NFactory via mock)
# ─────────────────────────────────────────────────────────────────────────────

class TestNObjBlock(unittest.TestCase):

    @patch("requests.request")
    def test_nfactory_find_paragraph(self, mock_req):
        from notion_lib.nModels.blocks.base_block import NFactory
        from notion_lib.nModels.blocks.paragraph import ParagraphBlock
        from notion_lib.client.https import invalidate_cache
        invalidate_cache()
        raw = {
            "object": "block",
            "id": "2a7b7a8f729481078b12e5862da8ce76",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text",
                               "text": {"content": "Hello", "link": None},
                               "annotations": {"bold": False, "italic": False,
                                               "strikethrough": False, "underline": False,
                                               "code": False, "color": "default"},
                               "plain_text": "Hello", "href": None}],
                "color": "default"
            },
            "archived": False, "in_trash": False,
            "has_children": False, "parent": {"type": "page_id", "page_id": "p" * 32},
            "created_time": "2025-01-01T00:00:00Z",
            "last_edited_time": "2025-01-01T00:00:00Z",
        }
        mock_req.return_value = _fake_response(raw)
        blk = NFactory.find({}, "2a7b7a8f729481078b12e5862da8ce76")
        self.assertIsInstance(blk, ParagraphBlock)

    @patch("requests.request")
    def test_nfactory_find_heading(self, mock_req):
        from notion_lib.nModels.blocks.base_block import NFactory
        from notion_lib.nModels.blocks.heading import Heading1
        from notion_lib.client.https import invalidate_cache
        invalidate_cache()
        raw = {
            "object": "block",
            "id": "2a7b7a8f7294814297b9cc59924601e3",
            "type": "heading_1",
            "heading_1": {"rich_text": [], "color": "default", "is_toggleable": False},
            "archived": False, "in_trash": False, "has_children": False,
            "parent": {"type": "page_id", "page_id": "p" * 32},
            "created_time": "2025-01-01T00:00:00Z",
            "last_edited_time": "2025-01-01T00:00:00Z",
        }
        mock_req.return_value = _fake_response(raw)
        blk = NFactory.find({}, "2a7b7a8f7294814297b9cc59924601e3")
        self.assertIsInstance(blk, Heading1)

    @patch("requests.request")
    def test_nfactory_unsupported_fallback(self, mock_req):
        from notion_lib.nModels.blocks.base_block import NFactory, UnsupportedBlock
        from notion_lib.client.https import invalidate_cache
        invalidate_cache()
        raw = {
            "object": "block",
            "id": "2a7b7a8f7294814297b9cc59924601e3",
            "type": "unknown_future_block",
            "unknown_future_block": {},
            "archived": False, "in_trash": False, "has_children": False,
            "parent": {"type": "page_id", "page_id": "p" * 32},
            "created_time": "2025-01-01T00:00:00Z",
            "last_edited_time": "2025-01-01T00:00:00Z",
        }
        mock_req.return_value = _fake_response(raw)
        blk = NFactory.find({}, "2a7b7a8f7294814297b9cc59924601e3")
        self.assertIsInstance(blk, UnsupportedBlock)


# ─────────────────────────────────────────────────────────────────────────────
# 16. nModels/base_object  (NObj properties via mock)
# ─────────────────────────────────────────────────────────────────────────────

class TestNObjProperties(unittest.TestCase):

    @patch("requests.request")
    def test_object_type(self, mock_req):
        from notion_lib.nModels.base_object import NObjPage
        from notion_lib.client.https import invalidate_cache
        invalidate_cache()
        mock_req.return_value = _fake_response({
            "object": "page",
            "id": "2a7b7a8f729480b3b420f8736c4116d7",
            "parent": {"type": "workspace", "workspace": True},
            "archived": False, "in_trash": False,
            "properties": {"title": {"id": "title", "type": "title", "title": []}},
            "icon": None, "cover": None, "url": "https://notion.so/x",
        })
        obj = NObjPage({}, "2a7b7a8f729480b3b420f8736c4116d7")
        self.assertEqual(obj.object_type, "page")

    @patch("requests.request")
    def test_in_trash(self, mock_req):
        from notion_lib.nModels.base_object import NObjPage
        from notion_lib.client.https import invalidate_cache
        invalidate_cache()
        mock_req.return_value = _fake_response({
            "object": "page",
            "id": "2a7b7a8f729480b3b420f8736c4116d7",
            "parent": {"type": "workspace", "workspace": True},
            "archived": False, "in_trash": True,
            "properties": {"title": {"id": "title", "type": "title", "title": []}},
            "icon": None, "cover": None, "url": "https://notion.so/x",
        })
        obj = NObjPage({}, "2a7b7a8f729480b3b420f8736c4116d7")
        self.assertTrue(obj.in_trash)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)