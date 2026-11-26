# Báo cáo Day 14 — Triệu Hoàng Hiếu — 2A202603294

- Mã học viên dùng với `--student`: `2A202603294`
- `seed_tag` trong `frames_A.txt`: `82ac3100fd`
- Công cụ hỗ trợ: Codex hỗ trợ chạy script, xem ảnh và soạn báo cáo. Các phần chưa kiểm chứng được ghi rõ, không coi pre-label là nhãn đã sửa.

## 1. Dự đoán trước sweep (bước 5b)

Ghi trước khi chạy sweep, dựa trên ảnh camera và BEV của `s01f27`, `s04f24`, `s05f30`. Giữ nguyên phần này sau khi có kết quả.

- Tham số dự đoán giảm công sửa nhiều nhất: tăng `score_thr` từ 0.1 lên khoảng 0.3–0.4. Thử thêm `min_points=5` để loại hộp rất thưa điểm, nhưng không giả định bộ lọc này luôn có lợi.
- Lý do: `s01f27` có nhiều hộp Car dọc dải cây và xe đạp dựng bên đường; `s05f30` cũng có nhiều hộp trên hàng cây. Ở `s04f24`, nhiều ô tô thật đã có hộp, trong khi người và người lái xe hai bánh tại giao lộ có thể bị sót. Tăng ngưỡng có thể giảm hộp thừa, nhưng cũng có thể làm mất vật thể thật.
- Tiêu chí đối chiếu: chi phí `0.3*xóa + 1.0*thêm + 0.5*sửa`. Vì thêm hộp tốn nhiều hơn xóa, không chọn cấu hình chỉ dựa vào số hộp ít đi. Chưa kết luận cấu hình tốt nhất khi chưa có nhãn tham chiếu.

## 2. Tập A: kiểm tra nhãn và tune

Chưa hoàn thành kiểm tra cuboid trên cả Top/Side/Front và camera. Chưa có nhãn tham chiếu A đã xác nhận; chưa chạy sweep.

| Cấu hình | Xóa | Thêm | Sửa | Chi phí |
|---|---:|---:|---:|---:|
| Gốc | Chưa đo | Chưa đo | Chưa đo | Chưa đo |
| `best_config.json` | Chưa đo | Chưa đo | Chưa đo | Chưa đo |

- Tham số đã đổi: chưa có kết quả.
- Leave-one-out: chưa chạy.
- Độ ổn định trên từng frame: chưa đánh giá.

## 3. Trước/sau (bước 8)

Chưa có ảnh compare hoặc số đo. Chưa kết luận dự đoán ở mục 1 đúng hay sai.

## 4. Tập B

Đã sinh danh sách 12 frame. Chưa có nhãn B đã kiểm tra, chưa đo công sửa.

| Xóa | Thêm | Sửa | Chi phí |
|---:|---:|---:|---:|
| Chưa đo | Chưa đo | Chưa đo | Chưa đo |

## 5. Giới hạn

- Chỉ 3 frame tune nên cấu hình có thể overfit; cần đọc kết quả leave-one-out và kiểm tra tập B riêng.
- Model học trên KITTI, khác miền dữ liệu VF; không học trực tiếp Truck/Bus và có thể bỏ sót Pedestrian/Cyclist.
- Chi phí sửa là công thức quy ước, không phải thời gian sửa thực tế và không thể quy thành số giờ tiết kiệm.
- Nhãn do model tạo hoặc AI hỗ trợ vẫn cần người gán nhãn kiểm tra trước khi nộp, theo yêu cầu lab.
