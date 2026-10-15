# nt-pm — Trợ lý Project Manager

Plugin giúp PM dự án phần mềm lập kế hoạch và điều hành dự án cùng Claude, trả lời bằng tiếng Việt.

## Plugin làm được gì

| Việc | Cách gọi |
|---|---|
| Lập kế hoạch từ một yêu cầu hoặc tài liệu (BRD, Excel nhân sự, Jira…): phân tích yêu cầu, ước lượng man-day, nguồn lực theo từng người × sprint, timeline, sprint, rủi ro, RACI | `/plan` hoặc nói tự nhiên: "lên kế hoạch giúp tôi…" |
| Báo cáo tiến độ (status report): RAG, kế hoạch vs thực tế, dự báo ngày xong, quyết định cần chốt | `/report` |
| Phân tích thay đổi yêu cầu (change request): ảnh hưởng, phương án, khuyến nghị | `/change-request` |
| Chuẩn bị họp (kickoff, sprint planning, retro…), viết biên bản, email cho stakeholder | `/meeting` |
| Hỏi kiến thức PM | Hỏi trực tiếp |

Kế hoạch, báo cáo và phân tích được xuất ra **file HTML**: có mục lục, timeline Gantt, bảng nguồn lực, ma trận rủi ro, in ra PDF được, và có nút **✏️ Chỉnh sửa / 💾 Lưu bản sửa** để sửa trực tiếp trên trình duyệt. Gửi lại file đã sửa cho Claude để cập nhật và tính lại số liệu.

Mặc định: mô hình Hybrid (giai đoạn + sprint), ước lượng man-day, sprint 2–4 tuần. Nếu team bạn làm khác (Scrum thuần, story point, có QA, dự án outsource…), cứ nói với Claude ở đầu cuộc trò chuyện. Mẹo: ghi thông tin team vào phần hướng dẫn của một Project để lần nào cũng dùng đúng.

## Yêu cầu

- Gói Claude trả phí (Pro, Max, Team hoặc Enterprise).
- Bật **tạo file và chạy code** (Code execution and file creation) trong cài đặt, vì plugin dùng script Python để tính năng lực và dựng file HTML.
- Tùy chọn: kết nối **Atlassian (Jira/Confluence)** để Claude đọc backlog, sprint, trang yêu cầu.

## Cài đặt

### Cách 1 — Cài bằng lệnh (Claude Code)
Trong một phiên Claude Code:
```
/plugin marketplace add TrungRN/nt-pm
/plugin install nt-pm@trungrn-plugins
```
Hoặc từ terminal:
```bash
claude plugin marketplace add TrungRN/nt-pm
claude plugin install nt-pm@trungrn-plugins
```
Gọi lệnh bằng `/nt-pm:plan`, `/nt-pm:report`, `/nt-pm:change-request`, `/nt-pm:meeting` — trong Claude Code luôn gõ kèm tiền tố `nt-pm:` để không trùng với lệnh có sẵn (ví dụ `/plan`). Cập nhật bản mới: `claude plugin marketplace update trungrn-plugins`.

### Cách 2 — Cài trên Claude (web/desktop)
1. Thanh bên trái → **Customize** → tab **Plugins** → **Add** → **Add marketplace** → **Add from a repository**, nhập `TrungRN/nt-pm`.
2. Tìm plugin **nt-pm** và bấm **Add**.
3. Kiểm tra: gõ `/` trong ô chat, thấy các lệnh `plan`, `report`, `change-request`, `meeting` là được.

Plugin cài trên web/desktop được lưu vào tài khoản và dùng được cả trong Claude Code khi đăng nhập cùng tài khoản.

### Cách 3 — Chia sẻ cho các PM trong công ty (gói Team/Enterprise, cần quyền Owner)
1. **Organization settings** → **Plugins & skills** → **Add** → **Upload a plugin**.
2. Lần đầu nhập tên marketplace (ví dụ "PMO"), kéo thả file zip của thư mục `plugins/nt-pm` (tải từ GitHub: **Code → Download ZIP**, rồi nén riêng thư mục `plugins/nt-pm`), bấm **Upload**.
3. Tab **Inventory** → menu cuối dòng `nt-pm` → **Default access**, chọn:
   - **Available to install**: PM tự vào **Customize → Plugins → Discover** để thêm, hoặc
   - **Installed by default**: tự có sẵn cho mọi người (vẫn tắt được).
4. Các PM nhận plugin ở phiên làm việc tiếp theo.

Nếu công ty quản lý plugin bằng GitHub: đưa thư mục plugin vào một repo private, rồi **Organization settings → Plugins & skills → Marketplaces → Add plugins → Sync from GitHub**.

### Sau khi cài
- Nếu trước đó đã lưu skill lẻ **nt-pm** hoặc **mypm**, hãy xóa chúng trong **Customize → Skills** để Claude không bị trùng lặp.

## Cập nhật phiên bản (dành cho người bảo trì)
Sửa plugin, tăng `version` trong `plugins/nt-pm/.claude-plugin/plugin.json`, commit và push lên GitHub. Người dùng nhận bản mới khi cập nhật marketplace. Với bản tải lên trong Organization settings: tải lại với cùng tên `nt-pm` để ghi đè.

## Giấy phép
MIT — xem file `LICENSE`.

## Cấu trúc
```
nt-pm/
├── .claude-plugin/plugin.json
├── skills/
│   ├── nt-pm/            # skill chính: quy trình PM, tài liệu tham khảo, script
│   │   ├── SKILL.md
│   │   ├── references/   # playbook lập kế hoạch, nguồn lực, tiến độ & CR, họp, định dạng HTML
│   │   └── scripts/      # render_report.py, capacity.py, preview.py
│   ├── plan/             # /plan
│   ├── report/           # /report
│   ├── change-request/   # /change-request
│   └── meeting/          # /meeting
└── README.md
```
