# Xuất HTML bằng render_report.py

Script: `scripts/render_report.py input.json output.html` — chỉ dùng thư viện chuẩn Python. Tạo một file HTML tự chứa: mục lục bên trái, các mục đánh số, hỗ trợ dark mode, in ra PDF đẹp (Ctrl+P). Script in CẢNH BÁO ra stderr nếu ngày sai, bảng lệch số cột… — đọc và sửa JSON rồi chạy lại nếu có cảnh báo.

## Cấu trúc JSON

```json
{
  "doc_type": "Kế hoạch dự án",
  "title": "Hệ thống đặt phòng họp nội bộ",
  "subtitle": "Kế hoạch triển khai giai đoạn 1 (MVP)",
  "meta": {"PM": "Nguyễn Văn A", "Ngày lập": "15/10/2026", "Phiên bản": "v1.0", "Trạng thái": "Bản nháp chờ duyệt"},
  "summary": "Đoạn tóm tắt điều hành 3–5 dòng. Hỗ trợ **đậm**, *nghiêng*, `code`, gạch đầu dòng '- '.",
  "sections": [
    {"title": "Tổng quan", "blocks": [ {"type": "kpis", "items": [...]}, {"type": "text", "content": "..."} ]}
  ]
}
```

Mọi trường văn bản hỗ trợ markdown tối giản: `**đậm**`, `*nghiêng*`, `` `code` ``. Trường `content` còn hỗ trợ đoạn văn (cách dòng trống), danh sách `- ` / `1. `, tiêu đề nhỏ `### `. Mỗi khối có thể có `"title"` riêng.

## Các loại khối

| type | Trường | Dùng cho |
|---|---|---|
| `text` | `content` | Đoạn văn, danh sách |
| `list` | `items` (mảng chuỗi), `ordered` | Danh sách ngắn |
| `checklist` | `items`: chuỗi hoặc `{"text","done"}` | Việc cần làm, checklist chốt |
| `callout` | `tone`: info/tip/warn/danger/success, `title`, `content` | Lưu ý, "💡 Góc PM" (tone `tip`), cảnh báo, quyết định cần chốt |
| `kpis` | `items`: `{"label","value","note","tone"}` (tone: ok/warn/danger/accent) | Thẻ chỉ số: tổng MD, số sprint, ngày go-live… |
| `table` | `columns`, `rows` (mảng mảng), `caption`, `note`, `total_row` (dòng cuối in đậm) | Mọi bảng. Cột toàn số tự căn phải |
| `bars` | `items`: `{"label","value","max","note"}`, `unit` | Effort theo vai trò; effort vs năng lực (vượt `max` sẽ tô đỏ) |
| `cards` | `items`: `{"title","content","tag","tone"}` | So sánh phương án, mô tả sprint, stakeholder |
| `rag` | `items`: `{"area","status","note"}` (status: Xanh/Vàng/Đỏ hoặc green/amber/red) | Trạng thái RAG trong status report |
| `risk_matrix` | `risks`: `{"id","probability","impact"}` (Cao/Trung bình/Thấp) | Ma trận rủi ro 3×3 |
| `gantt` | `items`, `today` | Timeline (xem dưới) |

**Badge tự động:** ô bảng có giá trị đúng bằng một trong các từ sau sẽ thành nhãn màu — Cao / Trung bình / Thấp, Xanh / Vàng / Đỏ, Must / Should / Could / Won't, Xong / Đang làm / Chưa bắt đầu / Trễ / Bị chặn, Đã duyệt / Chờ duyệt / Đề xuất, Done / In progress / To do / High / Medium / Low. Viết đúng nguyên từ trong ô (không thêm chữ khác) để badge hiện.

