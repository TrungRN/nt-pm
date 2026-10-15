# nt-pm — Trợ lý Project Manager cho Claude

Plugin giúp PM dự án phần mềm lập kế hoạch và điều hành dự án cùng Claude, trả lời bằng tiếng Việt.

- **Lập kế hoạch** từ yêu cầu hoặc tài liệu (BRD, Excel nhân sự, Jira…): phân tích yêu cầu, ước lượng man-day, nguồn lực theo từng người × sprint (người vào/ra, đổi % phân bổ, nghỉ phép), timeline Hybrid, sprint, rủi ro, RACI.
- **Báo cáo tiến độ**, **phân tích thay đổi yêu cầu**, **chuẩn bị họp** và viết biên bản, email cho stakeholder.
- Xuất ra **file HTML** có Gantt, bảng nguồn lực, ma trận rủi ro, in PDF được và **sửa trực tiếp trên trình duyệt**.

## Cài đặt nhanh

**Claude Code** (trong phiên làm việc):
```
/plugin marketplace add TrungRN/nt-pm
/plugin install nt-pm@trungrn-plugins
```
hoặc từ terminal:
```bash
claude plugin marketplace add TrungRN/nt-pm
claude plugin install nt-pm@trungrn-plugins
```

**Claude (web/desktop):** **Customize** → **Plugins** → **Add** → **Add marketplace** → **Add from a repository** → nhập `TrungRN/nt-pm` → bấm **Add** ở plugin **nt-pm**.

Yêu cầu: gói Claude trả phí; bật tạo file và chạy code (plugin dùng script Python).

## Sử dụng

| Lệnh | Việc |
|---|---|
| `/nt-pm:plan` | Lập kế hoạch dự án |
| `/nt-pm:report` | Báo cáo tiến độ |
| `/nt-pm:change-request` | Phân tích change request |
| `/nt-pm:meeting` | Chuẩn bị họp, biên bản, email |

Hoặc nói tự nhiên: *"Sếp vừa giao dự án X, lên kế hoạch giúp tôi"* — Claude tự dùng plugin.

Hướng dẫn đầy đủ: [plugins/nt-pm/README.md](plugins/nt-pm/README.md)

## Cập nhật
```bash
claude plugin marketplace update trungrn-plugins
```

## Giấy phép
MIT
