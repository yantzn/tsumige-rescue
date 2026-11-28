# AEP 配置基盤

共通の正本は core、Flutter規約は stacks/flutter、製品規約は project-config に置く。.aep/project.yaml は JSON 互換の YAML とし、platform.lock は基盤版を固定する。

リポジトリルートから `python ai-engineering-platform/scripts/sync.py` で生成し、`python ai-engineering-platform/scripts/sync.py --check` で差分を検出する。生成領域に未管理ファイルがある場合は停止する。必須ゲートを緩和する製品設定は拒否する。

catalog.json の initial は初期の責務移行、planned は後続実装を示す。旧 agents と workflows は移行照合用に保持する。Antigravity実環境で新配置の認識と引き継ぎを確認した後に旧ファイルを撤去する。
