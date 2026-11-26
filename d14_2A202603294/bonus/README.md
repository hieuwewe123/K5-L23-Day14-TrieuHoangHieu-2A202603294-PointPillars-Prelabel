# Bonus hướng 2 — PointPillars chạy trong CVAT

## Mục tiêu và trạng thái

Triển khai PointPillars thành function Nuclio để CVAT tự sinh cuboid từ dữ liệu PCD, thay vì tải file dự đoán offline vào task. Phần chạy model, lưu cuboid và so khớp đã thực hiện thành công. **Video màn hình chưa có; chưa khẳng định đủ bằng chứng cho mức +3.**

Thực hiện ngày 26/11/2026, trong giới hạn 45 phút của đề. Model và runtime được triển khai trên CVAT Docker local; dùng task bonus riêng để giữ nhãn đã sửa của bài chính.

## Thiết lập

- Mã học viên: `2A202603294`.
- Function: `pp-2a202603294`; Nuclio `1.16.3-amd64`; CVAT `2.81.0`.
- Task: [D14-2A202603294-BONUS-PointPillars](http://localhost:8080/tasks/31), job [30](http://localhost:8080/tasks/31/jobs/30).
- Code function: [`bonus/pointpillars`](../../bonus/pointpillars/README.md).
- Bộ frame: đúng 12 frame của `frames_B.txt`; cấu hình `score_thr=0.5`, `min_points=0` từ `best_config.json`.
- Runtime online: Python 3.10.22, PyTorch 2.5.1+cpu, NumPy 2.1.3.
- Runtime offline: Python 3.15.2, PyTorch 2.15.0+cpu, NumPy 2.5.5.
- Weights upstream: commit `620e6b0d07e4cb37b7b0114f26b934e8be92a0ba`; hash weights và cấu hình nằm trong `summary.json`.

## Quy trình đã chạy

1. Bật Nuclio và serverless cho CVAT; dashboard bind `127.0.0.1:8070`.
2. Viết bộ đọc PCD binary `x y z rgb`, đảo intensity theo công thức log-grayscale của lab.
3. Bọc `vf_pp.core.Detector` trong Nuclio, nạp model một lần và trả cuboid đúng 16 số.
4. Build function; xử lý lỗi dependency ở lần đầu; kiểm tra function đạt `ready` và xuất hiện trên trang Models của CVAT.
5. Gửi request auto-annotation qua API CVAT cho task 31 ở threshold 0.5. Request hoàn tất 100%, không exception, thời gian worker khoảng **56,80 giây**.
6. Đọc kết quả thực từ `GET /api/jobs/30/annotations`: **139 cuboid dạng Shape**, không có Track.
7. So với `pred_B.json` offline bằng ghép một-một, cùng lớp, khoảng cách Euclid của tâm XYZ ≤ 0,5 m.
8. Kiểm tra hash dữ liệu annotations task 29/30 trước/sau: **không thay đổi**.

## Kết quả so khớp

| Frame | Hộp CVAT | Hộp offline | Cặp cùng lớp, tâm ≤ 0,5 m |
|---|---:|---:|---:|
| s02f00 | 7 | 7 | 7 |
| s02f19 | 18 | 19 | 18 |
| s02f45 | 8 | 10 | 8 |
| s03f25 | 7 | 7 | 7 |
| s03f43 | 10 | 9 | 9 |
| s03f58 | 13 | 13 | 13 |
| s04f11 | 14 | 14 | 14 |
| s04f30 | 13 | 13 | 13 |
| s04f55 | 8 | 8 | 8 |
| s05f01 | 19 | 19 | 19 |
| s05f24 | 14 | 14 | 14 |
| s05f48 | 8 | 8 | 8 |
| **Tổng** | **139** | **141** | **138** |

Có 1 hộp online và 3 hộp offline không tìm được cặp theo tiêu chí trên. Tỷ lệ khớp là khoảng 99,28% số hộp online và 97,87% số hộp offline. Đây là **độ nhất quán giữa hai pipeline**, không phải precision/recall so với ground truth.

## Giới hạn và giải thích khác biệt

- Intensity từ PCD đã bị lượng tử hóa và giới hạn khi đổi thành màu; đảo ngược chỉ khôi phục xấp xỉ.
- Phiên bản PyTorch, Python và nền tảng online/offline khác nhau. Chưa làm thí nghiệm riêng để tách ảnh hưởng của runtime và intensity.
- Các hộp gần threshold/NMS có thể bị giữ hoặc loại khác nhau khi đầu vào hoặc phép tính thay đổi nhẹ.
- Khớp tâm và lớp không chứng minh kích thước, yaw hoặc độ khít hộp đúng. Kết quả model vẫn là pre-label, có hộp thừa và vật bị sót.
- Chưa có video màn hình. Cần quay model trên trang Models và cuboid trong job bonus để bổ sung bằng chứng theo đề.

## Bằng chứng trong repo

- `function_ready.json`: cấu hình và trạng thái function thực tế.
- `invocation.json`: phản hồi lúc gửi yêu cầu CVAT.
- `request_status.json`: request `finished`, progress 100%, exception null.
- `nuclio_B.json`: cuboid đọc từ annotations của job bonus sau khi chạy.
- `center_matches.csv`: kết quả ghép theo từng frame.
- `inference.log`: log nạp model và suy luận thực tế của function.
- `protected_tasks.json`: hash annotations A/B trước/sau khớp nhau.
- `summary.json`: phiên bản, thời gian, tổng số và hash model/cấu hình.
- `build_attempt1.json`: lỗi build thật ở lần đầu, đã được xử lý.

## Video còn cần bổ sung

1. Mở `http://localhost:8080/models`, hiển thị model PointPillars 2A202603294 CPU.
2. Quay màn hình, mở `http://localhost:8080/tasks/31/jobs/30`, chọn hộp và chuyển qua vài frame để thấy cuboid trên point cloud.
3. Lưu video ngắn vào `d14_2A202603294/bonus/demo.mp4`, commit và push; sau đó cập nhật trạng thái video trong báo cáo.

Chưa bổ sung video màn hình. Code function, log chạy và bảng so khớp đã được lưu; video vẫn là bằng chứng còn thiếu theo yêu cầu bonus.
