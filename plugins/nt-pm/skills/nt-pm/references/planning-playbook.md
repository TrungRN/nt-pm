# Playbook lập kế hoạch dự án (Chế độ A)

Mục lục:
1. Bộ câu hỏi làm rõ yêu cầu
2. Phân tích yêu cầu
3. WBS & ước lượng man-day
4. Nguồn lực & năng lực thực tế
5. Timeline Hybrid & đề xuất độ dài sprint
6. Kế hoạch sprint
7. Quản lý rủi ro
8. Vận hành dự án (RACI, ceremonies, truyền thông, DoR/DoD)
9. Checklist trước khi chốt

---

## 1. Bộ câu hỏi làm rõ yêu cầu

Không hỏi hết — chọn ~7 câu có tác động lớn nhất đến effort/timeline với dự án cụ thể. Kèm giả định mặc định cho mỗi câu.

**Mục tiêu & bối cảnh**
- Vấn đề nghiệp vụ nào cần giải quyết? Đo thành công bằng gì (KPI)?
- Ai là người ra quyết định cuối (sponsor/PO)? Ai là người dùng chính, bao nhiêu người?
- Có hệ thống cũ đang làm việc này không (thay thế, mở rộng, hay mới hoàn toàn)?

**Phạm vi**
- Danh sách tính năng chính? Cái nào bắt buộc cho lần ra mắt đầu tiên?
- Nền tảng: web, mobile (iOS/Android), nội bộ hay internet?
- Tích hợp với hệ thống nào (SSO/AD, ERP, HRM, email, thanh toán…)? Hệ thống đó có API chưa, ai quản lý?
- Dữ liệu: có cần migrate dữ liệu cũ không?

**Thời gian & nguồn lực**
- Có deadline không? Ai đặt, vì sao (sự kiện, quy định, kế hoạch năm)? Cứng hay mềm?
- Ai trong team có thể tham gia, mỗi người bao nhiêu %? Có đang chạy dự án khác không?
- **Ai kiểm thử?** (nhiều team không có QA chuyên trách)
- (Nếu chưa biết) team làm Scrum/Waterfall/Hybrid, ước lượng man-day hay story point, sprint dài bao lâu?
- Có ngân sách cho hạ tầng/license/thuê ngoài không?

**Phi chức năng**
- Bao nhiêu người dùng đồng thời? Yêu cầu bảo mật/phân quyền, audit log? Uptime?
- Tiêu chuẩn công ty bắt buộc (tech stack, quy trình duyệt bảo mật, deploy)?

## 2. Phân tích yêu cầu

Trình bày theo khung:
- **Mục tiêu nghiệp vụ & tiêu chí thành công** (đo được).
- **Stakeholder map:** tên/vai trò, quan tâm điều gì, mức ảnh hưởng (cao/thấp), cách làm việc với họ.
- **Scope In / Scope Out:** ghi rõ cái *không* làm — đây là công cụ mạnh nhất để chống phình scope.
- **Danh sách epic/tính năng với MoSCoW:**
  - Must: thiếu thì không ra mắt được.
  - Should: quan trọng nhưng có cách tạm thời.
  - Could: có thì tốt.
  - Won't (lần này): đã thống nhất để sau.
  - Quy tắc ngón tay cái: Must ≤ ~60% tổng effort để còn dư địa khi có sự cố.
- **Yêu cầu phi chức năng (NFR):** hiệu năng, bảo mật, khả dụng, khả năng mở rộng, tương thích.
- **Phụ thuộc:** team/hệ thống khác, quyết định đang chờ.
- **Giả định & ràng buộc:** mọi điều đang "coi như đúng" — mỗi giả định sai là một rủi ro tiềm ẩn.

💡 Góc PM: Scope Out và danh sách giả định là thứ PM mới hay bỏ qua nhất, nhưng lại là thứ bảo vệ PM khi lãnh đạo hỏi "sao trễ".

## 3. WBS & ước lượng man-day

**WBS (Work Breakdown Structure)** — chia nhỏ công việc đến mức mỗi đầu việc ≤ 5 MD (lớn hơn thì khó ước lượng chính xác).

Cấu trúc gợi ý theo giai đoạn:
- Khởi động & phân tích (BA, SA): làm rõ nghiệp vụ, SRS/user story, prototype/wireframe.
- Thiết kế (SA, TL): kiến trúc, thiết kế DB, API contract, setup môi trường/CI-CD.
- Phát triển (Dev, TL): theo epic/tính năng, chia FE/BE/Mobile nếu có.
- Kiểm thử (QA hoặc người được giao): viết test case, test chức năng, regression, test hiệu năng/bảo mật nếu cần.
- UAT & triển khai: hỗ trợ UAT, sửa lỗi UAT, deploy, đào tạo người dùng, tài liệu.
- Hypercare: 1–2 tuần hỗ trợ sau go-live.

