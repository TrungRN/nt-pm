# Lập kế hoạch nguồn lực theo từng người × sprint

Nhân sự trong dự án nội bộ hiếm khi cố định: người vào giữa chừng, người bị điều sang việc khác, tỉ lệ phân bổ đổi theo sprint, nghỉ phép, junior và senior làm nhanh chậm khác nhau. Vì vậy năng lực được tính **theo từng người, từng sprint**, rồi mới cộng lên theo vai trò. Tính bằng `scripts/capacity.py` để số liệu nhất quán và tính lại ngay khi người dùng đổi người. Không cộng nhẩm.

## Khi nào dùng
- Lập kế hoạch (Chế độ A), bước Nguồn lực và Kế hoạch sprint.
- Theo dõi tiến độ hoặc change request (Chế độ B, C) khi có người vào/ra/bị điều đi, cần tính lại năng lực còn lại.
- Người dùng gửi danh sách nhân sự (Excel, bảng dán vào chat, Jira…) thì chuyển nó thành `roster.json`.

## Hỏi gì về nhân sự
Nếu người dùng chưa nói, hỏi gọn (hoặc giả định và ghi rõ):
- Danh sách người (tên hoặc "Dev BE #1"), vai trò, cấp độ (Fresher/Junior/Middle/Senior).
- Ai không làm 100% cho dự án? Tỉ lệ có đổi theo sprint không?
- Ai vào muộn / rời sớm / bị điều đi trong khoảng nào?
- Nghỉ phép đã biết (cưới, phép năm, Tết…).
- Có người nào năng suất khác hẳn mức chung không?

## Định dạng roster.json

```json
{
  "focus_factor": 0.75,
  "focus_by_role": {"BA": 0.8, "TL": 0.5},
  "holidays": ["2027-01-01", {"start": "2027-02-04", "end": "2027-02-12", "name": "Tết Nguyên Đán"}],
  "sprints": {"first_start": "2026-11-02", "length_weeks": 2, "count": 6, "prefix": "Sprint "},
  "people": [
    {"name": "Nguyễn An", "role": "BE", "level": "Senior"},
    {"name": "Trần Bình", "role": "BE", "level": "Junior", "leave_days": {"Sprint 3": 2}},
    {"name": "Lê Cường", "role": "BE", "level": "Middle", "start": "2026-11-30"},
    {"name": "Phạm Dung", "role": "FE", "allocation": 0.5, "allocation_by_sprint": {"Sprint 4": 1.0}},
    {"name": "Hoàng Em", "role": "BA", "end": "2026-12-25"},
    {"name": "SA Hùng", "role": "SA", "allocation": 0.5, "capacity_override": {"Sprint 1": 2}}
  ],
  "demand": {"BE": {"Sprint 1": 10, "Sprint 2": 25}, "FE": {"Sprint 2": 8}}
}
```

