# Academic Writing Skills

三个来自个人长期学术写作实践的技能，仍在改进。它们分别处理论证诊断、可调整的修改偏好和科学绘图，可按任务单独使用。

| 技能 | 解决的问题 | 入口 |
|---|---|---|
| ADO | 段落任务不清、推理跳步、文献堆叠、概念关系含混，以及结构调整中的最小必要修改 | [ado-skill](skills/ado-skill/SKILL.md) |
| 论文修改偏好 | 原有表达被反复改掉、协作方式不一致、局部偏好被误作普遍规则 | [paper-revision-prefs](skills/paper-revision-prefs/SKILL.md) |
| 科学绘图 | 图的结构、文字、数值与证据对不齐，以及 SVG 模式图和模型模拟的可复现表达 | [scientific-diagram](skills/scientific-diagram/SKILL.md) |

三个目录各有自己的入口和必要参考文件，互不要求安装，也不依赖外部私人材料。按维护者说明，原修改偏好技能主要由 Claude 在逐段协作中维护，原 ADO 由 GPT 5.6 根据既往讨论总结。本项目不据此推断作者身份或模型效果。

## 使用

直接让有文件访问能力的 AI 读取所选 `SKILL.md`，并按其中的条件打开 references 或 styles。用 GitHub 连接时指定本仓库、实际分支和路径；从 PR 试用时显式指定 PR 分支。只有读到文件才报告已遵循。

本地 Codex 可将所需技能的完整目录复制到用户目录的 `.agents/skills/`，或项目的 `.agents/skills/`，再用 `$ado-skill`、`$paper-revision-prefs` 或 `$scientific-diagram` 调用。目标存在时先比较，避免覆盖已有技能；有同名旧技能时优先直接读取本仓库路径并说明版本。Python 脚本使用 Python 3，基本文件读取不要求 Python。[Codex 官方技能说明](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)列出了真实加载位置。

仓库包含 `.codex-plugin/plugin.json` 和 `skills/`，结构依据[官方插件规范](https://developers.openai.com/plugins/build/plugins#plugin-structure)。文件打包不代表插件已安装或已发布到插件目录。本项目当前提供文件读取和本地技能目录使用方法，没有执行插件安装。

## 合成使用示例

以下原文与编号均为**合成示例**，不是研究证据：

> 使用 ADO 直接修改并保留引文编号：“入口设计帮助用户找到功能[7]。信息提示帮助用户理解步骤[8]。因此，界面已经解决所有使用障碍。”

可得到：“入口设计帮助用户找到功能[7]，信息提示帮助用户理解操作步骤[8]，两类设计分别回应了功能发现与操作理解的问题。”修改去掉了材料无法支持的“所有使用障碍”，保持原编号。

## 偏好与责任

句长、否定句、人名在正文中的出现、段落节奏和结语形式属于可调整的作者偏好，按文体、期刊与本次任务设置。事实准确、引文来源与主张对应、数据可追溯、区分相关和因果则属于证据要求，不能为了文风取消。

AI 修改不能替代作者对论点、资料和学术规范的责任。本项目不承诺降低 AI 检测率、提高录用率或保证论文质量。脚本只提供机械复核线索，不给论文打质量分。

## 反馈与许可

通过本仓库的 [Issues](https://github.com/youngiry/academic-writing-skills/issues) 提交问题或建议，使用[反馈模板](.github/ISSUE_TEMPLATE/skill-feedback.yml)说明技能版本、场景、预期、实际结果、合成或脱敏的最小示例及必要环境。不要上传私人稿件、个人信息、凭据或受限材料；无需提供完整对话或全文。

详见 [CONTRIBUTING.md](CONTRIBUTING.md)、[脱敏与来源说明](PROVENANCE.md)和[验证记录](VALIDATION.md)。有权许可的原创文本、重新编写的合成示例和脚本采用 [MIT License](LICENSE)。第三方全文、字体、图片与许可不明的模板未随仓库分发。账号所有者仍会自然显示在 GitHub，本仓库不提供账号匿名。
