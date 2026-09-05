# Markdown 辅助检查

在技能目录中运行，路径均为使用者提供的实际文件：

```bash
python scripts/revision_lint.py draft.md --scope excerpt
python scripts/revision_lint.py revised.md --baseline draft.md --scope full
python scripts/revision_lint.py draft.md --scope full --numbering sequential
```

默认 `excerpt` 支持局部摘段，不要求编号从 1 开始。`full` 才检查文末参考文献和图表标题对应。`--numbering sequential` 只在目标编号规则确实要求首次出现为 1..N 时使用。`--baseline` 比较数字引文出现次数和首次出现顺序，提示可能误改，不自动重排。

支持 Markdown 方括号数字引用，包括范围和逗号列表；参考文献标题为 Markdown 的“参考文献”或“References”。作者年份制、上标 HTML、自定义编号和复杂 LaTeX 排版需要人工核对。代码块、行内代码和 HTML 注释排除。简单 Markdown 图像的本地路径会检查，远程图像不联网验证；复杂路径或标题语法仍需复核。

术语配置 `--terms terms.json` 格式为 `{"组名": ["术语全称", "简称"]}`；同一位置优先匹配较长词，减少包含关系误报。`--hints hints.json` 为可调整表达列表，所有命中仅作提示。JSON 配置不应包含私人信息。

脚本只读输入，输出 JSON。退出码 0 表示运行完成，存在检查提示时仍为 0；输入或用法错误为 2。句长是粗略描述统计，不设门槛。脚本不能核实文献真实、引文语义、概念是否同义、研究结论、图的实际可读性或 AI 生成概率。检查无提示不等于论文质量通过。
