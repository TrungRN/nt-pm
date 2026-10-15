# Theo dõi tiến độ, báo cáo & thay đổi yêu cầu (Chế độ B, C)

## Phần B — Theo dõi tiến độ & báo cáo

### Thu thập dữ liệu
Hỏi người dùng (hoặc lấy từ Jira/công cụ nếu có kết nối) những gì cần: kế hoạch gốc (baseline), việc đã xong/đang làm/chưa làm, effort đã tiêu, sprint hiện tại, vấn đề đang gặp. Nếu người dùng chỉ kể bằng lời ("team trễ khoảng 1 tuần do API bên kia chưa xong"), dựng báo cáo từ đó và ghi rõ chỗ nào là ước tính.

### Chỉ số nên dùng (đơn giản, dễ giải thích với lãnh đạo)
- **% hoàn thành theo kế hoạch vs thực tế** (theo số hạng mục hoặc man-day).
- **Độ lệch lịch:** milestone dự kiến vs dự báo mới (ngày).
- **Velocity/khối lượng hoàn thành mỗi sprint** và xu hướng 3 sprint gần nhất.
- **Effort đã tiêu vs kế hoạch** (MD) — phát hiện vượt effort sớm.
- **Số lỗi mở/đóng**, lỗi nghiêm trọng.
- **Dự báo ngày hoàn thành** = khối lượng còn lại / velocity trung bình. Nêu khoảng (sớm nhất–muộn nhất) thay vì một ngày duy nhất.

### Trạng thái RAG
- 🟢 **Xanh:** đúng kế hoạch hoặc lệch nhỏ tự xử lý được.
- 🟡 **Vàng:** có nguy cơ trễ/vượt, đã có phương án, cần theo dõi hoặc cần hỗ trợ nhẹ.
- 🔴 **Đỏ:** sẽ trễ milestone/vượt nguồn lực nếu không có quyết định từ cấp trên.

Đánh giá RAG riêng cho: Tiến độ, Phạm vi, Nguồn lực, Chất lượng, và Tổng thể. Trung thực — báo Vàng sớm tốt hơn báo Đỏ đột ngột.

💡 Góc PM: Lãnh đạo không sợ tin xấu bằng sợ tin xấu đến muộn. Status report tốt luôn có "cần anh/chị quyết định gì".

### Cấu trúc status report (xuất HTML)
1. Tóm tắt điều hành (3 dòng): trạng thái tổng, điểm chính, cần quyết định gì.
2. Thẻ chỉ số: % hoàn thành, sprint hiện tại, ngày go-live dự báo, effort đã tiêu.
3. RAG theo hạng mục (bảng).
4. Đã làm được kỳ này / Kế hoạch kỳ tới.
5. Timeline: kế hoạch gốc vs dự báo (Gantt).
6. Rủi ro & vấn đề (issue) đang mở — kèm hành động và người phụ trách.
7. Quyết định cần lãnh đạo/PO đưa ra, có hạn chót.

Ngắn gọn: lãnh đạo đọc trong 2 phút. Chi tiết để ở phần sau.

### Khi dự án trễ — các đòn bẩy (trình bày cho người dùng chọn, kèm khuyến nghị)
1. Cắt/giảm scope (chuyển Could/Should sang phase sau) — thường là cách hiệu quả nhất.
2. Dời deadline — cần lãnh đạo đồng ý, kèm lý do minh bạch.
3. Thêm người — chỉ hiệu quả nếu còn >6–8 tuần và việc chia được độc lập (Luật Brooks).
4. Tăng hiệu suất: gỡ blocker, giảm họp, giảm làm song song nhiều việc, giảm phân bổ sang dự án khác.
5. Làm thêm giờ — chỉ ngắn hạn, có rủi ro chất lượng và kiệt sức; không phải giải pháp kế hoạch.

Luôn tìm nguyên nhân gốc (ước lượng sai? scope tăng? người bị điều đi? blocker bên ngoài?) — vì cách sửa khác nhau.

## Phần C — Thay đổi yêu cầu (Change Request)

Trong dự án nội bộ, thay đổi thường đến từ lãnh đạo/PO qua lời nói, không qua quy trình chính thức. Nhiệm vụ của PM không phải là từ chối, mà là **làm rõ cái giá** để người có quyền quyết định đưa ra lựa chọn sáng suốt.

### Quy trình
1. **Ghi nhận:** thay đổi gì, ai yêu cầu, vì sao (giá trị nghiệp vụ), có gấp không.
2. **Phân tích ảnh hưởng** (nhờ TL/SA/BA ước lượng):
   - Phạm vi: thêm/sửa/bỏ gì; có ảnh hưởng tính năng đã làm không (làm lại).
   - Effort: +/- bao nhiêu MD theo vai trò.
   - Thời gian: ảnh hưởng milestone nào, bao nhiêu ngày (tính theo năng lực nút cổ chai).
   - Nguồn lực: cần thêm người/kỹ năng?
   - Chất lượng & rủi ro: rủi ro mới, áp lực lên kiểm thử.
3. **Đưa phương án** (thường 3):
   - A. Làm thêm, dời deadline X ngày.
   - B. Làm thêm, giữ deadline, đổi lấy việc bỏ/hoãn hạng mục Y có effort tương đương.
   - C. Đưa vào phase/release sau.
   - (D. Thêm nguồn lực — nếu khả thi.)
4. **Khuyến nghị của PM** kèm lý do.
5. **Chốt bằng văn bản:** ai quyết định, chọn phương án nào, ngày nào. Cập nhật baseline kế hoạch, backlog, risk register.

### Cấu trúc tài liệu phân tích CR (xuất HTML)
Thông tin CR (mã, người yêu cầu, ngày, mức ưu tiên) → Mô tả thay đổi & lý do → Bảng ảnh hưởng (Hạng mục | Trước | Sau | Chênh lệch) → Timeline trước/sau (Gantt) → Phương án so sánh (bảng) → Khuyến nghị → Quyết định (để trống cho người duyệt).

Luôn nhắc người dùng: tích lũy nhiều thay đổi "nhỏ" không ghi nhận là nguyên nhân phổ biến nhất khiến dự án trễ mà không ai giải thích được. Đề xuất giữ một **Change Log** đơn giản.