**Gantt:** mỗi item `{"name","start","end","kind","group","tone","note","baseline_start","baseline_end"}`
- Ngày dạng `YYYY-MM-DD`. `kind`: `phase` (giai đoạn, xanh đậm), `sprint` (xanh nhạt), `task` (xám), `milestone` (hình thoi, chỉ cần `start` hoặc `date`).
- `group`: các item liên tiếp cùng group được gom dưới một dòng tiêu đề nhóm — sắp xếp item theo nhóm.
- `tone`: ok/warn/danger để tô màu đặc biệt (ví dụ sprint đang trễ = danger).
- `baseline_start`/`baseline_end`: vẽ khung nét đứt kế hoạch gốc — dùng trong status report và change request để thấy độ lệch.
- `today`: vẽ vạch đỏ "hôm nay".

## Chèn bảng năng lực từ capacity.py
`scripts/capacity.py roster.json --blocks capacity_blocks.json` sinh sẵn các khối bảng năng lực, tải/năng lực và thay đổi nhân sự. Đọc file đó và nối các khối vào `blocks` của mục Nguồn lực — không gõ lại số bằng tay.

## Chỉnh sửa trên trình duyệt
Mọi file render ra đều có thanh nút góc dưới phải (Chỉnh sửa / Lưu bản sửa / In-PDF) và nhúng JSON nguồn trong `<script id="nt-pm-source">`. Không cần làm gì thêm; cách xử lý file người dùng sửa và gửi lại nằm trong SKILL.md.

## Bộ mục khuyến nghị

### Kế hoạch dự án (Chế độ A)
1. **Tổng quan** — `kpis` (tổng effort MD/MM, số người, số sprint, ngày go-live, mức rủi ro), `text` mục tiêu nghiệp vụ & tiêu chí thành công. Có tài liệu đầu vào thì thêm bảng Tài liệu đầu vào (Tài liệu | Phiên bản/ngày | Dùng cho) và `callout warn` các mâu thuẫn/chỗ thiếu đã phát hiện.
2. **Phạm vi & yêu cầu** — bảng Scope In/Out; bảng epic/tính năng (ID | Tính năng | Mô tả | MoSCoW | MD); NFR; `callout` giả định & ràng buộc.
3. **Stakeholder** — bảng hoặc `cards`.
4. **Ước lượng effort** — bảng WBS theo giai đoạn (có `total_row`); `bars` effort theo vai trò.
5. **Nguồn lực** — các khối từ `capacity.py` (năng lực vai trò × sprint, chi tiết từng người, tải/năng lực, thay đổi nhân sự); `bars` effort vs năng lực của vai trò nút cổ chai; `callout tip` giải thích focus factor và hệ số năng suất.
6. **Timeline & milestone** — `gantt` (giai đoạn, sprint, milestone, nhóm theo giai đoạn); bảng milestone (Milestone | Ngày | Tiêu chí hoàn thành). Ghi lý do chọn độ dài sprint.
7. **Kế hoạch sprint** — bảng (Sprint | Ngày | Mục tiêu | Hạng mục chính | Năng lực MD | Kế hoạch MD).
8. **Rủi ro** — `risk_matrix` + bảng risk register.
9. **Vận hành dự án** — RACI, lịch ceremonies, kế hoạch truyền thông, DoR/DoD.
10. **Quyết định cần chốt & bước tiếp theo** — `callout warn` các quyết định (ai, trước ngày nào); `checklist` việc PM 2 tuần tới; câu hỏi còn mở.

Dự án nhỏ có thể gộp/bỏ mục; đừng tạo mục rỗng.

### Status report (Chế độ B)
Tóm tắt điều hành → `kpis` → `rag` → Đã làm / Kế hoạch kỳ tới → `gantt` có baseline + `today` → bảng rủi ro & issue → `callout warn` quyết định cần đưa ra.

### Phân tích change request (Chế độ C)
Thông tin CR (bảng 2 cột) → mô tả & lý do → bảng ảnh hưởng (Hạng mục | Trước | Sau | Chênh lệch) → `gantt` có baseline → `cards` các phương án → `callout success` khuyến nghị PM → bảng quyết định (để trống ô người duyệt/ngày).

## Kiểm tra trước khi gửi
- Không có CẢNH BÁO từ script.
- Tổng cột MD trong bảng khớp với `kpis` và `bars`; ngày trong `gantt` khớp bảng sprint/milestone.
- Tên file không dấu, có nghĩa.