| Trường | Ý nghĩa |
|---|---|
| `sprints` | Danh sách `[{"name","start","end"}]` khi sprint có độ dài khác nhau; hoặc bộ sinh tự động như trên (thứ Hai → thứ Sáu cuối sprint). Tên sprint ở các trường khác phải khớp đúng. |
| `holidays` | Ngày lễ/nghỉ chung; trừ khỏi ngày làm việc của mọi người. |
| `focus_factor` / `focus_by_role` / `focus_factor` theo người | Tỉ lệ thời gian thực sự làm việc dự án (họp, hỗ trợ, gián đoạn). TL thường thấp (0.5) vì review, hỗ trợ team. |
| `level` | Hệ số năng suất mặc định: Fresher 0.5, Junior 0.7, Middle 1.0, Senior 1.1 — so với ước lượng chuẩn (thường do một người mức Middle ước lượng). Ghi đè bằng `productivity`. Nói rõ với người dùng đây là hệ số tham khảo, cần chỉnh theo team thật. |
| `allocation` | % mặc định cho dự án (1.0 = toàn thời gian). |
| `allocation_from` | % thay đổi **từ một ngày** (kể cả giữa sprint): `{"2027-01-04": 0.6}` → sprint chứa ngày đó được tính theo tỉ lệ ngày. Ưu tiên dùng khi người dùng nói "từ ngày X bị điều Y%". |
| `allocation_by_sprint` | % cố định cho một sprint cụ thể (ghi đè `allocation` và `allocation_from`), ví dụ `{"Sprint 4": 1.0}`. Dùng `"*"` cho mặc định. |
| `start` / `end` | Ngày vào / rời dự án; sprint bị cắt theo ngày làm việc thực tế. |
| `ramp_up` | Người vào sau ngày bắt đầu dự án tự nhận hệ số làm quen 0.5 ở sprint đầu tiên. `false` để tắt (người đã quen hệ thống), hoặc số khác (0.7). |
| `leave_days` | Số ngày nghỉ phép theo sprint. |
| `capacity_override` | Nhập thẳng MD cho sprint đó khi người dùng đã biết con số. |
| `work` | (Nên dùng) danh sách hạng mục WBS: `{"id","name","role","md","sprint","priority"}`, hoặc `md_by_role: {"BE": 10, "FE": 6}` thay cho `role`+`md` khi một hạng mục cần nhiều vai trò. Script tự cộng thành tải theo vai trò × sprint, sinh bảng WBS (có tổng), bảng kế hoạch sprint (effort vs năng lực) và cảnh báo hạng mục chưa xếp sprint — nhờ vậy WBS, kế hoạch sprint và năng lực luôn khớp nhau, không cần tự viết code cộng. |
| `demand` | (Tùy chọn) effort theo vai trò × sprint (MD) cho phần không nằm trong `work` (ví dụ overhead, buffer); cộng thêm vào tải. |

Giai đoạn không phải sprint (ổn định, UAT, hypercare) đưa vào danh sách `sprints` như một mục riêng với tên rõ ràng (ví dụ "Ổn định & UAT"), để năng lực của giai đoạn đó cũng được tính.

## Chạy và đưa vào tài liệu

```bash
python3 <skill>/scripts/capacity.py roster.json --blocks capacity_blocks.json --json capacity_result.json
```

- Màn hình in bảng năng lực theo vai trò và các dòng QUÁ TẢI; CẢNH BÁO nếu tên sprint gõ sai.
- `capacity_blocks.json` chứa sẵn các khối cho `render_report.py`: lịch sprint, năng lực vai trò × sprint (có dòng tổng), chi tiết từng người, tải/năng lực (nếu có `work`/`demand`), callout vai trò quá tải, bảng WBS và kế hoạch sprint (nếu có `work`), bảng thay đổi nhân sự theo sprint. Bảng WBS/kế hoạch sprint có thể đặt sang mục "Ước lượng effort" / "Kế hoạch sprint" của tài liệu. Chèn các khối này vào mục "Nguồn lực" của JSON tài liệu (đọc file rồi nối vào `blocks`).
- `capacity_result.json` dùng khi cần tính tiếp (dự báo ngày hoàn thành, so sánh phương án).

## Team dùng story point
capacity.py vẫn tính năng lực theo MD để thấy *tỉ lệ* năng lực từng sprint so với sprint bình thường (người nghỉ, người vào/ra). Năng lực theo point của sprint = velocity trung bình 3 sprint gần nhất × (năng lực MD sprint đó / năng lực MD của một sprint đủ người). Nếu team chưa có velocity, ước lượng sprint đầu theo MD rồi hiệu chỉnh sau 2–3 sprint.

## Diễn giải cho người dùng
- Chỉ ra **vai trò nút cổ chai** và sprint quá tải, đề xuất cách xử lý: dời việc sang sprint sau, chuyển người hỗ trợ chéo (mobile hỗ trợ FE…), xin thêm người, hoặc cắt scope.
- Người mới vào: nhắc chi phí làm quen và thời gian người cũ kèm (Luật Brooks); người sắp rời: lên kế hoạch bàn giao kiến thức trước ít nhất 1 sprint.
- Một người làm nhiều vai trò (TL kiêm dev): tách thành 2 dòng với `allocation` tương ứng.
- Khi người dùng đổi nhân sự: sửa roster.json, chạy lại, và nói rõ chênh lệch năng lực (trước → sau, MD) và ảnh hưởng tới timeline.
