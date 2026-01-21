# PR Gatekeeper Agent (V1)

PR Gatekeeper Agent 是一个本地 CLI 工具，用于在合入前对 PR/分支进行门禁检查与报告生成。V1 版本聚焦在 **LangGraph 工作流 + ruff/pytest + policy gate + artifacts 输出 + SQLite 记录** 的闭环。

## 核心流程（LangGraph 节点）

1. **ingest_pr**：收集 changed files 与 diff 摘要
2. **collect_context**：为变更文件生成上下文摘要，可选 ripgrep TODO/FIXME
3. **run_tools**：识别 Python repo 并运行 ruff + pytest
4. **analyze_findings**：解析工具输出为结构化 findings，评估门禁策略
5. **render_report**：生成 Markdown/JSON 报告内容
6. **publish_results**：写入 artifacts 与 SQLite

## 安装方式

```bash
cd pr-gatekeeper-agent
pip install -e .
```

或使用 uv：

```bash
uv pip install -e .
```

## 运行示例

```bash
python -m src.app.cli --repo . --base main --head HEAD
```

执行后会输出：

- `artifacts/<run_id>/report.md`
- `artifacts/<run_id>/report.json`
- `artifacts/gatekeeper.db`

## 输出示例

Markdown 片段：

```markdown
# PR Gatekeeper Report

## Summary
**Result:** WARN

**Blocked:** False

**Reasons:** Findings present but below threshold
```

JSON 结构说明：

```json
{
  "run_id": "...",
  "inputs": {"repo": ".", "base": "main", "head": "HEAD"},
  "changed_files": ["..."],
  "tool_results": {"ruff": {"returncode": 1, "duration_ms": 1200}},
  "findings": [{"tool": "ruff", "severity": "MEDIUM", "message": "..."}],
  "decision": {"result": "WARN", "blocked": false, "reasons": ["..."]},
  "metrics": {"duration_ms": 5000}
}
```

## 如何扩展

- **新增工具节点**：在 `src/graph/nodes` 添加节点，并在 `build_graph.py` 中接入。
- **新增 policy 规则**：在 `config/policy.yaml` 中增加配置，并在 `policy_engine.py` 内扩展逻辑。
- **GitHub 集成**：V2 可添加 FastAPI webhook，并在 publish 阶段创建 GitHub Check/PR 评论。
