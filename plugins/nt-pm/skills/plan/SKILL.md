---
name: plan
description: Lệnh tắt /plan — bắt đầu lập kế hoạch cho một dự án, yêu cầu hoặc tính năng mới (phân tích yêu cầu, ước lượng, nguồn lực, timeline, sprint, rủi ro, xuất file HTML). Dùng khi người dùng gõ /plan hoặc gọi lệnh này kèm mô tả yêu cầu và/hoặc tài liệu đính kèm.
---

# /plan — Lập kế hoạch dự án

1. Đọc `../nt-pm/SKILL.md` (tính từ thư mục của skill này; cũng là `${CLAUDE_PLUGIN_ROOT}/skills/nt-pm/SKILL.md`) và làm theo **Chế độ A — Lập kế hoạch**, kèm các file tham khảo nó chỉ định. Các đường dẫn `references/` và `scripts/` trong đó tính từ thư mục `nt-pm`.
2. Yêu cầu của người dùng: $ARGUMENTS
3. Nếu người dùng gửi kèm tài liệu, đi theo phần **Tài liệu đầu vào** trước.
4. Nếu lệnh được gọi mà không kèm nội dung và cũng không có tài liệu, hỏi ngắn: dự án/yêu cầu là gì, có tài liệu nào (BRD, Excel nhân sự, link Jira…) để gửi kèm không.
