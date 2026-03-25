# HEARTBEAT.md

## 镖人2主动检查

- 检查 output/ 最新生成结果，记录到 semantics_index.json
- 检查 git 状态，未 push 的 commit 超过3个则自动合并

## 系统健康

- 检查磁盘空间，低于 20% 告警
- 检查 GitHub backup 有无失败记录
