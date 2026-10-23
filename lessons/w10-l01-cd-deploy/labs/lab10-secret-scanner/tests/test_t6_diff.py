from fakes import GH, TG
from scanner import mask, scan_diff

DIFF = f"""diff --git a/bot/main.py b/bot/main.py
index 1111111..2222222 100644
--- a/bot/main.py
+++ b/bot/main.py
@@ -1,4 +1,5 @@
 import os
-TOKEN = os.getenv("BOT_TOKEN")
+TOKEN = "{TG}"
+DEBUG = True
 
 def main():
@@ -20,3 +21,3 @@ def main():
     run()
-    # old = "{GH}"
+    print("ok")
     stop()
diff --git a/.env b/.env
new file mode 100644
--- /dev/null
+++ b/.env
@@ -0,0 +1,2 @@
+DEBUG=1
+GH_TOKEN={GH}
diff --git a/old.py b/old.py
deleted file mode 100644
--- a/old.py
+++ /dev/null
@@ -1 +0,0 @@
-KEY = "{GH}"
"""


def test_only_added_lines_with_new_numbers():
    assert [(f.path, f.line, f.rule) for f in scan_diff(DIFF)] == [
        ("bot/main.py", 2, "telegram_bot_token"),
        (".env", 2, "github_token"),
    ]


def test_masked():
    assert scan_diff(DIFF)[0].preview == mask(TG)


def test_removed_secret_is_not_reported():
    assert all(f.path != "old.py" for f in scan_diff(DIFF))


def test_line_numbers_after_second_hunk():
    diff = f"--- a/x.py\n+++ b/x.py\n@@ -10,2 +10,3 @@\n a\n b\n+K = '{GH}'\n"
    assert [(f.path, f.line) for f in scan_diff(diff)] == [("x.py", 12)]