**Cách ước lượng:**
- Hỏi TL/SA ước lượng phần kỹ thuật, BA ước lượng phần nghiệp vụ — PM không tự đoán một mình. Trình bày con số đề xuất như "ước lượng ban đầu, cần TL xác nhận".
- Với đầu việc không chắc chắn, dùng **ước lượng 3 điểm (PERT):** E = (Lạc quan + 4×Khả dĩ + Bi quan) / 6.
- Tỉ lệ tham khảo (điều chỉnh theo dự án):
  - BA: 10–15% tổng effort
  - SA/thiết kế: 5–10%
  - Kiểm thử: 25–35% effort dev
  - Sửa lỗi (bug fixing): 15–20% effort dev
  - Quản lý dự án, họp, review: 10–15%
- **Buffer dự án:** 10–20% tùy độ không chắc chắn (công nghệ mới, tích hợp bên ngoài, yêu cầu chưa rõ → mức cao). Ghi buffer thành dòng riêng, không giấu vào từng task, để minh bạch khi báo cáo.

Trình bày bảng: Hạng mục | Vai trò | MD (khả dĩ) | Ghi chú/giả định. Tổng hợp theo vai trò và theo giai đoạn. Quy đổi MM = MD / 20.

## 4. Nguồn lực & năng lực thực tế

- **Focus factor:** một người không làm 8 tiếng code/ngày. Dùng 0.7–0.8 cho người toàn thời gian (họp, hỗ trợ, gián đoạn). Người kiêm nhiệm nhân thêm tỉ lệ phân bổ.
  - Năng lực (MD/sprint) = số người × số ngày làm việc trong sprint × % phân bổ × focus factor.
- **Thời gian = effort / năng lực**, và tính theo **vai trò nút cổ chai** (vai trò có tỉ lệ effort/năng lực cao nhất quyết định timeline).
- Thêm người không rút ngắn tuyến tính (Luật Brooks): người mới cần 2–4 tuần làm quen và tốn thời gian người cũ kèm.
- SA và TL thường bị chia sẻ cho nhiều dự án → nút cổ chai về review/quyết định kỹ thuật.
- Đội hình thường thay đổi theo sprint (người vào/ra, % đổi, nghỉ phép, junior/senior). Lập bảng **người × sprint** và tính bằng `scripts/capacity.py` — chi tiết trong `references/resource-planning.md`. Nếu chưa biết tên, dùng "Dev BE #1".

## 5. Timeline Hybrid & đề xuất độ dài sprint

**Khung giai đoạn Hybrid** (đặt milestone ở cuối mỗi giai đoạn để báo cáo lãnh đạo):
1. Inception / Khởi động (1–3 tuần): làm rõ yêu cầu, kiến trúc, backlog ban đầu, setup môi trường. Milestone: chốt scope & kiến trúc.
2. Build / Phát triển (N sprint): mỗi sprint ra phần mềm chạy được, demo cho PO. Milestone: MVP/feature complete.
3. Stabilization / Ổn định (1–2 sprint hoặc 1–3 tuần): regression, hiệu năng, sửa lỗi, hardening. Milestone: code freeze.
4. UAT (1–3 tuần): người dùng nghiệp vụ kiểm thử. Milestone: UAT sign-off.
5. Go-live & Hypercare (1–2 tuần).

Các giai đoạn có thể chồng lấn (ví dụ BA phân tích sprint sau trong khi dev làm sprint hiện tại) — đó là lợi thế của Hybrid.

**Đề xuất độ dài sprint** — luôn đưa một con số cụ thể kèm lý do:
- **2 tuần** (mặc định tốt): yêu cầu còn thay đổi, PO có thời gian review thường xuyên, team mới làm Scrum, cần phản hồi nhanh.
- **3 tuần**: tính năng lớn khó chia nhỏ, có tích hợp hệ thống khác cần thời gian, PO/stakeholder bận khó demo 2 tuần/lần, overhead họp 2 tuần thấy nặng.
- **4 tuần**: yêu cầu khá ổn định, dự án dài (>9 tháng), nhiều phụ thuộc bên ngoài, lãnh đạo chỉ cần báo cáo tháng. Nhược điểm: phát hiện vấn đề chậm.
- Không đổi độ dài sprint giữa chừng nếu không có lý do mạnh — velocity mất ý nghĩa so sánh.

**Lịch thực tế:** dùng ngày cụ thể (ngày bắt đầu → ngày kết thúc), trừ ngày lễ Việt Nam (Tết Dương lịch 1/1, Tết Nguyên Đán, Giỗ Tổ 10/3 ÂL, 30/4–1/5, 2/9 và ngày liền kề). Hỏi ngày bắt đầu nếu chưa biết; nếu không có thì giả định thứ Hai tuần sau và ghi rõ.

