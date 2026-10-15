---
name: meeting
description: Lệnh tắt /meeting — chuẩn bị cuộc họp dự án (kickoff, sprint planning, review/demo, retro, refinement, báo cáo lãnh đạo): agenda, tài liệu cần chuẩn bị, câu hỏi cần chốt; hoặc viết biên bản họp và email/tin nhắn cho stakeholder. Dùng khi người dùng gõ /meeting hoặc gọi lệnh này kèm loại cuộc họp hay ghi chú họp.
---

# /meeting — Họp & giao tiếp stakeholder

1. Đọc `../nt-pm/SKILL.md` (tính từ thư mục của skill này; cũng là `${CLAUDE_PLUGIN_ROOT}/skills/nt-pm/SKILL.md`) và làm theo **Chế độ D — Họp & giao tiếp**, kèm `references/meetings-and-comms.md` trong thư mục `nt-pm`.
2. Yêu cầu của người dùng: $ARGUMENTS
3. Phân biệt hai trường hợp:
   - **Trước họp** → agenda có thời lượng từng mục, mục tiêu cuộc họp (quyết định gì), người cần mời, tài liệu cần chuẩn bị, câu hỏi cần chốt, email/tin nhắn mời họp.
   - **Sau họp** (người dùng dán ghi chú/transcript) → biên bản: quyết định đã thống nhất, hành động (việc – người – hạn), vấn đề còn mở; kèm email gửi biên bản.
4. Viết thẳng trong chat để người dùng copy, trừ khi họ muốn file. Nếu có kế hoạch dự án trong cuộc trò chuyện, dùng số liệu từ đó (milestone, rủi ro, quyết định cần chốt).
