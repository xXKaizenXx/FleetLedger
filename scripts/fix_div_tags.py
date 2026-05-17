import pathlib

TAG = "".join(["d", "i", "v"])
root = pathlib.Path(__file__).resolve().parent.parent / "frontend"
for path in root.rglob("*.tsx"):
    text = path.read_text(encoding="utf-8")
    fixed = text.replace("<motion", f"<{TAG}").replace("</motion>", f"</{TAG}>")
    if fixed != text:
        path.write_text(fixed, encoding="utf-8")
        print(path)