Tết Nguyên Đán: mùng 1 Tết 2027 là **thứ Bảy 06/02/2027**; mùng 1 Tết 2028 là **thứ Tư 26/01/2028**. Lịch nghỉ chính thức thường được công bố vài tháng trước; nếu có công cụ tìm kiếm thì tra lịch nghỉ Tết của năm đó, nếu chưa có thì giả định nghỉ khoảng 29 Tết → mùng 5 (với 2027: khoảng 04/02–10/02) và ghi rõ là giả định. Tuần trước và sau Tết năng suất giảm, người dùng nghiệp vụ khó tham gia UAT — tránh go-live và UAT trong khoảng này.

## 6. Kế hoạch sprint

Cho mỗi sprint: Sprint # | Ngày | Mục tiêu sprint (1 câu, hướng giá trị) | Hạng mục chính | Năng lực (MD) | Effort dự kiến (MD) | Ghi chú/phụ thuộc.
- Lên kế hoạch ~80–85% năng lực, phần còn lại cho phát sinh.
- Sprint đầu tiên thường đạt thấp hơn (team làm quen) — lập kế hoạch nhẹ hơn.
- Ưu tiên Must sớm, rủi ro kỹ thuật cao sớm (làm spike/PoC ở sprint 1–2) để phát hiện vấn đề khi còn thời gian xoay xở.
- Mỗi sprint kết thúc bằng demo cho PO/stakeholder.

## 7. Quản lý rủi ro

**Risk register:** ID | Rủi ro (nguyên nhân → hậu quả) | Xác suất (Cao/TB/Thấp) | Ảnh hưởng (Cao/TB/Thấp) | Mức độ | Biện pháp phòng ngừa | Phương án dự phòng | Người phụ trách | Dấu hiệu cảnh báo.

Mức độ: Cao×Cao, Cao×TB, TB×Cao → **Cao**; TB×TB, Thấp×Cao, Cao×Thấp → **Trung bình**; còn lại **Thấp**.

Danh mục rủi ro hay gặp ở dự án phần mềm nội bộ (dùng để gợi ý, chỉ chọn cái liên quan):
- Yêu cầu chưa rõ/thay đổi liên tục; PO không có thời gian; nhiều phòng ban có yêu cầu mâu thuẫn.
- Nhân sự bị điều sang việc khác/dự án gấp; nghỉ việc; phụ thuộc 1 người duy nhất hiểu một mảng (bus factor = 1).
- Không có QA chuyên trách → chất lượng thấp, lỗi phát hiện muộn.
- Tích hợp hệ thống khác: API chưa có, team kia không ưu tiên, môi trường test không sẵn.
- Dữ liệu cũ bẩn, migrate lâu hơn dự kiến.
- Công nghệ mới với team; hiệu năng không đạt.
- Quy trình duyệt nội bộ (bảo mật, hạ tầng, mua license) chậm.
- UAT chậm vì người dùng bận việc chính; người dùng không chịu đổi thói quen (adoption).
- Tết/mùa cao điểm nghiệp vụ trùng giai đoạn quan trọng.

Mỗi rủi ro Cao phải có biện pháp cụ thể và người phụ trách. Rủi ro khác issue: rủi ro *có thể* xảy ra, issue *đã* xảy ra.

## 8. Vận hành dự án

**RACI** (Responsible – làm, Accountable – chịu trách nhiệm cuối, Consulted – được hỏi ý kiến, Informed – được thông báo) cho các hoạt động chính: chốt yêu cầu, thiết kế kiến trúc, ước lượng, code review, kiểm thử, duyệt release, báo cáo lãnh đạo. Mỗi hoạt động có đúng một A.

**Ceremonies (Hybrid):**
- Daily standup 15 phút (team trên ~10 người thì chia theo nhóm — đừng để 20 người đứng 15 phút).
- Sprint planning (2h/2 tuần sprint), Sprint review/demo với PO (1h), Retro (1h), Backlog refinement giữa sprint (1h, BA + TL + PO).
- Steering/báo cáo lãnh đạo: theo milestone hoặc hàng tháng.
- Báo cáo tuần ngắn gửi stakeholder.

**Kế hoạch truyền thông:** Đối tượng | Nội dung | Tần suất | Hình thức | Người gửi.

**DoR (Definition of Ready)** cho user story: có mô tả, tiêu chí chấp nhận, thiết kế/UI nếu cần, đã ước lượng, không bị chặn.
**DoD (Definition of Done):** code review xong, unit test, đã test chức năng, merge, deploy lên môi trường test, PO chấp nhận.

## 9. Checklist trước khi chốt

- [ ] Scope In/Out và MoSCoW đã được PO đồng ý
- [ ] Ước lượng có TL/SA xác nhận (hoặc ghi rõ là ước lượng sơ bộ)
- [ ] Có effort kiểm thử và người phụ trách kiểm thử
- [ ] Có buffer, có trừ ngày lễ/nghỉ phép
- [ ] Tổng man-day khớp giữa các bảng; ngày sprint liên tục, không chồng/hở
- [ ] Rủi ro Cao có biện pháp và người phụ trách
- [ ] Danh sách quyết định cần lãnh đạo chốt, có hạn
- [ ] Việc PM cần làm trong 2 tuần tới
