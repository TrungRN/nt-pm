---
name: report
description: Lệnh tắt /report — lập status report / báo cáo tiến độ dự án (RAG, kế hoạch vs thực tế, velocity, dự báo ngày hoàn thành, rủi ro, quyết định cần lãnh đạo chốt) dạng file HTML. Dùng khi người dùng gõ /report hoặc gọi lệnh này kèm tình hình dự án.
---

# /report — Báo cáo tiến độ

1. Đọc `../nt-pm/SKILL.md` (tính từ thư mục của skill này; cũng là `${CLAUDE_PLUGIN_ROOT}/skills/nt-pm/SKILL.md`) và làm theo **Chế độ B — Theo dõi & báo cáo**, kèm `references/tracking-and-change.md` và `references/html-report.md` trong thư mục `nt-pm`.
2. Thông tin người dùng đưa: $ARGUMENTS
3. Nếu thiếu dữ liệu cốt lõi (kế hoạch gốc, việc đã xong, sprint hiện tại, vấn đề đang gặp), hỏi gọn một lần; nếu có kế hoạch HTML/JSON cũ trong cuộc trò chuyện hoặc link Jira, lấy dữ liệu từ đó trước.
4. Hỏi (hoặc suy ra) báo cáo gửi cho ai — lãnh đạo, PO hay team — để chọn độ dài và mức chi tiết.
