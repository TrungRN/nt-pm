---
name: change-request
description: Lệnh tắt /change-request — phân tích một yêu cầu thay đổi (change request: thêm/bớt/đổi tính năng, đổi deadline, đổi nhân sự) — ảnh hưởng tới effort, timeline, nguồn lực, rủi ro, các phương án và khuyến nghị của PM, xuất file HTML để họp. Dùng khi người dùng gõ /change-request hoặc gọi lệnh này kèm nội dung thay đổi.
---

# /change-request — Phân tích thay đổi yêu cầu

1. Đọc `../nt-pm/SKILL.md` (tính từ thư mục của skill này; cũng là `${CLAUDE_PLUGIN_ROOT}/skills/nt-pm/SKILL.md`) và làm theo **Chế độ C — Thay đổi yêu cầu**, kèm `references/tracking-and-change.md`, `references/html-report.md`, và `references/resource-planning.md` nếu thay đổi chạm tới nhân sự (tất cả trong thư mục `nt-pm`).
2. Nội dung thay đổi: $ARGUMENTS
3. Cần biết tình trạng hiện tại của dự án để tính ảnh hưởng: dùng kế hoạch/báo cáo đã có trong cuộc trò chuyện hoặc tài liệu đính kèm; nếu không có thì hỏi gọn (đang ở sprint nào, deadline, năng lực/velocity hiện tại).
4. Luôn kết thúc bằng khuyến nghị cụ thể của PM và danh sách quyết định cần người có thẩm quyền chốt.
