# 临时工具（非交付物）：把 npmmirror 的 yarn/node 预置进 KGP 缓存目录。
import pathlib
import zipfile

tools = pathlib.Path(__file__).resolve().parent
home = pathlib.Path.home()
gradle = home / ".gradle"

yarn_root = gradle / "yarn"
yarn_root.mkdir(parents=True, exist_ok=True)
with tarfile_open(tools / "cache_yarn.tgz") if False else __import__("tarfile").open(
        tools / "cache_yarn.tgz") as t:
    t.extractall(yarn_root, filter="data")
yarn_dir = yarn_root / "yarn-v1.22.17"
(yarn_dir / ".ok").write_text("ok", encoding="utf-8")
print("yarn ready:", yarn_dir.exists())

node_root = gradle / "nodejs"
node_root.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(tools / "cache_node.zip") as z:
    z.extractall(node_root)
node_dir = node_root / "node-v20.11.1-win-x64"
(node_dir / ".ok").write_text("ok", encoding="utf-8")
print("node ready:", node_dir.exists(), (node_dir / "node.exe").exists())
